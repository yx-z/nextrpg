from collections import namedtuple

type Alpha = int
"""
Alpha channel that defines the transparency between [0, 255] for images.
0 is fully transparent, 255 is fully opaque.
"""


class Rgba(namedtuple("Rgba", "red green blue alpha")):
    """
    Represents an RGBA color with red, green, blue and alpha components.

    This immutable class provides a convenient way to represent colors
    with transparency support. All components are integers in the range
    0-255, where 0 represents no intensity and 255 represents full
    intensity.

    Arguments:
        `red`: The red component of the color (0-255).

        `green`: The green component of the color (0-255).

        `blue`: The blue component of the color (0-255).

        `alpha`: The alpha (opacity) component of the color (0-255).
            0 is fully transparent, 255 is fully opaque.

    Example:
        ```python
        # Create a semi-transparent red color
        red_color = Rgba(255, 0, 0, 128)

        # Create a fully opaque white color
        white_color = Rgba(255, 255, 255, 255)
        ```
    """

    red: int
    green: int
    blue: int
    alpha: Alpha


BLACK = Rgba(0, 0, 0, 255)
WHITE = Rgba(255, 255, 255, 255)


def alpha_from_percentage(percentage: float) -> Alpha:
    """
    Convert a percentage value to an alpha channel value.

    Converts a percentage (0.0 to 1.0) to an alpha channel value (0 to 255) for
    transparency calculations.

    Arguments:
        percentage: A float between 0.0 and 1.0 representing the transparency
            percentage.

    Returns:
        An integer between 0 and 255 representing the alpha channel value.
    """
    return int(255 * percentage)
