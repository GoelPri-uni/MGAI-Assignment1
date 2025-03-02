
# Import necessary modules
import matplotlib.pyplot as plt



import matplotlib.pyplot as plt
import random
from gdpc import Editor, Block
from gdpc import geometry as geo
from scipy.ndimage import gaussian_filter, find_objects
from gdpc.vector_tools import ivec3

def determine_front_wall(x1, z1, x2, z2):
    """Determine the front wall of the house."""
    width = x2 - x1
    depth = z2 - z1

    if width > depth:
        # The house is wider than deep → front is along Z-axis (north or south)
        return "north" if random.choice([True, False]) else "south"
    else:
        # The house is deeper than wide → front is along X-axis (east or west)
        return "east" if random.choice([True, False]) else "west"




def add_chimney(editor, position):
    """Adds a chimney with a smoke effect."""
    x, y, z = position

    #  Place Chimney Base (Above the House)
    geo.placeCuboid(editor, (x, y, z), (x, y + 3, z), Block("minecraft:bricks"))

    # Add Smoke Effect with a Campfire
    editor.placeBlock((x, y + 4, z), Block("minecraft:campfire"))

    print(f"Chimney added at ({x}, {y}, {z})")

def add_torches(editor, start, end):
    """Adds hanging torches or lanterns for lighting."""
    x1, y1, z1 = start
    x2, y2, z2 = end

    for x in range(x1, x2, max(2, (x2-x1)//3)):
        for z in range(z1, z2, max(2, (z2-z1)//3)):
            if random.random() < 0.5:
                editor.placeBlock((x, y2 - 1, z), Block("minecraft:torch"))  # Hanging torch
            else:
                editor.placeBlock((x, y2 - 1, z), Block("minecraft:lantern"))  # Hanging lantern



def add_furniture_all(editor: Editor, start: tuple, end: tuple):
    """Ensures proper placement of Kitchen, Bedroom, Study, Library, Carpet, and Dining Table only if space is available."""
    
    x1, y1, z1 = start
    x2, y2, z2 = end

    house_width = x2 - x1
    house_depth = z2 - z1
   
    # Ensure the house is large enough
    if house_width <= 4 or house_depth <= 4:
        print("House is too small for all furniture, reducing layout size.")
        return

    # **Divide house dynamically into sections**
    room_width = max(3, house_width // 3)  
    room_depth = max(3, house_depth // 2)  

    # Add Library (One Wall) if space allows
    if room_width >= 3:
        library_x = x1 + 1
        library_z = z1 + 1
        geo.placeCuboid(editor, (library_x, y1 + 1, library_z), 
                        (library_x + room_width - 1, y1 + 3, library_z + 1), 
                        Block("minecraft:bookshelf"))
        editor.placeBlock((library_x + 1, y1 + 1, library_z + 1), Block("minecraft:lectern"))
        print("Library added!")

    # Place Bedroom if at least 3x3 space is available
    if house_width >= 5 and house_depth >= 5:
        bed_x = x1 + house_width // 2 - 1
        bed_z = z1 + house_depth // 3
        editor.placeBlock((bed_x, y1 + 1, bed_z), Block("minecraft:cyan_bed[facing=south]"))
        editor.placeBlock((bed_x + 1, y1 + 1, bed_z), Block("minecraft:cyan_bed[facing=south, part=foot]"))
        editor.placeBlock((bed_x + 1, y1 + 1, bed_z - 1), Block("minecraft:chest"))
        
        print("Bedroom added!")

    # Place Kitchen if at least 3x2 space is available
    if room_width >= 3:
        kitchen_x = x1 + 1
        kitchen_z = z1 + room_depth + 1
        geo.placeCuboid(editor, (kitchen_x, y1 + 1, kitchen_z), 
                        (kitchen_x + 2, y1 + 1, kitchen_z + 1), 
                        Block("minecraft:quartz_block"))
        editor.placeBlock((kitchen_x, y1 + 2, kitchen_z), Block("minecraft:iron_block"))
        editor.placeBlock((kitchen_x + 1, y1 + 2, kitchen_z), Block("minecraft:barrel"))
        editor.placeBlock((kitchen_x + 2, y1 + 1, kitchen_z), Block("minecraft:furnace"))
        print("Kitchen added!")

    # Study Desk & Bookshelves if at least 4x2 space is available
    if room_width >= 4:
        study_x = x1 + 1
        study_z = z1 + house_depth - 2
        editor.placeBlock((study_x, y1 + 1, study_z), Block("minecraft:oak_fence"))  
        editor.placeBlock((study_x, y1 + 2, study_z), Block("minecraft:spruce_slab"))  
       
        print("Study Room added")

    # Place Carpet if at least 4x4 space is available
    if house_width >= 4 and house_depth >= 4:
        carpet_x = (x1 + x2) // 2
        carpet_z = (z1 + z2) // 2
        geo.placeCuboid(editor, (carpet_x - 1, y1 + 1, carpet_z - 1), 
                        (carpet_x + 1, y1 + 1, carpet_z + 1), 
                        Block("minecraft:red_carpet"))
        print("Carpet added!")

    
    print(f"Furniture placed successfully! (Library, Bedroom, Kitchen, Study, Carpet, Dining Table - if space allowed)")

def build_terrace(editor, start, end):
    """Adds a terrace on top of the house with seating, flower pots, and railings."""
    x1, y1, z1 = start
    x2, _, z2 = end

    # Terrace floor
    terrace_color = ['polished_andesite', 'polished_deepslate','grass_block']
    fence_color = ['oak_fence','birch_fence',  'crimson_fence']
    
    geo.placeCuboid(editor, (x1, y1, z1), (x2, y1, z2), Block("minecraft:"+random.choice(terrace_color)))

    # Railings
    geo.placeCuboid(editor, (x1, y1 + 1, z1), (x2, y1 + 1, z1),Block("minecraft:"+random.choice(fence_color)))
    geo.placeCuboid(editor, (x1, y1 + 1, z2 - 1), (x2, y1 + 1, z2 - 1), Block("minecraft:"+random.choice(fence_color)))

    # # Flower pots
    # editor.placeBlock((x1 + 2, y1 + 1, z1 + 2), Block("minecraft:flower_pot"))
   
    editor.placeBlock((x1 + 2, y1 + 1, z1 + 2), Block("minecraft:potted_blue_orchid"))
    
    # Seating area
    editor.placeBlock((x1 + 3, y1 + 1, z1 + 3), Block("minecraft:spruce_stairs[facing=south]"))
    editor.placeBlock((x1 + 3+2, y1 + 1, z1 + 3), Block("minecraft:spruce_stairs[facing=south]"))
    flowers = [
        "poppy", "dandelion", "azure_bluet",
        "blue_orchid", "oxeye_daisy", "cornflower"
    ]
    for x in range(x1, x2, 2):  # Every 2 blocks along X edges
        for z in [z1, z2 - 1]:  # Only place along Z edges
            if editor.getBlock((x, y1+1, z)).id == "minecraft:air":
                selected_flower = random.choice(flowers)
                
                editor.placeBlock((x, y1+1, z), Block(f"minecraft:potted_{selected_flower}"))
                
    #editor.placeBlock((x2 - 3, y1 + 1, z2 - 3), Block("minecraft:spruce_stairs[facing=north]"))

    print("Terrace added!")
    

def build_ocean_house(editor, bounding_box, ocean_data, terrain_data, build_area, min_terrain_height_house):
    """
    Constructs an ocean house with thick pillars, a wooden foundation, stairs, and a dock.
    
    :bounding_box: Tuple ((x1, y1, z1), (x2, y2, z2)) defining the house area.
    :ocean_data: Dictionary mapping (x, z) to ocean floor height.
    """
   

    # Define build area
    (x1, y1, z1), (x2, y2, z2) = bounding_box
    house_size = ivec3(x2 - x1, 6, z2 - z1)  # Width, height, depth
    dock_size = ivec3(8, 3, 5)  # Dock dimensions
    sea_level = 63  # referencefpr  Wooden platform height 

    # Define materials
    foundation_block = Block("minecraft:spruce_planks")
    pillar_block = Block("minecraft:spruce_log")
    wall_block = Block("minecraft:oak_planks")
    stair_block = Block("minecraft:spruce_stairs")
    fence_block = Block("minecraft:spruce_fence")

    # Get terrain heights for ocean floor detection
    ocean_terrain_heights = { 
        (x, z): ocean_data[x - build_area.offset.x, z - build_area.offset.z]  # Get height from terrain data (relative indexing)
        for x in range(x1, x2) for z in range(z1, z2)
    }
    

    # Determine the lowest terrain point and set foundation height
    min_height = min(ocean_terrain_heights.values())  # Lowest point (could be in water)
    foundation_height = max(sea_level, min_terrain_height_house)  # Ensure it's above water

    # Set house origin (adjusted for terrain)
    house_origin = ivec3(x1, foundation_height, z1)

    # Step 1: Build **thick 2x2 support pillars** where needed
    pillar_positions = [
        (x1, z1), (x2 - 2, z1),  # Front pillars
        (x1, z2 - 2), (x2 - 2, z2 - 2)  # Back pillars
    ]

    for px, pz in pillar_positions:
        terrain_y = ocean_terrain_heights.get((px, pz), sea_level)  # Get ocean floor height
        if terrain_y < sea_level:  # Only build pillars if terrain is below foundation
            pillar_start = ivec3(px, terrain_y- 1, pz)  # Bottom of pillar
            pillar_end = ivec3(px + 1, foundation_height, pz + 1)  # Top of pillar (2x2)
            geo.placeCuboid(editor, pillar_start, pillar_end, pillar_block)

    # Step 2: Build the **wooden platform at sea level**
    geo.placeCuboid(
        editor, 
        house_origin,
        house_origin + ivec3(house_size.x, 0, house_size.z),
        foundation_block
    )

    # Step 3: Add **fences around the platform**
    geo.placeCuboidHollow(
        editor, 
        house_origin + ivec3(0, 1, 0),  
        house_origin + ivec3(house_size.x, 1, house_size.z),  
        fence_block
    )
    
    house_box_platform = ((x1 + 1, -1, z1 + 1),(x2 - 1, -1, z2 - 1) )
    build_your_house(editor, house_box_platform, terrain_data, build_area, ref_height= True)
    
    print(f"Ocean house built at {house_origin}, with pillars and a floating dock!")

   
def final_build_house_terrain(editor, ocean_data, terrain_data,  build_area, final_house_box):
    ocean_heights_house = { 
    (x, z): ocean_data[ x- build_area.offset.x, z - build_area.offset.z]  # Correct local indexing
    for x in range(final_house_box[0][0], final_house_box[1][0]) for z in range(final_house_box[0][2], final_house_box[1][2])
    }
    

    terrain_house_heights = { 
            (x, z): terrain_data[x - build_area.offset.x, z - build_area.offset.z]  # Get height from terrain data (relative indexing)
            for x in range(final_house_box[0][0], final_house_box[1][0]) for z in range(final_house_box[0][2], final_house_box[1][2])
        }


    min_terrain_height_house = min(terrain_house_heights.values())
    print("At terrain, minimum height is ",min_terrain_height_house) 

    min_ocean_height_house = min(ocean_heights_house.values())
    print("If at ocean, minimum height from above is ",min_ocean_height_house) 


    if min_ocean_height_house < min_terrain_height_house:
        build_ocean_house(editor, final_house_box, ocean_data, terrain_data, build_area, min_terrain_height_house)
    else:
        if ((abs(final_house_box[0][2] - final_house_box[1][2])) <= 6 or abs((final_house_box[0][0] - final_house_box[1][0])) <=6):
            
            hilly_build_house(editor, final_house_box, terrain_data, build_area)
        
        else:
            
            build_your_house(editor, final_house_box, terrain_data, build_area)

def hilly_build_house(editor, final_house_box, terrain_data, build_area):
    """Builds a single treehouse using  on a pillar with different roof styles"""

   
    # Extract house placement bounds
    (x1, _, z1), (x2, _, z2) = final_house_box
    house_width = max(6, x2 - x1)
    house_depth = max(6, z2 - z1)
    house_height = random.randint(5,7)
    pillar_radius = 1  

    
    # Calculate house center and pillar placement
    pillar_x = (x1 + x2) // 2
    pillar_z = (z1 + z2) // 2

    # Use the highest terrain point to prevent floating pillars
    terrain_heights = {
        (x, z): terrain_data[x - build_area.offset.x, z - build_area.offset.z]  
        for x in range(x1, x2) for z in range(z1, z2)
    }

    highest_x, highest_z = min(terrain_heights, key=lambda pos: terrain_heights[pos])
    ground_y = terrain_heights[highest_x, highest_z]
    house_y = ground_y + random.randint(20, 23) 

    
    # ========== Build Pillar (Ensures It Reaches the Ground) ==========
    for y in range(int(ground_y), int(house_y)):
        for dx in range(-pillar_radius, pillar_radius + 1):
            for dz in range(-pillar_radius, pillar_radius + 1):
                editor.placeBlock((pillar_x + dx, y, pillar_z + dz), Block("minecraft:stone"))
        
    ladder_side_offset = pillar_radius + 1  # Offset for ladder placement (outside the pillar)

    # Ensure there's a solid block for the ladder to attach to
    for y in range(int(ground_y), int(house_y)):
        # Place a solid block (e.g., stone) next to the ladder for attachment
        editor.placeBlock((pillar_x + ladder_side_offset, y, pillar_z), Block("minecraft:stone"))
        
        # Place the ladder facing the correct direction
        editor.placeBlock((pillar_x + ladder_side_offset, y, pillar_z - 1), Block("minecraft:ladder", {"facing": "north"}))
    
    # ========== Floor ==========
    wall_material = ["minecraft:birch_planks", "minecraft:calcite", "minecraft:spruce_planks", "minecraft:crimson_planks"]
    floor_material= random.choice(["minecraft:stone", "minecraft:spruce_planks", "minecraft:polished_diorite"])
    
    house_x_start = pillar_x - house_width // 2
    house_z_start = pillar_z - house_depth // 2

    for x in range(house_width):
        for z in range(house_depth):
            editor.placeBlock((house_x_start + x, house_y, house_z_start + z), Block(floor_material))

    # ========== Walls ==========
   
    for x in range(house_width):
        for z in range(house_depth):
            if x in [0, house_width - 1] or z in [0, house_depth - 1]:  
                for y in range(1, house_height):
                    block_type = random.choice(wall_material) if random.random() > 0.5 else "minecraft:glass_pane"
                    editor.placeBlock((house_x_start + x, house_y + y, house_z_start + z), Block(block_type))

    # ========== Based Roof Options ==========
    roof_options = ["dome",  "terrace", "windmill"]
    chosen_roof = random.choice(roof_options)
    print(f"Using {chosen_roof} roof design.")

    roof_base_y = house_y + house_height  

    if chosen_roof == "dome":

        roof_material = random.choice(["minecraft:red_wool", "minecraft:dark_oak_planks", "minecraft:copper_block"])
        for y in range(4):
            radius = (house_width // 2) * (1 - y / 4)  
            for x in range(house_width):
                for z in range(house_depth):
                    dx = x - house_width // 2
                    dz = z - house_depth // 2
                    if dx**2 + dz**2 <= radius**2:
                        editor.placeBlock((house_x_start + x, roof_base_y + y, house_z_start + z), Block(roof_material))

   
    elif chosen_roof == "terrace":
        fence_material = "minecraft:spruce_fence"
        for x in range(house_width):
            for z in range(house_depth):
                editor.placeBlock((house_x_start + x, roof_base_y, house_z_start + z), Block("minecraft:oak_planks"))

        for x in range(house_width):
            editor.placeBlock((house_x_start + x, roof_base_y + 1, house_z_start), Block(fence_material))
            editor.placeBlock((house_x_start + x, roof_base_y + 1, house_z_start + house_depth - 1), Block(fence_material))

        for z in range(house_depth):
            editor.placeBlock((house_x_start, roof_base_y + 1, house_z_start + z), Block(fence_material))
            editor.placeBlock((house_x_start + house_width - 1, roof_base_y + 1, house_z_start + z), Block(fence_material))

    elif chosen_roof == "windmill":
        windmill_base_y = roof_base_y  
        windmill_center_x = pillar_x
        windmill_center_z = pillar_z

        # Create Windmill Base (Properly Attached to House)
        for x in range(-2, 3):
            for z in range(-2, 3):
                editor.placeBlock((windmill_center_x + x, windmill_base_y, windmill_center_z + z), Block("minecraft:spruce_planks"))

        # Windmill Tower
        for y in range(6):
            editor.placeBlock((windmill_center_x, windmill_base_y + y, windmill_center_z), Block("minecraft:spruce_log"))

        # Windmill Blades
        blade_length = 4
        for i in range(1, blade_length + 1):
            editor.placeBlock((windmill_center_x + i, windmill_base_y + 5, windmill_center_z), Block("minecraft:white_wool"))
            editor.placeBlock((windmill_center_x - i, windmill_base_y + 5, windmill_center_z), Block("minecraft:white_wool"))
            editor.placeBlock((windmill_center_x, windmill_base_y + 5, windmill_center_z + i), Block("minecraft:white_wool"))
            editor.placeBlock((windmill_center_x, windmill_base_y + 5, windmill_center_z - i), Block("minecraft:white_wool"))

        # Add Ladder for Windmill Access
        for y in range(1, 6):
            editor.placeBlock((windmill_center_x, windmill_base_y + y, windmill_center_z - 1), Block("minecraft:ladder"))
    add_furniture_all(editor, (x1, house_y, z1 ) ,(x2, _, z2))
    
    
    print(f"Treehouse Built with {chosen_roof} Roof and Windmill Base Successfully!")




def add_flowers_and_decorations(editor, x1, x2, z1, z2, terrain_data, ref_height, build_area, max_height):
    if ref_height:
        return
    flower_types = [
        "minecraft:dandelion", "minecraft:poppy", "minecraft:azure_bluet",
        "minecraft:oxeye_daisy", "minecraft:cornflower", "minecraft:allium",
        "minecraft:blue_orchid", "minecraft:lilac", "minecraft:rose_bush",
        "minecraft:sunflower", "minecraft:peony"
    ]
    potted_flowers = [
        "potted_dandelion", "potted_poppy", "potted_azure_bluet",
        "potted_oxeye_daisy", "potted_cornflower", "potted_allium",
        "potted_blue_orchid"
    ]

    for _ in range(4):  # Repeat the process 4 times for denser flower placement
        
        for x in range(x1 - 3, x2 + 3):  # Extend the area further
            try:
                for z in range(z1 - 3, z2 + 3):
                # if (x1 - 1 <= x <= x2 + 1 and z1 - 1 <= z <= z2 + 1):
                #     continue  # Skip directly next to the house
                    try:
                        if (
                            x < build_area.offset.x or x >= build_area.offset.x + build_area.size.x or
                            z < build_area.offset.z or z >= build_area.offset.z + build_area.size.z
                        ):
                            continue  # Skip if outside the build area

                        block_below = editor.getBlock((x, terrain_data[x - build_area.offset.x, z - build_area.offset.z] , z))  # Get the terrain block

                        if "grass" in block_below.id:  
                            
                            
                            editor.placeBlock((x, terrain_data[x - build_area.offset.x, z - build_area.offset.z] , z), Block(random.choice(flower_types)))
                            try:
                                block_above = editor.getBlock((x+1, terrain_data[x+1 - build_area.offset.x, z+1 - build_area.offset.z] + 1, z+1))  # Get the block above
                                if "air" in block_above.id:
                                    editor.placeBlock((x+1, terrain_data[x+1 - build_area.offset.x, z+1 - build_area.offset.z] , z+1), Block(f"minecraft:{random.choice(potted_flowers)}"))
                            except:
                                pass
                        
                        elif "sand" in block_below.id:  
                            try:
                                editor.placeBlock((x, terrain_data[x - build_area.offset.x, z - build_area.offset.z] , z), Block("minecraft:redstone_wire"))
                            except:
                                print("Could not place the redstoe wire")
                                pass
                            
                    except:
                        pass 
                
            except:
                pass
                   

def build_your_house(editor, bounding_box, terrain_data, build_area, ref_height = False):
    x1 , _, z1 = bounding_box[0]
    x2, _, z2 = bounding_box[1]
    
    wall_colors = ["minecraft:birch_planks", "minecraft:calcite",  "minecraft:crimson_planks"]
    roof_colors = ["minecraft:warped_stairs", "minecraft:spruce_stairs", "minecraft:blackstone_stairs", "minecraft:crismon_stairs"] 

    floor_colors = ["minecraft:stone", "minecraft:spruce_planks", "minecraft:polished_diorite"]
    
    window_colors = ["minecraft:glass", "minecraft:tinted_glass", "minecraft:glass_pane"]
    door_types = ['birch_door', 'acacia_door', 'spruce_door','oak_door','iron_door', 'dark_oak_door', 'mangrove_door']
    # Randomize 
    
    wall_block = Block(random.choice(wall_colors))
    roof_block = Block(random.choice(roof_colors))
  
    floor_block = Block(random.choice(floor_colors))
    window_block = Block(random.choice(window_colors))
   
    house_height = random.randint(6, 10)
    
    terrain_heights = { 
        (x, z): int(terrain_data[x - build_area.offset.x, z - build_area.offset.z])  # Get height from terrain data (relative indexing)
        for x in range(x1, x2) for z in range(z1, z2)
    }
    
    max_height = max(terrain_heights.values()) 
    if (max_height - min(terrain_heights.values()) > 3) and ref_height!=True:
        hilly_build_house(editor, bounding_box, terrain_data, build_area)
        return
    
    if ref_height:  #for ocean, to build only above the platform
        max_height = max_height + 1
    
    
    print("At max height ", max_height)
    for (x, z), terrain_y in terrain_heights.items():
        for y in range(int(terrain_y), int(max_height)+1 ):  # Grow the blocks upwards
            editor.placeBlock((x, y, z), floor_block)  # Fill in the foundation

    
    #once the foundation was built above, we placed a hollow cuboid for exterior of house, randomize the height of the wall
    geo.placeCuboidHollow(
    editor, 
    (x1, max_height, z1),  # Ensure it starts from the correct foundation height
    (x1 + (x2 - x1) - 1, max_height + house_height, z1 + (z2 - z1) - 1),  # Keep within bounds
    wall_block
    )
    
    door_x = x1 + (x2 - x1) // 2
    
    door_z = z1  # Assume door faces front
    # Determine the front wall
    front = determine_front_wall(x1, z1, x2, z2)
    
    if front == "north":
        door_x = (x1 + x2) // 2
        door_z = z1  
    elif front == "south":
        door_x = (x1 + x2) // 2
        door_z = z2 - 1  
    elif front == "east":
        door_x = x2 - 1 
        door_z = (z1 + z2) // 2
    else:  # west
        door_x = x1  
        door_z = (z1 + z2) // 2
        
    door_y = max_height + 1  # One block above the ground
   
    torch_x = door_x
    torch_y = door_y + 2  # Two blocks above the ground
    torch_z = door_z

   
    # Select a random door type
    selected_door = random.choice(door_types)

    # Place the door with correct facing
    editor.placeBlock((door_x, door_y, door_z), Block(f"minecraft:{selected_door}[facing={front},half=lower]"))
    editor.placeBlock((door_x, door_y+1 , door_z), Block(f"minecraft:{selected_door}[facing={front},half=upper]"))
    
    
    slab_y = door_y + 2  # One block above the top of the door
    
    if front=="north":
        slab_pos = (door_x, slab_y, door_z - 1)
    elif front=="south":
        slab_pos = (door_x, slab_y, door_z + 1)
    elif front=="west":
        slab_pos = (door_x - 1, slab_y, door_z)
    elif front=="east":
        slab_pos = (door_x + 1, slab_y, door_z)
    else:
        slab_pos = (door_x + 1, slab_y, door_z)  # Default behavior
        

    editor.placeBlock(slab_pos, Block("minecraft:stone_slab[type=top]"))
    ladder_start = max(door_y - 1, terrain_heights[door_x, door_z])
    for y in range(ladder_start, terrain_heights[door_x, door_z], -1):
        editor.placeBlock((slab_pos[0], y, slab_pos[2]), Block("minecraft:ladder", {"facing": front}))

    
    window_patterns = ["full_wall", "checkerboard", "symmetric", "random_sparse"]
    selected_pattern = random.choice(window_patterns)

    for y in range(max_height + 1, max_height + house_height - 1):
        for x in range(x1, x2):
            for z in range(z1, z2):
                if x not in (x1, x2 - 1) and z not in (z1, z2 - 1):
                    continue  # Only place windows on outer walls

                if (x, z) == (door_x, door_z):  
                    continue  # Skip door area
                
                # Avoid placing windows on corners
                if (x, z) in [(x1, z1), (x1, z2 - 1), (x2 - 1, z1), (x2 - 1, z2 - 1)]:
                    continue  # Skip all four corners

                # Apply the selected window pattern
                if selected_pattern == "full_wall":
                    if y % 2 == 0:
                        editor.placeBlock((x, y, z), window_block)

                elif selected_pattern == "checkerboard":
                    if (x + z) % 2 == 0:
                        editor.placeBlock((x, y, z), window_block)

                elif selected_pattern == "symmetric":
                    if x in [x1 + 2, x2 - 3] or z in [z1 + 2, z2 - 3]:
                        editor.placeBlock((x, y, z), window_block)

                elif selected_pattern == "random_sparse":
                    if random.random() < 0.3:
                        editor.placeBlock((x, y, z), window_block)

    roof_types = ['dome','terrace']
    roof_choice = random.choice(roof_types)
    roof_stair_types = ['end_stone_brick_stairs','spruce_stairs','smooth_red_sandstone_stairs']
    
    if roof_choice == 'dome':
        
        roof_block = Block("minecraft:"+ random.choice(roof_stair_types)+"[facing=south]")
        for i in range(3):
                geo.placeCuboid(
                    editor,
                    (x1 + i, max_height + house_height + i, z1 + i),
                    (x2 - i, max_height + house_height + i, z2 - i),
                    roof_block
                )
    if roof_choice == 'terrace':
        build_terrace(editor, (x1, max_height+ house_height, z1), (x2, _, z2))
        
    
    
    add_furniture_all(editor, (x1, max_height, z1 ) ,(x2, _, z2))
    
    add_chimney(editor, (x2 - 2, max_height + house_height - 1, z2 - 2))

    
    add_torches(editor, (x1, max_height  , z1 ), (x2, max_height + house_height, z2))
    
    
    add_flowers_and_decorations(editor, x1, x2, z1, z2, terrain_data, ref_height, build_area, max_height)
    
    

