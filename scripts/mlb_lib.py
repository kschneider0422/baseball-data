
import pandas as pd
import numpy as np
import statsapi
from time import sleep
from datetime import datetime, date, timedelta
from lookup import team_lookup, team_codes, divisions
# from lookup import team_colors
import os.path
from statsmodels.nonparametric.smoothers_lowess import lowess


def daterange(start_date, end_date):
    # start and end dates inclusive
    for days in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(days)

def get_full_season_from_api(year):
    pickle_file = f'pickle/schedule_and_results_{year}.p'
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    columns = ['game_date', 'game_datetime', 
               'game_num', 'status', 
               'away_name', 'home_name', 
               'away_score', 'home_score']
    schedule_and_results = pd.DataFrame(columns=columns)
    game_list = statsapi.schedule(start_date=start_date, 
                                  end_date=end_date)
    for game in game_list:
        if game['game_type'] != 'R':
            continue
        game_id = game['game_id']
        game_data = [game[_] for _ in columns]
        schedule_and_results.loc[game_id] = game_data
    schedule_and_results["game_date"] = pd.to_datetime(
        schedule_and_results["game_date"])
    schedule_and_results["game_datetime"] = pd.to_datetime(
        schedule_and_results["game_datetime"])
    schedule_and_results.index.name = 'game_id'
    schedule_and_results.sort_values('game_datetime', inplace=True)
    schedule_and_results.to_pickle(pickle_file)
    
    return schedule_and_results

def get_full_season_from_file(year):
    pickle_file = f'pickle/schedule_and_results_{year}.p'
    if os.path.isfile(pickle_file):
        schedule_and_results = pd.read_pickle(pickle_file)
    else:
        schedule_and_results = get_full_season_from_api(year)
    return schedule_and_results


def get_season(year=None):
    if year is None:
        year = datetime.now().year
    return get_full_season_from_file(year)

def update_season(year=None):
    if year is None:
        year = datetime.now().year
    return get_full_season_from_api(year)


def print_tally(df):
    tally = df.groupby(['status']).size()
    print(tally)
    
def print_day(df, the_date):
    print(the_date)
    games = df[df['game_date'] == the_date]
    for game_id, game_data in games.iterrows():
        print(game_data['away_name'], 
              game_data['away_score'],
              game_data['home_name'],
              game_data['home_score'],
              game_data['status'])


def get_completed_games(schedule, through_date=None):
    completed = schedule[(schedule['status'].str.startswith('Final'))
                         | (schedule['status'].str.startswith('Completed'))
                         | (schedule['status'].str.startswith('Game Over'))].copy()
    if through_date is not None:
        completed = completed[completed.game_date <= through_date]
    return completed
    
def select_games_to_be_played(df):
    incomplete_rows = df[(~df['status'].str.startswith('Final')) &
                         (~df['status'].str.startswith('Completed'))].copy()

    return incomplete_rows.copy()

def select_games_to_be_played_cg(df, cg):
    
    max_date = cg.game_date.max()


    return df[df.game_date > str(max_date)].copy()

def get_team_games(schedule, team_name):
    completed = get_completed_games(schedule)
    team_games = completed[(completed['home_name'] == team_name) 
                            | (completed['away_name'] == team_name)].copy()
    return team_games

def get_team_hitting_log(schedule, team_val):
    if len(team_val) <= 3:
        team_abbrev = team_val
        team = team_lookup[team_abbrev]
    else:
        team = team_val
        team_abbrev = team_lookup[team]
        
    year = schedule.game_date.max().year
    team = team_lookup[team_abbrev]
    team_games = get_team_games(schedule, team)
    p_file = f'pickle/{team_abbrev}_{year}_game_log.p'
    
    if os.path.isfile(p_file):
        log = pd.read_pickle(p_file)
    else:
        log = pd.DataFrame(columns=['game_date', 'game_datetime',
                                    'AB', 'R', 'H', '2B', '3B', 
                                    'HR', 'RBI', 'BB', 'SO', 
                                    'SB', 'CS', 'HBP', 'SF'])
        log.index.name = 'game_id'
    
    game_ids = list(team_games.index)
    logged_games = set(log.index)
    games_to_get = [_ for _ in game_ids if _ not in logged_games]
    
    for gid in games_to_get:
        box = statsapi.boxscore_data(gid)
        home_or_away = None
        if box['teamInfo']['away']['abbreviation'] == team_abbrev:
            home_or_away = 'away'
        else:
            home_or_away = 'home'
            
        stats = box[home_or_away]['teamStats']['batting']
        record = {'game_date': schedule.loc[gid].game_date,
                  'game_datetime': schedule.loc[gid].game_datetime,
                  'AB': stats['atBats'],
                  'R': stats['runs'],
                  'H': stats['hits'],
                  '2B': stats['doubles'],
                  '3B': stats['triples'],
                  'HR': stats['homeRuns'],
                  'RBI': stats['rbi'],
                  'BB': stats['baseOnBalls'],
                  'SO': stats['strikeOuts'],
                  'SB': stats['stolenBases'],
                  'CS': 0,
                  'HBP': 0,
                  'SF': 0}
        players = box[home_or_away]['players']
        player_info = box['playerInfo']
        boxscore_names = set([player_info[pid]['boxscoreName'] 
                              for pid in players.keys()])
        
        # Get hit by pitch
        for event in box['gameBoxInfo']:
            if event['label'] == 'HBP':
                hbps = event['value'].split(';')
                HBP = 0
                for hbp in hbps:
                    player, junk = hbp.strip().split(' (')
                    if player[-1].isdigit():
                        player, count = player.rsplit(' ', 1)
                        count = int(count)
                    else:
                        count = 1
                    if player in boxscore_names:
                        HBP += count
                record['HBP'] += HBP
                
        #Get sac fly
        for infotype in box[home_or_away]['info']:
            if infotype['title'] == 'BATTING':
                for event in infotype['fieldList']:
                    if event['label'] == 'SF':
                        sfs = event['value'][:-1].split(';')
                        SF = 0
                        for player in sfs:
                            player = player.strip()
                            if player[-1].isdigit():
                                player, count = player.rsplit(' ', 1)
                                count = int(count)
                            else:
                                count = 1
                            if player in boxscore_names:
                                SF += count
                        record['SF'] += SF
                        
        #Get caught stealing
        for infotype in box[home_or_away]['info']:
            if infotype['title'] == 'BASERUNNING':
                for event in infotype['fieldList']:
                    if event['label'] == 'CS':
                        css = event['value'][:-1].split(';')
                        CS = 0
                        for player in css:
                            player, junk = player.split(' (')
                            player = player.strip()
                            if player[-1].isdigit():
                                player, count = player.rsplit(' ', 1)
                                count = int(count)
                            else:
                                count = 1
                            if player in boxscore_names:
                                CS += count
                        record['CS'] += CS
                        
        log.loc[gid] = record
    log.sort_values('game_datetime', inplace=True)
    log.to_pickle(p_file)
    
    return log

def get_all_hitting_logs(schedule):
    hitting_logs = {}
    for team_short in team_codes:
        team_name = team_lookup[team_short]
        hitting_logs[team_name] = {}
        hitting_logs[team_name]['Hitting'] = get_team_hitting_log(
            schedule, team_short)
  
    return hitting_logs

def get_pitching_log(schedule, team_short, hitting_logs=None):

    if hitting_logs is None:
        hitting_logs = get_all_hitting_logs(schedule)
        
    year = schedule.game_date.max().year
    
    team = team_lookup[team_short]
    p_file = f'pickle/{team_short}_{year}_pitching_log.p'
    
    if os.path.isfile(p_file):
        log = pd.read_pickle(p_file)
    else:
        log = pd.DataFrame(columns=['game_date', 'game_datetime',
                                    'AB', 'R', 'H', '2B', '3B', 
                                    'HR', 'RBI', 'BB', 'SO', 
                                    'SB', 'CS', 'HBP', 'SF'])
        log.index.name = 'game_id'
        
    hitting_log = hitting_logs[team]['Hitting']
    
    game_ids = list(hitting_log.index)
    logged_games = set(log.index)
    games_to_get = [_ for _ in game_ids if _ not in logged_games]
    
    

    for gid in games_to_get:
        
        record = schedule.loc[gid]
        home = record.home_name
        away = record.away_name
        opponent = home if away == team else away
        opp_log = hitting_logs[opponent]['Hitting']
        opp_record = opp_log.loc[gid]
        log.loc[gid] = opp_record
        
    log.to_pickle(p_file)
        
    return log


    
def get_all_logs(schedule):
    logs = get_all_hitting_logs(schedule)
    for team_short in team_codes:
        team_name = team_lookup[team_short]
        logs[team_name]['Pitching'] = get_pitching_log(
            schedule, team_short, logs)
        
    return logs

def ops_log_cts(log):
    team_log = log.copy()
    team_log['obp_n'] = team_log['H'] + team_log['BB'] + team_log['HBP']
    team_log['obp_d'] = (team_log['AB'] + team_log['BB'] 
                         + team_log['HBP'] + team_log['SF'])
    team_log['slg_n'] = (team_log['H'] + team_log['2B'] 
                         + 2 * team_log['3B'] + 3 * team_log['HR'])
    team_log['slg_d'] = team_log['AB']
    team_log = team_log[['game_datetime',
                         'obp_n',
                         'obp_d',
                         'slg_n',
                         'slg_d']]
    team_log.sort_values('game_datetime', inplace=True)
    team_log.set_index('game_datetime', inplace=True)
    return team_log

def ops_log_cumulative(log):
    team_log = ops_log_cts(log).cumsum()
    team_log['obp'] = team_log['obp_n'] / team_log['obp_d']
    team_log['slg'] = team_log['slg_n'] / team_log['slg_d']
    team_log['ops'] = team_log['obp'] + team_log['slg']
    return team_log

def ops_log_rolling(log, games=10):
    team_log = ops_log_cts(log).rolling(games).mean().tail(
        len(log) - games + 1)
    team_log['obp'] = team_log['obp_n'] / team_log['obp_d']
    team_log['slg'] = team_log['slg_n'] / team_log['slg_d']
    team_log['ops'] = team_log['obp'] + team_log['slg']
    return team_log

def ops_log_smoothed(log, games=10):
    log_c = log.copy()
    n_games= len(log_c)
    cols = ['obp', 'slg', 'ops']
    raw_data = [np.array(log_c[col]) for col in cols]
    smoothed_data = [lowess(rd, range(n_games), 
                            frac=games/n_games)[:, 1] for rd in raw_data]
    for col, sd in zip(cols, smoothed_data):
        log_c[f'smoothed_{col}'] = sd
    return log_c

def league_average(logs):
    log_list = []
    for team_short in team_codes:
        team_name = team_lookup[team_short]
        log = logs[team_name]['Hitting'].copy()
        log.reset_index(inplace=True)
        log_list.append(log) 
    all_logs = pd.concat(log_list, ignore_index=True)

    log = ops_log_rolling(all_logs, 300)
    log = ops_log_smoothed(log, 10)
    
    return log


def get_homer_log(schedule, year=None):
    if year is None:
        year = datetime.now().year
    homer_file = f'pickle/homers_{year}.p'
    if os.path.isfile(homer_file):
        homer_df = pd.read_pickle(homer_file)

    else:
        homer_df = pd.DataFrame(columns=['game_id', 
                                          'team', 
                                          'batter', 
                                          'inning', 
                                          'half_inning', 
                                          'runs',
                                          'timestamp'])
    completed = get_completed_games(schedule)
    game_ids = list(completed.index)
    games_logged = set(homer_df.game_id)
    games_to_get = [_ for _ in game_ids if _ not in games_logged]
    for gid in games_to_get:
        starting_row = len(homer_df)
        scoring_plays = statsapi.game_scoring_play_data(gid)
        home = scoring_plays['home']['name']
        away = scoring_plays['away']['name']
        plays = scoring_plays['plays']
        for play in plays:
            description = play['result']['description']
            test_strings = [' homers',
                            ' hits a grand slam',
                            ' hits an inside-the-park']
            for test_string in test_strings:
                if test_string in description:
                    half_inning = play['about']['halfInning']
                    inning = play['about']['inning']
                    team = away if half_inning == 'top' else home
                    batter = description.split(test_string)[0]
                    if batter.startswith('Umpire'):
                        batter = batter.split(': ')[1]
                    runs = description.count('scores') + 1
                    timestamp = play['about']['endTime']
                    row = len(homer_df)
                    record = {'game_id': gid, 
                              'team': team, 
                              'batter': batter, 
                              'inning': inning, 
                              'half_inning': half_inning, 
                              'runs': runs,
                              'timestamp': timestamp}
                    homer_df.loc[row] = record
                    print(team, batter, timestamp)
                    break
        ending_row = len(homer_df)
        if starting_row == ending_row:
            record = {'game_id': gid, 
                      'team': 'na', 
                      'batter': 'na', 
                      'inning': 0, 
                      'half_inning': 'na',
                      'runs': 0,
                      'timestamp': 'na'}
            homer_df.loc[ending_row] = record
        sleep(5)
    homer_df.to_pickle(homer_file)
    return homer_df

def get_records_from_schedule(schedule):
    
    completed = get_completed_games(schedule)

    completed['away_win'] = completed['away_score'] > completed['home_score']
    completed['away_win'] = completed['away_win'].astype('int')
    completed['home_win'] = 1 - completed['away_win']


    record_cols = ['W', 'L', 'RS', 'RA']
    
    # Get away games
    away_records = completed.groupby(
        by=['away_name'])[['away_win', 'home_win',
                           'away_score', 'home_score']].sum()
    away_records.columns = record_cols
    away_records.index.name = 'Team'


    # Get home games
    home_records = completed.groupby(
        by=['home_name'])[['home_win', 'away_win',
                           'home_score', 'away_score']].sum()
    home_records.columns = record_cols
    home_records.index.name = 'Team'

    # Combine home and awar
    overall_records = pd.concat(
        [away_records.reset_index(), 
         home_records.reset_index()]).groupby(by='Team').sum()
    
    
    div_lookup = {}
    lg_lookup = {}
    for division, teams in divisions.items():
        league = division.split(' ')[0]
        for team_short in teams:
            team_name = team_lookup[team_short]
            div_lookup[team_name] = division
            lg_lookup[team_name] = league
            
    overall_records['Division'] = pd.Series(div_lookup)
    overall_records['League'] = pd.Series(lg_lookup)

    overall_records.reset_index(inplace=True)

    div_order = ['AL East', 'AL Central', 'AL West', 
                 'NL East', 'NL Central', 'NL West']
    lg_order = ['AL', 'NL']

    overall_records['League'] = pd.CategoricalIndex(
        overall_records['League'], lg_order,  ordered=True)

    overall_records['Division'] = pd.CategoricalIndex(
        overall_records['Division'], div_order,  ordered=True)
    overall_records.set_index(['League', 'Division', 'Team'], inplace=True)
    overall_records['PCT'] = overall_records.W / (overall_records.W 
                                                  + overall_records.L)
    overall_records = overall_records[['W', 'L', 'PCT', 'RS', 'RA']]
    overall_records.sort_values(['League', 'Division', 'PCT'], 
                                ascending=[True, True, False], 
                                inplace=True)

    return overall_records

def get_records_from_schedule_w_home_away(df, through_date=None):
    
    completed_games = get_completed_games(df, through_date=through_date)
    cg = completed_games
    cg['away_win'] = cg['away_score'] > cg['home_score']
    cg['away_win'] = cg['away_win'].astype('int')
    cg['home_win'] = 1 - cg['away_win']


    record_cols = ['W', 'L', 'RS', 'RA']
    
    # Get away games
    away_records = cg.groupby(by=['away_name'])[['away_win', 'home_win',
                                                 'away_score', 'home_score']].sum()
    away_records.columns = [_ + '_away' for _ in record_cols]
    away_records.index.name = 'TEAM'


    # Get home games
    home_records = cg.groupby(by=['home_name'])[['home_win', 'away_win',
                                                 'home_score', 'away_score']].sum()
    home_records.columns = [_ + '_home' for _ in record_cols]
    home_records.index.name = 'TEAM'

    # Combine home and awar
    overall_records = pd.concat([home_records, away_records], axis=1)
    
    for col in record_cols:
        overall_records[col] = overall_records[col + '_away'] + overall_records[col + '_home']

    return overall_records