from copy import deepcopy
from itertools import combinations as combos


class Cell:
    
    def __init__(self, address, val=None, locked=False):
        row, col = address
        self.address = address
        self.value = val
        self.restricted = set()
        self.locked = locked
        self.nbrs = {(row - 1, col),
                     (row, col + 1),
                     (row + 1, col),
                     (row, col - 1)}
        
    def copy(self):
        new = Cell(self.address, self.value, self.locked)
        new.restricted = deepcopy(self.restricted)
        return new
        
class Board:
    
    def __init__(self, dims, givens):
        rows, cols = dims
        self.dims = dims
        self.givens = deepcopy(givens)
        self.cells = {(r, c): Cell((r, c)) for r in range(rows) for c in range(cols)}
        for addy, val in givens.items():
            self.cells[addy].value = val
        for cell in self.cells.values():
            bad = set()
            for nbr in cell.nbrs:
                r, c = nbr
                if r < 0 or r >= rows or c < 0 or c >= cols or self.cells[nbr].value is not None:
                    bad.add(nbr)
            cell.nbrs = cell.nbrs - bad
        self.components = None
                    
    def copy(self):
        new = Board(self.dims, self.givens)
        new.cells = deepcopy(self.cells)
        
        return new
        
    def __str__(self):
        rows, cols = self.dims
        outrows = []
        for row in range(rows):
            thisrow = []
            for col in range(cols):
                tup = (row, col)
                val = self.cells[tup].value
                char = '.' if val is None else str(val)
                thisrow.append(char)
            outrows.append(''.join(thisrow))
        return '\n'.join(outrows)
    
    __repr__ = __str__
    
    def find_connected_components(self):
        

        pool = {tup for tup in self.cells.keys() if self.cells[tup].locked is False and self.cells[tup].value is not None}
        print((1,3) in pool)
        comp = set()
        comv = None
        to_check = set()
        components = []
        
        while len(pool) > 0 or len(to_check) > 0:
            
            
            if len(to_check) == 0:
                if len(comp) > 0:
                    components.append([comv, comp])
                    comp = set()
                seed = pool.pop()
                to_check.add(seed)
                comv = self.cells[seed].value
                
            current = to_check.pop()
            comp.add(current)
            row, col = self.cells[current].address
            nbrs = {(row - 1, col),
                    (row, col + 1),
                    (row + 1, col),
                    (row, col - 1)}
            for nbr in nbrs:
                if nbr in pool and self.cells[nbr].value == comv and nbr not in comp:
                    to_check.add(nbr)
                    pool.discard(nbr)
                    
        print(comp)
                
            
        self.components = components
        
    def check_connected_components(self):
        new = []
        for comv, comp in self.components:
            # print(comv, len(comp))
            if len(comp) > comv:
                return False
            if len(comp) == comv:
                for tup in comp:
                    self.cells[tup].locked = True
                    for nbr in self.cells[tup].nbrs:
                        self.cells[nbr].restricted.add(comv)
            else:
                cnbrs = set()
                for tup in comp:
                    cnbrs |= self.cells[tup].nbrs
                if len(comp) < comv and len(cnbrs) == 0:
                    return False
                new.append([comv, comp])
        self.components = new
        
        return True
                        
        
        
    def children_comp(self):
        children = []
        if len(self.components) == 0:
            return children
        
        for comv, comp in self.components:
            cnbrs = set()
            for tup in comp:
                cnbrs |= self.cells[tup].nbrs
            if len(cnbrs) == 1:
                break
        
        # comv, comp = self.components[0]
        # cnbrs = set()
        # for tup in comp:
        #     cnbrs |= self.cells[tup].nbrs
            
        diff = comv - len(cnbrs)
        
        for nadd in range(1, diff + 1):
            
            for combo in combos(cnbrs, nadd):
                
                complement = cnbrs - set(combo)
                child = self.copy()
                
                for new in combo:
                    child.cells[new].value = comv
                    row, col = new
                    
                    nbrs = {(row - 1, col),
                            (row, col + 1),
                            (row + 1, col),
                            (row, col - 1)}
                    
                    
                    for nbr in nbrs:
                        if nbr in child.cells:
                            child.cells[nbr].nbrs.discard(new)

                        
                for new in complement:
                    child.cells[new].restricted.add(comv)
                    
                child.find_connected_components()
                test = child.check_connected_components()
                if test is True:
                    children.append(child)
                    
        return children
    
    def children_cell(self):
        
        children = []
        
        found = False
        
        for addr, cell in self.cells.items():
            if cell.value is None:
                found = True
                break
        if found is False:
            return children
                    
        testval = 1
        while testval in cell.restricted:
            testval += 1
            
        child_with = self.copy()
        child_with.cells[addr].value = testval
        row, col = addr
        
        nbrs = {(row - 1, col),
                (row, col + 1),
                (row + 1, col),
                (row, col - 1)}
        for nbr in nbrs:
            if nbr in child_with.cells:
                child_with.cells[nbr].nbrs.discard(addr)
                
        child_with.find_connected_components()
        test = child_with.check_connected_components()
        if test is True:
            children.append(child_with)
                
        child_wo = self.copy()
        child_wo.cells[addr].restricted.add(testval)
        children.append(child_wo)
        
    def is_complete(self): 
        
        for cell in self.cells.values():
            if cell.locked is False:
                return False
            
        return True
        
class Fillomino:
    
    def __init__(self, dims, givens):
        
        self.board = Board(dims, givens)
        self.solutions = []
        
    # def solve(self):
        
    #     new = self.board.copy()
    #     new.find_connected_components()
    #     res = new.check_connected_components()
    #     if res is False:
    #         return False
        

    #     stack = [new]
        
    #     while len(stack) > 0:
            
            

                
                
            

    

                
        
d = (6, 6)
g = {(0, 1): 3, (0, 2): 5,
     (1, 0): 3, (1, 1): 2, (1, 3): 3, (1, 5): 2,
     (2, 2): 9, (2, 3): 9, (2, 5): 2,
     (3, 1): 9,
     (4, 2): 3, (4, 3): 5, 
     (5, 0): 1, (5, 1): 2, (5, 2): 3, (5, 5): 1,}

B = Board(d, g)
B.find_connected_components()
# res = B.check_connected_components()
# stack = [B]
# solutions = []

# count = 0

# while len(stack) > 0:
#     current = stack.pop()

#     if len(current.components) > 0:
#         children = current.children_comp()
        
#     else: 
#         children = current.children_cell()
        
#     for child in children:
#         if child.is_complete():
#             solutions.append(child)
#         else:
#             stack.append(child)
            
#     print(len(stack))
            
#     count += 1
    
#     # if count % 100 == 0:
#     #     print(count)
#     #     # print(current) 
#     #     # print()
#     #     print(stack[5])
#     #     print()
#     if count == 1:
#         break
    
    
            
    
    


# for val, tups in B.components:
#     print(val, tups)
    
# print()
    
# kids = B.children_comp()

# for kid in kids:
#     print(kid)
#     print()
#     for val, tups in kid.components:
#         print(val, tups)
#     print()