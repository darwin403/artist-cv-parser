import json
import logging
import re
import sys
from math import sqrt

import coloredlogs

coloredlogs.install(
    fmt='%(asctime)s [%(programname)s] %(levelname)s %(message)s')

# load aws response
blocks = json.load(open('lionel/apiResponse.json'))["Blocks"]

logging.info('[pdf] found blocks: %s' % len(blocks))



def find_year_indices(start_index,end_index):
    """Find all indicides of years between (and including) a starting and ending index.

    Args:
        start_index (int): The start index from which to search.
        end_index (int): The end index up to which to search.

    Returns:
        list: A list of indices where an year was found.
    """

    indices = []

    # iterate from first to start to find all years
    for i in range(start_index,end_index+1):
        text = blocks[i].get("Text")
        
        # push a valid year
        if text and re.compile("\d{4}").match(text) :
            indices.append(i)

    return indices

def determine_section_indexes(start_text , end_text):
    """Find all indicides that occur between two text blocks.

    Args:
        start_text (int): The start text from which to consider indices.
        end_text (int): The end text up to which to consider incides.

    Returns:
        tuple: A tuple of indices occuring between given texts.
    """

    start_index = 0
    end_index = 0
    
    for i,block in enumerate(blocks):
        text = block.get("Text")

        # push start_index
        if text and start_text.lower() in text.lower():
            start_index = i
        
        # push end_index
        if text and end_text.lower() in text.lower():
            end_index = i
            break

    return (start_index, end_index)

# find start and end index between solo and group exhibitions
start_index, end_index = determine_section_indexes("Solo Exhibitions","Group Exhibitions")

# find all year indices between solo and group exhibitions
year_indexes = find_year_indices(start_index,end_index)

logging.info('[solo] index range: %s, %s' %(start_index, end_index))
logging.info('[solo] year indices: %s' % year_indexes)



def distance(coordinate1, coordinate2):
    """Calculate the absolute distance between two coordinates.

    Args:
        coordinate1 (dict): A dictionary with properties "X" and "Y" which denote the cartesian coordinate.
        coordinate2 (dict): A dictionary with properties "X" and "Y" which denote the cartesian coordinate.

    Returns:
        float: The distance between the given two coordinates.
    """

    return sqrt((coordinate1["X"]-coordinate2["X"])**2 + (coordinate1["Y"]-coordinate2["Y"])**2)

def minimum_distance_between_indices(index1, index2):
    """Calculate the minimum distance between two texts by index.

    Args:
        index1 (int): The first index to consider.
        index2 (int): The second index to consider.

    Returns:
        float: The minimum distance between the Polygons for given two indexes.
    """
    poly1 = blocks[index1].get("Geometry", {}).get("Polygon")
    poly2 = blocks[index2].get("Geometry", {}).get("Polygon")

    all_distances = [distance(i,j) for i in poly1 for j in poly2]
    return min(all_distances)

def element_closest_to(base_index, far_indices):
    """Find the closest index to a given index.

    Args:
        base_index (str): The base index to calculate distances from.
        far_indices (list): The list of indices to check.

    Returns:
        tuple: A tuple of (index,distance) from a list of indices which is closest to base_index.
    """

    all_minimum_distances = [(i, minimum_distance_between_indices(base_index, i)) for i in far_indices]
    all_minimum_distances.sort(key=lambda x: x[1])
    closest_index,closest_distance = all_minimum_distances[0]
    return (closest_index,closest_distance)

def relations_to_text(relations):
    """Convert a indices relations object to text.

    Args:
        relations (dict): A dictionary of relation where each property is an year and the value is a list of indices children to this year.

    Returns:
        dict: The same dictionary where indices are replaced with respective text.
    """
    relations_text = {}
    for i,v in relations.items():
        relations_text[blocks[i].get("Text")] = list(map(lambda x: blocks[x].get("Text"),v))
    return relations_text

# hoist data
relations = {}

# create distance of indices
chunk_indexes = ([(index,year_indexes[i+1]) for i,index in enumerate(year_indexes) if i+1 != len(year_indexes) ])

# iterate over all chunks
for (year_start_index, year_end_index) in chunk_indexes:
    closest_index = year_start_index
    relations[year_start_index] = []
    while True:
        # find closest index to year_start_index
        closest_index,closest_distance  = element_closest_to(closest_index, range(closest_index+1,year_end_index+1))

        # if closest index is year_end_index, end loop
        if (closest_index >= year_end_index):
            break
        
        # if not push the index as an association of the year_start_index
        relations[year_start_index].append(closest_index)



result = relations_to_text(relations)
logging.info(json.dumps(result, indent=2))
