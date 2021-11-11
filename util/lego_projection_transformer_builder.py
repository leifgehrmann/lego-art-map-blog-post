from math import isclose

from typing import Tuple, Callable, TypedDict, List

from shapely.geometry import LineString, MultiLineString


class StretchRange(TypedDict):
    latitude_range_start: float
    latitude_range_stop: float
    canvas_range_start: float
    canvas_range_stop: float


class LegoProjectionTransformerBuilder:
    stretch_bands: List[StretchRange]

    def __init__(
            self,
            canvas_width: float,
            canvas_height: float
    ):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.stretch_bands = [
            {
                'latitude_range_start': -90.00001,
                'latitude_range_stop': -83.0,
                'canvas_range_start': 80.0001,
                'canvas_range_stop': 80,
            },
            {
                'latitude_range_start': -83.0,
                'latitude_range_stop': -60.0,
                'canvas_range_start': 80,
                'canvas_range_stop': 70,
            },
            {
                'latitude_range_start': -60.0,
                'latitude_range_stop': -57.0,
                'canvas_range_start': 70,
                'canvas_range_stop': 67,
            },
            {
                'latitude_range_start': -57.0,
                'latitude_range_stop': 86.0,
                'canvas_range_start': 67,
                'canvas_range_stop': 4,
            },
            {
                'latitude_range_start': 86.0,
                'latitude_range_stop': 90.000001,
                'canvas_range_start': 4,
                'canvas_range_stop': 0,
            }
        ]

    def get_latitude_bands_as_multi_line_string(self) -> MultiLineString:
        line_strings = []

        # Skip the first element
        for stretch_band in self.stretch_bands[1:]:
            start_x = -180
            end_x = 180
            y = stretch_band['latitude_range_start']
            line_strings.append(LineString([(start_x, y), (end_x, y)]))

        line_strings.reverse()
        return MultiLineString(line_strings)

    def get_canvas_bands_as_multi_line_string(self) -> MultiLineString:
        line_strings = []

        # Skip the first element
        for stretch_band in self.stretch_bands[1:]:
            start_x = -self.canvas_width / 2
            end_x = self.canvas_width / 2
            y = stretch_band['canvas_range_start']
            line_strings.append(LineString([(start_x, y), (end_x, y)]))

        line_strings.reverse()
        return MultiLineString(line_strings)

    def build_wgs84_to_lego(
            self
    ) -> Callable[[Tuple[float, float]], Tuple[float, float, float]]:
        def wgs84_to_lego_transformer(
                coord: Tuple[float, float]
        ) -> Tuple[float, float, float]:
            longitude = coord[0]
            latitude = coord[1]
            x_percentage = longitude / 360
            x_offset = 0
            x_canvas = x_percentage * self.canvas_width + x_offset

            min_latitude_range = None
            max_latitude_range = None
            min_y_range = None
            max_y_range = None

            # The latitude mappings below assume that the canvas height is
            # 80px.
            for stretch_band in self.stretch_bands:
                if ((
                        stretch_band['latitude_range_start'] <= latitude or
                        isclose(stretch_band['latitude_range_start'], latitude)
                ) and
                        latitude < stretch_band['latitude_range_stop']
                ):
                    min_latitude_range = stretch_band['latitude_range_start']
                    max_latitude_range = stretch_band['latitude_range_stop']
                    min_y_range = stretch_band['canvas_range_start']
                    max_y_range = stretch_band['canvas_range_stop']
                    break

            if (
                    min_latitude_range is None or
                    max_latitude_range is None or
                    min_y_range is None or
                    max_y_range is None
            ):
                raise Exception(
                    'Coordinate (%f, %f) could not be projected' %
                    (longitude, latitude)
                )

            y_percentage = (latitude - min_latitude_range) / \
                           (max_latitude_range - min_latitude_range)
            y_canvas = y_percentage * (max_y_range - min_y_range) + min_y_range
            y_canvas = y_canvas * - 1 + self.canvas_height / 2
            return x_canvas, y_canvas, 0

        return wgs84_to_lego_transformer
