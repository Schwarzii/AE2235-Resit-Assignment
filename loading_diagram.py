import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from matplotlib.ticker import MultipleLocator
from ac_parameters import *


def lemac(arm):
    return (arm - lemac_arm) / mac * 100


def to_datum(arm):
    return arm / 100 * mac + lemac_arm


class LoadDiagram:
    def __init__(self, init_mass, init_cg, cmap='Set2', margin=2):
        self.acc_mass = init_mass
        self.acc_moment = init_mass * init_cg

        self.load_mass = {'OEW': [np.array([init_mass])]}
        self.load_cg = {'OEW': [np.array([init_cg])]}

        # Dummy variables
        self.cg_min = 100
        self.cg_max = 0

        self.cmap = cmap
        self.margin = margin

    def calculate(self, payload, mass, arm, arm_conversion=True, loaded=False):
        acc_mass = self.acc_mass + np.hstack([0, np.cumsum(mass)])

        if arm_conversion:
            arm = lemac(arm)
        moment = mass * arm
        acc_moment = self.acc_moment + np.hstack([0, np.cumsum(moment)])
        cg = acc_moment / acc_mass

        self.cg_min = min(np.min(cg), self.cg_min)
        self.cg_max = max(np.max(cg), self.cg_max)

        if loaded:
            self.acc_mass = acc_mass[-1]
            self.acc_moment = acc_moment[-1]

        if payload in self.load_mass:
            self.load_mass[payload].append(acc_mass)
            self.load_cg[payload].append(cg)
        else:
            self.load_mass[payload] = [acc_mass]
            self.load_cg[payload] = [cg]

    def load_cargo(self, payload='Cargo'):
        # fwd -> aft
        mass_fwd = cargo_mass
        mass_aft = np.flip(mass_fwd)
        arm_fwd = cargo_arm
        arm_aft = np.flip(arm_fwd)

        self.calculate(payload, mass_fwd, arm_fwd)
        self.calculate(payload, mass_aft, arm_aft, loaded=True)

    def load_pilot(self, payload='Pilot'):
        mass = np.ones(2) * pilot_mass
        arm = np.ones(2) * pilot_arm
        self.calculate(payload, mass, arm, loaded=True)

    def load_pax_w(self, pos, payload='Seats', n_row=18, w_pax=76.3):
        n_seat = 2
        payload = f'{payload} ({pos})'

        # fwd -> aft
        arm = np.arange(n_row) * pitch + first_arm
        mass = np.ones(n_row) * n_seat * w_pax  # No order
        self.calculate(payload, mass, arm)
        self.calculate(payload, mass, arm[::-1], loaded=True)

    def load_fuel(self, payload='Fuel', fuel_limit=fw, load_limit=mtow):
        fuel_arm = interp1d(fuel_quantity, fuel_h_arm)

        ava_fuel = min(load_limit - self.acc_mass, fuel_limit)
        arm = fuel_arm(ava_fuel / 2)  # Divide fuel into two tanks
        self.calculate(payload, ava_fuel, arm)

    def load_standard(self):
        self.load_cargo()
        self.load_pilot()
        self.load_pax_w('window')
        self.load_pax_w('aisle')
        self.load_fuel()

    def load_modified(self):
        self.load_cargo()
        self.load_pilot()
        self.load_pax_w('window', n_row=16)
        self.load_pax_w('aisle', n_row=16)
        self.load_fuel()

    def plot(self, title='', overlay=False, save=None):
        if self.cmap == 'gray':
            colors = ['lightgray'] * len(self.load_mass)
            alpha = 0.4
        else:
            color_map = plt.get_cmap(self.cmap)
            colors = color_map(np.arange(len(self.load_mass)))
            alpha = 1

            plt.axhline(y=mtow, linestyle='dashed', color='tomato')
            plt.text(71, 23000 - 150, 'MTOW')
            plt.axhline(y=self.load_mass['Fuel'][0][0], linestyle='dashed', color='lightsalmon', alpha=0.7)
            plt.text(71, self.load_mass['Fuel'][0][0] - 150, 'MZFW')

        order = np.arange(1, len(self.load_mass) + 1)[::-1]

        ax = plt.subplot(111)
        for (l, m), cg, c, o in zip(self.load_mass.items(), self.load_cg.values(), colors, order):
            b = 0
            for lm, lcg in zip(m, cg):
                line_style = '-o' if b == 0 else '-^'
                label = '' if self.cmap == 'gray' else l

                ax.plot(lcg, lm, line_style, color=c, label=label, zorder=o, alpha=alpha)

                b += 1

        if overlay:
            alpha = 0.4
            plt.plot(-1, 1, '-o', color='lightgray', label='Original design', alpha=alpha)
            plt.plot(-1, 1, '-^', color='lightgray', label='Original design', alpha=alpha)

        if self.cmap != 'gray':
            plt.xlim([0, 70])
            y_low_lim = oew // 2000 * 2000
            plt.ylim([y_low_lim, mtow // 2000 * 2000])

            plt.plot(np.ones(2) * (self.cg_min - self.margin), [y_low_lim, mtow], '-.k', label='Min/Max CG')
            plt.plot(np.ones(2) * (self.cg_max + self.margin), [y_low_lim, mtow], '-.k')

            # Position legend
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.14,
                             box.width, box.height * 0.95])
            plt.legend(loc='center', bbox_to_anchor=(0.5, -0.2), ncols=4)

            # Position the legend on the right side
            # ax.set_position([box.x0, box.y0,
            #                  box.width * 0.8, box.height * 1.08])
            # plt.legend(loc='lower left', bbox_to_anchor=(1.02, 0))

            ax.xaxis.set_minor_locator(MultipleLocator(2.5))
            ax.yaxis.set_minor_locator(MultipleLocator(500))
            plt.grid()

            plt.xlabel(r'$x_{CG}$ [%MAC]')
            plt.ylabel('Mass [kg]')
            plt.title(title)

        if save:
            plt.savefig(f'plots/{save}.png', dpi=300)


if __name__ == '__main__':
    # oew_o = 13294
    oew_o = 13600
    oew_arm_o = 31.36

    oew_n = mtow * 62.02339 / 100 + 306
    # print(oew_n)
    # oew_arm_n = 44.5  # LEMAC -> 44.5% MAC
    oew_arm_n = lemac(12.26682 + datum)

    fig = plt.figure(figsize=(7, 6))
    # fig = plt.figure(figsize=(8, 6))  # Legend at right

    # Part I loading diagram
    # ld_i = LoadDiagram(oew_o, oew_arm_o, cmap='Set2')
    # ld_i.load_standard()
    # # ld_i.plot('Loading diagram of ATR 72-600')
    # print(ld_i.cg_min, ld_i.cg_max)
    # print(ld_i.cg_min - 2, ld_i.cg_max + 2)
    # # print(to_datum(np.array([ld_i.cg_min, ld_i.cg_max])))
    # # print(to_datum(np.array([ld_i.cg_min - 2, ld_i.cg_max + 2])))
    # ld_i.plot('Loading diagram of ATR 72-600', save='loading_diagram_600')

    # Setting for overlaid plot
    # ld_o = LoadDiagram(oew_o, oew_arm_o, cmap='gray')
    # ld_o.load_standard()
    # ld_o.plot()

    # ld_1 = LoadDiagram(oew_n, oew_arm_n, cmap='gray')
    # ld_1.load_modified()
    # ld_1.plot()
    #
    ld_n = LoadDiagram(oew_n, oew_arm_n, cmap='Set2')
    ld_n.load_modified()
    ld_n.plot('Loading diagram (modified design)', overlay=True)
    print(ld_n.cg_min, ld_n.cg_max)
    print(ld_n.cg_min - 2, ld_n.cg_max + 2)

    # ld_e = LoadDiagram(oew_n, oew_arm_n)
    # ld_e.load_pilot()
    # ld_e.load_cargo()
    # ld_e.load_fuel()
    # ld_e.plot()

    plt.show()
