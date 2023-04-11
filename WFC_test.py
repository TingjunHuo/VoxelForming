import numpy as np
from itertools import product

# 定义单元类型
A = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
B = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 1]])
C = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])

# 定义3种单元类型的数组列表
patterns = [A, B, C]

# 定义数组形状和空数组
shape = (5, 5, 5)
array = np.zeros(shape, dtype=int)

# 定义用于检查约束条件的函数
def satisfies_constraints(array, pattern, position):
    i, j, k = position
    n = pattern.shape[0]
    for di, dj, dk in product(range(n), repeat=3):
        if i + di - n // 2 < 0 or i + di - n // 2 >= shape[0]:
            continue
        if j + dj - n // 2 < 0 or j + dj - n // 2 >= shape[1]:
            continue
        if k + dk - n // 2 < 0 or k + dk - n // 2 >= shape[2]:
            continue
        if array[i + di - n // 2, j + dj - n // 2, k + dk - n // 2] != 0 and array[i + di - n // 2, j + dj - n // 2, k + dk - n // 2] != pattern[di, dj]:
            return False
    return True

# 循环直到所有位置都被填满
while np.any(array == 0):
    # 找到空位置的坐标
    i, j, k = np.unravel_index(np.argmax(array == 0), shape)
    # 找到满足约束条件的单元类型
    valid_patterns = [p for p in patterns if satisfies_constraints(array, p, (i, j, k))]
    # 如果没有满足约束条件的单元类型，回溯到上一个位置
    if len(valid_patterns) == 0:
        array[i, j, k] = 0
        i, j, k = np.unravel_index(np.argmax(array != 0), shape)
        array[i, j, k] = 0
    else:
        # 在满足约束条件的单元类型中随机选择一个
        pattern = valid_patterns[np.random.randint(len(valid_patterns))]
        # 在空位置处放置单元类型
        array[i:i+pattern.shape[0], j:j+pattern.shape[0], k:k+pattern.shape[0]] = pattern

print(array)