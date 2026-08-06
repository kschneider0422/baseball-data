from copy import deepcopy


class Cave:
    def __init__(self, dims=(6, 6), clues=None):
        self.dims = dims
        rows, cols = dims
        self.pool = {(i, j) for i in range(rows) for j in range(cols)}
        self.shaded = set()
        self.unshaded = set()
        if clues is None:
            clues = {}
        self.clues = deepcopy(clues)
        for cell, val in clues.items():
            self.place_clue(cell, val)
        self.locked = {}
        
        self.border = ({(i, -1) for i in range(-1, dims[1] + 1)}
                       | {(i, dims[1]) for i in range(-1, dims[1] + 1)}
                       | {(-1, i) for i in range( dims[0] )}
                       | {(dims[0], i) for i in range( dims[0] )})
            
    def place_clue(self, coords, val):
        self.unshaded.add(coords)
        self.pool.discard(coords)
        self.clues[coords] = val
        
    def shade_cell(self, coords):
        self.shaded.add(coords)
        self.pool.discard(coords)
        
    def unshade_cell(self, coords):
        self.unshaded.add(coords)
        self.pool.discard(coords)
        
    def copy(self):
        new = Cave(self.dims, self.clues)
        new.pool = deepcopy(self.pool)
        new.shaded = deepcopy(self.shaded)
        new.unshaded = deepcopy(self.unshaded)
        new.locked = deepcopy(self.locked)
        
        return new
        
    def children(self):
        
        light_child = self.copy()
        dark_child = self.copy()
        cell = min(self.pool)
        light_child.unshade_cell(cell)
        dark_child.shade_cell(cell)
        
        return [light_child, dark_child]
    
    def check_clues(self):
        out = True
        done = False
        while not done:
            # print('start of big loop')
            done = True
            for cell, val in self.clues.items():
                if val < 2:
                    
                    out = False
                    break
                lock = False
                row, col = cell
                flex = [0] * 4
                total = 1
                ucells = 1
                pcells = 0
                # print()
                # print(val, total)
                if row > 0:
                    a = 0
                    b = 0
                    r = row - 1
                    while True:
                        flag = True
                        if r < 0 or (r, col) in self.shaded:
                            break
                        elif (r, col) in self.unshaded and flag is True:
                            a += 1
                        else:
                            flag = False
                            b += 1
                            flex[0] = 1
                        r -= 1
                    total += a + b
                    # print('up', total)
                    ucells += a
                    pcells += b
                if row < self.dims[0] - 1:
                    a = 0
                    b = 0
                    r = row + 1
                    # print(r)
                    while True:
                        flag = True
                        if r == self.dims[0] or (r, col) in self.shaded:
                            break
                        elif (r, col) in self.unshaded and flag is True:
                            a += 1
                        else:
                            flag = False
                            b += 1
                            flex[1] = 1
                        r += 1
                    total += a + b
                    # print('down', total)
                    ucells += a
                    pcells += b
                        
                if col > 0:
                    a = 0
                    b = 0
                    c = col - 1
                    while True:
                        flag = True
                        if c < 0 or (row, c) in self.shaded:
                            break
                        elif (row, c) in self.unshaded and flag is True:
                            a += 1
                        else:
                            flag = False
                            b += 1
                            flex[2] = 1
                        c -= 1
                    total += a + b
                    # print('left', total)
                    ucells += a
                    pcells += b
                    
                if col < self.dims[1] - 1:
                    a = 0
                    b = 0
                    c = col + 1
                    while True:
                        flag = True
                        if c == self.dims[1] or (row, c) in self.shaded:
                            break
                        elif (row, c) in self.unshaded and flag is True:
                            a += 1
                        else:
                            flag = False
                            b += 1
                            flex[3] = 1
                        c += 1
                    total += a + b
                    # print('right', total)
                    ucells += a
                    pcells += b
                    
                    
                if total < val:
                    print(total, val)
                    out = False
                    break
                
                if ucells > val and pcells == 0:
                    out = False
                    break
                
                if total == val:
                    lock = True
                    break
                
                if total > val:
                    if sum(flex) > 1:
                        continue
                    else:
                        lock = True
                        break
            
            if lock is True:
                # print('LOCK')
                
                while ucells <= total:
                    
                    if flex[0] == 1:
                        r = row - 1
                        while True:
                            if ucells == total:
                                if (r, col) in self.pool:
                                    self.shaded.add((r, col))
                                    self.pool.discard((r, col))
                                    break
                                
                            if r < 0 or (r, col) in self.shaded:
                                break
                            elif (r, col) in self.pool:
                                self.unshaded.add((r, col))
                                self.pool.discard((r, col))
                                ucells += 1
                            r -= 1
                            
                    if flex[1] == 1:
                        r = row + 1
                        while True:
                            if ucells == total:
                                if (r, col) in self.pool:
                                    self.shaded.add((r, col))
                                    self.pool.discard((r, col))
                                    break

                            if r == self.dims[0] or (r, col) in self.shaded:
                                break
                            elif (r, col) in self.pool:
                                self.unshaded.add((r, col))
                                self.pool.discard((r, col))
                                ucells += 1
                            r += 1
                    if flex[2] == 1:
                        c = col - 1
                        
                        while True:
                            if ucells == total:
                                if (row, c) in self.pool:
                                    self.shaded.add((row, c))
                                    self.pool.discard((row, c))
                                    break
                                
                            if c < 0 or (row, c) in self.shaded:
                                break
                            elif (row, c) in self.pool:
                                self.unshaded.add((row, c))
                                self.pool.discard((row, c))
                                ucells += 1
                            c -= 1
                        
                    if flex[3] == 1:
                        c = col + 1
                        while True:
                            if ucells == total:
                                if (row, c) in self.pool:
                                    self.shaded.add((row, c))
                                    self.pool.discard((row, c))
                                    break
                            if c == self.dims[1] or (row, c) in self.shaded:
                                break
                            elif (row, c) in self.pool:
                                self.unshaded.add((row, c))
                                self.pool.discard((row, c))
                                ucells += 1
                            c += 1
                    if ucells == total:
                        break
                            
                self.locked[cell] = val
                del self.clues[cell]
                done = False
                # print('end of lock', done)
                
            # print('end of big loop', done)
        # print('sgd')
        return out
    
    def connected_unshaded(self):

        
        cells = self.unshaded | self.pool
        ucells = cells - self.pool
        rep = ucells.pop()
        cells.discard(rep)
        to_check = {rep}
        comp = set()

        
        while len(to_check) > 0:
            current = to_check.pop()
            r, c = current
            nbrs = {(r, c - 1), (r - 1, c),
                    (r, c + 1), (r + 1, c)}
            to_check |= nbrs & cells
            cells = cells - nbrs
            comp.add(current)
            # print(len(to_check), len(cells), len(comp))
            
        # print(cells)
        # print(comp)
        
        return len(cells & self.unshaded) == 0
    
    def connected_shaded(self):
        
        
        if len(self.shaded) == 0:
            return True
        
        cells = self.shaded | self.pool | self.border
        scells = self.shaded | self.border
        rep = scells.pop()
        cells.discard(rep)
        to_check = {rep}
        comp = set()
        

        
        # to_check = {(r, c) for r, c in cells if ((r==0)  
        #                                          or (c==0)
        #                                          or (r == self.dims[0] - 1)
        #                                          or (c == self.dims[1] - 1))}
        # cells = cells - to_check
        # comp = set()

        
        while len(to_check) > 0:
            current = to_check.pop()
            to_check.discard(current)
            r, c = current
            nbrs = {(r, c - 1), (r - 1, c),
                    (r, c + 1), (r + 1, c)}
            to_check |= nbrs & cells
            cells = cells - nbrs
            comp.add(current)
            # print(len(to_check), len(cells), len(comp))
            # if len( to_check & self.shaded) == 0:
            #     break
            
        # print(cells)
        # print(comp)
        
        return len(cells & self.shaded) == 0
    
    def __str__(self):
        
        rows, cols = self.dims
        out = []
        for row in range(rows):
            row_out = ''
            for col in range(cols):
                tup = (row, col)
                if tup in self.clues:
                    row_out += f"{self.clues[tup]: 3}"
                elif tup in self.locked:
                    row_out += f"{self.locked[tup]: 3}"
                elif tup in self.shaded:
                    row_out += '  X'
                elif tup in self.unshaded:
                    row_out += '   '
                else:
                    row_out += '  ·'
            out.append(row_out)
        return '\n'.join(out)
    
    
        
    
    __repr__ = __str__
                    
dims = (6, 6)               
clues = {(0, 1): 3,
         (2, 1): 2,
         (2, 4): 3,
         (3, 3): 11,
         (4, 2): 3,
         (5, 0): 3,
         (5, 4): 2}             
                    
C = Cave(dims, clues)
                        
print(C.check_clues())
print(C.connected_unshaded())
print(C.connected_shaded())

stack = [C.copy()]
solutions = []

count = 0

while len(stack) > 0:
    current = stack.pop()
    
    left, right = current.children()
    
    if ((left.check_clues() is True)
        and (left.connected_unshaded() is True)
        and (left.connected_shaded() is True)):
        if len(left.pool) == 0:
            solutions.append(left)
        else:
            stack.append(left)
    else:
        print()
        print(left)
            
            
    if ((right.check_clues() is True)
        and (right.connected_unshaded() is True)
        and (right.connected_shaded() is True)):
        if len(left.pool) == 0:
            solutions.append(right)
        else:
            stack.append(right)
            
    else:
        print()
        print(right)
            
            
    if len(solutions) > 1:
        break
    
    count += 1
    
    if count == 1000:
        break
    
    
print(len(solutions))  
print(len(stack))            
                        
            
        
        