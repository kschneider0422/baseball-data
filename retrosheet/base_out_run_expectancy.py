from pickle import load
from random import choices

p_file = 'pickle/base_out_2015_2024.p'

with open(p_file, 'rb') as f:
    base_out = load(f)
    
    



def get_next_state(node, graph):
    
    population = list(graph[node].keys())
    weights = [graph[node][_] for _ in population]
    
    next_node = choices(population, weights=weights, k=1)[0]
    
    next_base_out = next_node[:4]
    runs = next_base_out[-1]
    
    return [next_base_out, runs]



trials = 1000000

final_dict = {}

for bout in sorted(base_out.keys()):
    print(bout)
    run_dict = {}
    for t in range(trials):
        current = bout
        runs_scored = 0
        outs = current[0]
        while outs < 3:
            current, runs = get_next_state(current, base_out)
            runs_scored += runs
            outs = current[0]
        if runs_scored not in run_dict:
            run_dict[runs_scored] = 0
        run_dict[runs_scored] += 1
    final_dict[bout] = run_dict