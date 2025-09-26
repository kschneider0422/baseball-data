import pandas as pd
from datetime import date, timedelta, datetime

from mlb_lib import (get_season,
                     get_completed_games,
                     get_records_from_schedule,
                     get_records_from_schedule_w_home_away,
                     select_games_to_be_played_cg)

from random import random, choice, shuffle
from itertools import combinations as combos
from copy import deepcopy

from functools import cmp_to_key


def pythagorean(rs, ra):
    return rs**2 / (rs**2 + ra**2)

def project_wins(wins, losses, rs, ra, ngames):
    games_left = ngames - wins - losses
    pythag = pythagorean(rs, ra)
    
    return wins + games_left * pythag

def win_distro(wins, losses, rs, ra, ngames):
    games_left = ngames - wins - losses
    pythag = pythagorean(rs, ra)
    p = pythag
    q = 1 - p
    
    distro = {_: 0.0 for _ in range(wins - 1, wins + games_left + 1)}
    distro[wins] = 1.0
    for _ in range(games_left):
        for stretch_wins in range(wins + games_left, wins - 1, -1):
            distro[stretch_wins] = q * distro[stretch_wins] + p * distro[stretch_wins - 1]
    del distro[wins - 1]
    return distro
        
def get_stretch_wins(W, L, P, G):
    W = int(W)
    L = int(L)
    games_left = G - W - L
    for _ in range(games_left):
        if random() < P:
            W += 1
    return W
        
def one_trial(team, div_df, wc_df, ngames):
    
    all_df = pd.concat([div_df, wc_df]).drop_duplicates()
    all_df['sim_W'] = all_df.apply(axis=1, func=lambda row: get_stretch_wins(row.W, row.L, row.pyth, ngames))

    div_teams = list(div_df.index)
    
    div_dict = {}
    for div_team in div_teams:
        sw = int(all_df.loc[div_team]['sim_W'])
        if sw not in div_dict:
            div_dict[sw] = []
        div_dict[sw].append(div_team)
        
    div_winners = div_dict[max(div_dict.keys())]
    div_winner = choice(div_winners)
    
    if div_winner == team:
        return "Win Division"
    
    wc_teams = list(wc_df.index)
    wc_dict = {}
    for wc_team in wc_teams:
        sw = int(all_df.loc[wc_team]['sim_W'])
        if sw not in wc_dict:
            wc_dict[sw] = []
        wc_dict[sw].append(wc_team)
        
        
    wc_list = []
    
    while len(wc_list) < 3:
        key = max(wc_dict.keys())
        wc_winners = wc_dict[key]
        shuffle(wc_winners)
        wc_list += wc_winners
        wc_dict.pop(key)
        
    if team == wc_list[0]:
        return "Wild Card 1"
    if team == wc_list[1]:
        return "Wild Card 2"
    if team == wc_list[2]:
        return "Wild Card 3"
    
    return "Miss Playoffs"
        
        
        
    
def get_hth(schedule, through_date):
    played_games = get_completed_games(schedule, through_date=through_date)
    played_games['left'] = played_games[['away_name', 'home_name']].min(axis=1)
    played_games['right'] = played_games[['away_name', 'home_name']].max(axis=1)
    
    played_games['left_win'] = (((played_games['away_name'] < played_games['home_name']) & 
                                 (played_games['away_score'] > played_games['home_score'])) | 
                                ((played_games['home_name'] < played_games['away_name']) & 
                                 (played_games['home_score'] > played_games['away_score'])))
    played_games['left_win'] = played_games['left_win'].astype('int')
    played_games['right_win'] = 1 - played_games['left_win'] 
    
    played_games['games_left'] = 0
    
    unplayed_games = select_games_to_be_played_cg(schedule, played_games)
    unplayed_games['left'] = unplayed_games[['away_name', 'home_name']].min(axis=1)
    unplayed_games['right'] = unplayed_games[['away_name', 'home_name']].max(axis=1)
    unplayed_games['left_win'] = 0
    unplayed_games['right_win'] = 0
    unplayed_games['games_left'] = 1
    
    cols = ['left', 'right', 'left_win', 'right_win', 'games_left']
    
    results = pd.concat([played_games[cols], unplayed_games[cols]])

    hth = results.groupby(by=['left', 'right']).sum()

    return hth.to_dict(orient='index')



def sim_stretch(sim_dict, hth, games):  
    
    sim_dict = deepcopy(sim_dict)
    hth = deepcopy(hth)

    
    for game in games:
        away, home = game
        left = min(game)
        right = max(game)
        
        key = tuple([left, right])
        
        p = sim_dict[away]['P_away']
        q = sim_dict[home]['P_home']
        
        P = p / (p + q)
        R = random()
        
        winner = away if R < P else home

        away_win = 1 if winner == away else 0
        home_win = 1 - away_win
        
        sim_dict[away]['W'] += away_win
        sim_dict[away]['L'] += home_win
        sim_dict[home]['W'] += home_win
        sim_dict[home]['L'] += away_win
        
        left_win = 1 if winner == left else 0
        right_win = 1 - left_win
        
        hth[key]['left_win'] += left_win
        hth[key]['right_win'] += right_win
        hth[key]['games_left'] -= 1
        
    return sim_dict, hth

def rank_teams(sim_dict, hth, div_dict):

    def compare(a, b):
        wa = sim_dict[a]['W']
        la = sim_dict[a]['L']
        ga = wa + la
        wb = sim_dict[b]['W']
        lb = sim_dict[b]['L']
        gb = wb + lb
        if wa * gb == wb * ga:
            tup = tuple(sorted([a, b]))
            hthr = hth[tup]
            hthd = {tup[0]: hthr['left_win'],
                    tup[1]: hthr['right_win']}
            htha = hthd[a]
            hthb = hthd[b]
            if htha == hthb:
                # Using coin flip for 2nd tiebreaker rather than div record
                out = choice([-1, 1])
            else:
                out = htha - hthb
        else:
            out = wa - wb
        return out
            

    output = {}
    for lg, lg_dict in division_dict.items():
        wc_teams = []
        div_winners = []
        for div, div_set in lg_dict.items():
            shuffle(list(div_set))
            div_ranked = sorted(div_set, key=cmp_to_key(compare), reverse=True)
            winner, *rest = div_ranked
            div_winners.append(winner)
            wc_teams += rest
            
        div_winners = sorted(div_winners, key=cmp_to_key(compare), reverse=True)
        wc_teams = sorted(wc_teams, key=cmp_to_key(compare), reverse=True)
        
        teams = div_winners + wc_teams
        nteams = len(teams)

        output[lg] = pd.DataFrame(index=range(1, nteams + 1),
                                  data=teams,
                                  columns=['TEAM'])
        for _ in ['W', 'L']:
            output[lg][_] = output[lg]['TEAM'].map(lambda tm: sim_dict[tm][_])
            
    return output


def sim_wc_series(sim_dict, away, home):
    
    p = sim_dict[away]['P_away']
    q = sim_dict[home]['P_home']
    
    P = p / (p + q)
    away_wins = 0
    home_wins = 0
    for game in range(3):
        R = random()
        winner = away if R < P else home
        if winner == away:
            away_wins += 1
            if away_wins == 2:
                series_winner = away
                break
        else:
            home_wins += 1
            if home_wins == 2:
                series_winner = home
                break

    return series_winner

def sim_division_series(sim_dict, away, home):
    p = sim_dict[away]['P_away']
    q = sim_dict[home]['P_home']
    
    P1 = p / (p + q)
    
    p = sim_dict[away]['P_home']
    q = sim_dict[home]['P_away']
    
    P2 = p / (p + q)
    away_wins = 0
    home_wins = 0
    
    plist = [P1, P1, P2, P2, P1]
    
    for game in range(5):
        P = plist[game]
        R = random()
        winner = away if R < P else home
        if winner == away:
            away_wins += 1
            if away_wins == 3:
                series_winner = away
                break
        else:
            home_wins += 1
            if home_wins == 3:
                series_winner = home
                break

    return series_winner
    
def seven_game_series(sim_dict, away, home):
    
    p = sim_dict[away]['P_away']
    q = sim_dict[home]['P_home']
    
    P1 = p / (p + q)
    
    p = sim_dict[away]['P_home']
    q = sim_dict[home]['P_away']
    
    P2 = p / (p + q)
    away_wins = 0
    home_wins = 0
    
    plist = [P1, P1, P2, P2, P2, P1, P1]
    for game in range(7):
        P = plist[game]
        R = random()
        winner = away if R < P else home
        if winner == away:
            away_wins += 1
            if away_wins == 4:
                series_winner = away
                break
        else:
            home_wins += 1
            if home_wins == 4:
                series_winner = home
                break

    return series_winner
    
    
div_data = pd.read_csv('csv/mlb_divisions_2025.csv')
leagues = sorted(set(div_data['League']))
divisions = sorted(set(div_data['Division']))
division_dict = {league: {} for league in leagues}

for div in divisions:
    lg = div.split()[0]
    sub_df = div_data[div_data['Division'] == div]
    division_dict[lg][div] = set(sub_df['Team'])


schedule = get_season()

# overall_records = get_records_from_schedule_w_home_away(schedule)


current_date = date(2025, 9, 1)

print(current_date)
print()
trials = 1000000

overall_records = get_records_from_schedule_w_home_away(schedule, through_date=str(current_date))


for _ in ['away', 'home']:
    overall_records['P_' + _] = overall_records.apply(axis=1, func=lambda row: pythagorean(row['RS_' + _], row['RA_' + _]))
sim_dict = overall_records[['W', 'L', 'P_away', 'P_home']].to_dict(orient='index')

complete = get_completed_games(schedule, through_date=str(current_date))


head_to_head = get_hth(schedule, str(current_date))
unplayed_games = select_games_to_be_played_cg(schedule, complete)
games = list(zip(list(unplayed_games['away_name']), list(unplayed_games['home_name'])))




result_order = ["Division Winner 1",
                "Division Winner 2",
                "Division Winner 3",
                "Wild Card 1",
                "Wild Card 2",
                "Wild Card 3",
                "Miss Playoffs"]

results = {i % 7: r for i, r in enumerate(result_order, start=1)}

# target_team = 'Chicago Cubs'
# target_team = 'San Diego Padres'
# target_team = 'Atlanta Braves'
# target_team_league = 'NL'

# target_team = 'Seattle Mariners'
# target_team_league = 'AL'

tally_df = div_data[['Team', 'League']].copy()
tally_df.set_index('Team', inplace=True)
tally_df.columns = ['lg']


seed_df = div_data[['Team', 'League']].copy()
seed_df.set_index('Team', inplace=True)
seed_df.columns = ['lg']





tally_cols = ['po', 'bye', 'wcs', 
             'ds', 'lcs', 'ws']

for col in tally_cols:
    tally_df[col] = 0
    
for i in range(1, 7):
    seed_df[str(i)] = 0

result_dict = {_: 0 for _ in results.values()}
win_total = 0

champ_dict = {}
for trial in range(trials):
    if (trial + 1) % (trials // 10) == 0:
        print(trial + 1, 'of', trials)
        print()

        for team, wins in sorted(champ_dict.items(), key=lambda x: (-x[1], x[0])):
            print(f'{team} : {wins}')
        print()
    
    sd, hth = sim_stretch(sim_dict, head_to_head, games)
    lg_dfs = rank_teams(sd, hth, division_dict)
    NL_df = lg_dfs['NL']
    AL_df = lg_dfs['AL']
    
    nl_ranks = {NL_df.loc[_].TEAM: _ for _ in range(1, 7)}
    al_ranks = {AL_df.loc[_].TEAM: _ for _ in range(1, 7)}
    
    nl_wins = {NL_df.loc[_].TEAM: NL_df.loc[_].W for _ in range(1, 7)}
    al_wins = {AL_df.loc[_].TEAM: AL_df.loc[_].W for _ in range(1, 7)}
    
    for i in range(1, 7):
        tms = [NL_df.loc[i].TEAM, AL_df.loc[i].TEAM]
        for tm in tms:
            if i < 3:
                tally_df.loc[tm, 'bye'] += 1
            tally_df.loc[tm, 'po'] += 1
            seed_df.loc[tm, str(i)] += 1
    

    
    nl_wc_1 = sim_wc_series(sim_dict, NL_df.loc[5].TEAM, NL_df.loc[4].TEAM)
    nl_wc_2 = sim_wc_series(sim_dict, NL_df.loc[6].TEAM, NL_df.loc[3].TEAM)
    nl_ds_1 = sim_division_series(sim_dict, nl_wc_1, NL_df.loc[1].TEAM)
    nl_ds_2 = sim_division_series(sim_dict, nl_wc_2, NL_df.loc[2].TEAM)
    
    
    
    
    if nl_ranks[nl_ds_1] > nl_ranks[nl_ds_2]:
        nl_cs = seven_game_series(sim_dict, nl_ds_1, nl_ds_2)
    else:
        nl_cs = seven_game_series(sim_dict, nl_ds_2, nl_ds_1)
        
    
    
    al_wc_1 = sim_wc_series(sim_dict, AL_df.loc[5].TEAM, AL_df.loc[4].TEAM)
    al_wc_2 = sim_wc_series(sim_dict, AL_df.loc[6].TEAM, AL_df.loc[3].TEAM)
    al_ds_1 = sim_division_series(sim_dict, al_wc_1, AL_df.loc[1].TEAM)
    al_ds_2 = sim_division_series(sim_dict, al_wc_2, AL_df.loc[2].TEAM)
    
    if al_ranks[al_ds_1] > al_ranks[al_ds_2]:
        al_cs = seven_game_series(sim_dict, al_ds_1, al_ds_2)
    else:
        al_cs = seven_game_series(sim_dict, al_ds_2, al_ds_1)
    
    
    nlw = nl_wins[nl_cs]
    alw = al_wins[al_cs]
    
    if nlw == alw:
        R = random()
        if R < 0.5:
            nlw += 1
        else:
            alw += 1
            
    if nlw < alw:
        champ = seven_game_series(sim_dict, nl_cs, al_cs)
    else:
        champ = seven_game_series(sim_dict, al_cs, nl_cs)
        
    if champ not in champ_dict:
        champ_dict[champ] = 0
    champ_dict[champ] += 1
    
    for tm in [nl_wc_1, nl_wc_2, al_wc_1, al_wc_2]:
        tally_df.loc[tm, 'wcs'] += 1
    for tm in [nl_ds_1, nl_ds_2, al_ds_1, al_ds_2]:
        tally_df.loc[tm, 'ds'] += 1 
    for tm in [nl_cs, al_cs]:
        tally_df.loc[tm, 'lcs'] += 1 
    tally_df.loc[champ, 'ws'] += 1
    
    

tally_df = tally_df[tally_df.po > 0]  
tally_df.sort_values(by=['lg'] + tally_cols[::-1], ascending=False, inplace=True)

print(tally_df)
print()

seed_df['po'] = tally_df.po
seed_df = seed_df[seed_df.po > 0]
seed_df.drop('po', axis=1, inplace=True)
seed_df.sort_values(by=['lg'] + [str(i) for i in range(1, 7)], ascending=False, inplace=True)
print(seed_df)

print()
print(current_date)