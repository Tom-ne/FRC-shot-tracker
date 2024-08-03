import math
import numpy as np

# replace with actual shot positions
shot_positions = [(320, 240), (310, 230), (330, 250), (315, 235), (340, 260)]

# replace with center
target_center = (320, 240)

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

distances = [calculate_distance(position, target_center) for position in shot_positions]

mean_distance = np.mean(distances)

std_deviation = np.std(distances)

max_spread = max(
    calculate_distance(shot_positions[i], shot_positions[j])
    for i in range(len(shot_positions))
    for j in range(i + 1, len(shot_positions))
)

print(f"Mean Distance from Center: {mean_distance:.2f}")
print(f"Standard Deviation of Distances: {std_deviation:.2f}")
print(f"Maximum Spread between Shots: {max_spread:.2f}")
