from mlb_lib import get_season, get_completed_games, get_team_games
from lookup import current_divisions, team_colors, logos, team_lookup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.dates as mdates
import matplotlib.patheffects as path_effects
from datetime import datetime

def get_team_above_500(team, all_games_df):
    team_df = get_team_games(schedule, team)

    
    # if team_df.shape[0] == 0:
    #     return -1
    
    team_df['home'] = team_df['home_name'] == team
    team_df['RSg'] = team_df['home'] * team_df['home_score'] + (1 - team_df['home']) * team_df['away_score']
    team_df['RAg'] = team_df['home'] * team_df['away_score'] + (1 - team_df['home']) * team_df['home_score']
    team_df['Wg'] = 1 * (team_df['RSg'] > team_df['RAg'])
    team_df['Lg'] = 1 - team_df['Wg']
    team_df['Netg'] = team_df['Wg'] - team_df['Lg']
    out_df = team_df[['game_datetime', 'Netg']].groupby('game_datetime')['Netg'].sum().reset_index()
    zero_row_date = out_df['game_datetime'].min() - pd.DateOffset(1)
    out_df.loc[-1] = [zero_row_date, 0]
    out_df = out_df.set_index('game_datetime').sort_index()
    out_df[team] = out_df['Netg'].cumsum()

    return out_df[[team]]

def get_teams_above_500(teams, all_games_df):
    out_df = pd.DataFrame()
    out_df.index.name = 'date'
    for team in teams:
        
        team_df = get_team_above_500(team, all_games_df)
        print(team, team_df.shape)
        if team_df.shape[0] < 5:
            continue
        out_df = out_df.join(team_df, how='outer')
    out_df.ffill(inplace=True)
    out_df.fillna(0, inplace=True)
    out_df = out_df.apply(pd.to_numeric, downcast='integer')
    
    new_columns = out_df.columns[(out_df.loc[out_df.last_valid_index()]).argsort()]
    return out_df[new_columns]

season = 2025  
schedule = get_season(season)
games = get_completed_games(schedule)
current_teams = set(schedule.home_name)



# scale_fact = 4.0



for title, short_teams in current_divisions.items():
    teams = [team_lookup[_] for _ in short_teams]
    div_df = get_teams_above_500(teams, schedule)

    # Create matplotlib objects
    fig, ax = plt.subplots(dpi=200)

    # Format x-axis datetimes
    monthlocator = mdates.MonthLocator(interval=1)
    ax.xaxis.set_major_locator(monthlocator) 
    month_day_formatter = mdates.DateFormatter("%B %e")
    ax.xaxis.set_major_formatter(month_day_formatter)

    # Basic df.plot() for the core of the plot
    colors = [team_colors[team]['ColorA'] for team in div_df.columns]
    div_df.plot(ax=ax, color=colors, x_compat=True, lw=1)

    # Assorted formatting
    ax.get_legend().remove()
    #ax.set_aspect("equal", adjustable="datalim")
    ax.set_aspect("equal", adjustable=None)
    ax.set_xlabel(None)
    ax.set_title(title)
    ax.tick_params(left=False, labelleft=False, right=True, labelright=True)
    ax.set_ylabel('Games above/below .500')
    ax.yaxis.set_label_position("right")
    
    whys = ax.get_ylim()
    vrange = whys[1] - whys[0]
    
    scale_fact = vrange**0.5/2.0
    print(vrange)

    # Add horizontal gridlines
    y_ticks = ax.get_yticks()
    for tick in y_ticks:
        ax.axhline(tick, c='k', lw=1, alpha=0.1)
    
    # Get x and y coords to add logos later
    last_day = div_df.index.max()
    logo_xval = last_day.timestamp()/(60*60*24)
    y_dict = div_df.loc[last_day].to_dict()

    for i, item in enumerate(y_dict.items()):
        team, logo_yval = item
        step = 5 * i
        
        # Add logo
        ifile = logos[team]
        arr_img = plt.imread(ifile)
        im = OffsetImage(arr_img, zoom=scale_fact/12.0, alpha=1.0)
        ab = AnnotationBbox(im, (logo_xval, logo_yval), xycoords='data', 
                            box_alignment=(0.5,0.5), frameon=False, zorder=40+step)
        ax.add_artist(ab)
        
        # Add circle around logo    
        circle = plt.Circle((logo_xval, logo_yval), scale_fact, ec=team_colors[team]['ColorA'], fc='white', zorder=39+step)
        ax.add_patch(circle)

    # Add fancy line effects    
    lines = ax.get_lines()
    teams_set = set(teams)
    for line in lines:
        line_label = line._label
        if line_label in teams_set:
            pe = [path_effects.Normal(),
                  path_effects.SimpleLineShadow(shadow_color=team_colors[line_label]['ColorB'], 
                                                alpha=1.0, offset=(-0.5, -1)),
                  path_effects.SimpleLineShadow(shadow_color=team_colors[line_label]['ColorA'], 
                                                alpha=1.0, offset=(-1, -2)),]
            line.set_path_effects(pe)
        

    # Add background image
    ax.margins(x=0, y=0)
    xlims = ax.get_xlim()
    ylims = ax.get_ylim()
    arr_img = plt.imread('images/grass2.png')
    # plt.imshow(arr_img, interpolation='nearest', aspect='auto', alpha=0.5,
    #            extent=[xlims[0], xlims[1], ylims[0], ylims[1]])
    
    ax.imshow(arr_img, interpolation='nearest', alpha=0.5,
              extent=[xlims[0], xlims[1] + 1, ylims[0], ylims[1]])
    

    
    fig_file = f'plots/{title.replace(" ", "-")}-{str(datetime.now().date())}.png'
    
    fig.savefig(fig_file)
