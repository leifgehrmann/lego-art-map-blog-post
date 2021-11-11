from typing import Tuple

from manim import VGroup, Scene, config, FadeIn, AnimationGroup, Transform, \
    ReplacementTransform, Rectangle, Create, UP, Text, DOWN, FadeOut, Write, \
    LEFT, RIGHT

# The scene will contain a rectangle that is 128 by 80 units. We add a margin
# of 20 units to allow us to display text if necessary.
from util.lego_projection_transformer_builder import \
    LegoProjectionTransformerBuilder
from util.number_plane_helper import generate_transformable_number_plane
from util.shapely_helper import load_world_map
from util.shapely_manim_helper import shapely_multi_polygon_to_manim, \
    shapely_multi_line_string_to_manim

content_width = 128
content_height = 80
content_offset = 10 * UP
frame_padding = 20
frame_height_old = config.frame_height
config.frame_height = content_height + frame_padding * 2
config.frame_width = config.frame_width * config.frame_height / frame_height_old


def get_wgs84_scale():
    return config.frame_width / 360


def transform_wgs84_to_void(
        coord: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    scale_x = content_width / 360
    return coord[0] * scale_x, coord[1] * scale_x, 0


def transform_wgs84_to_fit_content(
        coord: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    scale_x = content_width / 360
    scale_y = content_height / 180
    return coord[0] * scale_x, coord[1] * scale_y, 0


class Render(Scene):
    def construct(self):
        # Prepare some objects that we will use throughout the animation.
        land_shapes = load_world_map()
        builder = LegoProjectionTransformerBuilder(
            canvas_width=content_width,
            canvas_height=content_height
        )
        transform_wgs84_to_lego = builder.build_wgs84_to_lego()

        wgs84_rect = Rectangle(
            width=content_width,
            height=180 * content_width / 360,
            background_stroke_width=50,
            stroke_width=20,
            stroke_opacity=1
        )
        content_rect = Rectangle(
            width=content_width,
            height=content_height,
            background_stroke_width=50,
            stroke_width=20,
            stroke_opacity=1
        )
        wgs84_rect.shift(content_offset)
        content_rect.shift(content_offset)

        # Scene: Display WGS84 world map container
        step_1_text = Text(
            'Step 1: World map in standard WGS84 projection.',
            font="sans-serif"
        )\
            .scale(8)\
            .next_to(content_rect, DOWN)
        step_1_text.shift(frame_padding / 2 * DOWN)
        self.play(Write(step_1_text))
        self.play(Create(wgs84_rect))

        # Scene: Display world map.
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
        land_group.shift(content_offset)
        axis_group.shift(content_offset)
        self.play(FadeIn(VGroup(land_group, axis_group)))
        self.wait()
        self.play(AnimationGroup(FadeOut(wgs84_rect), FadeOut(step_1_text)))

        # Scene: Text that explains we are fitting the world map to the canvas
        step_2_text = Text(
            'Step 2: Stretch the map to the size-ratio of the LEGO world map.',
            font="sans-serif"
        )\
            .scale(8) \
            .next_to(content_rect, DOWN)
        step_2_text.shift(frame_padding / 2 * DOWN)
        self.play(AnimationGroup(Write(step_2_text)))

        # Scene: Draw the expected canvas size
        self.play(Create(content_rect))

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
        land_group_stretched.shift(content_offset)
        axis_group_stretched.shift(content_offset)
        self.play(Transform(
            VGroup(land_group, axis_group),
            VGroup(land_group_stretched, axis_group_stretched)
        ))
        self.wait()
        self.play(FadeOut(step_2_text))

        # Scene: Text that explains we are shifting each latitude individually,
        # and display individual stretch latitudes (In red)
        step_3_text = Text(
            'Step 3: Distort the latitudes individually.',
            font="sans-serif"
        ) \
            .scale(8) \
            .next_to(content_rect, DOWN)
        step_3_text.shift(frame_padding / 2 * DOWN)

        latitude_lines = shapely_multi_line_string_to_manim(
            builder.get_latitude_bands_as_multi_line_string(),
            '#FF0000',
            transform_wgs84_to_fit_content
        )
        canvas_lines = shapely_multi_line_string_to_manim(
            builder.get_canvas_bands_as_multi_line_string(),
            '#FF0000',
            lambda x: (x[0], content_height / 2 - x[1], 0)
        )
        latitude_lines.shift(content_offset)
        canvas_lines.shift(content_offset)

        self.play(AnimationGroup(
            Write(step_3_text),
            Create(latitude_lines)
        ))
        self.wait()

        # Scene: Stretch individual latitudes
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
        land_group_lego.shift(content_offset)
        axis_group_lego.shift(content_offset)

        self.play(ReplacementTransform(
            VGroup(land_group, axis_group, latitude_lines),
            VGroup(land_group_lego, axis_group_lego, canvas_lines)
        ))
        self.wait()
        self.play(AnimationGroup(
            FadeOut(step_3_text),
            FadeOut(canvas_lines)
        ))

        # Scene: Text that explains why the map is being shifted by 4 units
        step_4_text = Text(
            'Step 4: Shift the world map to the left.',
            font="sans-serif"
        ) \
            .scale(8) \
            .next_to(content_rect, DOWN)
        step_4_text.shift(frame_padding / 2 * DOWN)
        self.play(Write(step_4_text))

        # Scene: Display repeating x-axis. In other words, one on the left,
        # another to the right of the center map.
        land_group_lego_left = land_group_lego.copy()
        land_group_lego_right = land_group_lego.copy()
        axis_group_lego_left = axis_group_lego.copy()
        axis_group_lego_right = axis_group_lego.copy()
        land_group_lego_left.shift(content_width * LEFT)
        land_group_lego_right.shift(content_width * RIGHT)
        axis_group_lego_left.shift(content_width * LEFT)
        axis_group_lego_right.shift(content_width * RIGHT)
        self.play(FadeIn(VGroup(
            land_group_lego_left,
            land_group_lego_right,
            axis_group_lego_left,
            axis_group_lego_right
        )))

        # Scene: Shift the worlds to the left
        self.play(
            VGroup(
                land_group_lego,
                land_group_lego_left,
                land_group_lego_right,
                axis_group_lego,
                axis_group_lego_left,
                axis_group_lego_right
            ).animate.shift(4 * LEFT),
        )

        # Scene: Un-hide the left and right maps, with the correctly cropped
        # center map, using a fade in animation.
        # Todo: Get center and right polygons, perform a difference against the
        # two rectangles, and get a unionized MultiPolygon.
        self.wait()
        self.play(FadeOut(step_4_text))

        # Scene: Text that explains what we are comparing it to.
        step_5_text = Text(
            'For comparison, here is LEGO\' World Map',
            font="sans-serif"
        ) \
            .scale(8) \
            .next_to(content_rect, DOWN)
        step_5_text.shift(frame_padding / 2 * DOWN)
        self.play(Write(step_5_text))

        # Scene: Fade in the actual LEGO world map in bitmap form.
        # Todo:
