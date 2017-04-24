# coding: utf-8


# Joining segments (intersection and non-intersection) to crash/concern data
# Draws on: http://bit.ly/2m7469y
# Developed by: bpben

import fiona
import json
import pyproj
import rtree
import csv
import pandas as pd
import os.path
from shapely.geometry import Point, shape, mapping
from util import write_shp, read_shp


def read_record(record, x, y, orig=None, new=pyproj.Proj(init='epsg:3857')):
    """
    Reads record, outputs dictionary with point and properties, reprojecting if necessary
    
    Arguments:
        record: 
        x (float): X coordinate 
        y (float): Y coordinate
        orig: Original pyproj projection, e.g. pyproj.Proj(init="epsg:3857")
        new: A new pyproj projection, e.g. pyproj.Proj(
    """
    if (orig is not None):
        x, y = pyproj.transform(orig, new, x, y)
    r_dict = {
        'point': Point(float(x), float(y)),
        'properties': record
    }
    return r_dict


def make_schema(geometry, properties):
    """
    Utility for making schema with 'str' value for each key in properties

    Args:
        geometry:  
        properties (dict):   

    Returns:
        dict: Schema for a feature
    """
    properties_dict = {k: 'str' for k, v in properties.items()}
    schema = {
        'geometry': geometry,
        'properties': properties_dict
    }
    return schema


def find_nearest(records, segments, segments_index, tolerance):
    """ For each record, finds nearest segment 

    Args:
        records: An array of 
        segments: A list of segments
        segments_index: an Rtree spatial index for segments
        tolerance: Max distance from record point to consider (in projection units) 
    """

    print "Using tolerance {}".format(tolerance)

    for record in records:
        record_point = record['point']
        record_buffer_bounds = record_point.buffer(tolerance).bounds
        nearby_segments = segments_index.intersection(record_buffer_bounds)
        segment_id_with_distance = [
            # Get db index and distance to point
            (
                segments[segment_id][1]['id'],
                segments[segment_id][0].distance(record_point)
            )
            for segment_id in nearby_segments
        ]
        # Find nearest segment
        if len(segment_id_with_distance):
            nearest = min(segment_id_with_distance, key=lambda tup: tup[1])
            db_segment_id = nearest[0]
            # Add db_segment_id to record
            record['properties']['near_id'] = db_segment_id
        # If no segment matched, populate key = ''
        else:
            record['properties']['near_id'] = ''


def main():
    """ Links point data (crashes, VZ concerns) to road network 
     
    Dependencies:
        raw/cad_crash_events_with_transport_2017_wgs84.csv
        raw/Vision_Zero_Entry.csv
        interim/inters_segments.shp
        interim/non_inters.segments.shp
        
    Outputs:
        interim/concern_joined.shp
        interim/concern_joined.json
        interim/crash_joined.shp
        interim/crash_joined.json
    """
    # Project projection = EPSG:3857
    # MAP_FP = './data/maps'
    # DATA_FP = './data'
    INTERIM_FP = os.path.normpath('./data/interim')
    # PROCESSED_FP = './data/processed'
    RAW_FP = os.path.normpath('./data/raw')

    # Read in CAD crash data
    crash = []

    with open(os.path.join(RAW_FP, "cad_crash_events_with_transport_2016_wgs84.csv")) as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            # Some crash 0 / blank coordinates
            if r['X'] != '':
                crash.append(
                    read_record(r, r['X'], r['Y'],
                                orig=pyproj.Proj(init='epsg:4326'))
                )
    print "Read in data from {} crashes".format(len(crash))

    # Read in vision zero data
    concern = []
    # Have to use pandas read_csv, unicode trubs
    concern_raw = pd.read_csv(os.path.join(RAW_FP, "Vision_Zero_Entry.csv"), encoding='utf-8-sig')
    concern_raw = concern_raw.to_dict('records')
    for r in concern_raw:
        concern.append(
            read_record(r, r['X'], r['Y'],
                        orig=pyproj.Proj(init='epsg:4326'))
        )
    print "Read in data from {} concerns".format(len(concern))

    # Read in segments
    inter = read_shp(os.path.join(INTERIM_FP, 'inters_segments.shp'))
    non_inter = read_shp(os.path.join(INTERIM_FP, 'non_inters_segments.shp'))
    print "Read in {} intersection, {} non-intersection segments".format(len(inter), len(non_inter))

    # Combine inter + non_inter
    combined_seg = inter + non_inter

    # Create spatial index for quick lookup
    segments_index = rtree.index.Index()
    for idx, element in enumerate(combined_seg):
        segments_index.insert(idx, element[0].bounds)

    # Find nearest crashes - 30 tolerance
    print "snapping crashes to segments"
    find_nearest(crash, combined_seg, segments_index, 30)

    # Find nearest concerns - 20 tolerance
    print "snapping concerns to segments"
    find_nearest(concern, combined_seg, segments_index, 20)

    # Write concerns
    concern_schema = make_schema('Point', concern[0]['properties'])
    print "output concerns shp to ", INTERIM_FP
    write_shp(concern_schema, os.path.join(INTERIM_FP, 'concern_joined.shp'),
              concern, 'point', 'properties')
    print "output concerns data to ", INTERIM_FP
    with open(os.path.join(INTERIM_FP, 'concern_joined.json'), 'w') as f:
        json.dump([c['properties'] for c in concern], f)

    # Write crash
    crash_schema = make_schema('Point', crash[0]['properties'])
    print "output crash shp to ", INTERIM_FP
    write_shp(crash_schema, os.path.join(INTERIM_FP, 'crash_joined.shp'),
              crash, 'point', 'properties')
    print "output crash data to ", INTERIM_FP
    with open(os.path.join(INTERIM_FP, 'crash_joined.json'), 'w') as f:
        json.dump([c['properties'] for c in crash], f)


if __name__ == '__main__':
    main()
