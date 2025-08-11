from pickle import load, dump
from random import choices


    
    
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
    

    
    
p_file = 'pickle/transitions_2015_2024_m.p'

with open(p_file, 'rb') as f:
    transition_graph = load(f)
    
    
base_out = {}
for pre_state, posts in transition_graph.items():
    
    pre_margin = pre_state[-1]
    
    t_pre = pre_state[2:6]
    
    if t_pre not in base_out:
        base_out[t_pre] = {}
    
    nposts = len(posts)
    pset = set()
    for post_state, count in posts.items():
        post_margin = post_state[-1]
        
        runs = abs(post_margin - pre_margin)
        
        t_post = tuple(list(post_state[2:6]) + [runs])

        if t_post not in base_out[t_pre]:
            base_out[t_pre][t_post] = 0
        base_out[t_pre][t_post] += count


p_file = 'pickle/base_out_2015_2024.p'

with open(p_file, 'wb') as f:
    dump(base_out, f)
    