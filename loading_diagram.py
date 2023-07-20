import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from matplotlib.ticker import MultipleLocator
from ac_parameters import *
from CG_calc import lemac, Aircraft


class LoadDiagram:
    def __init__(self, init_mass, init_cg, cmap='Set2', margin=2):
        self.acc_mass = init_mass
        self.acc_moment = [init_mass * init_cg, init_mass * init_cg]

        self.load_mass = {'OEW': [np.array([init_mass])]}
        self.load_cg = {'OEW': [np.array([init_cg])]}

        # Dummy variables
        self.cg_min = 100
        self.cg_max = 0

        self.cmap = cmap
        self.margin = margin

        self.cg_range = np.array([self.cg_min - self.margin, self.cg_max + self.margin])

    def calculate(self, payload, mass, arm, arm_conversion=True, loaded=False, fwd=True):
        acc_mass = self.acc_mass + np.hstack([0, np.cumsum(mass)])

        if arm_conversion:
            arm = lemac(arm)
        moment = mass * arm
        acc_moment = self.acc_moment[not fwd] + np.hstack([0, np.cumsum(moment)])
        cg = acc_moment / acc_mass

        self.cg_min = min(np.min(cg), self.cg_min)
        self.cg_max = max(np.max(cg), self.cg_max)

        if loaded:
            self.acc_mass = acc_mass[-1]
        if fwd:
            self.acc_moment[0] = acc_moment[-1]
        else:
            self.acc_moment[1] = acc_moment[-1]

        if payload in self.load_mass:
            self.load_mass[payload].append(acc_mass)
            self.load_cg[payload].append(cg)
        else:
            self.load_mass[payload] = [acc_mass]
            self.load_cg[payload] = [cg]

    def load_cargo(self, payload='Cargo', overload=False):
        # fwd -> aft
        mass_fwd = cargo_mass.copy()
        mass_aft = np.flip(mass_fwd).copy()

        arm_fwd = cargo_arm
        arm_aft = np.flip(arm_fwd)

        if overload:
            max_cargo = plw - pax_n * pax_w
            if max_cargo < np.sum(cargo_mass):
                for m in (mass_fwd, mass_aft):
                    capacity = np.cumsum(m) - max_cargo
                    m[capacity > 0] -= capacity[capacity > 0]
                    m[m < 0] = np.zeros(len(m[m < 0]))  # Not fill the rest cargo holds
        self.calculate(payload, mass_fwd, arm_fwd)
        self.calculate(payload, mass_aft, arm_aft, loaded=True, fwd=False)

    def load_pilot(self, payload='Pilot', observer=False, loaded=True, fwd=True):
        crew = 2 if not observer else 3
        mass = np.ones(crew) * pilot_mass
        arm = np.ones(crew) * pilot_arm
        if observer:
            mass[-1] = obs_mass
            arm[-1] = obs_arm
        self.calculate(payload, mass, arm, loaded=loaded, fwd=fwd)

    def load_pax_w(self, pos, payload='Seats', n_seat=2, n_row=seat_row, w_pax=pax_w,
                   seat_counter=None):
        payload = f'{payload} ({pos})'

        # fwd -> aft
        arm = np.arange(n_row) * pitch + first_arm
        mass = np.ones(n_row) * n_seat * w_pax  # No order
        if seat_counter:
            for r, n in seat_counter.items():
                mass[r] = n * w_pax
        self.calculate(payload, mass, arm)
        self.calculate(payload, mass[::-1], arm[::-1], loaded=True, fwd=False)

    def load_fuel(self, payload='Fuel', fuel_arm_curve='linear',
                  fuel_limit=fw, load_limit=mtow, center_tank=False,
                  loaded=True, fwd=True):
        if center_tank:
            fuel_arm = interp1d(fuel_center, fuel_center_index)
        else:
            fuel_arm = interp1d(fuel_wing, fuel_wing_index, kind=fuel_arm_curve)

        ava_fuel = min(load_limit - self.acc_mass, fuel_limit)
        if ava_fuel <= 0:
            return

        fuel_load = np.linspace(0, ava_fuel, 10, retstep=True)
        # print(fuel_load)

        fuel_load, fuel_step = fuel_load[0][1:], fuel_load[1]
        fuel_load_index = fuel_arm(fuel_load) * -1

        arm = index_to_arm(fuel_load + self.acc_mass, fuel_load_index)

        fuel = np.ones(len(arm)) * fuel_step
        # arm = fuel_arm(ava_fuel / 2)  # Divide fuel into two tanks
        self.calculate(payload, fuel, arm, loaded=loaded, fwd=fwd)

    def load_standard(self, observer=False, overload=False):
        self.load_cargo(overload=overload)
        self.load_pilot(observer=observer, loaded=False)
        self.load_pilot(observer=observer, fwd=False)
        self.load_pax_w('window')
        self.load_pax_w('aisle')
        self.load_pax_w('middle', n_seat=1, n_row=seat_row - 1)
        self.load_fuel('Fuel (wing)', fuel_arm_curve='quadratic', fuel_limit=fuel_wing_max, loaded=False)
        self.load_fuel('Fuel (wing)', fuel_arm_curve='quadratic', fuel_limit=fuel_wing_max, fwd=False)

        self.load_fuel('Fuel (center)', fuel_limit=fuel_center_max, center_tank=True, loaded=False)
        self.load_fuel('Fuel (center)', fuel_limit=fuel_center_max, center_tank=True, fwd=False)
        self.cg_range = np.array([self.cg_min - self.margin, self.cg_max + self.margin])

    def load_modified(self):
        self.load_cargo()  # Modified
        self.load_pilot()
        self.load_pax_w('window')
        self.load_pax_w('aisle')
        self.load_pax_w('middle', n_seat=1, n_row=seat_row - 1)
        self.load_fuel()

    def plot(self, title='', overlay=False, save=None):
        # Limit of plot range
        x_lim = [((self.cg_min - self.margin) // 10 - 1) * 10,
                 ((self.cg_max + self.margin) // 10 + 1) * 10]
        y_lim = [oew // 2000 * 2000,
                 (mtow // 8000 + 1) * 8000]

        if self.cmap == 'gray':
            colors = ['lightgray'] * len(self.load_mass)
            alpha = 0.4
        else:
            color_map = plt.get_cmap(self.cmap)
            colors = color_map(np.arange(len(self.load_mass)))
            alpha = 1

            # MTOW line
            plt.axhline(y=mtow, linestyle='dashed', color='tomato')
            plt.text(x_lim[1] + 1, mtow - 150, 'MTOW')

            # MZFW line
            plt.axhline(y=self.load_mass['Fuel (wing)'][0][0], linestyle='dashed', color='lightsalmon', alpha=0.7)
            plt.text(x_lim[1] + 1, self.load_mass['Fuel (wing)'][0][0] - 150, 'MZFW')

        # Flip the plotting order (previous plotted line is on top)
        order = np.arange(1, len(self.load_mass) + 1)[::-1]

        ax = plt.subplot(111)
        for (l, m), cg, c, o in zip(self.load_mass.items(), self.load_cg.values(), colors, order):
            back = 0  # Check loading direction
            for lm, lcg in zip(m, cg):
                line_style = '-o' if back == 0 else '-^'
                label = '' if self.cmap == 'gray' else l  # Hide label if overlaid

                ax.plot(lcg, lm, line_style, color=c, label=label, zorder=o, alpha=alpha)

                back += 1

        if overlay:
            # Draw two dummy points to manually add two legend labels
            plt.plot(-1, 1, '-o', color='lightgray', label='Original design', alpha=alpha)
            plt.plot(-1, 1, '-^', color='lightgray', label='Original design', alpha=alpha)

        if self.cmap != 'gray':
            plt.xlim(x_lim)
            plt.ylim(y_lim)

            # Draw min / max CG lines
            plt.plot(np.ones(2) * (self.cg_min - self.margin), [y_lim[0], mtow], '-.k', label='Min/Max CG')
            plt.plot(np.ones(2) * (self.cg_max + self.margin), [y_lim[0], mtow], '-.k')

            # Position legend at the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.21,
                             box.width, box.height * 0.85])
            plt.legend(loc='center', bbox_to_anchor=(0.5, -0.25), ncols=4)

            # Position the legend on the right side
            # ax.set_position([box.x0, box.y0,
            #                  box.width * 0.8, box.height * 1.08])
            # plt.legend(loc='lower left', bbox_to_anchor=(1.02, 0))

            # Minor tickers and grid
            ax.xaxis.set_minor_locator(MultipleLocator(2.5))
            ax.yaxis.set_minor_locator(MultipleLocator(500))
            plt.grid()

            # Axis label and title
            plt.xlabel(r'$x_{CG}$ [%MAC]')
            plt.ylabel('Mass [kg]')
            plt.title(title)

        if save:
            plt.savefig(f'plots/{save}.png', dpi=300)


if __name__ == '__main__':
    fokker = Aircraft()
    print(lemac_arm)

    # oew_arm_n = 44.5  # LEMAC -> 44.5% MAC
    # oew_arm_n = lemac(12.26682 + datum)

    fig = plt.figure(figsize=(7, 6))
    # fig = plt.figure(figsize=(8, 6))  # Legend at right

    # Part I loading diagram
    ld_i = LoadDiagram(fokker.oew, fokker.cg_oew)
    ld_i.load_standard(True, True)
    ld_i.plot(f'Loading diagram of Fokker 100, LEMAC @ {round(lemac_arm, 2)} m')
    # ld_i.plot(f'Loading diagram of Fokker 100, LEMAC @ {round(lemac_arm, 2)} m', save='loading_diagram_sep_I')
    print(ld_i.cg_range)

    # Setting for overlaid plot
    # ld_o = LoadDiagram(oew_o, oew_arm_o, cmap='gray')
    # ld_o.load_standard()
    # ld_o.plot()

    # ld_1 = LoadDiagram(oew_n, oew_arm_n, cmap='gray')
    # ld_1.load_modified()
    # ld_1.plot()
    #
    # ld_n = LoadDiagram(oew, 79, cmap='Set2')
    # ld_n.load_modified()
    # ld_n.plot('Loading diagram (modified design)', overlay=True)
    # print(ld_n.cg_min, ld_n.cg_max)
    # print(ld_n.cg_min - 2, ld_n.cg_max + 2)

    # ld_e = LoadDiagram(oew_n, oew_arm_n)
    # ld_e.load_pilot()
    # ld_e.load_cargo()
    # ld_e.load_fuel()
    # ld_e.plot()

    plt.show()
