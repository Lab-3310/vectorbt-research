import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import os

fig_path = f"{os.path.dirname(__file__)}/../data_base/OPTIMIZATION"
os.makedirs(fig_path, exist_ok=True)

def two_parameter_plot(df_data: pd.DataFrame, perf_name: str, par_name1: str, par_name2: str, fig_name: str=None, show: bool=False):
    
    """
    Create and display a set of plots for analyzing two parameters and performance.

    Parameters:
    df_data (pd.DataFrame): The DataFrame containing the data to be analyzed.
    perf_name (str): The name of the performance metric column in df_data.
    par_name1 (str): The name of the first parameter column in df_data.
    par_name2 (str): The name of the second parameter column in df_data.
    """

    # All_Heatmap
    fig = go.Figure(data=go.Heatmap(
            z = df_data[perf_name],
            x = df_data[par_name1],
            y = df_data[par_name2],
            colorscale='Viridis'))
    fig.update_layout(title = f"All_Heatmap_{perf_name}", width=600, height=400)
    #fig.write_image(f"{fig_path}/all_heatmap.png") # TODO:save the figure in right path
    if show:
        fig.show()


    # Range_Heatmap
    fig = px.density_heatmap(
            data_frame = df_data,
            z = perf_name,
            x = par_name1,
            y = par_name2,
            color_continuous_scale = 'Viridis',
            title = f"Range_Heatmap_{perf_name}",
            )
    fig.update_layout(width=600, height=400)
    #fig.write_image(f"{fig_path}/range_heatmap.png") # TODO:save the figure in right path
    if show:
        fig.show()


    # Histgram
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(x = df_data[perf_name], bins=10)
    plt.title(f"Histgram_{perf_name}", fontsize=18)
    plt.xlabel(perf_name, fontsize=12)
    plt.ylabel('Times', fontsize=12)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    #fig.savefig(f"{fig_path}/histgram.png") # TODO:save the figure in right path

    if show:
        plt.show()


    # 3D_Surface
    fig = go.Figure(data=[go.Surface(
        z = df_data[[perf_name, par_name1, par_name2]].set_index([par_name1, par_name2]).unstack().values,         
        colorscale='Viridis',)])
    fig.update_layout(
        title = f"3D_Surface_{perf_name}",
        width=900, 
        height=600)
    #fig.write_image(f"{fig_path}/plot.png") # TODO:save the figure in right path
    
    if show:
        fig.show()



def three_parameter_plot(df_data: pd.DataFrame, perf_name: str, par_name1: str, par_name2: str, par_name3: str, show=False):

    """
    Create and display a 3D scatter plot for analyzing three parameters and performance.

    Parameters:
    df_data (pd.DataFrame): The DataFrame containing the data to be analyzed.
    perf_name (str): The name of the performance metric column in df_data.
    par_name1 (str): The name of the first parameter column in df_data.
    par_name2 (str): The name of the second parameter column in df_data.
    par_name3 (str): The name of the third parameter column in df_data.

    """

    fig = px.scatter_3d(
        data_frame = df_data,
        x = par_name1,
        y = par_name2,
        z = par_name3,
        color = perf_name,
        color_continuous_scale = 'Viridis',
        title = f'{perf_name}',
        )
    fig.update_layout(width=1000, height=600)
    #fig.write_image(f"{fig_path}/plot.png") # TODO:save the figure in right path

    if show:
        fig.show()
