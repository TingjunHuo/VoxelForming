import numpy as np

temple = np.array([[0, 1, 0],
              [1, 0, 1],
              [0, 1, 0]])

occ = np.array([[0, 1, 1],
       [0, 0, 0],
       [0, 0, 0]])

cand = np.array([[0, 0, 0],
       [0, 1, 0],
       [0, 0, 0]])

neig = occ * temple
print(neig)

