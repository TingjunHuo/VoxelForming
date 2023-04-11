import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import Grasshopper
import math
import System
import operator

# input Geometry and Unit Size

unit = Size
mesh = Mesh

# output geometry
V = []
C = []
E = []

#Convert Geometry to Mesh
# if(geometryRaw.HasBrepForm):
# 		meshingParameter = rg.MeshingParameters.FastRenderMesh
# 		meshes = rg.Mesh.CreateFromBrep(rg.Brep.TryConvertBrep(geometryRaw), meshingParameter)
# 		for face in meshes:
# 			mesh.Append(face)
# 		mesh.UnifyNormals()
# 		mesh.Weld(math.pi)

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

x_curves = {}
vertical_curves   = {}

horizontal_planes = {}
y_cutter_planes   = {}



hc = []
vc = []

for i in range(num_y + 1):
	# y coordination: cutter
	y = min_y+ 0.01 + i * unit

	p = rg.Point3d(0, y, 0)
	plane = rg.Plane(p, rg.Plane.WorldXY.YAxis)
	
	curves = rg.Mesh.CreateContourCurves(mesh, plane)
	for i in rg.Curve.JoinCurves(curves):
		vc.append(i)
	vertical_curves[y] = rg.Curve.JoinCurves(curves)
	y_cutter_planes[y] = plane

for i in range(num_x + 1):
	# x coordination
	x = min_x + i * unit
	p = rg.Point3d(x,0,0)
	plane = rg.Plane(p, rg.Plane.WorldXY.XAxis)
	
	curves = rg.Mesh.CreateContourCurves(mesh, plane)
	
	for i in rg.Curve.JoinCurves(curves):
		hc.append(i)

	x_curves[x] = rg.Curve.JoinCurves(curves)
	horizontal_planes[x] = plane

sorted_x_curves_keys = sorted(x_curves.keys())
sorted_y_cutter_planes_keys = sorted(y_cutter_planes.keys())


refer_min_pt = rg.Point3d(0,min_y-999999,0)
refer_max_pt = rg.Point3d(0,min_y+999999,0)

# Iterate every x_curves
for x in sorted_x_curves_keys:
	for curve in x_curves[x]:
		if not isinstance(curve, rg.Polyline):
			curve = curve.ToPolyline()

		if not curve.IsClosed:
			curve.Add(curve.PointAt(0))

		min_pt = curve.ClosestPoint(refer_min_pt)
		max_pt = curve.ClosestPoint(refer_max_pt)
	
		for y in sorted_y_cutter_planes_keys:
			# if the curves is out of boundary
			if y < min_pt.Y or max_pt.Y < y:
				continue

			plane = y_cutter_planes[y]
			#intersection as the boundary of ech level
			curve = curve.ToNurbsCurve()
			intersections = rg.Intersect.Intersection.CurvePlane(curve, plane, unit * 0.01)
		

			#skip if only have one section
			if len(intersections) < 2:
				continue

			intersection_points = []


			for intersect in intersections:
				has_point = False

				for point in intersection_points:
					#skip overlap point
					if point.DistanceTo(intersect.PointA) < 0.01:
						has_point = True

				if not has_point:
					intersection_points.append(intersect.PointA)
			

			intersection_points.sort(key= lambda p:p.Z)

			

			grid_num = int(len(intersection_points)/2)

			for i in range(num_z + 1):
				z = min_z + unit * i
				# the contained area: if the grid is within the intersection part
				for j in range(grid_num):
					grid_min_z = intersection_points[j * 2].Z
					grid_max_z = intersection_points[j *2 + 1].Z
					if grid_min_z <= z <= grid_max_z:
						voxel_grid = rg.Point3d(x, y, z)
						voxel_plane = rg.Plane(voxel_grid, rg.Plane.WorldXY.ZAxis)
						box = rg.Box(voxel_plane, unit_interval, unit_interval, unit_interval)
						V.append(box)
						C.append(voxel_grid)
						continue
					else:
						void_grid = rg.Point3d(-999, -999, -999)
						voxel_grid = rg.Point3d(x, y, z)
						voxel_plane = rg.Plane(voxel_grid, rg.Plane.WorldXY.ZAxis)
						box = rg.Box(voxel_plane, unit_interval, unit_interval, unit_interval)
						C.append(void_grid)
						E.append(box)




# sort point list
# V.sort(key= lambda p:p.Center.Z)
# V.sort(key= lambda p:p.Center.Y)
# V.sort(key= lambda p:p.Center.X)
# C.sort(key= lambda p:p.Z)
# C.sort(key= lambda p:p.Y)
# C.sort(key= lambda p:p.X)