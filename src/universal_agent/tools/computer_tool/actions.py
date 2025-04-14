"""
Enumerations for the ComputerTool module defining the types of actions
and parameters that can be performed.
"""

from enum import Enum, auto


class Action(str, Enum):
    """Actions supported by the ComputerTool."""
    # Mouse actions
    KEY = "key"
    TYPE = "type"
    MOUSE_MOVE = "mouse_move"
    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    MIDDLE_CLICK = "middle_click"
    DOUBLE_CLICK = "double_click"
    LEFT_CLICK_DRAG = "left_click_drag"
    SCROLL = "scroll"
    
    # Screen actions
    SCREENSHOT = "screenshot"
    CURSOR_POSITION = "cursor_position"
    
    # Windows-specific window actions
    FIND_WINDOW = "find_window"
    MOVE_WINDOW = "move_window"
    SET_WINDOW_FOCUS = "set_window_focus"
    GET_WINDOW_INFO = "get_window_info"


class ScrollDirection(str, Enum):
    """Scroll directions for the scroll action."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class ScalingSource(str, Enum):
    """Sources for coordinate scaling."""
    COMPUTER = "computer"  # Scaling from the computer's actual coordinates
    API = "api"  # Scaling from the API's standardized coordinates
