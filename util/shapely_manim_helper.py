from manim import VGroup, Polygon, Cutout, Line
from shapely.geometry.multilinestring import MultiLineString as ShapelyMultiLineString
from shapely.geometry.multipolygon import MultiPolygon as ShapelyMultiPolygon
from shapely.geometry.linestring import LineString as ShapelyLineString
from shapely.geometry.polygon import Polygon as ShapelyPolygon


def shapely_multi_line_string_to_manim(
    multi_line_string: ShapelyMultiLineString,
    stroke_color: str,
    transformer
) -> VGroup:
    manim_lines = []
    geom: ShapelyLineString
    for geom in multi_line_string.geoms:
        manim_coords = []
        for shapely_coord in geom.coords:
            manim_coords.append(transformer(shapely_coord))
        manim_object = Line(*manim_coords)
        manim_object.set_stroke(color=stroke_color, opacity=1, width=30)
        manim_lines.append(manim_object)

    return VGroup(*manim_lines)


def shapely_multi_polygon_to_manim(
        multi_polygon: ShapelyMultiPolygon,
        fill_color: str,
        transformer
) -> VGroup:
    manim_polygons = []
    geom: ShapelyPolygon
    for geom in multi_polygon.geoms:
        manim_exterior_coords = []
        for shapely_exterior_coord in geom.exterior.coords:
            manim_exterior_coords.append(
                transformer(shapely_exterior_coord)
            )
        manim_exterior_polygon = Polygon(*manim_exterior_coords)

        manim_interior_polygons = []
        for shapely_interior_geom in geom.interiors:
            manim_interior_coords = []
            for shapely_interior_coord in shapely_interior_geom.coords:
                manim_interior_coords.append(
                    transformer(shapely_interior_coord)
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
