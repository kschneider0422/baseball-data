import pandas as pd


transition_graph = {}

for season in range(2015, 2025):
    print(season)

    infile = f'data/{season}plays.csv'

    season_df = pd.read_csv(infile, low_memory=False)
    season_df = season_df[season_df.gametype == 'regular']
    season_df = season_df[['gid',
                           'inning', 'top_bot',
                           'outs_pre', 'outs_post', 
                           'br1_pre', 'br2_pre', 'br3_pre',
                           'br1_post', 'br2_post', 'br3_post',
                           'runs', 'pn']]
    
    
    for game_id in season_df.gid.unique():
        game_df = season_df[season_df.gid == game_id].copy()
        game_df.sort_values(by='pn', inplace=True)
        game_df.set_index('pn', inplace=True)

        away_score = 0
        home_score = 0
        state_transitions = []

        for play in game_df.index:
            
            play_details = game_df.loc[play]
            
            top_bot = int(play_details.top_bot)
            br1_pre = 0 if isinstance(play_details.br1_pre, float) else 1
            br2_pre = 0 if isinstance(play_details.br2_pre, float) else 1
            br3_pre = 0 if isinstance(play_details.br3_pre, float) else 1
            br1_post = 0 if isinstance(play_details.br1_post, float) else 1
            br2_post = 0 if isinstance(play_details.br2_post, float) else 1
            br3_post = 0 if isinstance(play_details.br3_post, float) else 1
            
            away_pre = away_score
            home_pre = home_score
            
            runs = int(play_details.runs)
            
            away_score += (1 - top_bot) * runs
            home_score += top_bot * runs
            
            
            pre_state = (int(play_details.inning),
                         int(play_details.top_bot),
                         int(play_details.outs_pre),
                         br1_pre, br2_pre, br3_pre,
                         away_pre, home_pre)
            
            post_state = (int(play_details.inning),
                          int(play_details.top_bot),
                          int(play_details.outs_post),
                          br1_post, br2_post, br3_post,
                          away_score, home_score)
            
            if pre_state != post_state:
                state_transitions.append([pre_state, post_state])
                if pre_state not in transition_graph:
                    transition_graph[pre_state] = {}
                if post_state not in transition_graph[pre_state]:
                    transition_graph[pre_state][post_state] = 0
                    
                transition_graph[pre_state][post_state] += 1
                
            
        
