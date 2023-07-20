import numpy as np

mtow = 45810  # kg
oew = 24747  # kg
fw = 10293  # kg
plw = 11993  # kg
mlw = 39915  # kg


def trans_top(x):
    return x * 35.528 / 21.168  # m


def trans_side(x):
    return x * l_f / 20.029  # m


# Geometry + loading diagram
# datum = 2.362  # m, distance to the ac head
# lemac_arm = 13.335  # m
lemac_arm = trans_top(9.404)
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
mlw_n = mlw * 9.81  # N, maximum landing weight
rho_0 = 1.225  # kg/m^3, sea-level density
a_0 = np.sqrt(1.4 * 287.15 * 288.15)  # m/s, sea-level sound speed
l_f = 32.501  # m, length of fuselage
l_h = 16  # m, tail arm, distance between 0.25 chord of mac and h tail
l_fn = trans_top(8.3516985794)  # m, characteristic length of fuselage nose
l_n = -trans_top(6.0506921084)  # m, characteristic distance of nacelle w.r.t 0.25 MAC
b = 28.08  # m, wing span
sweep_le = np.radians(90 - 67.8059412113)  # rad, sweep angle at leading edge of wing
sweep_quarter = np.radians(17.45)  # rad, sweep angle at 0.25 chord of wing
sweep_half = np.radians(90 - 76.4340451036)  # rad, sweep angle at 0.5 chord of wing
sweep_h = np.radians(90 - 66.5184668378)  # rad, sweep angle at 0.5 chord of h tail
s = 93.5  # m^2, wing area
ar = 8.43  # -, aspect ratio of wing
ar_mod = (1 + 0.3) * ar  # -, aspect ratio of wing after modification
b_h = 10.04  # m, wing span of h tail
b_f = 3.3  # m, fuselage diameter
b_n = trans_top(0.9028428563)  # m, width of nacelle
s_h = 0.232 * s  # m^2, area of h tail
ar_h = 4.64  # -, aspect ratio of h tail
h_f = b_f  # m, height of fuselage = fuselage diameter
taper = 0.235  # -, taper ratio
c_r = trans_top(3.1782058575)  # m, root chord
c_t = trans_top(0.8621005777)  # m, tip chord
s_net = s - c_r * b_f  # m^2, net wing area, wing area - fuselage projected area

# Performance parameters
v_cruise = 234.72  # m/s
mach = 0.77  # -
v_app = 128.611  # m/s
v_app_mod = 56.3
