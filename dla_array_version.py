import copy
import random

import numpy as np
from utils import get_nh_ind
from utils import export_history
from utils import diagonal_control
from voxels.module import Module
from voxels.module_part import Part
from voxels.slot import Slot
from voxels.slot_array import SlotArray
from main import load_file
from wfc.wfc import WFC


class Dla:
    def __init__(self, rhino_slot_arr, agent_number):
        arr = rhino_slot_arr.slot_arr
        self.entire_arr = np.zeros(arr.shape)
        self.occ_arr = np.zeros(arr.shape)
        self.agt_arr = np.zeros(arr.shape)
        self.cand_arr = np.zeros(arr.shape)
        empty_indices = np.argwhere(arr == rhino_slot_arr.EMPTY_SLOT)
        self.cand_arr[tuple(empty_indices.T)] = -1
        self.occ_arr[tuple(empty_indices.T)] = -1
        self.agent_number = agent_number
        self.export_indices = []

    def gen_occs(self, initial_points):
        for index in initial_points:
            self.occ_arr[index[0], index[1], index[2]] = 1
            self.update_cand((index[0], index[1], index[2]))


    def gen_agents(self):
        axis_indices = [np.linspace(0,
                                    self.entire_arr.shape[i] - 1,
                                    num=int(np.ceil(np.power(self.agent_number, 1 / 3))),
                                    dtype=int) for i in range(3)]
        while np.sum(self.agt_arr) < self.agent_number:
            index_0 = np.random.choice(axis_indices[0])
            index_1 = np.random.choice(axis_indices[1])
            index_2 = np.random.choice(axis_indices[2])
            self.agt_arr[index_0, index_1, index_2] = 1

    # initializing cand
    def update_cand(self, occ_index):

        # find the neighbour of occupied slot
        nh_ind = get_nh_ind(self.occ_arr, occ_index)
        nh_values = copy.deepcopy(self.cand_arr[nh_ind])

        # Check the corresponding values in self.occ_arr
        occ_values = self.occ_arr[nh_ind]
        # Set nh_values to 1 or -1 only if the corresponding self.occ_arr element is 0
        nh_values = np.where((occ_values == 0) & (nh_values != -1), 1, nh_values)
        self.cand_arr[nh_ind] = nh_values
        nh_values_after = self.cand_arr[nh_ind]

    # movement
    def move_agents(self):
        agt_slots = np.argwhere(self.agt_arr == 1)

        for prev_slot in agt_slots:

            # make random movement
            movement = np.random.randint(-1, 3, size=(3,))

            # move an agent
            next_slot = prev_slot + movement

            # clip
            next_slot = np.clip(next_slot, 0, np.array(self.entire_arr.shape) - 1)

            # update agent position
            if np.sum(np.equal(next_slot, prev_slot)) != len(prev_slot):
                self.agt_arr[tuple(next_slot.T)] = 1
                self.agt_arr[tuple(prev_slot.T)] = 0

            # if it moves to a candidate slot.
            if self.cand_arr[tuple(next_slot.T)] == 1:
                # 1) get neighbor
                # get list of indices in ortho
                nh_cur_cand = get_nh_ind(self.occ_arr, next_slot)
                nh_cur_occ = self.occ_arr[nh_cur_cand]

                # 2) controller
                diag_count = diagonal_control(nh_cur_occ)
                if diag_count >= 1:
                    # check orthogonality
                    # module type
                    # if controller satisfied:
                    self.occ_arr[tuple(next_slot.T)] = 1
                    # based on legality
                    # updated entire with module numbers
                    num_ones = np.count_nonzero(self.cand_arr == 1)
                    self.cand_arr[tuple(next_slot.T)] = 0
                    self.update_cand(tuple(next_slot.T))
                    num_ones = np.count_nonzero(self.cand_arr == 1)
                    self.agt_arr[tuple(next_slot.T)] = 0
                    agent_sum = np.sum(self.agt_arr)
                    self.gen_agents()
                    self.export_indices.append(tuple(next_slot.T))
                else:
                    continue

    def dla_observe(self, agent: Slot, coords, voxel_array: SlotArray):

        # Check if agent.module_opts is not empty
        if not agent.module_opts:
            return

        test_opt = random.choice(agent.module_opts)
        if test_opt.is_child:
            parent = test_opt.parent
            rel_coords = parent.cul_rel(test_opt)
            tar_slots = voxel_array.get_arr()
            abs_coords = []
            array_shape = tar_slots.shape
            for i, rel_coord in enumerate(rel_coords):  # Use enumerate() to get index and element
                abs_x = coords[0] + rel_coord[0]
                abs_y = coords[1] + rel_coord[1]
                abs_z = coords[2] + rel_coord[2]
                internal_part = parent.parts[i]
                if abs_x < 0 or abs_x >= array_shape[0] or \
                        abs_y < 0 or abs_y >= array_shape[1] \
                        or abs_z < 0 or abs_z >= array_shape[2]:
                    return
                tar_slot = tar_slots[abs_x, abs_y, abs_z]

                if tar_slot.is_collapsed or internal_part not in tar_slot.module_opts:
                    return
                abs_coords.append([abs_x, abs_y, abs_z])

            for i, abs_coord in enumerate(abs_coords):
                x, y, z = abs_coord
                tar_slot = tar_slots[x, y, z]
                opts = parent.parts[i]
                tar_slot.module_opts = [opts]
                tar_slot.is_collapsed = True
                self.occ_arr[x, y, z] = 1
                self.update_cand([x, y, z])

        else:
            agent.module_opts = [test_opt]
            agent.is_collapsed = True


    def occ_ratio(self):
        occ_size = np.count_nonzero(self.occ_arr == 1)
        entire_size = np.count_nonzero(self.cand_arr != -1)
        ratio = occ_size / entire_size
        return ratio


point_list = load_file('points.anything')
dimension = load_file('dimension.anything')
initial_points = load_file('initial_points.anything')
length = dimension[0]
width = dimension[1]
height = dimension[2]

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

history_export = []

initial_list = [(4, 39, 2),
                (7, 32, 1),
                (9, 13, 1),
                (12, 1, 5)]
dla = Dla(slot_arr, 100)
dla.gen_occs(initial_list)
dla.gen_agents()

initial_export = []
for index in initial_list:
    slot_arr.get_arr()[index].observe()
    initial_export.append(slot_arr.get_arr()[index])
history_export.append(initial_export)

loop = True
loop_index = 0


while loop:
    dla.move_agents()
    if len(dla.export_indices) > 0:
        arr = slot_arr.get_arr()
        exported_slot_list = []
        for index in dla.export_indices:
            slot = arr[index]
            WFC.agent_collapse(slot, slot_arr)
            dla.dla_observe(slot, index, slot_arr)
            exported_slot_list.append(slot)
        dla.export_indices = []
        history_export.append(exported_slot_list)
    loop_index += 1
    occ_ratio = dla.occ_ratio()
    if occ_ratio > 0.65 or loop_index > 1000:
        loop = False

export_history(history_export)
print(dla.occ_ratio())
