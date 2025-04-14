"""
Coordinate handling utilities for the ComputerTool module.
"""

from typing import Tuple, Dict, List

from .actions import ScalingSource


def scale_coordinates(
    source: ScalingSource,
    x: int,
    y: int,
    screen_width: int,
    screen_height: int,
    target_scaling: Dict[str, int]
) -> Tuple[int, int]:
    """
    Scale coordinates between the actual screen space and target space.
    
    Args:
        source: Whether the coordinates are from API (need to be scaled up) or 
               from COMPUTER (need to be scaled down).
        x, y: The coordinates to scale.
        screen_width: The actual width of the screen.
        screen_height: The actual height of the screen.
        target_scaling: The target dimensions for scaling.
        
    Returns:
        The scaled coordinates.
    """
    # Get scaling factors
    x_scaling_factor = target_scaling["width"] / screen_width
    y_scaling_factor = target_scaling["height"] / screen_height
    
    if source == ScalingSource.API:
        # Scale from API (small) to computer screen (potentially larger)
        if x > target_scaling["width"] or y > target_scaling["height"]:
            raise ValueError(f"Coordinates {x}, {y} are out of bounds for target scaling")
        # Scale up from API coordinates to actual screen coordinates
        return round(x / x_scaling_factor), round(y / y_scaling_factor)
        
    # Scale from computer screen to API
    # Scale down from actual screen coordinates to standardized API coordinates
    return round(x * x_scaling_factor), round(y * y_scaling_factor)


def validate_coordinates(
    coordinate: List[int],
    enable_scaling: bool,
    screen_width: int,
    screen_height: int,
    offset_x: int,
    offset_y: int,
    target_scaling: Dict[str, int]
) -> Tuple[int, int]:
    """
    Validate and process coordinates, including scaling if enabled.
    
    Args:
        coordinate: Raw coordinates [x, y] from the API.
        enable_scaling: Whether to enable coordinate scaling.
        screen_width: The actual width of the screen.
        screen_height: The actual height of the screen.
        offset_x: The x offset of the screen.
        offset_y: The y offset of the screen.
        target_scaling: The target dimensions for scaling.
        
    Returns:
        Processed coordinates (x, y) with proper scaling and offset applied.
    """
    x, y = coordinate
    
    # Apply scaling if enabled
    if enable_scaling:
        x, y = scale_coordinates(
            ScalingSource.API, 
            x, 
            y, 
            screen_width, 
            screen_height, 
            target_scaling
        )
    
    # Apply offset for the selected screen
    x += offset_x
    y += offset_y
    
    return x, y
