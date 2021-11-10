from pathlib import Path
from typing import List

import shapefile
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import unary_union


def shapely_polygons_to_multipolygon(
        polygons: List[Polygon]
) -> MultiPolygon:
    return unary_union(polygons)


def load_world_map() -> MultiPolygon:
    data_path = Path(__file__).parent.parent.joinpath('data')
    land_shape_path = data_path.joinpath('ne_110m_land/ne_110m_land.shp')
    lake_shape_path = data_path.joinpath('ne_110m_lakes/ne_110m_lakes.shp')

    # Read world map shapefile
    def parse_shapefile(shapefile_path: Path):
        shapefile_collection = shapefile.Reader(shapefile_path.as_posix())
        shapely_objects = []
        for shape_record in shapefile_collection.shapeRecords():
            shapely_objects.append(shape(shape_record.shape.__geo_interface__))
        return shapely_objects

    land_shapes = parse_shapefile(land_shape_path)
    land_shapes = shapely_polygons_to_multipolygon(land_shapes)
    lake_shapes = parse_shapefile(lake_shape_path)
    for lake_shape in lake_shapes:
        land_shapes = land_shapes.difference(lake_shape)

    return land_shapes
