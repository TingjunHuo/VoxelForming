from voxels.slot_array import SlotArray


test = SlotArray()

print(test)


# import numpy as np
# import src.voxels.slot_array
#
# class person:
#     def __init__(self, age, name):
#         self.age = age
#         self.name = name
#
#
# # 生成随机的三维数组
# steven = person(21, "stven")
# iiii = person(11, "iiii")
# sdasd = person(41, "iiii")
# alist = person(19, "iiii")
#
# person_list = [steven, sdasd, iiii, alist]
# np_list = np.reshape(person_list, (2, 2))
#
# # 按照age属性排序
# indices = np.argsort(np_list, axis=None, order=('age',))
# sorted_arr = np_list.flat[indices].reshape(np_list.shape)
