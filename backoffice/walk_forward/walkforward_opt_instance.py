import vectorbt as vbt
import numpy as np
import pandas as pd

class WalkForwardOpt:

    def __init__(self, data: pd.DataFrame, n: int, window_len: int, set_lens: int):
        """
        n (int): Total length of the time series.
        window_len (int): Length of each rolling window.
        set_lens (int): Length of the in-sample and out-of-sample sets.
        """
        self.data = data
        self.n = n
        self.window_len = window_len
        self.set_lens = set_lens

    def get_optimal(self, x):
        """
        Get the optimal values based on a DataFrame.

        Parameters:
        x (pd.DataFrame): A DataFrame.

        Returns:
        None
        """
        df = x[x.groupby('split_idx').idxmax()].index
        return print(df)
        
    def rolling_split(self, left_to_right=False):
        """
        Split a time series into rolling in-sample and out-of-sample sets.

        Parameters:
        left_to_right (bool, optional): If True, the rolling split is from left to right, otherwise right to left.

        Returns:
        tuple: A tuple containing two tuples: (in-sample prices, in-sample dates), and (out-of-sample prices, out-of-sample dates).
        """

        (in_sample_prices, in_sample_dates), (out_sample_prices, out_sample_dates) = self.data.vbt.rolling_split(
            n=self.n,
            window_len=self.window_len,
            set_lens=(self.set_lens, ),
            left_to_right=left_to_right
            )

        return (in_sample_prices, in_sample_dates), (out_sample_prices, out_sample_dates)

    def rolling_split_plot(self, left_to_right=False, plot=True, trace_names=['in_sample', 'out_sample']):
        """
        Generate a plot of rolling in-sample and out-of-sample sets.

        Parameters:
        left_to_right (bool, optional): If True, the rolling split is from left to right, otherwise right to left.
        plot (bool, optional): If True, display the plot. If False, return the plot data.
        trace_names (list of str, optional): Names for the plot traces.

        Returns:
        plotly.graph_objs._figure.Figure: A Plotly figure if plot=True, otherwise None.
        """

        graph = self.data.vbt.rolling_split(
            n=self.n,
            window_len=self.window_len,
            set_lens=(self.set_lens, ),
            left_to_right=left_to_right,
            plot=plot,
            trace_names=trace_names
            )
        
        return graph

    def in_sample_prices(self, left_to_right=False):
        """
        Get the in-sample prices from a rolling split.

        Parameters:
        left_to_right (bool, optional): If True, the rolling split is from left to right, otherwise right to left.

        Returns:
        pd.Series: In-sample prices.
        """

        (in_sample_prices, in_sample_dates), (out_sample_prices, out_sample_dates) = self.data.vbt.rolling_split(
            n=self.n,
            window_len=self.window_len,
            set_lens=(self.set_lens, ),
            left_to_right=left_to_right
            )

        return in_sample_prices



