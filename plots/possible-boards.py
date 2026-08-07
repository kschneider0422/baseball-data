from copy import deepcopy
from itertools import combinations as combos
from itertools import permutations as perms
from itertools import product as prod

from cave import Cave


def citer(indices, col, val, freq):

    for combo in combos(indices, freq):
        cdict = {(_, col): val for _ in combo}
        remains = [_ for _ in indices if _ not in set(combo)]

        yield [cdict, remains]


dims = (9, 9)
fixed = {(8, 0): 11, (5, 4): 14}


fixed_indices = {_: set() for _ in range(9)}

for coords in fixed.keys():
    row, col = coords
    fixed_indices[col].add(row)

question = (5, 8)

columns = {
    0: [9, 9, 9, 9, 9, 11, 11, 12],
    1: [4, 4],
    2: [5, 5],
    5: [2, 2, 2],
    6: [2],
    7: [2, 5, 5, 5, 7],
    8: [2],
}


all_cols = {_: [] for _ in range(9)}

for col, nums in columns.items():
    seen = set()
    indices = [_ for _ in range(9) if _ not in fixed_indices[col]]
    base = {(_, col): fixed[(_, col)] for _ in fixed_indices[col]}
    for perm in perms(indices, len(nums)):
        pairs = [(a, b) for a, b in zip(perm, nums)]
        tup = tuple(sorted(pairs))
        if tup not in seen:
            seen.add(tup)
            current = deepcopy(base)
            for row, val in pairs:
                # if (row, col) == question:
                #     break
                current[(row, col)] = val
            if question not in current:
                all_cols[col].append(current)


current = None

test = [_ for _ in all_cols.values() if len(_) > 0]

# count = 0
# for cdicts in prod(*test):
#     count += 1
#     # print(count)
#     new = cdicts[:3]

#     if current is None or new != current:
#         current = new
#         print(new)
#     clues = {}
#     for cdict in cdicts:
#         clues |= cdict

#     C = Cave(dims, clues)
#     C.board.unshaded.add(question)
#     C.solve()

#     if count % 1000 == 0:
#         print(count)
# break

# break

good = []

count = 0
for cdicts in prod(*test[:2]):
    count += 1
    # print(count)
    # new = cdicts[:3]

    # if current is None or new != current:
    #     current = new
    #     print(new)
    clues = deepcopy(fixed)
    for cdict in cdicts:
        clues |= cdict

    C = Cave(dims, clues)
    C.board.unshaded.add(question)
    check = C.board.check_clues()
    if check is True:
        check = C.board.connected_unshaded()
    if check is True:
        check = C.board.connected_shaded()

    if check is True:
        good.append(clues)
        # print()
        # print(C.board)


count = 0

starts = deepcopy(good)
good = []

common_clues = None
for cdicts in prod(starts, test[2]):
    count += 1
    # print(count)
    # new = cdicts[:3]

    # if current is None or new != current:
    #     current = new
    #     print(new)
    clues = deepcopy(fixed)
    for cdict in cdicts:
        clues |= cdict

    C = Cave(dims, clues)
    C.board.unshaded.add(question)
    check = C.board.check_clues()
    if check is True:
        check = C.board.connected_unshaded()
    if check is True:
        check = C.board.connected_shaded()

    if check is True:
        good.append(clues)
        if common_clues is None:
            common_clues = deepcopy(clues)
        else:
            common_clues = dict(common_clues.items() & clues.items())

        # print()
        # print(C.board)

    if count % 10000 == 0:
        print(count)

leftside = deepcopy(good)
print(len(good))

# count = 0


good = []
for cdicts in prod(*test[5:]):
    count += 1
    # print(count)
    # new = cdicts[:3]

    # if current is None or new != current:
    #     current = new
    #     print(new)
    clues = deepcopy(common_clues)
    for cdict in cdicts:
        clues |= cdict

    C = Cave(dims, clues)
    C.board.unshaded.add(question)
    check = C.board.check_clues()
    if check is True:
        check = C.board.connected_unshaded()
    if check is True:
        check = C.board.connected_shaded()

    if check is True:
        good.append(clues)

    if count % 10000 == 0:
        print(count)

count = 0

starts = deepcopy(good)
good = []
for cdicts in prod(starts, test[4]):
    count += 1
    # print(count)
    # new = cdicts[:3]

    # if current is None or new != current:
    #     current = new
    #     print(new)
    clues = deepcopy(common_clues)
    for cdict in cdicts:
        clues |= cdict

    C = Cave(dims, clues)
    C.board.unshaded.add(question)
    check = C.board.check_clues()
    if check is True:
        check = C.board.connected_unshaded()
    if check is True:
        check = C.board.connected_shaded()

    if check is True:
        good.append(clues)

    if count % 10000 == 0:
        print(count)

count = 0

starts = deepcopy(good)
good = []

common_clues_r = None
for cdicts in prod(starts, test[3]):
    count += 1
    # print(count)
    # new = cdicts[:3]

    # if current is None or new != current:
    #     current = new
    #     print(new)
    clues = deepcopy(common_clues)
    for cdict in cdicts:
        clues |= cdict

    C = Cave(dims, clues)
    C.board.unshaded.add(question)
    check = C.board.check_clues()
    if check is True:
        check = C.board.connected_unshaded()
    if check is True:
        check = C.board.connected_shaded()

    if check is True:
        good.append(clues)
        if common_clues_r is None:
            common_clues_r = deepcopy(clues)
        else:
            common_clues_r = dict(common_clues_r.items() & clues.items())
        # print(C.board)
        # print()

    if count % 10000 == 0:
        print(count)

rightside = deepcopy(good)
print(len(good))
print()


all_sols = []
count = 0

current = None
cl_count = 0

for clues_l, clues_r in prod(leftside, rightside):
    if current is None or clues_l != current:
        current = deepcopy(clues_l)
        cl_count += 1
        print(cl_count)
    clues = clues_l | clues_r
    C = Cave(dims, clues)
    C.board.unshaded.add(question)
    C.solve()

    if len(C.solutions) > 0:
        all_sols.extend(C.solutions)
        print(len(all_sols))

        for sol in C.solutions:
            print(sol)
            print()

    count += 1
    if count % 100000 == 0:
        print(count)
