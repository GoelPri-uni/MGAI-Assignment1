# Import necessary modules
import numpy as np
import matplotlib.pyplot as plt


import numpy as np
import matplotlib.pyplot as plt
import random
from gdpc import Editor, Block
from gdpc import geometry as geo
from scipy.ndimage import gaussian_filter, find_objects
from gdpc.vector_tools import ivec3


import gdpc
from gdpc import Editor, geometry as geo
from gdpc.vector_tools import ivec3
import get_locations as get_loc
import build_houses 

editor = Editor(buffering=True)
# Get build area dimensions
build_area = editor.getBuildArea()


print("Build Area:", build_area)

# Convert to rectangle and load world data
buildRect = build_area.toRect()   
worldSlices = editor.loadWorldSlice(buildRect)

#geo.placeRectOutline(editor, build_area.toRect(), 64, Block("red_concrete"))

# Load heightmap
heightmap = worldSlices.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
ocean_heightmap = worldSlices.heightmaps["OCEAN_FLOOR"]
  
# Get terrain bounds
x1, z1 = build_area.begin.x, build_area.begin.z
x2, z2 = build_area.end.x, build_area.end.z


terrain_data = np.zeros((x2 - x1, z2 - z1))
ocean_data = np.zeros((x2 - x1, z2 - z1))

for x in range(x1, x2):
    for z in range(z1, z2):
        local_x, local_z = x - build_area.offset.x, z - build_area.offset.z
        

        terrain_data[local_x, local_z] = heightmap[local_x, local_z]
        ocean_data[local_x, local_z]  = ocean_heightmap[local_x, local_z]


smoothed_terrain = gaussian_filter(terrain_data, sigma=2) #why ?

# Step 6: Compute Slope
gradient_x, gradient_z = np.gradient(smoothed_terrain)
slope = np.sqrt(gradient_x**2 + gradient_z**2)

# Step 7: Define Flat Areas
flat_threshold = 1  # Define what is "flat"
flat_areas = slope <= flat_threshold 

water_threshold = 63


# BFS to find the largest connected flat/smooth area

bfs_region = get_loc.bfs_find_largest_area(flat_areas, terrain_data, water_threshold)
final_house_box = get_loc.observe_localized_region(flat_areas,bfs_region, terrain_data, build_area)


build_houses.final_build_house_terrain(editor, ocean_data, terrain_data,  build_area, final_house_box)
print("House bounding box with placeholder for height i.e y as -1: ",final_house_box)


