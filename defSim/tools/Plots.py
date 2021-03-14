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
import itertools

class dsPlot():
    """
    This class is responsible for generating plots.
    Inherit from this class and implement at least the plot method for each type of plot.
    """

    def __init__(self):
        pass

    def plot(self):
        raise NotImplementedError

    def show(self):
        # required when not in interactive session
        plt.show()


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
        :param layout=networkx.spring_layout: Function to use to generate the network layout. Can also be set to
            'grid' to plot grid networks accurately, as there is no standard networkx layout for this.
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
            if isinstance(layout, str) and layout.lower() == 'grid':
                # we infer the positions of the nodes from their index
                pos = dict()
                for i in network.nodes():
                    pos[i] = [int(i / 10), i % 10]
            else:
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
    :param colors: List of colors, used to color the lines. If None,
    colors are set based on the palette. Usually, the number of hues should equal the number of agents
    (showing the opinions for each agent at each step). However, it is possible to specify another variable
    (see 'hue' in DynamicsPlot.plot()) on which to color. Then, the list of colors should be equal in length
    to the number of unique values of that variable.
    :param palette: Seaborn palette or matplotlib colormap to use.
    :param float linewidth=3: Width of lines drawn.
    :param ylim: Iterable with 2 values, which gives (ymin, ymax)
    :param xlim: Iterable with 2 values, which gives (xmin, xmax)
    :param bool fast=False: If True, show plain (but fast) plot. If False, show plot with customizable markup (slow).
    """
    def __init__(self, colors=None, palette="deep", linewidth=3, ylim=None, xlim=None, fast: bool = False):
        super().__init__()
        self.colors = colors
        self.palette = palette
        self.linewidth = linewidth
        self.ylim = ylim
        self.xlim = xlim
        self.fast = fast

    def plot(self, data, y: str, hue=None, xlab: str = None, ylab: str = None, ylim=None, xlim=None):
        """
        Creates a plot showing one line for each agent, indicating their value on a chosen feature at a
        specific step.
        :param values: Pandas dataframe containing all variables to use in the plot.
        :param str y: The feature to plot, by name of the column in dataframe.
        If the pandas DataFrame in which results of the simulation are stored is named 'results', and the tickwise
        feature is named 'f01', the column name is 'Tickwise_f01'
        :param hue: Variable on which to group by color. To show all agents separately, leave this set to None.
        One line wil be drawn for each group.
        To color agents based on a variable but show lines for all agents individually, use a list of colors
        in DynamicsPlot.colors instead (equal in length to nr of agents).
        :param str xlab: Label for x-axis
        :param str ylab: Label for y-axis
        :param ylim: Iterable with 2 values, which gives (ymin, ymax). Overrides self.ylim if present
        :param xlim: Iterable with 2 values, which gives (xmin, xmax). Overrides self.xlim if present
        """

        if ylim is None:
            ylim = self.ylim
        if xlim is None:
            xlim = self.xlim

        if self.fast:
            plt.plot(data[y][0])
        else:
            listvals = data[y][0]
            n_steps = len(listvals)
            n_agents = len(listvals[0])

            # set format: the first n_agents values are step 1, then the next n_agents values are step 2, etc...
            values = list(itertools.chain(*listvals))
            agents = [i + 1 for i in range(n_agents)] * n_steps
            steps = np.repeat([i + 1 for i in range(n_steps)], repeats=n_agents)
            records = list(zip(steps, agents, values))
            df = pd.DataFrame.from_records(records, columns=['step', 'agent', 'value'])

            if hue is None:
                hue = 'agent'
            else:
                hue = list(hue) * n_steps

            df['hue'] = df['agent'] if hue == 'agent' else hue

            if self.colors is not None:
                palette = sns.color_palette(self.colors)
            else:
                n_unique_hues = len(set(df['hue']))
                palette = sns.color_palette(self.palette, n_colors=n_unique_hues)

            ax = sns.relplot(data=df, x='step', y='value',
                             hue='hue', palette=palette, kind='line',
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
    :param ylim: Iterable with 2 values, which gives (ymin, ymax)
    :param xlim: Iterable with 2 values, which gives (xmin, xmax)
    :param float linewidth=3: Width of lines drawn.
    :param kind: Determines type of plot. Select from 'line' or 'scatter'.
    """
    def __init__(self, colors=None, palette="rocket", palette_as_cmap: bool = False, ylim=None, xlim=None, linewidth=3, kind='line'):
        super().__init__()
        self.colors=colors
        self.palette = palette
        self.palette_as_cmap = palette_as_cmap
        self.ylim = ylim
        self.xlim = xlim
        self.linewidth = linewidth
        self.kind = kind

    def plot(self, data, x: str, y: str, hue: str = None, xlab: str = None, ylab: str = None):
        """
        Creates a plot showing the relationship between X and Y, separately for all values of hue. Hue is used to
        create multiple lines with distinct colors.
        :param data: Pandas dataframe containing all variables to use in the plot.
        :param str x: Name of the X-variable
        :param str y: Name of the Y-variable
        :param str hue: Name of the variable on which to split into lines with different colors (optional)
        :param str xlab: Label for X-axis. If None, name of the X-variable is used
        :param str ylab: Label for Y-axis. If None, name of the Y-variable is used
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

        ax.set(ylim=self.ylim, xlim=self.xlim, xlabel=xlab, ylabel=ylab)


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
    def __init__(self, colors=None, palette="rocket", palette_as_cmap=False, ylim=None, xlim=None, linewidth=3):
        super().__init__(colors=colors, palette=palette, palette_as_cmap=palette_as_cmap, ylim=ylim, xlim=xlim, linewidth=linewidth, kind='line')


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
    def __init__(self, colors=None, palette="rocket", palette_as_cmap=False, ylim=None, xlim=None, linewidth=3):
        super().__init__(colors=colors, palette=palette, palette_as_cmap=palette_as_cmap, ylim=ylim, xlim=xlim, linewidth=linewidth, kind='scatter')


class HeatMap(dsPlot):
    """
    Facilitates creation of a heatmap. X and Y are variables which determine the coordinates on the heatmap, while
    hue determines the 'heat' value.
    :param colors: List of colors to use (if 'hue' is set on calling plot()).If None,
    colors are set based on the palette.
    :param palette: Seaborn palette or matplotlib colormap to use.
    :param float vmin: Minimum value for hue.
    :param float vmax: Maximum value for hue.
    :param annot: True, False or dataset. If true, writes data value in each cell.  If array with same shape as data
    then this is used to annotate the heatmap.
    :param str fmt: String formatting code to use when adding annotations.
    :param annot_kws: Dictionary of keyword arguments for drawing annotation text
    :param float linewidths=3: Width of lines drawn.
    :param linecolor: Color to use for lines between cells.
    :param bool square: If True, axes are adjusted so that each cell is square.
    :param bool cbar: Whether to draw a color bar.
    :param cbar_kws: Dictionary of keyword arguments to draw colorbar.
    """
    def __init__(self,
                 colors=None,
                 palette="rocket",
                 vmin=None, vmax=None,
                 annot=False,
                 fmt=None,
                 annot_kws=None,
                 linewidths=None,
                 linecolor=None,
                 square=False,
                 cbar=True,
                 cbar_kws=None):

        self.colors = colors
        self.palette = palette
        self.vmin = vmin
        self.vmax = vmax
        self.annot = annot
        self.fmt = fmt
        self.annot_kws = annot_kws
        self.linewidths = linewidths
        self.linecolor = linecolor
        self.square = square
        self.cbar = cbar
        self.cbar_kws = cbar_kws


    def plot(self, data, x, y, hue,
             sort_y_ascending=False,
             summary='mean',
             center=None,
             robust=False,
             xticklabels="auto",
             yticklabels="auto",
             mask=None,
             ax=None,
             cbar_ax=None,
             **kwargs):

        """
        Creates a heatmap showing the relationship between X, Y and some outcome represented by hue.
        :param data: Pandas dataframe containing all variables to use in the plot.
        :param str x: Name of the X-variable
        :param str y: Name of the Y-variable
        :param str hue: Name of the variable on which to color the cells ('heat')
        :param bool sort_y_ascending: Whether to sort Y ascending (True) or descending (False)
        :param str summary: Type of summary to prsent in the heatmap. Default is mean. The hue presented in each cell
        is the result of the summary function applied to all cases with a particular combination of X and Y
        :param float center: Value at which to center the colormap
        :param bool robust: If True and vmin, vmax are None, colormap range is computed with robust quantiles instead
        of extreme values.
        :param xticklabels: Labels for ticks on X-axis
        :param yticklabels: Labels for tick on Y-axis
        :param mask: If set, data is not shown in cells where mask is True.
        :param ax: Matplotlib axes in which to draw the plot (currently-active axes used if not specified)
        :param cbar_ax: Matplotlib axes in which to draw the colorbar (takes space from main axes if not specified)
        """

        if self.colors is None:
            cmap = sns.color_palette(self.palette, as_cmap=True)
        else:
            cmap = self.colors

        data = getattr(data.groupby([x, y]), summary)().reset_index()
        data = data.pivot(y, x, hue).sort_values(y, ascending=sort_y_ascending)
        sns.heatmap(data,
                    vmin=self.vmin, vmax=self.vmax,
                    cmap=cmap,
                    center=center,
                    robust=robust,
                    annot=self.annot, fmt=self.fmt, annot_kws=self.annot_kws,
                    linewidths=self.linewidths, linecolor=self.linecolor,
                    cbar=self.cbar, cbar_kws=self.cbar_kws, cbar_ax=cbar_ax,
                    square=self.square,
                    xticklabels=xticklabels, yticklabels=yticklabels,
                    mask=mask,
                    ax=ax,
                    **kwargs)
