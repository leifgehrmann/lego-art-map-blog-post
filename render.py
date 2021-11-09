from pathlib import Path
from typing import Tuple, List

import shapefile
from manim import VGroup, Polygon, Scene, config, FadeIn, AnimationGroup, Cutout, NumberPlane
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon as ShapelyMultiPolygon
from shapely.geometry.polygon import Polygon as ShapelyPolygon
from shapely.ops import unary_union


def shapely_polygons_to_multipolygon(
        polygons: List[ShapelyPolygon]
) -> ShapelyMultiPolygon:
    return unary_union(polygons)


def load_world_map() -> ShapelyMultiPolygon:
    data_path = Path(__file__).parent.joinpath('data')
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


def get_wgs84_scale():
    return 1 / 360 * config["frame_width"] * 0.8


def transform_wgs84(coord) -> Tuple[float, float, float]:
    scale = get_wgs84_scale()
    return coord[0] * scale, coord[1] * scale, 0


def shapely_multi_polygon_to_manim(
        multi_polygon: ShapelyMultiPolygon,
        fill_color: str
) -> VGroup:
    manim_polygons = []
    geom: ShapelyPolygon
    for geom in multi_polygon.geoms:
        manim_exterior_coords = []
        for shapely_exterior_coord in geom.exterior.coords:
            manim_exterior_coords.append(
                transform_wgs84(shapely_exterior_coord)
            )
        manim_exterior_polygon = Polygon(*manim_exterior_coords)

        manim_interior_polygons = []
        for shapely_interior_geom in geom.interiors:
            manim_interior_coords = []
            for shapely_interior_coord in shapely_interior_geom.coords:
                manim_interior_coords.append(
                    transform_wgs84(shapely_interior_coord)
                )
            manim_interior_polygons.append(Polygon(*manim_interior_coords))

        manim_object = manim_exterior_polygon
        if len(manim_interior_polygons) != 0:
            manim_object = Cutout(
                manim_exterior_polygon,
                *manim_interior_polygons
            )

        manim_object.set_fill(color=fill_color, opacity=1)
        manim_object.set_stroke(opacity=0)
        manim_polygons.append(manim_object)
    return VGroup(*manim_polygons)





class Render(Scene):
    def construct(self):
        scale = get_wgs84_scale()
        number_plane = NumberPlane(
            x_range=[-180 * scale, 180 * scale, 5 * scale],
            y_range=[-90 * scale, 90 * scale, 5 * scale],
            background_line_style={
                "stroke_color": '#FFFFFF',
                "stroke_width": 1,
                "stroke_opacity": 0.3
            }
        )
        self.add(number_plane)

        land_shapes = load_world_map()
        land_group = shapely_multi_polygon_to_manim(land_shapes, '#FFFFFF')

        animations = [
            FadeIn(VGroup(land_group))
        ]

        self.play(AnimationGroup(*animations))

