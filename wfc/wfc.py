import numpy as np
import random

from voxels.slot import Slot
from voxels.slot_array import SlotArray


class WFC:

    @staticmethod
    def heuristic_pick(voxel_array: SlotArray):
        # shallow copy slot_arr to a 1d list
        copy_arr = voxel_array.slot_arr.reshape(-1)
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
    @staticmethod
    def collapse(voxel_array: SlotArray):
        # pick a random slot
        pick_slot = voxel_array.heuristic_pick()
        if pick_slot:
            pick_slot.observe()
        else:
            return

        for index, cur_slot in np.ndenumerate(voxel_array.slot_arr):
            i, j, k = index
            if cur_slot is voxel_array.EMPTY_SLOT:
                continue
            elif cur_slot.is_collapsed:
                continue
            else:
                # cum_valid_opts(module) will hold all the options that satisfy the connection rules of each face
                # the valid_options(module) are computed by the condition of each slot
                cum_valid_opts = []
                for module in voxel_array.options:
                    for part in module.parts:
                        cum_valid_opts.append(part)

                # check front slot
                if cur_slot.front != 0:
                    front_slot = voxel_array.slot_arr[i][j - 1][k]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module_part in front_slot.module_opts:
                        valid_options.extend(module_part.back)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check back slot
                if cur_slot.back != 0:
                    back_slot = voxel_array.slot_arr[i][j + 1][k]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module_part in back_slot.module_opts:
                        valid_options.extend(module_part.front)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check left slot
                if cur_slot.left != 0:
                    left_slot = voxel_array.slot_arr[i - 1][j][k]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module_part in left_slot.module_opts:
                        valid_options.extend(module_part.right)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check right slot
                if cur_slot.right != 0:
                    right_slot = voxel_array.slot_arr[i + 1][j][k]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module_part in right_slot.module_opts:
                        valid_options.extend(module_part.left)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check top slot
                if cur_slot.top != 0:
                    top_slot = voxel_array.slot_arr[i][j][k + 1]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module_part in top_slot.module_opts:
                        valid_options.extend(module_part.bottom)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # check bottom slot
                if cur_slot.bottom != 0:
                    bottom_slot = voxel_array.slot_arr[i][j][k - 1]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    for module_part in bottom_slot.module_opts:
                        valid_options.extend(module_part.top)
                    cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

                # finally assign the cum_valid_opts options to be the current cells valid options
                cur_slot.module_opts = cum_valid_opts
                cur_slot.update()

    @staticmethod
    def agent_collapse(agent: Slot, voxel_array: SlotArray):
        i, j, k = np.argwhere(voxel_array.get_arr() == agent)[0]
        if agent is voxel_array.EMPTY_SLOT:
            return
        elif agent.is_collapsed:
            return
        else:
            # cum_valid_opts(module) will hold all the options that satisfy the connection rules of each face
            # the valid_options(module) are computed by the condition of each slot
            cum_valid_opts = []
            for module in voxel_array.options:
                for part in module.parts:
                    cum_valid_opts.append(part)

            # check front slot
            if agent.front != 0:
                front_slot = voxel_array.slot_arr[i][j - 1][k]
                valid_options = []  # holds the valid options for the current cell to fit with the above cell
                for module_part in front_slot.module_opts:
                    valid_options.extend(module_part.back)
                cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

            # check back slot
            if agent.back != 0:
                back_slot = voxel_array.slot_arr[i][j + 1][k]
                valid_options = []  # holds the valid options for the current cell to fit with the above cell
                for module_part in back_slot.module_opts:
                    valid_options.extend(module_part.front)
                cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

            # check left slot
            if agent.left != 0:
                left_slot = voxel_array.slot_arr[i - 1][j][k]
                valid_options = []  # holds the valid options for the current cell to fit with the above cell
                for module_part in left_slot.module_opts:
                    valid_options.extend(module_part.right)
                cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

            # check right slot
            if agent.right != 0:
                right_slot = voxel_array.slot_arr[i + 1][j][k]
                valid_options = []  # holds the valid options for the current cell to fit with the above cell
                for module_part in right_slot.module_opts:
                    valid_options.extend(module_part.left)
                cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

            # check top slot
            if agent.top != 0:
                top_slot = voxel_array.slot_arr[i][j][k + 1]
                valid_options = []  # holds the valid options for the current cell to fit with the above cell
                for module_part in top_slot.module_opts:
                    valid_options.extend(module_part.bottom)
                cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

            # check bottom slot
            if agent.bottom != 0:
                bottom_slot = voxel_array.slot_arr[i][j][k - 1]
                valid_options = []  # holds the valid options for the current cell to fit with the above cell
                for module_part in bottom_slot.module_opts:
                    valid_options.extend(module_part.top)
                cum_valid_opts = [option for option in cum_valid_opts if option in valid_options]

            # finally assign the cum_valid_opts options to be the current cells valid options
            agent.module_opts = cum_valid_opts
            agent.update()

    # check if the slot array is fully collapsed
    @staticmethod
    def is_fully_collapsed(voxel_array: SlotArray):
        for index, slot in np.ndenumerate(voxel_array.slot_arr):
            if not slot.is_collapsed:
                return False
        return True

    @staticmethod
    def observe(agent: Slot, coords, voxel_array: SlotArray):
        if not agent.module_opts:  # Check if agent.module_opts is not empty
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

            for i, abs_coord in enumerate(abs_coords):  # Use enumerate() again
                x, y, z = abs_coord
                tar_slot = tar_slots[x, y, z]
                opts = parent.parts[i]
                tar_slot.module_opts = [opts]
                tar_slot.is_collapsed = True
        else:
            agent.module_opts = [test_opt]
            agent.is_collapsed = True

    # observe every un-collapsed slots in array
    # do it when the loop meet the max iteration times
    @staticmethod
    def observe_array(voxel_array: SlotArray):
        for index, slot in np.ndenumerate(voxel_array.slot_arr):
            if not slot.is_collapsed:
                slot.observe()

    @staticmethod
    def dla_observe(agent: Slot, coords, voxel_array: SlotArray):

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
        else:
            agent.module_opts = [test_opt]
            agent.is_collapsed = True
