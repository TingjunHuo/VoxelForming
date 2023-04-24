import os
from collections import defaultdict

import numpy as np


def get_nh_ind(grid, cell):
    x, y, z = cell[0], cell[1], cell[2]
    shape = grid.shape
    neighborhood_indices = []

    for i in range(-1, 2):
        for j in range(-1, 2):
            for k in range(-1, 2):
                if i == 0 and j == 0 and k == 0:
                    continue
                xi = (x + i) % shape[0]
                yj = (y + j) % shape[1]
                zk = (z + k) % shape[2]
                neighborhood_indices.append((xi, yj, zk))
    neighborhood_indices = tuple(np.array(neighborhood_indices).T)
    return neighborhood_indices


# make neighbor matrix including myself 3,3,3
# make ortho matrix incdluing myself 3,3,3
# (3,3,3) --> binary array

def diagonal_control(occ_neighbour):
    # orthogonal template
    ortho_temp = np.zeros([26])
    ortho_indices = (4, 10, 12, 13, 15, 21)
    np.put(ortho_temp, ortho_indices, 1)

    # diagonal template
    diag_temp = np.ones([26])
    np.put(diag_temp, ortho_indices, 0)

    cal_ortho = ortho_temp * occ_neighbour
    cal_diag = diag_temp * occ_neighbour

    return np.sum(cal_diag == 1)




def load_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        return [eval(line) for line in lines]


def save_file(data, filename):
    file_dir = os.path.join(filename)
    f2 = open(file_dir, 'w')
    f2.write("{}".format(data))
    f2.close()


def export_slot(arr):
    coords = defaultdict(list)

    for index, slot in np.ndenumerate(arr.slot_arr):
        if slot is arr.EMPTY_SLOT or not slot.is_collapsed:
            continue
        if len(slot.module_opts) != 0:
            coords_index = slot.module_opts[0].index
            coords[coords_index].append((slot.x, slot.y, slot.z))
        else:
            coords["Empty"].append((slot.x, slot.y, slot.z))

    for key, values in coords.items():
        content = '\n'.join(str(x) for x in values)
        save_file(content, f'{key}.anything')


def export_list(fixed_list):
    coords = defaultdict(list)

    for slot in fixed_list:
        if len(slot.module_opts) != 0:
            coords_index = slot.module_opts[0].index
            coords[coords_index].append((slot.x, slot.y, slot.z))
        else:
            coords["Empty"].append((slot.x, slot.y, slot.z))

    for key, values in coords.items():
        content = '\n'.join(str(x) for x in values)
        save_file(content, f'{key}.anything')


def export_history(fixed_list_history):
    coords_history = defaultdict(lambda: defaultdict(list))

    for iteration, fixed_list in enumerate(fixed_list_history, start=1):
        coords = defaultdict(list)
        for slot in fixed_list:
            if len(slot.module_opts) != 0:
                coords_index = slot.module_opts[0].index
                coords[coords_index].append((slot.x, slot.y, slot.z))
            else:
                coords["Empty"].append((slot.x, slot.y, slot.z))

        for key, values in coords.items():
            coords_history[key][iteration] = values

    for key, values in coords_history.items():
        with open(f'{key}.anything', 'w') as file:
            for iteration, coords in values.items():
                file.write(f'---\n')
                content = '\n'.join(str(x) for x in coords)
                file.write(f'{content}\n')


def export_agent_history(agents_history, slotarray):
    arr = slotarray.get_arr()

    with open(f'agents.anything', 'w') as file:
        for coords_index in agents_history:
            coords = []  # 将coords移动到此处，以便在每次循环开始时清空列表
            for coord in coords_index:
                slot = arr[coord[0], coord[1], coord[2]]
                if slot is slotarray.EMPTY_SLOT:
                    continue
                else:
                    coords.append((slot.x, slot.y, slot.z))
            file.write(f'---\n')
            content = '\n'.join(str(x) for x in coords)
            file.write(f'{content}\n')
