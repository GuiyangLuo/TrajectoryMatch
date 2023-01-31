# -*- encoding: utf-8 -*-
'''
@File        :   map_util.py
@Modify Time :   2023/1/30 10:37
@Author      :   wyt
@Version     :   1.0
@Desciption  :   download map
'''

import os
import pickle

import osmnx as ox
import networkx


def _save_graph_shapefile_directional(G, filepath, edges_name, nodes_name, encoding="utf-8"):
    """
    save nodes and edges shape file. These files will be used to match trajectory.
    :param G:
    :param filepath:
    :param edges_name:
    :param nodes_name:
    :param encoding:
    :return:
    """
    # default filepath if none was provided
    filepath_nodes = os.path.join(filepath, nodes_name)
    filepath_edges = os.path.join(filepath, edges_name)

    # convert undirected graph to gdfs and stringify non-numeric columns
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
    gdf_nodes = ox.io._stringify_nonnumeric_cols(gdf_nodes)
    gdf_edges = ox.io._stringify_nonnumeric_cols(gdf_edges)
    gdf_edges["fid"] = gdf_edges['osmid']
    # save the nodes and edges as separate ESRI shapefiles
    gdf_nodes.to_file(filepath_nodes, encoding=encoding)
    gdf_edges.to_file(filepath_edges, encoding=encoding)


def _save_graph_osm(G, filepath, graph_name, dropEdge):
    """
    save map by pickle.
    :param G:
    :param filepath:
    :param graph_name:
    :param dropEdge: is True, remove the low level edge.
    :return:
    """
    filepath = os.path.join(filepath, graph_name)
    if dropEdge:
        uvk2remove = []
        for u, v, keys in G.edges(keys=True):
            highway = G.edges[u, v, keys]['highway']
            if highway != 'motorway' and highway != 'trunk' and highway != 'primary' and highway != 'secondary' and highway != 'tertiary':
                uvk2remove.append((u, v, keys))
        G.remove_edges_from(uvk2remove)
    f = open(filepath, 'wb')
    pickle.dump(G, f)
    f.close()


def download_map(polygon, file_directory: str, edges_name: str, nodes_name: str, origin_graph_name: str,
                 graph_name: str,
                 simplify=True, custom_filter='["highway"~"motorway|trunk|primary|secondary|tertiary"]',
                 way_type='drive',
                 consolidate=True, tolerance=48, dropEdge=True):
    """
    Download a map from OSM and SHP within the boundaries of some shapely polygon. This method provides some parameters
    for custom maps. However, due to too many parameters, you can see `osmnx.graph_from_polygon`, `osmnx.simplify_graph`
    and `osmnx.consolidate_intersections` to customize your own map.
    :param polygon: the boundaries of map. You can see `osmnx.graph_from_polygon` for detail.
    :param file_directory: the map files will be saved in file_directory.
    :param edges_name: edge shape file name.
    :param nodes_name: node shape file name.
    :param origin_graph_name: origin map osm file name. Origin map is the map before simplify and consolidate.
    :param graph_name: map osm file name.
    :param simplify: if True, simplify graph topology with the `osmnx.simplify_graph` function
    :param custom_filter: see `osmnx.graph_from_polygon` for detail. If custom_filter is not None, way_type will not
    take effect.
    :param way_type: see `osmnx.graph_from_polygon` for detail. It is only taking effect when custom_filter is None.
    :param consolidate: if True, call the `osmnx.consolidate_intersections` method.
    :param dropEdge: if True, remove the edge which type is not in set {motorway, trunk, primary, secondary, tertiary}.
    :param tolerance: see `osmnx.consolidate_intersections` for detail.
    """
    if custom_filter is None and way_type is None:
        raise Exception('custom_filter and way_type cannot both be None.')
    if custom_filter is None:
        G = ox.graph_from_polygon(polygon=polygon, retain_all=True, network_type=way_type,
                                  simplify=False, truncate_by_edge=True, clean_periphery=True)
    else:
        G = ox.graph_from_polygon(polygon=polygon, retain_all=True,
                                  custom_filter=custom_filter,
                                  simplify=False, truncate_by_edge=True, clean_periphery=True)
    _save_graph_osm(G, file_directory, origin_graph_name, False)
    print(
        f'before simplify, the number of nodes is {G.number_of_nodes()}, the number of edges is {G.number_of_edges()}.')
    if simplify:
        G = ox.simplify_graph(G, strict=True, remove_rings=True)
        print(
            f'after simplify, the number of nodes is {G.number_of_nodes()}, the number of edges is {G.number_of_edges()}.')
    print("map download complete.")
    if consolidate:
        crs = G.graph["crs"]
        G = ox.project_graph(G)  # 116.382245,39.912269
        G = ox.consolidate_intersections(G, tolerance=tolerance, rebuild_graph=True, dead_ends=False,
                                         reconnect_edges=True)
        print("graph consolidate complete.")
        G = ox.project_graph(G, crs)

    # convert G to osm format, The all_oneway must be set to True
    # ox.utils.config(all_oneway=True)
    # ox.save_graph_xml(G, filepath='graph_drive.osm')
    # print('save the simplified graph!')
    idx = 0
    for u, v, keys in G.edges(keys=True):
        G.edges[u, v, keys]['osmid'] = idx
        idx += 1
    print("convert OSMID complete.")
    _save_graph_shapefile_directional(G, filepath=file_directory, edges_name=edges_name, nodes_name=nodes_name)
    print("save shape file complete.")
    _save_graph_osm(G, filepath=file_directory, graph_name=graph_name, dropEdge=dropEdge)
    print("save networkx.MultiDiGraph complete.")


def load_map(file_directory: str, map_name: str) -> networkx.MultiDiGraph:
    """
    load a map by `pickle`.
    :param file_directory: the file_directory which map files are saved.
    :param map_name: map file name.
    :return: map
    """
    map_path = os.path.join(file_directory, map_name)
    with open(map_path, 'rb') as f:
        return pickle.load(f)
