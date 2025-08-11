import pickle
from random import choices

p_file = 'pickle/transitions_2015_2024.p'

with open(p_file, 'rb') as f:
    transition_graph = pickle.load(f)
    
    
def terminal_state(state):
    
    inning = state[0]
    top_bot = state[1]
    outs = state[2]
    away_score = state[-2]
    home_score = state[-1]
    
    return (inning >= 9 and (
        (top_bot == 0 and home_score > away_score and outs == 3) 
        or (top_bot == 1 and home_score > away_score) 
        or (top_bot == 1 and home_score < away_score and outs == 3)))
    
    

    
def inning_transition(state, ghost=True):
    
    
    inning = state[0]
    top_bot = state[1]
    away_score = state[-2]
    home_score = state[-1]
    
    ghost_runner = 0 if ghost is False or inning <= 9 else 1
    
    
    
    new_state = (inning + top_bot,
                 1 - top_bot,
                 0,
                 0,
                 ghost_runner,
                 0,
                 away_score,
                 home_score)
    
    return new_state


def get_next_state(node, graph):
    
    population = list(graph[node].keys())
    weights = [graph[node][_] for _ in population]
    
    return choices(population, weights=weights, k=1)[0]
    

    
    
    
state = (5, 1, 0, 0, 0, 0, 9, 0)


trials = 100000


wins = 0
losses = 0
for _ in range(trials):
    current = state
    while terminal_state(current) is False:
        outs = current[2]
        if outs == 3:
            current = inning_transition(current)
        if current not in transition_graph:
            current = state
        else:
            current = get_next_state(current, transition_graph)
        
    away_score = current[-2]
    home_score = current[-1]
    
    if home_score > away_score:
        wins += 1
    if home_score < away_score:
        losses += 1

        
print(f'W: {wins}, L: {losses}, G: {trials}, P_home = {wins / trials}, P_away = {losses / trials}')

