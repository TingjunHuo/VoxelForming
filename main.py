import os
from collections import defaultdict

import numpy as np

from dla.dla import DLA
from voxels.slot_array import SlotArray
from voxels.module import Module
from voxels.module_part import Part
from wfc.wfc import WFC

# ------------------------------------------------------------------------------------------#
# global variables
max_iterations = 100
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


# ------------------------------------------------------------------------------------------#
# global variables
point_list = load_file('points.anything')
dimension = load_file('dimension.anything')
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
    options[0].parts = [Part([0, 0, 0, 0, 1, 1], options[0])]
    # module1
    options[1].parts = [Part([0, 0, 0, 0, 2, 1], options[1])]
    # module2
    options[2].parts = [Part([0, 0, 0, 0, 1, 2], options[2])]
    # module3 
    options[3].parts = [Part([0, 0, 0, 0, 2, 2], options[3])]


    # update rule for each module
    for i, module in enumerate(options):
        module.index = i
        module.set_rules(options)

    # 3d slot array
    slot_arr = SlotArray(length, width, height, point_list, options)
    slot_arr.set_up()
    dla_forming = DLA(slot_arr, 100, 2)
    # WFC
    loop = True
    loop_index = 0
    while loop:
        # Using WFC to form
        # ------------------------------------------------------------------------------------------#
        # WFC.collapse(slot_arr)
        # loop = not WFC.is_fully_collapsed(slot_arr)

        # Using dla to from
        # ------------------------------------------------------------------------------------------#
        dla_forming.dla_run()

        loop_index += 1
        if dla_forming.fixed_slots_ratio(0.3) or loop_index == max_iterations:
            loop = False
    print(loop_index)

    export_slot(slot_arr)


# calling the main function
if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------------- #
