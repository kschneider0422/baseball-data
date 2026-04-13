

import pickle
import sympy as sp

x = sp.symbols('x')


filename = 'func_dict.p'

with open(filename, 'rb') as f:
    func_dict = pickle.load(f)
    
    
# for bo in range(24):
    
#     num, den = func_dict[bo].as_numer_denom() 
        
#     ncoeffs = sp.Poly(num, x).all_coeffs() [::-1]
#     dcoeffs = sp.Poly(den, x).all_coeffs() [::-1]
    
    
    
#     # []
#     print(bo)
        
#     for _ in dcoeffs[1:]:
#         print((- _ / dcoeffs[0]).evalf())
#     print()

f = func_dict[23]

series_poly = sp.Poly(f.series(x, 0, 21).removeO(), x)
coeffs = series_poly.all_coeffs()                
numerical_coeffs = [c.evalf() for c in coeffs[::-1]]

for _ in numerical_coeffs:
    print(_)