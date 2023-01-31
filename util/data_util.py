# -*- encoding: utf-8 -*-
'''
@File        :   data_util.py    
@Modify Time :   2023/1/30 19:04
@Author      :   wyt
@Version     :   1.0
@Desciption  :   None
'''
import codecs
import copy
import numpy as np
from geopy.distance import geodesic
from shapely.geometry import Point


def process_points(points, time_begin, time_end, polygon, need_polygon: bool) -> list:
    """
    preprocess trajectory, include these operations:
    1. remove the point that is not within the time range.
    2. remove the point that is not in the polygon.
    If these parameters are already set during `import_data`, this method does not need to be called.
    :param points: trajectory.
    :param time_begin: the begin time of trajectory.
    :param time_end: the end time of trajectory.
    :param polygon: the boundaries of map
    :param need_polygon: if True, remove the point of trajectory which is not in the polygon.
    :return: a new trajectory.
    """
    res = []
    for point in points:
        point['time'] = int(point['time'])
        if point['time'] < time_begin or point['time'] > time_end:
            continue
        point['x'] = point['longitude']
        point['y'] = point['latitude']
        if need_polygon:
            if polygon.contains(Point(point['x'], point['y'])):
                res.append(point)
        else:
            res.append(point)
    return res


def import_data(file_path: str, time_begin: int = None, time_end: int = None, polygon=None) -> {str: []}:
    """
    import data.
    :param file_path: the data file path.
    :param time_begin: a filter. If not None and record's time < time_begin, this record will be discarded. It takes effect only when time_begin and time_end are both not None.
    :param time_end: a filter. If not None and record's time > time_end, this record will be discarded. It takes effect only when time_begin and time_end are both not None.
    :param polygon: a filter. If not Node and record's position not in polygon, this record will be discarded.
    :return: a dict of data. Key is car_id, value is a list of trajectory.
    """
    res = {}
    with codecs.open(file_path, 'r', 'utf-8') as f:
        for line in f:
            if line.__contains__('定位无效'):
                continue
            row = {}
            try:
                columns = line.split('\t')
                row['car_id'] = columns[1]
                row['time'] = int(columns[2])
                row['latitude'] = float(columns[4]) / 100000
                row['longitude'] = float(columns[5]) / 100000
                row['speed'] = columns[7]
                if not car_id.__eq__(row['car_id']) and len(data) != 0:
                    # begin a new car data.
                    if len(data) > 10:
                        print(f'finished:{car_id}, numbers:{len(data)}')
                    else:
                        print(f'discard:{car_id}, numbers:{len(data)}')
                    data.sort(key=lambda node: node['time'])
                    res[car_id] = copy.deepcopy(data)
                    data = []
                valid = True
                if time_begin is not None and time_end is not None:
                    valid = valid and time_begin <= row['time'] <= time_end
                if polygon is not None:
                    valid = valid and polygon.contains(Point(row['longitude'], row['latitude']))
                if valid:
                    data.append(row)
                car_id = row['car_id']
            except Exception as e:
                print(e)
                continue
        data.sort(key=lambda node: node['time'])
        res[car_id] = data
    return res


def gen_speed(points:list):
    """
    calculate speed.
    :param points: trajectory points list.
    """
    if len(points) == 1:
        points[0]['speed_cal'] = 0
        return
    for i in range(len(points) - 1):
        first = points[i]
        second = points[i + 1]
        if first['time'] == second['time']:
            if i == 0:
                first['speed_cal'] = 0
            else:
                first['speed_cal'] = points[i - 1]['speed_cal']
            continue
        first['speed_cal'] = geodesic((second['y'], second['x']), (first['y'], first['x'])).m / (
                second['time'] - first['time'])
    front = points[len(points) - 2]
    last = points[len(points) - 1]
    if front['time'] == last['time']:
        last['speed_cal'] = front['speed_cal']
    else:
        last['speed_cal'] = geodesic((last['y'], last['x']), (front['y'], front['x'])).m / (
                last['time'] - front['time'])


def preprocess_data(points: [{}], duration=120, minimum_point_size=10):
    """
    because the original trajectory may be discontinuous, this method split the whole trajectory points to many short
    and continuous points list.
    :param points:  trajectory point list.
    :param duration:  maximum duration for continuous points.
    :param minimum_point_size: The minimum points' size for a matching.
    :return a list of continuous points.
    """
    if len(points) < minimum_point_size:
        return []
    times = [x['time'] for x in points]
    times_np = np.array(times)
    diff_times_np = times_np[1:] - times_np[:-1]
    cut_index = np.where(diff_times_np > duration)
    list_points = []
    begin = 0
    for end in cut_index[0]:
        if end - begin > minimum_point_size:
            list_points.append(points[begin: end])
            begin = end + 1
    return list_points
