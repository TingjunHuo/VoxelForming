import random


class Slot:
    is_collapsed = False

    def __init__(self, x, y, z, options):
        self.x = x
        self.y = y
        self.z = z
        self.front = 1
        self.back = 1
        self.left = 1
        self.right = 1
        self.top = 1
        self.bottom = 1
        self.is_collapsed = False
        self.module_opts = []
        for module in options:
            for part in module.parts:
                self.module_opts.append(part)

    def __str__(self):
        return "x:%d, y:%d, z:%d," % (self.x, self.y, self.z)

    # return the entropy/the length of the options
    def entropy(self):
        return len(self.module_opts)

    def update(self):
        self.is_collapsed = bool(self.entropy() == 1)

    # observe the cell/or collapse the cell
    def observe(self):
        try:
            test_opts = random.choice(self.module_opts)
            # random pick an option from the options list
            self.module_opts = [test_opts]
            self.is_collapsed = True
        except IndexError:
            return

    def set_front(self, front):
        self.front = front

    def set_back(self, back):
        self.back = back

    def set_left(self, left):
        self.left = left

    def set_right(self, right):
        self.right = right

    def set_top(self, top):
        self.top = top

    def set_bottom(self, bottom):
        self.bottom = bottom
