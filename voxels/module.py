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
