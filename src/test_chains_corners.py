# Minimal test for Chains corner clipping
import sys
sys.path.insert(0, '../src')
from Chains import Chains

# Define a square boundary
boundary = [(0.0, 0.0), (10.0, 10.0)]

# Test cases: lines that cross, touch, or start/end at corners
chains = [
    [(0.0, 0.0), (10.0, 10.0)],  # Diagonal through both corners
    [(0.0, 10.0), (10.0, 0.0)],  # Other diagonal
    [(0.0, 0.0), (0.0, 10.0)],   # Along left edge
    [(10.0, 0.0), (10.0, 10.0)], # Along right edge
    [(0.0, 0.0), (10.0, 0.0)],   # Along bottom edge
    [(0.0, 10.0), (10.0, 10.0)], # Along top edge
    [(-5.0, 0.0), (15.0, 10.0)], # Crosses through two corners
    [(0.0, -5.0), (10.0, 15.0)], # Crosses through two corners vertically
]

clipped = Chains.bound([chain for chain in chains], boundary)

for i, chain in enumerate(clipped):
    print(f"Chain {i}:")
    for pt in chain:
        print(f"  {pt}")
    print()
