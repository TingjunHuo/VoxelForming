import random
import numpy as np
from voxels.slot_array import SlotArray
from wfc.wfc import WFC


def are_adjacent(index1, index2):
    x_diff = abs(index1[0] - index2[0])
    y_diff = abs(index1[1] - index2[1])
    z_diff = abs(index1[2] - index2[2])

    return (x_diff <= 1) and (y_diff <= 1) and (z_diff <= 1) and not (
            x_diff == y_diff == z_diff == 0)


def are_orthogonal(index1, index2):
    x_diff = abs(index1[0] - index2[0])
    y_diff = abs(index1[1] - index2[1])
    z_diff = abs(index1[2] - index2[2])

    # Check if exactly one of the dimensions has a non-zero difference
    if (x_diff > 0 and y_diff == 0 and z_diff == 0) or (x_diff == 0 and y_diff > 0 and z_diff == 0) or (
            x_diff == 0 and y_diff == 0 and z_diff > 0):
        return True
    else:
        return False


def diagonal_add(probability):
    return random.random() < probability


probability = 0.8


class DLA:
    def __init__(self, slots_array: SlotArray, particles_num, noise):
        self.free_slots = []
        self.fixed_slots = []
        self.noise = noise
        self.slots = slots_array
        self.particles_num = particles_num

        fixed = WFC.heuristic_pick(slots_array)
        fixed.observe()
        self.fixed_slots.append(fixed)

    def agent_generate(self):
        self.free_slots = []
        arr_size = self.slots.get_size()
        if self.particles_num > arr_size:
            self.particles_num = arr_size * 0.1

        loop = True
        index = 0
        while loop:
            shape = self.slots.get_arr().shape
            index_0 = np.random.randint(0, shape[0])
            index_1 = np.random.randint(0, shape[1])
            index_2 = np.random.randint(0, shape[2])
            agent = self.slots.get_arr()[index_0, index_1, index_2]
            if agent.is_collapsed:
                continue
            self.free_slots.append(agent)
            index += 1
            if len(self.free_slots) == self.particles_num or index == self.particles_num * 3:
                loop = False
                index = 0

    def fixed_slots_ratio(self, percentage):
        total_size = self.slots.get_size()
        fixed_size = len(self.fixed_slots)
        ratio = fixed_size / total_size
        return percentage - 0.05 < ratio < percentage + 0.05

    def dla_run(self):
        # generate new agents in the dla system
        self.agent_generate()
        # move agents
        np_arr = self.slots.get_arr()
        for ag in self.free_slots:
            coords = np.argwhere(np_arr == ag)
            x_coord = coords[0][0] + random.normalvariate(1.5, self.noise)
            y_coord = coords[0][1] + random.normalvariate(1.5, self.noise)
            z_coord = coords[0][2] + random.normalvariate(1.5, self.noise)
            shape = np_arr.shape
            # clip shape
            x_coord = int(np.clip(x_coord, 0, shape[0] - 1))
            y_coord = int(np.clip(y_coord, 0, shape[1] - 1))
            z_coord = int(np.clip(z_coord, 0, shape[2] - 1))
            ag = np_arr[x_coord][y_coord][z_coord]

        # loop particles
        for i in range(len(self.free_slots) - 1, -1, -1):
            agent = self.free_slots[i]
            coords = np.argwhere(np_arr == agent)[0]
            for j in self.fixed_slots:
                fix_coords = np.argwhere(np_arr == j)[0]
                if are_adjacent(coords, fix_coords):
                    # diagonal situation and the probability is not ture
                    if not are_orthogonal(coords, fix_coords) and not diagonal_add(probability):
                        continue
                    else:
                        self.fixed_slots.append(self.free_slots.pop(i))
                        WFC.agent_collapse(agent, self.slots)
                        agent.observe()
                        # break the loop the agent is fixed
                        break

    @staticmethod
    def clip(n, min_n, max_n):
        return max(min(n, max_n), min_n)

    @staticmethod
    def update(cur_state, ants):
        pass
        return cur_state
