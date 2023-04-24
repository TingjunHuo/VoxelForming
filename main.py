import os
from collections import defaultdict
import copy
import numpy as np

from dla.dla import DLA
from voxels.slot_array import SlotArray
from voxels.module import Module
from voxels.module_part import Part


# ------------------------------------------------------------------------------------------#
# global variables
max_iterations = 500
a_coords = []
b_coords = []
c_coords = []
d_coords = []
e_coords = []


# ------------------------------------------------------------------------------------------#
# helper function
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


# ------------------------------------------------------------------------------------------#
# global variables
point_list = load_file('points.anything')
dimension = load_file('dimension.anything')
initial_points = load_file('initial_points.anything')
length = dimension[0]
width = dimension[1]
height = dimension[2]


# ------------------------------------------------------------------------------------------#
# main function
def main():
    # store modules
    options = []
    for i in range(4):
        module = Module()
        module.index = i
        options.append(module)

    # face condition of each module
    # define connection rules
    # order: front:0 ,back:1, left:2, right:3, top:4, bottom:5
    # module0
    options[0].parts = [Part([1, 1, 1, 1, 0, 0], options[0])]
    # module1
    options[1].parts = [Part([2, 2, 1, 1, 0, 0], options[1])]
    # module2
    options[2].parts = [Part([1, 1, 2, 2, 0, 0], options[2])]
    # module3 
    options[3].parts = [Part([1, 1, 2, 2, 0, 0], options[3], [0, 0, 0]),
                        Part([1, 1, 2, 2, 0, 0], options[3], [1, 0, 0]),
                        Part([1, 1, 2, 2, 0, 0], options[3], [2, 0, 0])]
    # update rule for each module
    for i, module in enumerate(options):
        module.index = i
        module.set_rules(options)

    # 3d slot array
    slot_arr = SlotArray(length, width, height, point_list, options)
    slot_arr.set_up()
    dla_forming = DLA(slot_arr, 10, 3)
    dla_forming.fixed_generate(initial_points)
    dla_forming.agent_generate()

    arr_history = []
    agent_history = []
    deep_copied_list = copy.deepcopy(dla_forming.fixed_slots)
    deep_copied_agents = copy.deepcopy(dla_forming.free_agent)
    arr_history.append(deep_copied_list)
    agent_history.append(deep_copied_agents)

    # WFC
    loop = True
    loop_index = 0
    while loop:

        dla_forming.dla_run()
        # Export List
        deep_copied_list = copy.deepcopy(dla_forming.fixed_slots)
        deep_copied_agents = copy.deepcopy(dla_forming.free_agent)
        arr_history.append(deep_copied_list)
        agent_history.append(deep_copied_agents)
        loop_index += 1
        if dla_forming.fixed_slots_ratio(0.7) or loop_index == max_iterations:
            loop = False
    print(loop_index)
    export_history(arr_history)
    export_agent_history(agent_history, dla_forming.slots)

    # export_list(dla_forming.fixed_slots)


# calling the main function
if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------------- #
