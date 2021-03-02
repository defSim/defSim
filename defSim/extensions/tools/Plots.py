"""

Requires:
- matplotlib >= 3.3.4
- seaborn >= 0.11.1

"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import numpy as np

class dsPlot():

    def __init__(self):
        pass

    def plot(self):
        raise NotImplementedError

    def show(self):
        plt.show()

# 1: plot network, colored by a feature

class NetworkPlot(dsPlot):
    def __init__(self, node_size=100, cmap=plt.cm.winter):
        super().__init__()
        self.cmap = cmap
        self.node_size = node_size

    def plot(self, network, feature=None, title=None, pos=None, layout=nx.spring_layout):

        nodes = network.nodes()

        if feature is not None:
            vmin = min([network.nodes[n][feature] for n in nodes])
            vmax = max([network.nodes[n][feature] for n in nodes])
        else:
            vmin, vmax = 1,1

        if feature is None:
            colors = [1 for _ in nodes]
        else:
            colors = [network.nodes[n][feature] for n in nodes]

        if pos is None:
            pos = layout(network)

        ec = nx.draw_networkx_edges(network, pos, alpha=0.2)
        if feature is not None:
            nc = nx.draw_networkx_nodes(network, pos, nodelist=nodes, node_color=colors,
                                node_size=self.node_size, cmap=self.cmap,
                                vmin=vmin, vmax=vmax
                                )
        else:
            nc = nx.draw_networkx_nodes(network, pos, nodelist=nodes,
                                        node_size=self.node_size, cmap=self.cmap,
                                        vmin=vmin, vmax=vmax
                                        )

        if title is not None:
            plt.title(title)

        plt.colorbar(nc)
        plt.axis('off')


class DynamicsPlot(dsPlot):
    def __init__(self):
        super().__init__()

    def plot(self, tickwise_feature, title=None, colors=None):
        feature_values = tickwise_feature[0]
        if colors is not None:
            feature_values = np.array(feature_values).transpose()
            for i in range(len(feature_values)):
                plt.plot(feature_values[i], color=colors[i])
        else:
            plt.plot(feature_values)



class RelPlot(dsPlot):
    def __init__(self, colors=None, palette="rocket", palette_as_cmap=False, linewidth=3, kind='line'):
        super().__init__()
        self.colors=colors
        self.palette = palette
        self.palette_as_cmap = palette_as_cmap
        self.linewidth = linewidth
        self.kind = kind

    def plot(self, data, x, y, hue=None, xlab=None, ylab=None, colors=None):
        if self.colors is not None:
            palette = sns.color_palette(colors)
        elif self.palette_as_cmap:
            palette = sns.color_palette(self.palette, as_cmap=True)
        else:
            n_unique_hues = len(set(data[hue])) if hue is not None else 1
            palette = sns.color_palette(self.palette, n_colors=n_unique_hues)

        ax = sns.relplot(x=x, y=y,
                     data=data, hue=hue, palette=palette, kind=self.kind,
                     linewidth=self.linewidth)

        if xlab is None:
            xlab = x
        if ylab is None:
            ylab = y

        ylim = [min(data[y]), max(data[y])]

        ax.set(ylim=ylim, xlabel=xlab, ylabel=ylab)

class LinePlot(RelPlot):
    def __init__(self, palette=sns.color_palette("rocket"), linewidth=3):
        super().__init__(palette=palette, linewidth=linewidth, kind='line')

class ScatterPlot(RelPlot):
    def __init__(self, palette=sns.color_palette("rocket")):
        super().__init__(palette=palette, kind='scatter')

def plot_experiment(results, x, y, xlab=None, ylab=None):
    # plt.figure(figsize=[5, 5])
    # plt.ylim(0,1.01)
    # plt.title('Average opinion distance\nBy when between-group connections are introduced', y=1.04)
    colors = ['red', 'blue']
    ax = sns.relplot(x=x, y=y,
                     data=results, hue="communication_regime", palette=sns.color_palette(colors), kind='line',
                     linewidth=3)
    if xlab is None:
        xlab = x
    if ylab is None:
        ylab = y
    ax.set(ylim=[0, 1],
           xlabel=xlab,
           ylabel=ylab)

    # plt.show()