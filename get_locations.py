from collections import deque


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
from collections import deque

import gdpc
from gdpc import Editor, geometry as geo
from gdpc.vector_tools import ivec3




def bfs_find_largest_area1(grid, terrain_data, water_threshold, slope_threshold=1):
    """ BFS to find the largest connected flat area while avoiding water & houses, stopping at steep jumps """
    rows, cols = grid.shape
    visited = set()
    largest_region = []

    def bfs(start_x, start_z):
        """ Perform BFS to explore the connected region, stopping at steep height changes """
        queue = deque([(start_x, start_z)])
        region = []
        visited.add((start_x, start_z))

        while queue:
            x, z = queue.popleft()
            height = terrain_data[x, z]  # Get height

            # Store (X, Height, Z)
            region.append((x, height, z))

            # Check in four directions (N, S, E, W)
            for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, nz = x + dx, z + dz  # New coordinates

                if (
                    0 <= nx < rows and 0 <= nz < cols and  # Stay within grid bounds
                    (nx, nz) not in visited and  # Ensure we haven't visited this already
                    grid[nx, nz] and  # Must be a flat area
                    terrain_data[nx, nz] >= water_threshold  # Must be above water level
                ):
                    # Calculate the height difference between current and next block
                    height_difference = abs(terrain_data[nx, nz] - height)
                    if height_difference <= slope_threshold:
                        # If within allowed slope, continue BFS expansion
                     
                        
                        queue.append((nx, nz))
                        visited.add((nx, nz))
                    else:
                        
                        # STOP BFS ENTIRELY IF A STEEP CHANGE IS FOUND
                        return region  # Return what we found so far without expanding further

        return region  # Return all connected points with heights

    # Run BFS for all unvisited valid starting points, looking for the largest region
    for x in range(rows):
        for z in range(cols):
            if grid[x, z] and (x, z) not in visited and terrain_data[x, z] > water_threshold:
                region = bfs(x, z)  # Run BFS for this region
                
                if len(region) > len(largest_region):
                    largest_region = region  # Update the largest found region

    return largest_region  # Return the largest detected area with height data


def bfs_find_largest_area(grid, terrain_data, water_threshold, slope_threshold=1):
    """ BFS to find the largest connected rectangular buildable region avoiding water & steep slopes """
    rows, cols = grid.shape
    visited = set()
    largest_region = []
    largest_bbox = (0, 0, 0, 0)  # (xmin, zmin, xmax, zmax)

    def bfs(start_x, start_z):
        """ Perform BFS to explore the connected region, tracking its bounding box """
        queue = deque([(start_x, start_z)])
        region = []
        visited.add((start_x, start_z))

        xmin, xmax = start_x, start_x
        zmin, zmax = start_z, start_z

        while queue:
            x, z = queue.popleft()
            height = terrain_data[x, z]  # Get height

            # Store (X, Height, Z)
            region.append((x, height, z))

            # Update bounding box
            xmin = min(xmin, x)
            xmax = max(xmax, x)
            zmin = min(zmin, z)
            zmax = max(zmax, z)

            # Check in four directions (N, S, E, W)
            for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, nz = x + dx, z + dz  # New coordinates

                if (
                    0 <= nx < rows and 0 <= nz < cols and  # Stay within grid bounds
                    (nx, nz) not in visited and  # Ensure we haven't visited this already
                    grid[nx, nz] and  # Must be a valid buildable area
                    terrain_data[nx, nz] >= water_threshold  # Must be above water level
                ):
                    # Calculate height difference
                    height_difference = abs(terrain_data[nx, nz] - height)
                    
                    if height_difference <= slope_threshold:
                        queue.append((nx, nz))
                        visited.add((nx, nz))

        # Return the region points and bounding box
        
        return region, (xmin, zmin, xmax, zmax)

    # Run BFS for all unvisited valid starting points, looking for the widest/tallest region
    for x in range(rows):
        for z in range(cols):
            if grid[x, z] and (x, z) not in visited and terrain_data[x, z] >= water_threshold:
            
                region, bbox = bfs(x, z)  # Run BFS for this region
                
                # Calculate width * height of bounding box
                bbox_width = bbox[2] - bbox[0]
                bbox_height = bbox[3] - bbox[1]
                bbox_area = bbox_width * bbox_height
                
                # Check if this is the largest bounding box found
                largest_bbox_width = largest_bbox[2] - largest_bbox[0]
                largest_bbox_height = largest_bbox[3] - largest_bbox[1]
                largest_bbox_area = largest_bbox_width * largest_bbox_height
                
                if (len(region)> len(largest_region)) and (bbox_area > largest_bbox_area):
                 
                    largest_region = region
                    largest_bbox = bbox  # Update largest bounding box
                    
    return largest_region # Return the largest detected area with bounding box

def maxArea(mat):
    """Finds the maximum rectangular area in a binary mask using dynamic programming."""
    n, m = len(mat), len(mat[0])

    # 2D matrix to store the width of 1's ending at each cell.
    memo = [[0] * m for _ in range(n)]
    ans = 0
    best_coords = (0, 0, 0, 0)  # (xmin, zmin, xmax, zmax)
    min_size = 6  # Minimum width and height constraint
    max_ratio = 2  # Maximum allowed aspect ratio (longer side should not be >2x shorter side)

    for i in range(n):
        for j in range(m):
            if mat[i][j] == 0:
                continue

            # Set width of 1's at (i, j)
            if j == 0:
                memo[i][j] = 1
            else:
                memo[i][j] = 1 + memo[i][j - 1]

            width = memo[i][j]

            # Traverse row by row, update the minimum width and calculate area.
            
            for k in range(i, -1, -1):
                height = i - k + 1 
                width = min(width, memo[k][j]) 
                area = width * (i - k + 1)
                
                if width >= min_size and height >= min_size:
                # Enforce proportionality constraint
                    if max(width / height, height / width) < max_ratio:
                        if area > ans:
                            ans = area
                            best_coords = (k, j - width + 1, i, j)  # (xmin, zmin, xmax, zmax)

    return best_coords

def plot_bfs_region(binary_grid):
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(binary_grid, cmap="gray", origin="lower", extent=[0, binary_grid.shape[1], 0, binary_grid.shape[0]])
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Region Presence (1 = Inside, 0 = Outside)")

    ax.set_title("Binary Grid Representation of Largest Detected Region")
    ax.set_xlabel("Z (East-West) (Relative to Build Area)")
    ax.set_ylabel("X (North-South) (Relative to Build Area)")
    plt.show()


def get_part_region(xmin, zmin, xmax, zmax):
    z_diff = zmax - zmin
    x_diff = xmax - xmin

    if z_diff >= 12:
        z_diff = random.randint(12, min(15, z_diff))  # Ensuring max is 15

    if x_diff >= 12:
        x_diff = random.randint(12, min(15, x_diff))  # Ensuring max is 15

    return (xmin, zmin, xmin + x_diff, zmin + z_diff)

def observe_localized_region(flat_areas,largest_region, terrain_data, build_area):
        
    
    rows, cols = terrain_data.shape
    
    
    binary_grid = np.zeros( terrain_data.shape, dtype=int)

    # Fill binary grid (1 if part of largest region, 0 otherwise)
    for x, _, z in largest_region:
        binary_grid[x, z] = 1

    plot_bfs_region(binary_grid)
    # Visualization of the binary grid
    
   
    xmin, xmax = min(x for x, _, _ in largest_region), max(x for x, _, _ in largest_region)
    zmin, zmax = min(z for _, _, z in largest_region), max(z for _, _, z in largest_region)

    
   
    # Find the largest rectangular area in the binary grid
    (xmin, zmin, xmax, zmax) = maxArea(binary_grid)
    #(xmin, zmin, xmax, zmax) = maxArea(flat_areas)
    (xmin, zmin, xmax, zmax) = get_part_region(xmin, zmin, xmax, zmax)
    
   
    
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(terrain_data, cmap="terrain", origin="lower", extent=[0, terrain_data.shape[1], 0, terrain_data.shape[0]])
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Height (Y-level)")





    if xmin != xmax and zmin != zmax:
        rect = plt.Rectangle((zmin, xmin), zmax - zmin, xmax - xmin,
                            linewidth=3, edgecolor='red', facecolor='none')#, linestyle='dashed')
        ax.add_patch(rect)
    else:
        print("Bounding box is too small or invalid.")

    ax.set_title("Largest Connected Buildable Region above sea level")
    ax.set_xlabel("Z (East-West) (Relative to Build Area)")
    ax.set_ylabel("X (North-South) (Relative to Build Area)")

    # Show plot
    plt.show()
    
    
    x1, z1 = build_area.begin.x, build_area.begin.z
    x2, z2 = build_area.end.x, build_area.end.z
    final_house_box = ((xmin + x1 + 1, -1, zmin +z1 + 1), (xmax + x1 -1, -1 ,zmax + z1 - 1))
    
    return final_house_box
