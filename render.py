from typing import Tuple

from manim import VGroup, Scene, config, FadeIn, AnimationGroup, NumberPlane, Transform, ReplacementTransform

# The scene will contain a rectangle that is 128 by 80 units. We add a margin
# of 20 units to allow us to display text if necessary.
from util.lego_projection_transformer_builder import LegoProjectionTransformerBuilder
from util.number_plane_helper import generate_transformable_number_plane
from util.shapely_helper import load_world_map
from util.shapely_manim_helper import shapely_multi_polygon_to_manim

content_width = 128
content_height = 80
frame_padding = 20
frame_height_old = config.frame_height
config.frame_height = content_height + frame_padding * 2
config.frame_width = config.frame_width * config.frame_height / frame_height_old


def get_wgs84_scale():
    return 1 / 360 * config.frame_width


def transform_wgs84_to_void(
        coord: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    scale_x = 1 / 180 * content_width / 2
    return coord[0] * scale_x, coord[1] * scale_x, 0


def transform_wgs84_to_fit_content(
        coord: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    scale_x = 1 / 180 * content_width / 2
    scale_y = 1 / 90 * content_height / 2
    return coord[0] * scale_x, coord[1] * scale_y, 0


class Render(Scene):
    def construct(self):
        land_shapes = load_world_map()

        # Scene: Display world map
        land_group = shapely_multi_polygon_to_manim(
            land_shapes,
            '#FFFFFF',
            transform_wgs84_to_void
        )
        axis_group = generate_transformable_number_plane(
            -180, 180, 5,
            -90, 90, 5,
            transform_wgs84_to_void
        )
        self.play(AnimationGroup(FadeIn(VGroup(land_group, axis_group))))

        # Scene: Draw the expected canvas size

        # Scene: Stretch to fit the expected canvas size
        land_group_stretched = shapely_multi_polygon_to_manim(
            land_shapes,
            '#FFFFFF',
            transform_wgs84_to_fit_content
        )
        axis_group_stretched = generate_transformable_number_plane(
            -180, 180, 5,
            -90, 90, 5,
            transform_wgs84_to_fit_content
        )
        self.play(Transform(
            VGroup(land_group, axis_group),
            VGroup(land_group_stretched, axis_group_stretched)
        ))

        # Scene: Display individual stretch latitudes (In red)

        # Scene: Stretch individual latitudes
        builder = LegoProjectionTransformerBuilder(
            canvas_width=content_width,
            canvas_height=content_height
        )
        transform_wgs84_to_lego = builder.build_wgs84_to_lego()
        land_group_lego = shapely_multi_polygon_to_manim(
            land_shapes,
            '#FFFFFF',
            transform_wgs84_to_lego
        )
        axis_group_lego = generate_transformable_number_plane(
            -180, 180, 5,
            -90, 90, 5,
            transform_wgs84_to_lego
        )

        self.play(ReplacementTransform(
            VGroup(land_group, axis_group),
            VGroup(land_group_lego, axis_group_lego)
        ))

        # Scene: Display repeating x-axis. In other words, one on the left,
        # another to the right of the center map.

        # Scene: Draw a center line (in red)

        # Scene: Shift the worlds to the left

        # Scene: Un-hide the left and right maps, with the correctly cropped
        # center map, using a fade in animation.

        # Scene: Fade in the actual LEGO world map in bitmap form.

