from ..ports import elevator_range, aileron_range, rudder_range

# Limits are a tuple:
# (set_neutral, set_fullpos, set_fullneg, fullpos_deg, fullneg_deg)

limits = {
        'elevator':    (0, -33, 36, elevator_range[1], elevator_range[0]),
        'rudder':      (0, 53, -53, rudder_range[1], rudder_range[0]),
        'aileron_r':   (0, 72, -72, aileron_range[1], aileron_range[0]),
        'aileron_l':   (0, 72, -72, aileron_range[1], aileron_range[0])
}
