import numpy as np

mtow = 23000  # kg
oew = 22  # kg
fw = 22  # kg
plw = 222  # kg

# Loading diagram
datum = 2.362
lemac_arm = 13.604 * 0.99
mac = 2.303

# From forward to backward
# Arms with respect to the ac head
cargo_mass = np.array([480 + 448, 442, 254])
cargo_arm = np.array([6.697, 24.31, 23.246])

# Pilot
pilot_mass = 75  # kg, assumed
pilot_arm = 3.02

# Pax
pitch = 0.75
first_arm = 6.4151

# Interpolate fuel loading arm
fuel_quantity = np.arange(100, 1700, 100)
fuel_quantity = np.hstack([fuel_quantity, 2000, 2300, 2500, 2700, 3000, 3185])
fuel_h_arm = np.array([14.59, 14.535, 14.505, 14.488, 14.477, 14.47, 14.466, 14.463, 14.46, 14.458,
                       14.457, 14.456, 14.455, 14.455, 14.455, 14.454,
                       14.452, 14.451, 14.45, 14.446, 14.438, 14.43])