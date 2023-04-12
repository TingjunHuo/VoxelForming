class Module:
    def __init__(self):
        self.index = -1
        # front:0 ,back:1, left:2, right:3, top:4, bottom:5
        self.parts = []

    # set the rules for each module: basic connection rule: just connect opposite faces
    # Each module will store the optional modules it can connect to

    # Set rules for all parts of this module
    def set_rules(self, modules):
        for part in self.parts:
            part.set_rules(modules)
            part.parent = self.index

    def cul_rel(self, chosen_part):
        rel_coords = []
        x, y, z = chosen_part.re_coords
        for part in self.parts:
            tar_x, tar_y, tar_z = part.re_coords
            rel_coord = [tar_x - x, tar_y - y, tar_z - z]
            rel_coords.append(rel_coord)
        return rel_coords
