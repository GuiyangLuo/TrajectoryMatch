# -*- encoding: utf-8 -*-
'''
@File        :   demo_beijing.py
@Modify Time :   2023/1/30 18:37
@Author      :   wyt
@Version     :   1.0
@Desciption  :   a demo of Beijing
'''
import data.polygon_data as pd
from util import map_util, draw_util, match_util, data_util

file_directory = './'
edge_name = 'beijing_edge.shp'
node_name = 'beijing_node.shp'
origin_map_name = 'origin_beijing.txt'
map_name = 'beijing.txt'
# download and draw map.
# 1. get polygon
polygon = pd.get_beijing()
# 2. download map
map_util.download_map(polygon, file_directory, edge_name, node_name, origin_map_name, map_name)
# 3. load the map that before simplify as origin_G
origin_G = map_util.load_map(file_directory, origin_map_name)
# 4. draw origin_G.
draw_util.draw_map(origin_G)
# 5. load the map that after simplify as G
G = map_util.load_map(file_directory, map_name)
# 6. draw G
fig, ax = draw_util.draw_map(G)
# import trajectory, preprocess data, match trajectory and draw it.
data_path = 'xxx'
ubodt_name = 'beijing_ubodt.txt'
# 1. import trajectory data and preprocess it.
car_traj = data_util.import_data(data_path, polygon=polygon)
points_group = data_util.preprocess_data(car_traj)
processed_points = []
# 2. prepares tools for match
network = match_util.get_network(file_directory, edge_name)
graph = match_util.get_graph(network)
match_util.gen_ubodt(network, graph, file_directory, ubodt_name)
ubodt = match_util.get_ubodt(file_directory, ubodt_name)
fmm_config = match_util.gen_match_config()
# 3. match points
points_with_opath = []
fix_trajectory = []
for points in points_group:
    try:
        pwo, ft = match_util.match_points(ubodt, graph, network, points_group, fmm_config)
        points_with_opath += pwo
        fix_trajectory += ft
        processed_points += points
    except Exception as e:
        print(e)
        continue
# 4. draw origin trajectory and draw repaired trajectory
# draw_util.draw_point(processed_points, ax, 'red', 1, 10)
draw_util.draw_point(fix_trajectory, ax, 'red', 1, 10)
