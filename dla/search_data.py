
class SearchData:
    def __init__(self, pt, pts):
        self.pt = pt # a particles
        self.pts = pts # fixed points
        self.distances = [] # a list for distance between the particles and fixed points
        self.indices = []  # a list for map of indices of

    def SearchCallback(self, sender, e):  # e = data --> searchData object
        self.indices.append(e.Id)  # get data's id
        self.distances.append(self.pt.DistanceTo(self.pts[e.Id]))  # get the distance

