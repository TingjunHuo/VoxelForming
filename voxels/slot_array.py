import random
import numpy as np

from voxels.slot import Slot


class SlotArray:

    def __init__(self, length, width, height, point_list, options):
        # define a empty slot
        self.EMPTY_SLOT = Slot(-9999, -9999, -9999, [])
        self.EMPTY_SLOT.is_collapsed = True
        self.length = length
        self.width = width
        self.height = height
        self._point_list = point_list
        self.slot_arr = np.empty((self.length, self.width, self.height), dtype=Slot)
        self._point_arr = np.empty(len(point_list), dtype=object)
        # options are modules
        self.options = options
        self.size = 0

    def set_up(self):
        self._point_arr[:] = self._point_list
        arr_reshaped = np.reshape(self._point_arr, (self.length, self.width, self.height))
        for index, value in np.ndenumerate(arr_reshaped):
            i, j, k = index

            if [value[0], value[1], value[2]] == [-999, -999, -999]:
                self.slot_arr[i][j][k] = self.EMPTY_SLOT
            else:
                self.slot_arr[i][j][k] = Slot(value[0], value[1], value[2], self.options)

        x_size = np.shape(self.slot_arr)[0]
        y_size = np.shape(self.slot_arr)[1]
        z_size = np.shape(self.slot_arr)[2]

        # iterator slots array and check condition
        for index, value in np.ndenumerate(self.slot_arr):
            i, j, k = index
            # skip if it is an empty slot
            if self.slot_arr[i][j][k] is self.EMPTY_SLOT:
                continue
            # check left
            if i - 1 < 0 or self.slot_arr[i - 1][j][k] is self.EMPTY_SLOT:
                self.slot_arr[i][j][k].set_left(0)
            # check right
            if i + 1 >= x_size or self.slot_arr[i + 1][j][k] is self.EMPTY_SLOT:
                self.slot_arr[i][j][k].set_right(0)
            # check front
            if j - 1 < 0 or self.slot_arr[i][j - 1][k] is self.EMPTY_SLOT:
                self.slot_arr[i][j][k].set_front(0)
            # check back
            if j + 1 >= y_size or self.slot_arr[i][j + 1][k] is self.EMPTY_SLOT:
                self.slot_arr[i][j][k].set_back(0)
            # check top
            if k + 1 >= z_size or self.slot_arr[i][j][k + 1] is self.EMPTY_SLOT:
                self.slot_arr[i][j][k].set_top(0)
            # check bottom
            if k - 1 < 0 or self.slot_arr[i][j][k - 1] is self.EMPTY_SLOT:
                self.slot_arr[i][j][k].set_bottom(0)
            # count the valid slot number
            self.size += 1

    # randomly pick a slot
    def heuristic_pick(self):
        # shallow copy slot_arr to a 1d list
        copy_arr = self.slot_arr.reshape(-1)
        get_entropy = lambda slot: slot.entropy()
        sorted_indices = np.argsort([get_entropy(slot) for slot in copy_arr])
        sorted_arr = copy_arr[sorted_indices]
        # select from un-collapsed slot
        filtered_arr = list(filter(lambda x: x.entropy() > 1, sorted_arr))
        if not filtered_arr:
            return None

        # select from the least entropy ones
        init_slot = filtered_arr[0]
        filtered_arr = list(filter(lambda x: x.entropy() == init_slot.entropy(), filtered_arr))
        pick_slot = random.choice(filtered_arr)
        return pick_slot

    # WFC function
    def collapse(self):
        # pick a random slot
        pick_slot = self.heuristic_pick()
        if pick_slot:
            pick_slot.observe()
        else:
            return

        for index, cur_slot in np.ndenumerate(self.slot_arr):
            i, j, k = index
            if cur_slot is self.EMPTY_SLOT:
                continue
            elif cur_slot.is_collapsed:
                continue
            else:
                # cum_valid_opts(module) will hold all the options that satisfy the connection rules of each face
                # the valid_options(module) are computed by the condition of each slot
                cum_valid_opts = self.options

                # check front slot
                if cur_slot.front != 0:
                    front_slot = self.slot_arr[i][j - 1][k]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module in front_slot.module_opts:
                        valid_options.extend(module.back)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check back slot
                if cur_slot.back != 0:
                    back_slot = self.slot_arr[i][j + 1][k]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module in back_slot.module_opts:
                        valid_options.extend(module.front)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check left slot
                if cur_slot.left != 0:
                    left_slot = self.slot_arr[i - 1][j][k]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module in left_slot.module_opts:
                        valid_options.extend(module.right)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check right slot
                if cur_slot.right != 0:
                    right_slot = self.slot_arr[i + 1][j][k]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module in right_slot.module_opts:
                        valid_options.extend(module.left)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check top slot
                if cur_slot.top != 0:
                    top_slot = self.slot_arr[i][j][k + 1]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module in top_slot.module_opts:
                        valid_options.extend(module.bottom)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check bottom slot
                if cur_slot.bottom != 0:
                    bottom_slot = self.slot_arr[i][j][k - 1]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module in bottom_slot.module_opts:
                        valid_options.extend(module.top)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # finally assign the cum_valid_opts options to be the current cells valid options
                cur_slot.module_opts = cum_valid_opts
                cur_slot.update()

    def get_np(self):
        return self.slot_arr

    def get_size(self):
        return self.size

    def get_shape(self):
        return self.slot_arr.shape

    # check if the slot array is fully collapsed
    def is_fully_collapsed(self):
        for index, slot in np.ndenumerate(self.slot_arr):
            if not slot.is_collapsed:
                return False
        return True

    # observe every un-collapsed slots in array
    # do it when the loop meet the max iteration times
    def observe_slot(self):
        for index, slot in np.ndenumerate(self.slot_arr):
            if not slot.is_collapsed:
                slot.observe()

    def get_arr(self):
        return self.slot_arr
