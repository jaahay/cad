"""Canonical tactile-dice design parameters and face definitions."""

SIZE = 24.0
HALF = SIZE / 2.0
PIP_OFFSET = 4.7
PIP_SPHERE_RADIUS = 2.4
PIP_DEPTH = 0.9

# Raised tactile count marks.
BUBBLE_RADIUS = 2.0
BUBBLE_HEIGHT = 0.75
BUTTON_RADIUS = 1.75
BUTTON_HEIGHT = 0.65
BUTTON_EMBED = 0.65

# Raised paw-print count marks. Toe lobes overlap the main pad so one paw
# remains one connected, countable tactile mark.
PAW_PAD_RADIUS = 1.45
PAW_PAD_HEIGHT = 0.72
PAW_TOE_RADIUS = 0.72
PAW_TOE_HEIGHT = 0.58
PAW_TOE_OFFSETS = (
    (-0.95, 1.05),
    (-0.33, 1.38),
    (0.33, 1.38),
    (0.95, 1.05),
)

# Nested-steps body treatment.
NESTED_OUTER_PANEL = 17.5
NESTED_INNER_PANEL = 13.5
NESTED_OUTER_DEPTH = 0.25
NESTED_INNER_DEPTH = 0.45

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
