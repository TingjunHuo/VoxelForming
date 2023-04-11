import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import Grasshopper
import math
import System

# input Geometry and Unit Size

unit = Size
mesh = Mesh

# output geometry
V = []
C = []
E = []
D = []


#Create BoundingBox
box = mesh.GetBoundingBox(rg.Plane.WorldXY)

#The world boundary
min_x = 99999999
max_x = -min_x
min_y = 99999999
max_y = -min_y
min_z = 99999999
max_z = -min_z


#edges of boundary box
pts = box.GetCorners()
for p in pts:
	if p.X > max_x:
		max_x = p.X

	if p.X < min_x:
		min_x = p.X

	if p.Y > max_y:
		max_y = p.Y

	if p.Y < min_y:
		min_y = p.Y

	if p.Z > max_z:
		max_z = p.Z
	if p.Z < min_z:
		min_z = p.Z

if (unit == None):
	max_length = max(max_z-min_z, max_x-min_x, max_y-min_y)
	unit = int(max_length / 10)

unit_interval = rg.Interval(-unit * 0.5, unit * 0.5)

#number of voxel
num_x = int((max_x - min_x) / unit)
num_y = int((max_y - min_y) / unit)
num_z = int((max_z - min_z) / unit)

min_x = (max_x + min_x) * 0.5 - (num_x * unit * 0.5) 
min_y = (max_y + min_y) * 0.5 - (num_y * unit * 0.5) 
min_z = (max_z + min_z) * 0.5 - (num_z * unit * 0.5)

D.append(num_x + 1)
D.append(num_y + 1)
D.append(num_z + 1)


for i in range(num_x + 1):
	for j in range(num_y + 1):
		for k in range(num_z + 1):
			x = min_x + i * unit
			y = min_y + j * unit
			z = min_z + k * unit
			point = rg.Point3d(x, y, z)
			if mesh.IsPointInside(point, 0.001, False):
				coor_list = (x,y,z)
				voxel_grid = rg.Point3d(x, y, z)
				voxel_plane = rg.Plane(voxel_grid, rg.Plane.WorldXY.ZAxis)
				box = rg.Box(voxel_plane, unit_interval, unit_interval, unit_interval)
				C.append(coor_list)
				V.append(box)
			else:
				coor_list = (-999,-999,-999)
				voxel_grid = rg.Point3d(x, y, z)
				voxel_plane = rg.Plane(voxel_grid, rg.Plane.WorldXY.ZAxis)
				box = rg.Box(voxel_plane, unit_interval, unit_interval, unit_interval)
				C.append(coor_list)
				E.append(box)

S = '\n'.join(str(x) for x in C)
D = '\n'.join(str(x) for x in D)