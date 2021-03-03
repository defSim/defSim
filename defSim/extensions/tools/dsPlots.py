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
import pandas as pd

class dsPlot():
    """
    This class is responsible for generating plots.
    Inheirt from this class and implement at least the plot method for each type of plot.
    """

    def __init__(self):
        pass

    def plot(self):
        raise NotImplementedError

    def show(self):
        plt.show()

# 1: plot network, colored by a feature

class NetworkPlot(dsPlot):
    """
    Facilitates creating network plots, using networkx plot functions. These functions
    use matplotlib behind the scenes.

    :param float node_size=100: Sets the size of nodes in the plot.
    :param cmap: Matplotlib color map to apply to the network nodes.
    :param float edge_alpha=0.2: Sets opacity of edges.
    """

    def __init__(self, node_size: float = 100, cmap=plt.cm.winter, edge_alpha: float = 0.2):
        super().__init__()
        self.node_size = node_size
        self.cmap = cmap
        self.edge_alpha = edge_alpha

    def plot(self, network, feature: str = None, colors=None, title=None, pos=None, layout=nx.spring_layout):
        """
        Creates the network plot.
        :param network: Network to draw
        :param str feature: Feature (by name) on which colors should be based. If none is given all nodes are colored
            the same.
        :param colors: List of colors equal in length to the number of nodes, used to color the nodes. If None,
            colors are set based on the colormap.
        :param str title: Title for the plot
        :param pos: (Optional) representation of network position for each node, can be used to keep the network
            layout exactly the same between plots. If pos is not given, network positions are generated using
            layout function.
        :param layout=networkx.spring_layout: Function to use to generate the network layout.
        """

        # Get all nodes in the network
        nodes = network.nodes()

        # If a feature is chosen, colors and associated limits are set based on values of that feature
        # If no feature is chose, all agents get the same color
        if colors is None:
            if feature is not None:
                vmin = min([network.nodes[n][feature] for n in nodes])
                vmax = max([network.nodes[n][feature] for n in nodes])
                colors = [network.nodes[n][feature] for n in nodes]
            else:
                vmin, vmax = 1,1

        # Determine network layout if pos is not set
        if pos is None:
            pos = layout(network)

        # Draw edges
        ec = nx.draw_networkx_edges(network, pos, alpha=self.edge_alpha)

        # Draw nodes
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

        if feature is not None:
            plt.colorbar(nc)
        plt.axis('off')


class DynamicsPlot(dsPlot):
    """
    Facilitates plotting the dynamics of opinion changes for a feature.
    Uses seaborn relplot behind the scenes.
    :param colors: List of colors equal in length to the number of agents, used to color the lines. If None,
            colors are set based on the palette.
    :param palette: Seaborn palette or matplotlib colormap to use.
    :param float linewidth=3: Width of lines drawn.

    """
    def __init__(self, colors=None, palette="deep", linewidth=3):
        super().__init__()
        self.colors = colors
        self.palette = palette
        self.linewidth = linewidth

    def plot(self, tickwise_feature, xlab: str = None, ylab: str = None, ylim=None, xlim=None):
        """
        Creates a plot showing one line for each agent, indicating their value on a chosen feature at a
        specific step.
        :param tickwise_feature: The feature to plot, based on stored tickwise data.
            If the pandas DataFrame in which results of the simulation are stored is named 'results', and the tickwise
            feature is named 'f01', values should be selected as results['Tickwise_f01']
        :param str xlab: Label for x-axis
        :param str ylab: Label for y-axis
        :param ylim: Iterable with 2 values, which gives (ymin, ymax)
        :param xlim: Iterable with 2 values, which gives (xmin, xmax)
        """
        listvals = np.array(tickwise_feature[0]).transpose()
        vals = []
        for i in range(len(listvals)):
            nsteps = len(listvals[i])
            for j in range(nsteps):
                vals.append({'agent': i, 'step': j, 'value': listvals[i][j]})
        df = pd.DataFrame(vals)

        if self.colors is not None:
            palette = sns.color_palette(self.colors)
        else:
            n_unique_hues = len(set(df['agent']))
            palette = sns.color_palette(self.palette, n_colors=n_unique_hues)

        ax = sns.relplot(data=df, x='step', y='value',
                         hue='agent', palette=palette, kind='line',
                         linewidth=self.linewidth, legend=False)

        if xlab is None:
            xlab = 'step'
        if ylab is None:
            ylab = 'value'

        ax.set(ylim=ylim, xlim=xlim, xlabel=xlab, ylabel=ylab)

class RelPlot(dsPlot):
    """
    Facilitates plotting the relationship between two variables, most commonly from an experiment.
    Has two variants (LinePlot and ScatterPlot) which can both be accessed through RelPlot by
    specifying kind. Alternatively, use dsPlots.LinePlot or dsPlots.ScatterPlot.
    :param colors: List of colors to use (if 'hue' is set on calling plot()).If None,
            colors are set based on the palette.
    :param palette: Seaborn palette or matplotlib colormap to use.
    :param bool palette_as_cmap=False: If True, the palette is used as a matplotlib colormap, suitable for continuous
        variables. If False, the palette is used to generate distinct hues, equal in number to the number of unique
        values in the hue parameter when calling plot(). This is suitable for categorical variables.
    :param float linewidth=3: Width of lines drawn.
    :param kind: Determines type of plot. Select from 'line' or 'scatter'.
    """
    def __init__(self, colors=None, palette="rocket", palette_as_cmap: bool = False, linewidth=3, kind='line'):
        super().__init__()
        self.colors=colors
        self.palette = palette
        self.palette_as_cmap = palette_as_cmap
        self.linewidth = linewidth
        self.kind = kind

    def plot(self, data, x: str, y: str, hue: str = None, xlab: str = None, ylab: str = None, ylim=None, xlim=None):
        """
        Creates a plot showing the relationship between X and Y, separately for all values of hue. Hue is used to
        create multiple lines with distinct colors.
        :param data: Pandas dataframe containing all variables to use in the plot.
        :param str x: Name of the X-variable
        :param str y: Name of the Y-variable
        :param str hue: Name of the variable on which to split into lines with different colors (optional)
        :param str xlab: Label for X-axis. If None, name of the X-variable is used
        :param str ylab: Label for Y-axis. If None, name of the Y-variable is used
        :param ylim: Iterable with 2 values, which gives (ymin, ymax)
        :param xlim: Iterable with 2 values, which gives (xmin, xmax)
        """
        if self.colors is not None:
            palette = sns.color_palette(self.colors)
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

        ax.set(ylim=ylim, xlim=xlim, xlabel=xlab, ylabel=ylab)


class LinePlot(RelPlot):
    """
    Shorthand for using RelPlot with kind='line'.
    :param colors: List of colors to use (if 'hue' is set on calling plot()).If None,
            colors are set based on the palette.
    :param palette: Seaborn palette or matplotlib colormap to use.
    :param bool palette_as_cmap=False: If True, the palette is used as a matplotlib colormap, suitable for continuous
        variables. If False, the palette is used to generate distinct hues, equal in number to the number of unique
        values in the hue parameter when calling plot(). This is suitable for categorical variables.
    :param float linewidth=3: Width of lines drawn.
    """
    def __init__(self, colors=None, palette="rocket", palette_as_cmap=False, linewidth=3):
        super().__init__(colors=colors, palette=palette, palette_as_cmap=palette_as_cmap, linewidth=linewidth, kind='line')


class ScatterPlot(RelPlot):
    """
    Shorthand for using RelPlot with kind='scatter'.
    :param colors: List of colors to use (if 'hue' is set on calling plot()).If None,
            colors are set based on the palette.
    :param palette: Seaborn palette or matplotlib colormap to use.
    :param bool palette_as_cmap=False: If True, the palette is used as a matplotlib colormap, suitable for continuous
        variables. If False, the palette is used to generate distinct hues, equal in number to the number of unique
        values in the hue parameter when calling plot(). This is suitable for categorical variables.
    :param float linewidth=3: Width of lines drawn.
    """
    def __init__(self, colors=None, palette="rocket", palette_as_cmap=False, linewidth=3):
        super().__init__(colors=colors, palette=palette, palette_as_cmap=palette_as_cmap, linewidth=linewidth, kind='scatter')