from ac_parameters import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from loading_diagram import LoadDiagram
from CG_calc import Aircraft


class Stability:
    def __init__(self, eta=0.95, margin=5):
        self.wing_ac = 0.25  # Assumed aerodynamic center of wing

        self.eta = eta  # Wing's efficiency, assumed constant
        self.beta = np.sqrt(1 - mach ** 2)
        self.v_ratio = 1  # Speed ratio between wing and tail, assumed to 1 due to T-tail

        self.r = l_h / (b / 2)
        self.m_tv = trans_side(3.670914406) / (b / 2)

        self.beta_a = self.beta * ar
        self.lambda_beta = np.degrees(np.arctan(np.tan(sweep_quarter) / self.beta))

        self.margin = margin

    def stab_line(self, cg):
        cl_ratio = self.cl_alpha_h() / self.cl_alpha_ah()
        tail_arm = l_h / mac
        # cl_ratio = (4.17 / 3.8)
        # self.aero_center = 14.18
        # return (cg - (14.18 - self.margin)) / (cl_ratio * (1 - self.downwash()) * 13.56 / 2.303 * self.v_ratio ** 2)
        return (cg - (self.aero_center() - self.margin)) / (cl_ratio * (1 - 0) * tail_arm * self.v_ratio ** 2) / 100

    def cl_alpha_ah(self):
        return self.cl_alpha_w() * (1 + 2.15 * b_f / b) * s_net / s + np.pi / 2 * b_f ** 2 / s

    def cl_alpha_w(self):
        return 2 * np.pi * ar / (2 + np.sqrt(4 + (ar * self.beta / self.eta) ** 2 *
                                             (1 + np.tan(sweep_half) ** 2 / (self.beta ** 2))))

    def cl_alpha_h(self):
        return 2 * np.pi * ar_h / (2 + np.sqrt(4 + (ar_h * self.beta / self.eta) ** 2 *
                                               (1 + np.tan(sweep_h) ** 2 / (self.beta ** 2))))

    def aero_center(self):
        self.wing_ac = 28.5  # %MAC See slide
        fus_ac_1 = -1.8 / self.cl_alpha_ah() * b_f * h_f * l_fn / (s * mac)
        fus_ac_2 = 0.273 / (1 + taper) * b_f * s / b * (b - b_f) / (mac ** 2 * (b + 2.15 * b_f)) * np.tan(sweep_quarter)
        nacelle_ac = -2.5 * b_n ** 2 * l_n / (s * mac * self.cl_alpha_ah()) * 2
        return self.wing_ac + fus_ac_1 + fus_ac_2 + nacelle_ac

    def downwash(self):
        rsq = self.r ** 2
        msq = self.m_tv ** 2
        k_ep_lambda = (0.1124 + 0.1265 * sweep_quarter + 0.1766 * sweep_quarter ** 2) / rsq + 0.1024 / self.r + 2
        k_ep_lambda0 = 0.1124 / rsq + 0.1024 / self.r + 2
        return k_ep_lambda / k_ep_lambda0 * self.cl_alpha_w() / (np.pi * ar) * (
                self.r / (rsq + msq) * 0.4876 / np.sqrt(rsq + 0.6319 + msq) +
                (1 + (rsq / (rsq + 0.7915 + 5.0734 * msq)) ** 0.3113) * (1 - np.sqrt(msq / (1 + msq))))


class Controllability(Stability):
    def __init__(self, eta=0.95, margin=5):
        super().__init__(eta, margin)
        self.cl_h = -0.35 * ar_h ** (1 / 3)  # Fixed tail
        self.cm_airfoil = -0.025  # NACA 1408, AOA = 0
        self.cl_0 = 0.372  # Zero AOA lift
        # v_app = 61.67
        self.beta = np.sqrt(1 - (v_app / a_0) ** 2)

    def control_line(self, cg):
        cl_ah = self.cl() - self.cl_h
        cl_ratio = self.cl_h / cl_ah
        tail_arm = l_h / mac
        # return (cg - 0.065 / 2.34 - 14.18) / (-0.8 / 2.34 * 13.56 / 2.303 * self.v_ratio ** 2)
        return (cg + self.cm_ac() / cl_ah - self.aero_center()) / (cl_ratio * tail_arm * self.v_ratio ** 2) / 100

    @staticmethod
    def cl():
        return mlw_n / (0.5 * rho_0 * v_app ** 2 * s)

    def cm_ac(self):
        cm_w = self.cm_airfoil * ar * np.cos(sweep_quarter) ** 2 / (ar + 2 * np.cos(sweep_quarter))
        cm_fus = -1.8 * (1 - 2.5 * b_f / l_f) * np.pi * b_f * h_f * l_f / (4 * s * mac) * self.cl_0 / self.cl_alpha_ah()
        cm_flap = -0.35  # See slide
        return cm_w + cm_fus + cm_flap


class ScissorPlot:
    def __init__(self, mod=False, cmap_top='Set2', cmap_bottom='Pastel2'):
        self.cg = np.array([-10, 120])
        self.stab_neutral = Stability(margin=0)
        self.stab = Stability()
        self.control = Controllability()

        self.lines = {'Stability': self.stab.stab_line(self.cg),
                      'Neutral stability': self.stab_neutral.stab_line(self.cg),
                      'Controllability': self.control.control_line(self.cg)}

        self.cmap = [cmap_top, cmap_bottom]  # Set2 if not overlay, else Pastel2
        self.cg_range = None
        self.mod = mod

    def ac_cg_range(self, ac_oew, oew_cg):
        ld = LoadDiagram(ac_oew, oew_cg)
        if self.mod:
            ld.load_modified()
        else:
            ld.load_standard(True, True)
        self.cg_range = ld.cg_range
        print(self.cg_range)

    def plot(self, title='', overlay=False, save=None):
        x_lim = [0, 100]
        plt.xlim(x_lim)
        plt.ylim([0, 0.4])

        color_map = plt.get_cmap(self.cmap[overlay])
        colors = color_map(np.arange(len(self.lines)))
        alpha = 0.4 if overlay else 1

        # # MTOW line
        # plt.axhline(y=mtow, linestyle='dashed', color='tomato')
        # plt.text(x_lim[1] + 1, mtow - 150, 'MTOW')
        #
        # # MZFW line
        # plt.axhline(y=self.load_mass['Fuel (wing)'][0][0], linestyle='dashed', color='lightsalmon', alpha=0.7)
        # plt.text(x_lim[1] + 1, self.load_mass['Fuel (wing)'][0][0] - 150, 'MZFW')
        ax = plt.subplot(111)
        for (n, line), c in zip(self.lines.items(), colors):
            ax.plot(self.cg, line, color=c, label=n, alpha=alpha)

        # Reference S_h/S ratio
        plt.axhline(y=s_h / s, color='gray', linestyle='dashed', alpha=0.6)
        plt.text(x_lim[1] + 1, s_h / s * 0.98, r'$\frac{S_h}{S}_{Ref}$')

        if self.cg_range is not None:
            min_cg, max_cg = self.cg_range
            s_control = self.control.control_line(min_cg)
            s_stab = self.stab.stab_line(max_cg)
            s_ratio = max(s_control, s_stab)
            if self.mod:
                label = 'CG range (modified)'
            else:
                label = 'CG range (reference)'
            ax.plot(self.cg_range, [s_ratio] * 2, '-xk', label=label)

        plt.legend()

        # Minor tickers and grid
        ax.xaxis.set_minor_locator(MultipleLocator(2.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.01))
        plt.grid()

        # Axis label and title
        plt.xlabel(r'$x_{CG}$ [% MAC]')
        plt.ylabel(r'$S_h/S$')
        plt.title(title)
        plt.tight_layout()

        if save:
            plt.savefig(f'plots/{save}.png', dpi=300)


if __name__ == '__main__':
    fig = plt.figure(figsize=(6, 4))

    fokker = Aircraft()

    sp = ScissorPlot()
    sp.ac_cg_range(fokker.oew, fokker.cg_oew)
    # sp.plot('Scissor plot of Fokker 100')
    sp.plot('Scissor plot of Fokker 100', save='scissor_plot_I')

    plt.show()
