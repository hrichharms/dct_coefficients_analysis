from matplotlib import pyplot, pylab
from numpy.core.numeric import outer
from seaborn import heatmap, dark_palette

from json import load
from sys import argv


if __name__ == "__main__":

    data = load(open(argv[1]))

    color_names = ["Blue", "Green", "Red"]

    # variation histograms for each channel
    for color_index, color_name in enumerate(color_names):
        hist = data["variation_hists"][color_index]
        plot_color = [0, 0, 0]; plot_color[color_index] = 1; plot_color.reverse()
        fig1 = pyplot.figure(f"{argv[1]} Variation Histogram ({color_name})", facecolor="0.15")
        ax = fig1.add_subplot(111, facecolor="0.175")
        ax.tick_params(labelcolor="#AAAAAA")
        ax.set_xlabel("Variation", color="#AAAAAA")
        ax.set_ylabel("Frequency", color="#AAAAAA")
        ax.bar(range(100), hist[:100], color=plot_color)
        ax.annotate(f"{sum(hist[:100]) / sum(hist) * 100:.2f}%", (0.88, 0.95), xycoords="axes fraction", color="#AAAAAA")

    # heatmap figures for each color channel
    cmaps = ["mako", "crest_r", "rocket"]
    lower, upper = data["lowest_val"], data["highest_val"]
    outer_bound = abs(lower) if abs(lower) > abs(upper) else abs(upper) 
    for color_index, color_name in enumerate(color_names):
        fig1 = pyplot.figure(f"{argv[1]} Heatmap ({color_name})", facecolor="0.175")
        ax_heatmap = fig1.add_subplot()
        ax_heatmap.tick_params(labelcolor="#AAAAAA")
        heatmap(data["function_of_dct_2_hists"][color_index][1024 - outer_bound: 1024 + outer_bound][::-1], vmax=5000, ax=ax_heatmap, cmap=cmaps[color_index])
        ax_heatmap.set_xticks(range(0, 2049, 128))
        ax_heatmap.set_xticklabels(range(0, 2049, 128))
        ax_heatmap.set_yticks([0] + list(range(outer_bound % 32 + 32, outer_bound * 2 - 1 - outer_bound % 32, 32)) + [outer_bound * 2 - 1])
        ax_heatmap.set_yticklabels([outer_bound] + list(range(outer_bound - outer_bound % 32 - 32, -outer_bound + 32, -32)) + [-outer_bound])

    pylab.show()
