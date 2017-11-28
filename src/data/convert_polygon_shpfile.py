import fiona
import math
from shapely.geometry import Point, shape, mapping
import itertools
import cPickle
import os
import argparse

MAP_DATA_FP = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)))) + '/data/processed/maps/'


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("shp", help="Segments shape file")
    parser.add_argument("-d", "--dir", type=str,
                        help="Can give alternate data directory")

    args = parser.parse_args()

    # Import shapefile specified at commandline
    shp = args.shp

    # Can override the hardcoded maps directory
    if args.dir:
        MAP_DATA_FP = args.dir + '/processed/maps/'

    # Get all lines, dummy id
    lines = [
        (
            line[0],
            shape(line[1]['geometry'])
        ) for line in enumerate(fiona.open(shp))
    ]

    with fiona.open(shp, 'r') as source:
        schema = source.schema.copy()
        with fiona.open(
                '/home/jenny/boston-crash-modeling/cambridge_data/test.shp',
                'w', driver=source.driver, crs=source.crs,
                schema=schema) as output:
            i = 0
            for f in source:
                import ipdb; ipdb.set_trace()

                if i < 30:
                    output.write(f)
                i += 1


