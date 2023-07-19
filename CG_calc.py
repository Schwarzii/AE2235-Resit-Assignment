from ac_parameters import *


def lemac(arm):
    return (arm - lemac_arm) / mac * 100


def to_datum(arm):
    return arm / 100 * mac + lemac_arm


class Aircraft:
    def __init__(self):
        self.components = {'wing': 14.77,
                           'h tail': 1.37,
                           'v tail': 0.95,
                           'fuselage': 19.29,
                           'nose lg': 0.47,
                           'main lg': 2.71,
                           'nacelle': 1.83,
                           'propulsion': 9.12}
        self.groups = {'wing group': ['wing', 'main lg'],
                       'fuselage group': ['h tail', 'v tail', 'fuselage', 'nose lg', 'nacelle', 'propulsion']}

        self.cg_abs_pos = {}
        self.cg_pos()

        self.cg_group = {g: 0 for g in self.groups.keys()}
        self.calc_cg_group()

        self.cg_oew = 0
        self.calc_cg_oew()

    @staticmethod
    def trans_top(x):
        return x * 35.528 / 21.168  # m

    @staticmethod
    def trans_side(x):
        return x * l_f / 20.029  # m

    def cg_pos(self):
        # m
        self.cg_abs_pos = {'wing': [self.trans_top(10.663)],
                           'h tail': [self.trans_top(19.879)],
                           'v tail': [self.trans_side(19.2054372)],
                           'fuselage': [0.46 * l_f],
                           'nose lg': [self.trans_side(2.272232562)],
                           'main lg': [self.trans_side(2.272232562) + 14.006],
                           'nacelle': [self.trans_side(15.0534649971)],
                           'propulsion': [self.trans_side(15.0534649971)]}
        for c, a in self.cg_abs_pos.items():
            self.cg_abs_pos[c].append(lemac(a[0]))

    @staticmethod
    def avg_cg(com_cg, com_weight):
        return np.sum(com_cg.T * com_weight) / np.sum(com_weight)

    def calc_cg_oew(self):
        cg_arm = np.vstack(list(self.cg_abs_pos.values()))
        self.cg_oew = self.avg_cg(cg_arm[:, 1], np.array(list(self.components.values())))

    def calc_cg_group(self):
        for g, c in self.groups.items():
            cg_arm = np.vstack([self.cg_abs_pos[p][1] for p in c])
            self.cg_group[g] = self.avg_cg(cg_arm, np.array([self.components[j] for j in c]))

    def modification(self):
        modification = self.components.copy()
        modification['wing'] *= 1.1
        return modification

    def mod_oew(self):
        misc_w = oew - np.sum(list(self.components.values())) / 100 * mtow
        mod_component = self.modification()
        mod_w = np.sum(list(mod_component.values())) / 100 * mtow + misc_w
        return misc_w, mod_w, mod_w - oew


if __name__ == '__main__':
    ac = Aircraft()
    # print(ac.cg_abs_pos)
    print(ac.cg_group)
    print(ac.cg_oew)
    print(ac.modification())
    print(ac.mod_oew())
