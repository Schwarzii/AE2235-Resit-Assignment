from pie_setting import *
from ac_parameters import *
from CG_calc import Aircraft


def pie_plot(oe, fuel, payload, title='', percent_label=True):
    weights = np.round(np.array([oe, fuel, payload]), 1)
    weight_type = ["OEW", "Max fuel Weight", "Max payload Weight"]
    if percent_label:
        labels = [f'{w} kg \n{round(w/mtow * 100, 2)}% MTOW' for w in weights]
    else:
        labels = [f'{w} kg' for w in weights]

    plt.pie(weights, autopct=percentage, colors=color(weights), labels=labels, startangle=90, wedgeprops=pie_wedges)
    plt.legend(labels=weight_type, title=f'Weight types: \n(MTOW = {mtow} kg)', loc='upper left')
    plt.tight_layout()

    plt.savefig(f'plots/{title}.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    fokker = Aircraft()
    fokker_mod = Aircraft(mod=True)
    fig = plt.figure(figsize=(6, 4))
    # pie_plot(fokker.oew, fw, plw, title='part1_weight_pie')
    fuel_load = mtow - fokker.oew - plw
    pie_plot(fokker_mod.oew, fuel_load, plw - fokker_mod.mod[2], title='part2_weight_pie', percent_label=False)
