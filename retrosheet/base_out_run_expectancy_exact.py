from pickle import load
from random import choices

p_file = 'pickle/base_out_2015_2024.p'

with open(p_file, 'rb') as f:
    base_out = load(f)
    
    




transition_dict = {}
run_dict = {}


for pre, changes in base_out.items():
    transition_dict[pre] = {}
    run_dict[pre] = 0

    
    denom = sum(changes.values())
    

    for state, count in changes.items():
        
        substate = state[:4]
        runs = state[-1]
        
        prob = count / denom
        
        if substate not in transition_dict[pre]:
            transition_dict[pre][substate] = 0
            
        transition_dict[pre][substate] += prob
        run_dict[pre] += prob * runs