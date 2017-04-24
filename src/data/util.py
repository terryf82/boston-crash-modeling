import fiona
from shapely.geometry import shape, mapping


def write_shp(schema, fp, data, shape_key, prop_key):
    """ Write spatial data to shapefile 

    Args:
        schema (dict): 
        fp (str): Filename to write to
        data: Iterable of records 
        shape_key: In a record, key to a Shapely geometry
        prop_key: In a record, key to a properties dict
    """
    with fiona.open(fp, 'w', 'ESRI Shapefile', schema) as c:
        for i in data:
            c.write({
                'geometry': mapping(i[shape_key]),
                'properties': i[prop_key],
            })


def read_shp(fp):
    """ Read shp, output tuple geometry + property 

    Args:
        fp: Filename to read

    Returns:
        object: list of tuples (geometry, properties)
    """
    out = [(shape(line['geometry']), line['properties'])
           for line in fiona.open(fp)]
    return (out)
