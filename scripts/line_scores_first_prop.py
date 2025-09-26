from mlb_lib import get_season, get_completed_games, get_team_games
import pickle
# import os
# import statsapi
# from time import sleep
from lookup import divisions, team_lookup, team_codes, logos
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.ticker import (MultipleLocator,
                               FormatStrFormatter,
                               AutoMinorLocator,
                               MaxNLocator,
                               FixedLocator)

season = 2025
p_file = f'pickle/linescores_{season}.p'
with open(p_file, 'rb') as p:
    ls_dict = pickle.load(p)
    

schedule = get_season(season)
games = get_completed_games(schedule)
current_teams = set(schedule.home_name)


overall_W = 0
overall_G = 0

data = []
for short_team in team_codes:
    
    fruitless = 0
    bl_loss = 0
    trob = 0
    
    team = team_lookup[short_team]
    if team not in current_teams:
        continue


    team_games = get_team_games(games, team)
    
    record_when_scoring_first = [0, 0]
    record = [0, 0]
    

    
    for gid in team_games.index:
        
        game = team_games.loc[gid]
        line_score = ls_dict[gid]
        
        home_or_away = 'home' if line_score['home'] == team else 'away'
        
        innings = line_score['innings']
        
        n_innings = len(innings)
        
        away_runs = [0] * n_innings
        home_runs = [0] * n_innings
        
        first_to_score = None
        
        for inning in innings:
            num = inning['num']
            away_runs[num - 1] = inning['away'].setdefault('runs', 0)
            home_runs[num - 1] = inning['home'].setdefault('runs', 0)
        score_progression = [[0, 0]]
        for a, h in zip(away_runs, home_runs):
            if a > 0:
                new = [score_progression[-1][0] + a, score_progression[-1][1]]
                score_progression.append(new)
                
            if first_to_score is None and len(score_progression) == 2:
                first_to_score = 'away'
                
            if h > 0:
                new = [score_progression[-1][0], score_progression[-1][1] + h]
                score_progression.append(new)
                
            if first_to_score is None and len(score_progression) == 2:
                first_to_score = 'home'
                
        # leads = [a - h for a, h in score_progression]
        
        
        # away_largest_lead = max(leads)
        # home_largest_lead = -min(leads)
        # largest_lead = home_largest_lead if home_or_away == 'home' else away_largest_lead
        
        winner = 'home' if score_progression[-1][1] > score_progression[-1][0] else 'away'
        
        win = winner is home_or_away
        loss = not win
        if win is True:
            record[0] += 1
        else:
            record[1] += 1

    
        
        scored_first = first_to_score == home_or_away
        
        if scored_first is True:
            overall_G += 1

            if win is True:
                record_when_scoring_first[0] += 1

                overall_W += 1
            else:
                record_when_scoring_first[1] += 1

    print(f'{team}: {record_when_scoring_first[0]} - {record_when_scoring_first[1]},  {record[0]} - {record[1]}')
    G = sum(record_when_scoring_first)
    W = record_when_scoring_first[0]
    
    data.append([team, G, W/G, G/sum(record)])
        

teams, Gs, PCTs, prop = zip(*data)
plt.plot(prop, PCTs, 'bo', markersize=0)
ax = plt.gca()


for team, z, y, x in data:


    
    path = logos[team]
    
    ab = AnnotationBbox(OffsetImage(plt.imread(
        path, format="png"), zoom=0.45), (x, y), frameon=False)
    ax.add_artist(ab)
    
#ax.title(f'{season}')
ax.set_xlabel('Proportion of games scoring first')
ax.set_ylabel('Win percentage in those games')
ax.set_title(f'{season}')
ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
yticks = ax.get_yticks()
ax.yaxis.set_major_locator(FixedLocator(yticks))
ylabels = [_.get_text()[1:] for _ in ax.get_yticklabels()]
ax.set_yticklabels(ylabels)
ax.xaxis.set_major_locator(MaxNLocator(integer=True))


avgG = sum(Gs) / 30
avgP = overall_W/overall_G

plt.axvline(x=0.5, zorder=-10, color='#CCCCCC')
plt.axhline(y=avgP, zorder=-10, color='#CCCCCC')
plt.axhline(y=0.5, zorder=-10, color='#CCCCCC', ls='--')

     
