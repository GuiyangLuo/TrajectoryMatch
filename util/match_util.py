# -*- encoding: utf-8 -*-
'''
@File        :   match_util.py    
@Modify Time :   2023/1/30 21:07
@Author      :   wyt
@Version     :   1.0
@Desciption  :   match util
'''
import sys

sys.path.append("/data/wyt/packages/fmm-master/build/python/")
from fmm import Network, NetworkGraph, UBODT, FastMapMatchConfig, UBODTGenAlgorithm
from util import data_util
import os


def gen_match_config(k=8, radius=100, gps_error=50):
    """
    generate match config.
    :param k: number of candidates.
    :param radius: search radius.
    :param gps_error: GPS error.
    :return:
    """
    fmm_config = FastMapMatchConfig(k, radius, gps_error)
    return fmm_config


def gen_ubodt(network, graph, file_directory: str, ubodt_name: str):
    """
    generate ubodt(Upper bounded origin destination table) file.
    :param network: fmm Network class.
    :param graph: fmm NetworkGraph class.
    :param file_directory: the map files will be saved in file_directory.
    :param ubodt_name: ubodt file name.
    :return:
    """
    ubodt_gen = UBODTGenAlgorithm(network, graph)
    # The delta is defined as 3 km approximately. 0.03 degrees.
    ubodt_gen.generate_ubodt(os.path.join(file_directory, ubodt_name), 0.03, binary=False, use_omp=True)


def get_ubodt(file_directory: str, ubodt_name: str):
    """
    get ubodt.
    :param file_directory: the file_directory which map files are saved.
    :param ubodt_name:ubodt file name.
    :return: ubodt
    """
    ubodt = UBODT.read_ubodt_csv(os.path.join(file_directory, ubodt_name))
    return ubodt


def get_graph(network):
    """
    get the fmm NetworkGraph class.
    :param network: fmm Network class.
    :return:
    """
    return NetworkGraph(network)


def get_network(file_directory: str, edge_name: str, id='fid', source='u', target='v'):
    """
    get the fmm Network class.
    :param file_directory: the file_directory which map files are saved.
    :param edge_name: edge shape file name.
    :param id: edge shape attribute, edge id.
    :param source: edge shape attribute, edge source.
    :param target: edge shape attribute, edge target.
    :return:
    """
    network = Network(os.path.join(file_directory, edge_name), id, source, target)
    return network


def _gen_trajectory(points) -> str:
    """
    convert points list to LINESTRING.
    :param points:
    :return: LINESTRING
    """
    trajectory = ''
    for point in points:
        trajectory += str(point['longitude'])
        trajectory += ' '
        trajectory += str(point['latitude'])
        trajectory += ','
    wkt = "LINESTRING({})".format(trajectory)

    return wkt


def _get_fix_traj(res_wkt) -> list:
    """
    convert fmm result to points list.
    :param res_wkt: fmm result.
    :return: points list.
    """
    s = res_wkt[11:-1]
    coors = s.split(',')
    points = []
    for coor in coors:
        temp = coor.split(' ')
        if temp is None or len(temp) != 2:
            continue
        tax = {'latitude': float(temp[1]), 'longitude': float(temp[0])}
        tax['y'] = tax['latitude']
        tax['x'] = tax['longitude']
        points.append(tax)
    return points


def _match(points, fmm_model, fmm_config):
    """
    :param points: trajectory that is going to be matched.
    :param fmm_model: fmm model.
    :param fmm_config: fmm config.
    :return: opath and the repair trajectory. Opath is the optimal path, containing id of edges matched to each point in a trajectory.
    """
    wkt = _gen_trajectory(points)
    result = fmm_model.match_wkt(wkt, fmm_config)
    fix_traj = _get_fix_traj(result.mgeom.export_wkt())
    points_opath = []
    for path, point in zip(list(result.opath), points):
        point['opath'] = path
        points_opath.append(point)
    return points_opath, fix_traj


def match_points(ubodt, graph, network, points, fmm_config) -> (list, list):
    """
    match points. Due to some trajectories are discontinuous, match algorithm will be called multi times.
    :param ubodt: ubodt.
    :param graph: fmm NetworkGraph class.
    :param network: fmm Network class.
    :param points: trajectory.
    :param fmm_config: fmm config.
    :return: opath and the repair trajectory. Opath is the optimal path, containing id of edges matched to each point in a trajectory.
    """
    wkt = _gen_trajectory(points)
    fmm_model = FastMapMatch(network, graph, ubodt)
    points_with_opath = []
    fix_trajectory = []
    while True:
        _result = fmm_model.check_match_wkt(wkt, fmm_config)
        if int(_result) == -1:
            points_opath, fix_traj = _match(points, fmm_model, fmm_config)
            data_util.gen_speed(points_opath)
            points_with_opath += points_opath
            fix_trajectory += fix_traj
            break
        first = points[:int(_result) + 1]
        points_opath, fix_traj = _match(first, fmm_model, fmm_config)
        # generate each point group's speed
        data_util.gen_speed(points_opath)
        points_with_opath += points_opath
        fix_trajectory += fix_traj
        points = points[int(_result) + 1:]
        wkt = _gen_trajectory(points)
    return points_with_opath, fix_trajectory
