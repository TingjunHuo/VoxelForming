class Part:

    def __init__(self, faces_list,  parent_module=None, re_coords=None):
        self.index = parent_module.index
        self.faces = faces_list
        self.front = []
        self.back = []
        self.left = []
        self.right = []
        self.top = []
        self.bottom = []
        self.parent = parent_module
        if re_coords is None:
            self.re_coords = []
            self.is_child = False
        else:
            self.re_coords = re_coords
            self.is_child = True

    def set_rules(self, modules):
        for module in modules:
            for part in module.parts:
                # front
                if self.faces[0] == part.faces[1]:
                    self.front.append(part)
                # back
                if self.faces[1] == part.faces[0]:
                    self.back.append(part)
                # left
                if self.faces[2] == part.faces[3]:
                    self.left.append(part)
                # right
                if self.faces[3] == part.faces[2]:
                    self.right.append(part)
                # top
                if self.faces[4] == part.faces[5]:
                    self.top.append(part)
                # bottom
                if self.faces[5] == part.faces[4]:
                    self.bottom.append(part)
