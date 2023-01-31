# Simplify Map And Match Trajectory
- Simplify Map:
This project can download a map from OSM and SHP within the boundaries of some shapely polygon and then simplify it by remove extra points and edges.
- Match trajectory:
This project can match trajectory for the map you download.

# Project structure 
- data: A map polygon example of the second Ring Road of Beijing.
- example: A example code to execute download map and match trajectory.
- util: Some utils.
    - data_util: import and preprocess data.
    - draw_util: draw map and trajectory points.
    - map_util: download and simplify map.
    - match_util: match trajectory.

# How to run it
1. download the code and install the packages.
2. install fast_match_map, and change the `sys.path.append("/data/wyt/packages/fmm-master/build/python/")` in match_util.py to your own path. To install it, you can see https://github.com/cyang-kth/fmm
3. `python demo_beijing.py`

# Notes
- This project simplify the map by using osmnx(https://github.com/gboeing/osmnx).
- You can get the map polygon through this web site https://extract.bbbike.org/
