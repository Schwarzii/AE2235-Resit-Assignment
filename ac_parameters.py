import numpy as np

mtow = 45810  # kg
oew = 24747  # kg
fw = 10293  # kg
plw = 11993  # kg
mlw = 39915  # kg

# Loading diagram
datum = 2.362  # m, distance to the ac head
lemac_arm = 13.604 * 0.99  # m
mac = 2.303  # m

# From forward to backward
# Arms with respect to the ac head, m
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

# Geometrical and performance parameters
mlw_n = mlw * 9.81  # N
rho_0 = 1.225  # kg/m^3
l_f = 27.17  # m
l_h = 13.56  # m
l_fn = 11.05  # m
l_n = 2.95  # m
b_ = 27.05  # m
sweep = 0  # deg
s = 61  # m^2
s_net = 32.71  # m^2
ar = 12  # -
ar_mod = (1 + 0.2) * ar
b_h = 7.31  # m
b_f = 2.7  # m
s_h = 12  # m^2
ar_h = 4.4  # -
h_f = 7.65  # m
# lambda_ = 0.24  # -
c_r = 4.87  # m
c_t = 1.16  # m
c_ = 5.64  # m
c_f = 1.8  # m
s_wf = 55.15  # m^2
e_wing = 0.95  # - (wing efficiency)
cl_h = -0.8  # - lift coeff of tail from reference

# Performance parameters
r_max_pax = 1370  # km
v_climb = 87.45  # m/s
v_max_cruise = 138.89  # m/s
fuel_cruise = 650  # kg/h
net_ceiling = 2990  # m
ho = 7620  # m
v_cruise = 128.61  # m/s
R70_pax = 1528  # km
roc = 6.88  # m/s
mach = 0.43  # -
v_app = 61.67  # m/s
v_app_mod = 56.3
