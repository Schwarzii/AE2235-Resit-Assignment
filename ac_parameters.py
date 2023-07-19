import numpy as np

mtow = 45810  # kg
oew = 24747  # kg
fw = 10293  # kg
plw = 11993  # kg
mlw = 39915  # kg

# Geometry + loading diagram
# datum = 2.362  # m, distance to the ac head
# lemac_arm = 13.335  # m
lemac_arm = 15.783508692365835
mac = 3.8326  # m

# From forward to backward
# Arms with respect to the ac head, m
cargo_mass = np.array([1239, 1567, 1387, 982])
cargo_arm = np.array([8683, 11836, 20575, 23475]) / 1000

# Pilot
pilot_mass = 75  # kg, assumed
pilot_arm = 2452 / 1000  # m
obs_mass = 75
obs_arm = 3060 / 1000

# Pax
pax_n = 109
pax_w = 79
pitch = 0.8128
first_arm = 5.4346
seat_row = 22

index_to_arm = lambda w, i: (lemac_arm + 0.4 * mac) - (-i * 100) / w

# Interpolate fuel loading arm
fuel_wing = np.append(np.arange(0, 7500, 500), 7745)
fuel_wing_index = np.array([0, 5, 11, 17, 19, 21, 23, 25, 25, 26, 27, 27, 26, 25, 23, 20])
fuel_wing_max = 7744  # kg
fuel_center = np.append(np.arange(0, 2600, 200), 2501)
fuel_center_index = np.array([0, 2, 4, 7, 9, 12, 15, 18, 20, 23, 26, 29, 31, 33])
fuel_center_max = max(fw - fuel_wing_max, 2512)

# Geometrical and performance parameters
mlw_n = mlw * 9.81  # N
rho_0 = 1.225  # kg/m^3
l_f = 32.501  # m
l_h = 13.56  # m
l_fn = 11.05  # m
l_n = 2.95  # m
b_ = 27.05  # m
sweep = 0  # deg
s = 61  # m^2
s_net = 32.71  # m^2
ar = 12  # -
ar_mod = (1 + 0.3) * ar
b_h = 7.31  # m
b_f = 2.7  # m
s_h = 12  # m^2
ar_h = 4.4  # -
h_f = 7.65  # m
lambda_ = 0.235  # -
c_r = 4.87  # m
c_t = 1.16  # m
c_ = 5.64  # m
c_f = 1.8  # m
s_wf = 55.15  # m^2
e_wing = 0.95  # - (wing efficiency)
cl_h = -0.8  # - lift coefficient of tail from reference

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
