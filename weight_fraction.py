from pie_setting import *
from ac_parameters import *


def pie_plot(oe, fuel, payload):
    weights = np.array([oe, fuel, payload])
    weight_type = ["OEW", "Max fuel Weight", "Max payload Weight"]
    labels = [f'{w} kg \n{round(w/mtow * 100, 2)}% MTOW' for w in weights]

    plt.pie(weights, autopct=percentage, colors=color(weights), labels=labels, startangle=90, wedgeprops=pie_wedges)
    plt.legend(labels=weight_type, title=f'Weight types: \n(MTOW = {mtow} kg)', loc='upper left')
    plt.tight_layout()
    plt.savefig('plots/part1_weight_pie.png', dpi=300)
    plt.show()


pie_plot(oew, fw, plw)
