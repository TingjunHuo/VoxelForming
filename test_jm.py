import numpy as np





# Example usage
grid = np.random.randint(0, 2, size=(4, 4, 4))

x, y, z = 1, 1, 1
moore_neighborhood_indices = get_3d_moore_neighborhood_indices(grid, x, y, z)

print("Original grid:")
print(grid)
print("\nIndices of the Moore neighborhood of cell (1, 1, 1):")
print(moore_neighborhood_indices)
