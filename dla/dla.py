import random
import numpy as np

from voxels.slot import Slot
from voxels.slot_array import SlotArray
from wfc.wfc import WFC


def are_adjacent(index1, index2):
    '''checking whether two cells are adjacent'''
    x_diff = abs(index1[0] - index2[0])
    y_diff = abs(index1[1] - index2[1])
    z_diff = abs(index1[2] - index2[2])

    return (x_diff <= 1) and (y_diff <= 1) and (z_diff <= 1) and not (
            x_diff == y_diff == z_diff == 0)


def are_orthogonal(index1, index2):
    '''checking whether two cells are adjacent'''
    x_diff = abs(index1[0] - index2[0])
    y_diff = abs(index1[1] - index2[1])
    z_diff = abs(index1[2] - index2[2])

    # Check if exactly one of the dimensions has a non-zero difference
    if (x_diff > 0 and y_diff == 0 and z_diff == 0) or (x_diff == 0 and y_diff > 0 and z_diff == 0) or (
            x_diff == 0 and y_diff == 0 and z_diff > 0):
        return True
    else:
        return False


def diagonal_add(prob):
    return random.random() < prob


probability = 0.8


class DLA:
    def __init__(self, slots_array: SlotArray, particles_num, noise):
        self.free_agent = []  # agent cells
        self.fixed_slots = []  # class of slots in occupied cells
        self.noise = noise   # constant float
        self.slots = slots_array   # 3D array consist of slot instance (0,0,0)---> Slot
        self.particles_num = particles_num  # constant int: number agent

    def fixed_generate(self, initial_points=None):
        '''create initial occupied slot'''
        np_arr = self.slots.get_arr()
        if initial_points is None:
            export_list = []
            for i in range(4):
                fixed = WFC.heuristic_pick(self.slots)
                coords = np.argwhere(np_arr == fixed)
                self._dla_observe(fixed, coords[0], self.slots)
                export_list.append(fixed)
            self.fixed_slots.append(export_list)
        else:
            export_list = []
            for index in initial_points:
                fixed = np_arr[index[0], index[1], index[2]]
                self._dla_observe(fixed, index, self.slots)
                export_list.append(fixed)
            self.fixed_slots.append(export_list)


    def agent_generate(self):
        '''create agent position in tuples'''
        arr_size = self.slots.get_size()
        if self.particles_num > arr_size:  # mostly not happen, but test it
            self.particles_num = round(arr_size * 0.1)

        shape = self.slots.get_arr().shape
        axis_indices = [np.linspace(0, shape[i] - 1, num=int(np.ceil(np.power(self.particles_num, 1 / 3))), dtype=int)
                        for i in range(3)]

        index = 0
        while index < self.particles_num:
            index_0 = np.random.choice(axis_indices[0])
            index_1 = np.random.choice(axis_indices[1])
            index_2 = np.random.choice(axis_indices[2])
            coord = [index_0, index_1, index_2]

            if coord not in self.free_agent:
                self.free_agent.append(coord)
                index += 1

    def fixed_slots_ratio(self, percentage):
        total_size = self.slots.get_size()
        fixed_size = len(self.fixed_slots)
        ratio = fixed_size / total_size
        return ratio > percentage

    def dla_run(self):
        # Get the slots array
        np_arr = self.slots.get_arr()
        loop = True
        index = 0
        move_index = 0
        shape = np_arr.shape



        # for i in range(len(self.free_agent)):
        #     ag_index = self.free_agent[i] # tuple now
        #     ag_index = np.array(ag_index)  # now array
        #     print(111, ag_index, ag_index.shape)
        #
        #     # movement
        #     movement = np.random.randint(-1,2,size=(3,))
        #     print(222, movement, movement.shape)
        #
        #     # move an agnet
        #     next_ag = ag_index + movement
        #     print(333, next_ag, next_ag.shape)
        #
        #     # clip
        #     next_ag = np.clip(next_ag, 0, np.array(np_arr.shape) - 1)
        #     print(444,next_ag, next_ag.shape)
        #
        #     # check availability
        #     # 1) should not be occupied
        #     # [0,1,1,
        #     #  0,0,1,
        #     #  0,0,0]  [0,2]  ==1: illegal  ==0: legal
        #
        #
        #     break

        while loop:
        # for i in range(len(self.free_agent)):
            ag_index = self.free_agent[index]
            # move agents
            x_coord = ag_index[0] + random.normalvariate(1, self.noise)
            y_coord = ag_index[1] + random.normalvariate(1, self.noise)
            z_coord = ag_index[2] + random.normalvariate(1, self.noise)

            # clip shape
            x_coord = int(np.clip(x_coord, 0, shape[0] - 1))
            y_coord = int(np.clip(y_coord, 0, shape[1] - 1))
            z_coord = int(np.clip(z_coord, 0, shape[2] - 1))
            ag_index = [x_coord, y_coord, z_coord]
            # check if the moved agent is in a fixed slot
            ag_slot = np_arr[ag_index[0], ag_index[1], ag_index[2]]
            # Finsh this agent move
            if ag_slot is self.slots.EMPTY_SLOT:
                move_index += 1
            elif not ag_slot.is_collapsed or move_index == 5:
                self.free_agent[index] = ag_index
                index += 1
                move_index = 0
            else:
                move_index += 1

            if index == self.particles_num:
                index = 0
                loop = False

        # loop particles
        for i in range(len(self.free_agent) - 1, -1, -1):
            ag_index = self.free_agent[i]
            ag_slot = np_arr[ag_index[0], ag_index[1], ag_index[2]]
            # if agent move to a fixed slots, continue the loop
            if ag_slot.is_collapsed:
                continue

            break_all_loops = False
            for x in range(-1, 2):
                if break_all_loops:
                    break
                for y in range(-1, 2):
                    if break_all_loops:
                        break
                    for z in range(-1, 2):
                        if x == 0 and y == 0 and z == 0:
                            continue
                        # check if the index is out of bouncy
                        adjacent_x = ag_index[0] + x
                        adjacent_y = ag_index[1] + y
                        adjacent_z = ag_index[2] + z
                        if adjacent_x >= shape[0] or adjacent_y >= shape[1] or adjacent_z >= shape[2]:
                            continue
                        adjacent_slot = np_arr[adjacent_x, adjacent_y, adjacent_z]
                        if adjacent_slot not in self.fixed_slots:
                            continue
                        else:
                            fix_coords = [adjacent_x, adjacent_y, adjacent_z]
                            if not are_orthogonal(ag_index, fix_coords) and not diagonal_add(probability):
                                continue
                            else:
                                WFC.agent_collapse(ag_slot, self.slots)
                                self._dla_observe(ag_slot, ag_index, self.slots)

                                if ag_slot.is_collapsed:
                                    self.fixed_slots.append(ag_slot)
                                else:
                                    continue
                                # break the loop the agent is fixed
                                break_all_loops = True
                                break

    # observe the selected slot and add it to the fixed list
    def _dla_observe(self, agent: Slot, coords, voxel_array: SlotArray):
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

            export_list = []
            for i, abs_coord in enumerate(abs_coords):
                x, y, z = abs_coord
                tar_slot = tar_slots[x, y, z]
                opts = parent.parts[i]
                tar_slot.module_opts = [opts]
                tar_slot.is_collapsed = True
                if tar_slot not in self.fixed_slots:
                    export_list.append(tar_slot)
            self.fixed_slots.append(export_list)
        else:
            agent.module_opts = [test_opt]
            agent.is_collapsed = True


