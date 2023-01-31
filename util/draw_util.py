# -*- encoding: utf-8 -*-
'''
@File        :   draw_util.py    
@Modify Time :   2023/1/30 19:12
@Author      :   wyt
@Version     :   1.0
@Desciption  :   None
'''
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx
import osmnx as ox
from shapely.geometry import Point


def draw_map(G: networkx.MultiDiGraph, edge_color='gray', node_color='red', edge_linewidth=2, node_size=3):
    """
    draw a map. You can add the parameters of `ox.plot_graph` to draw a greater picture.
    :param G: the map. You can use `map_util.download_map` to download it and use `map_util.load_map` to get it.
    :param edge_color: the edge color. You can specify a single color or get a dynamic color from a edge's attribute by
    `osmnx.plot.get_edge_colors_by_attr` method.
    :param node_color: the node color.
    :param edge_linewidth: the edge line width.
    :param node_size: the node size.
    :return: fig, ax
    """
    fig, ax = ox.plot_graph(G, edge_color=edge_color, node_color=node_color, edge_linewidth=edge_linewidth,
                            node_size=node_size, show=False)
    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)
    font2 = {'family': 'SimHei',
             'weight': 'normal',
             'size': 30,
             }
    plt.tick_params(labelsize=24)
    ax.set_xlabel('longitude', font2)
    ax.set_ylabel('latitude', font2)
    font3 = {'family': 'SimHei',
             'weight': 'normal',
             'size': 35,
             }
    plt.title('Beijing', font3)
    plt.show()
    return fig, ax


def _convert_gdf(points) -> gpd.GeoDataFrame:
    """
    convert points list to GeoDataFrame.
    :param points: the points list.
    :return: GeoDataFrame
    """
    taxi_data = tuple(points)
    taxi_nodes = tuple(i for i in range(len(taxi_data)))
    geom = (Point(d["x"], d["y"]) for d in taxi_data)
    gdf_nodes = gpd.GeoDataFrame(taxi_data, index=taxi_nodes, crs='epsg:4326', geometry=list(geom))
    return gdf_nodes


def draw_point(points, ax, color, alpha, markersize):
    """
    draw point on a map picture.
    :param points: points list.
    :param ax: fig ax.
    :param color: points color.
    :param alpha: points alpha.
    :param markersize: points markersize.
    """
    if len(points) == 0 or points is None:
        return
    _convert_gdf(points).plot(ax=ax, color=color, alpha=alpha, markersize=markersize)
    plt.show()
