"""Canonical tactile-dice design parameters and face definitions."""

SIZE = 24.0
HALF = SIZE / 2.0
PIP_OFFSET = 4.7
PIP_SPHERE_RADIUS = 2.4
PIP_DEPTH = 0.9

# Standard d6 layout chosen for this family:
# +Z=1, -Z=6, +Y=2, -Y=5, +X=3, -X=4.
# Opposite faces sum to 7.
FACE_VALUES = {
    "+Z": 1,
    "-Z": 6,
    "+Y": 2,
    "-Y": 5,
    "+X": 3,
    "-X": 4,
}

PIPS = {
    1: [(0, 0)],
    2: [(-1, 1), (1, -1)],
    3: [(-1, 1), (0, 0), (1, -1)],
    4: [(-1, 1), (1, 1), (-1, -1), (1, -1)],
    5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)],
    6: [(-1, 1), (-1, 0), (-1, -1), (1, 1), (1, 0), (1, -1)],
}

OPPOSITE_FACES = (("+Z", "-Z"), ("+Y", "-Y"), ("+X", "-X"))
