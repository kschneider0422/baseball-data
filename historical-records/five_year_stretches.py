import pandas as pd
import os


folder = 'historical_records'


columns = ['team', 'from', 'to', 'g', 'w', 'l', 'pct']
dtypes = {'team': 'object', 
          'from': 'int32', 
          'to': 'int32', 
          'g': 'int32', 
          'w': 'int32', 
          'l': 'int32', 
          'pct': 'float64'}

collector = pd.DataFrame(columns=columns).astype(dtypes)

for file in os.listdir(folder):
    team, junk = file.split('.')
    
    df = pd.read_csv(f'{folder}/{file}')
    sub_df = df[['Year', 'G', 'W', 'L']].copy()
    
    sub_df['g'] = sub_df.G.rolling(5).sum()
    sub_df['w'] = sub_df.W.rolling(5).sum()
    sub_df['l'] = sub_df.L.rolling(5).sum()
    
    sub_df['from'] = sub_df.Year
    sub_df['to'] = sub_df.Year + 4
    sub_df.drop(['Year', 'G', 'W', 'L'], axis=1, inplace=True)
    
    sub_df = sub_df.iloc[4:]
    sub_df['team'] = team
    sub_df['pct'] = sub_df.w / sub_df.g
    
    sub_df.g = sub_df.g.astype('int32')
    sub_df.w = sub_df.w.astype('int32')
    sub_df.l = sub_df.l.astype('int32')
    
    collector = pd.concat([collector, sub_df], axis=0, ignore_index=True)
    
    
    
out = collector.sort_values(by='l').tail(15).copy()
print(out)
    