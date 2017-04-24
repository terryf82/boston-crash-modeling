import fiona
import sys
import math
from shapely.geometry import Point, shape, mapping
import itertools
import cPickle


def track(index, step, tot):
    """ Utility function for printing progress to console 

    Args:
        index: 
        step: 
        tot: 
    """
    if index % step == 0:
        print "finished {} of {}".format(index, tot)


def ex_inters(inter, prop):
    """ Function for extracting intersections, return coordinates + properties

    Args:
        inter: intersection geometry
        prop: properties to associate with each output
        
    Returns:
        iterable of tuples (point geometry, properties)
    """
    if "Point" == inter.type:
        yield inter, prop
    # If multiple intersections, return each point
    elif "MultiPoint" == inter.type:
        for i in inter:
            yield (i, prop)
    # If line with overlap, find start/end, return
    elif "MultiLineString" == inter.type:
        multiLine = [line for line in inter]
        first_coords = multiLine[0].coords[0]
        last_coords = multiLine[-1].coords[1]
        for i in [Point(first_coords[0], first_coords[1]), Point(last_coords[0], last_coords[1])]:
            yield (i, prop)
    # If collection points/lines (rare), just re-run on each part
    elif "GeometryCollection" == inter.type:
        for geom in inter:
            for i in ex_inters(geom, prop):
                yield i


def nCr(n, r):
    """  Total combinations

    Args:
        n: 
        r: 

    Returns:

    """
    f = math.factorial
    return f(n) / f(r) / f(n - r)


def main(shp, pickle_out="intersections.pkl", out="intersections.shp"):
    """ Given shapefile, extracts intersections

    Args:
        shp: Shapefile to process
        pickle_out: Filename for output pickle 
        out: Filename for output shapefile

    """
    # Import shapefile specified at commandline


    # Get all lines, dummy id
    lines = [
        (
            line[0],
            shape(line[1]['geometry'])
        ) for line in enumerate(fiona.open(shp))
    ]

    if not os.path.exists(pickle_out):
        inters = []
        i = 0

        tot = nCr(len(lines), 2)
        # Iterate, extract intersections
        for line1, line2 in itertools.combinations(lines, 2):
            track(i, 10000, tot)
            if line1[1].intersects(line2[1]):
                inter = line1[1].intersection(line2[1])
                inters.extend(ex_inters(inter,
                                        {'id_1': line1[0], 'id_2': line2[0]}
                                        ))
            i += 1

        # Save to pickle in case script breaks
        with open(pickle_out, 'w') as f:
            cPickle.dump(inters, f)
    else:
        with open(pickle_out, 'w') as f:
            inters = cPickle.load(f)

    # de duplicated
    inters_de = []
    # schema of the shapefile
    schema = {'geometry': 'Point',
              'properties': {'id_1': 'int',
                             'id_2': 'int'}
              }
    # creation of the shapefile
    with fiona.open(out, 'w', 'ESRI Shapefile', schema) as output:
        i = 0
        for pt in inters:
            if pt[0] not in inters_de:
                track(i, 10000, len(inters))
                output.write({'geometry': mapping(pt[0]), 'properties': pt[1]})
                inters_de.append(pt[0])
                i += 1


if __name__ == '__main__':
    shp = sys.argv[1]
    main(shp)
