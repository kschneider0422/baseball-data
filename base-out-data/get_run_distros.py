import sympy as sp
import numpy as np
import pandas as pd
from pathlib import Path
import pickle

x = sp.symbols('x')

data_file = 'raw_count_data.tsv'
with Path(data_file).open('r') as f:
    raw = f.read().split('\n')
raw = [[int(_) for _ in row.split('\t')] for row in raw]

row_sums = {_: 0 for _ in range(24)}
M_dict = {(r, c): 0 for r in range(24) for c in range(24)}
V_dict = {r: 0 for r in range(24)}
for row in raw:
    pre, post, runs, freq = row
    row_sums[pre] += freq
    if post < 24:
        term = -freq * x**runs
        tup = (pre, post)
        M_dict[tup] += term
    else:
        term = freq * x**runs
        V_dict[pre] += term
for _ in range(24):
    tup = (_, _)
    M_dict[tup] += row_sums[_]
    
M = sp.zeros(8)
V = sp.zeros(8, 1)
for row in range(16, 24):
    V[row - 16] += V_dict[row]
    for col in range(16, 24):
        tup = (row, col)
        M[row - 16, col - 16] += M_dict[tup]
X = sp.simplify(M**-1 * V)

func_dict = {r + 16: X[r] for r in range(8)}
func_dict[24] = 1

print('2 outs')

M = sp.zeros(8)
V = sp.zeros(8, 1)
for row in range(8, 16):
    V[row - 8] += V_dict[row]
    for col in range(8, 16):
        tup = (row, col)
        M[row - 8, col - 8] += M_dict[tup]
        tup2 = (row, col + 8)
        V[row - 8] -=  M_dict[tup2] * func_dict[col + 8]
X = sp.simplify(M**-1 * V)

for r in range(8):
    func_dict[r + 8] = X[r]
    
print('1 out')
    
M = sp.zeros(8)
V = sp.zeros(8, 1)
for row in range(8):
    V[row] += V_dict[row]
    for col in range(8):
        tup = (row, col)
        M[row, col] += M_dict[tup]
        tup2 = (row, col + 8)
        V[row] -=  M_dict[tup2] * func_dict[col + 8]
        tup3 = (row, col + 16)
        V[row] -=  M_dict[tup3] * func_dict[col + 16]
X = sp.simplify(M**-1 * V)

for r in range(8):
    func_dict[r] = X[r]
    
print('0 outs')
    
for r in range(24):
    f = func_dict[r]
    fprime = sp.diff(f, x)
    print(r, f.subs(x, 1), fprime.subs(x, 1).evalf())
    

data = []
max_runs = 20
for r in range(24):
    print(r)
    series_poly = sp.Poly(func_dict[r].series(x, 0, max_runs + 1).removeO(), x)
    coeffs = series_poly.all_coeffs()                
    numerical_coeffs = [c.evalf() for c in coeffs][::-1]
    prob_vec = np.array(numerical_coeffs)
    normalized = prob_vec / prob_vec.sum()
    data.append(normalized)
cols = [f'p_{r}' for r in range(max_runs + 1)]
df = pd.DataFrame(data, columns=cols)
    
df.to_csv('run_distros.csv')


with open('func_dict.p','wb') as f:
    pickle.dump(func_dict, f)

