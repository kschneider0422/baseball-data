


def translate(poly, vec):
    dr, dc = vec
    out = [(r + dr, c + dc) for r, c in poly]
    return tuple(sorted(out))
    
def canonical(poly):
    vec = [-min(_) for _ in zip(*poly)]
    return translate(poly, vec)

def cell_neighbors(coords):
    r, c = coords
    out = [
        (r - 1, c),
        (r, c + 1),
        (r + 1, c),
        (r, c - 1)
        ]
    return out

def poly_neighbors(poly):
    pset = set(poly)
    nbrs = set()
    for cell in poly:
        nbrs |= set(cell_neighbors(cell))
    return sorted(nbrs - pset)
    

def children(poly):
    nbrs = poly_neighbors(poly)
    out = set()
    for nbr in nbrs:
        new = list(poly)
        new.append(nbr)
        out.add(canonical(new))
    return sorted(out)
        
        
    
def get_polyominoes(n, D = {0: [tuple()], 1: [((0, 0),)]}):
    if n not in D:
        current = max(D.keys())
        while current < n:
            current += 1
            nextgen = set()
            for ancestor in D[current - 1]:
                nextgen |= set(children(ancestor))
            D[current] = sorted(nextgen)
    return D[n]
        
        



for n in range(10):
    polys = get_polyominoes(n)
    print(n, len(polys))
    
        
        
        
