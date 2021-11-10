from manim import VGroup, Line


def generate_transformable_number_plane(
        x_start: float,
        x_stop: float,
        x_step: float,
        y_start: float,
        y_stop: float,
        y_step: float,
        post_transformer,
        x_inclusive: bool = True,
        y_inclusive: bool = True
) -> VGroup:
    lines = []

    x_pos = x_start
    x_faux_stop = x_stop
    if x_inclusive:
        x_faux_stop = x_stop + x_step / 2
    while x_pos < x_faux_stop:
        start_pos = post_transformer((x_pos, y_start, 0))
        stop_pos = post_transformer((x_pos, y_stop, 0))
        lines.append(Line(
            start_pos,
            stop_pos,
            stroke_width=3,
        ))
        x_pos += x_step

    y_pos = y_start
    y_faux_stop = y_stop
    if y_inclusive:
        y_faux_stop = y_stop + y_step / 2
    while y_pos < y_faux_stop:
        start_pos = post_transformer((x_start, y_pos, 0))
        stop_pos = post_transformer((x_stop, y_pos, 0))
        lines.append(Line(
            start_pos,
            stop_pos,
            stroke_width=3,
        ))
        y_pos += y_step

    return VGroup(*lines)
