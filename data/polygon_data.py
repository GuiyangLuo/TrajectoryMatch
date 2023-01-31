# -*- encoding: utf-8 -*-
'''
@File        :   polygon_data.py    
@Modify Time :   2023/1/30 19:24
@Author      :   wyt
@Version     :   1.0
@Desciption  :   There is a map polygon example.
'''

from shapely import wkt


def get_beijing():
    """
    Get a map boundaries of the second Ring Road of Beijing
    :return: the polygon
    """
    return wkt.loads((
        "  POLYGON((116.304   39.867 , 116.308   39.857 , 116.319   39.847 , 116.34   39.847 , 116.365   39.855 , 116.393   39.855 , 116.443   39.857 , 116.456   39.866 , 116.457   39.899 , 116.457   39.952 , 116.431   39.969 , 116.314   39.967 , 116.302   39.962 , 116.303   39.942 , 116.304   39.867 ))"
    ))
