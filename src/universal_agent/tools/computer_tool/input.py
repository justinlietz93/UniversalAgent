"""
Input operations (mouse, keyboard) for the ComputerTool module.
"""

import platform
import time
from typing import Dict, Any, List, Tuple, Optional

import pyautogui

# Configure pyautogui
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small delay between actions for stability


def handle_mouse_movement(x: int, y: int, duration: float = 0.1) -> Dict[str, Any]:
    """
    Move the mouse to the specified coordinates.
    
    Args:
        x (int): X coordinate.
        y (int): Y coordinate.
        duration (float): Duration of movement in seconds.
        
    Returns:
        Dict[str, Any]: Result of the operation.
    """
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return {
            "success": True,
            "position": {"x": x, "y": y},
            "message": f"Moved mouse to ({x}, {y})"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error moving mouse: {str(e)}"
        }


def handle_mouse_click(
    button: str = "left",
    clicks: int = 1,
    interval: float = 0.0,
    position: Optional[Tuple[int, int]] = None
) -> Dict[str, Any]:
    """
    Perform a mouse click.
    
    Args:
        button (str): Mouse button to click ('left', 'right', 'middle').
        clicks (int): Number of clicks.
        interval (float): Interval between clicks.
        position (Optional[Tuple[int, int]]): Position to move to before clicking.
        
    Returns:
        Dict[str, Any]: Result of the operation.
    """
    try:
        if position:
            pyautogui.moveTo(position[0], position[1])
            position_info = f" at ({position[0]}, {position[1]})"
        else:
            position_info = ""
        
        pyautogui.click(button=button, clicks=clicks, interval=interval)
        
        return {
            "success": True,
            "action": f"{button} click",
            "clicks": clicks,
            "message": f"Performed {button} click{position_info}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error clicking: {str(e)}"
        }


def handle_mouse_drag(
    x: int,
    y: int,
    duration: float = 0.5
) -> Dict[str, Any]:
    """
    Perform a mouse drag from current position to new coordinates.
    
    Args:
        x (int): Target X coordinate.
        y (int): Target Y coordinate.
        duration (float): Duration of drag in seconds.
        
    Returns:
        Dict[str, Any]: Result of the operation.
    """
    try:
        current_x, current_y = pyautogui.position()
        pyautogui.dragTo(x, y, duration=duration)
        
        return {
            "success": True,
            "from": {"x": current_x, "y": current_y},
            "to": {"x": x, "y": y},
            "message": f"Dragged mouse from ({current_x}, {current_y}) to ({x}, {y})"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error dragging mouse: {str(e)}"
        }


def handle_scroll(
    direction: str,
    amount: int = 10,
    x: Optional[int] = None,
    y: Optional[int] = None
) -> Dict[str, Any]:
    """
    Perform a scroll operation.
    
    Args:
        direction (str): Scroll direction ('up', 'down', 'left', 'right').
        amount (int): Amount to scroll.
        x (Optional[int]): X coordinate to move to before scrolling.
        y (Optional[int]): Y coordinate to move to before scrolling.
        
    Returns:
        Dict[str, Any]: Result of the operation.
    """
    try:
        position_info = ""
        if x is not None and y is not None:
            pyautogui.moveTo(x, y)
            position_info = f" at ({x}, {y})"
        
        if direction in ["up", "down"]:
            # Vertical scrolling
            scroll_amount = amount if direction == "up" else -amount
            pyautogui.scroll(scroll_amount)
        else:
            # Horizontal scrolling
            scroll_amount = amount if direction == "right" else -amount
            pyautogui.hscroll(scroll_amount)
        
        return {
            "success": True,
            "direction": direction,
            "amount": amount,
            "message": f"Scrolled {direction} by {amount}{position_info}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error scrolling: {str(e)}"
        }


def handle_key_press(text: str) -> Dict[str, Any]:
    """
    Simulate key presses.
    
    Args:
        text (str): Key combination to press (e.g., 'ctrl+c').
        
    Returns:
        Dict[str, Any]: Result of the operation.
    """
    try:
        # Map some common keys that might be named differently between platforms
        key_mapping = {
            "super": "win" if platform.system() == "Windows" else "command",
            "super_l": "win" if platform.system() == "Windows" else "command",
            "escape": "esc",
            "page_down": "pagedown",
            "page_up": "pageup"
        }
        
        # Split and press keys
        keys = text.split('+')
        for key in keys:
            key = key.strip().lower()
            # Apply mapping if needed
            key = key_mapping.get(key, key)
            pyautogui.keyDown(key)
        
        # Release keys in reverse order
        for key in reversed(keys):
            key = key.strip().lower()
            key = key_mapping.get(key, key)
            pyautogui.keyUp(key)
        
        return {
            "success": True,
            "keys": text,
            "message": f"Pressed keys: {text}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error pressing keys: {str(e)}"
        }


def handle_typing(text: str, interval: float = 0.01) -> Dict[str, Any]:
    """
    Type text.
    
    Args:
        text (str): Text to type.
        interval (float): Interval between keystrokes.
        
    Returns:
        Dict[str, Any]: Result of the operation.
    """
    try:
        pyautogui.write(text, interval=interval)
        
        return {
            "success": True,
            "text": text,
            "message": f"Typed text: {text}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error typing text: {str(e)}"
        }


def get_cursor_position(
    enable_scaling: bool = False,
    scale_func = None
) -> Dict[str, Any]:
    """
    Get the current cursor position.
    
    Args:
        enable_scaling (bool): Whether to apply scaling.
        scale_func: Function to scale coordinates.
        
    Returns:
        Dict[str, Any]: Result of the operation with cursor position.
    """
    try:
        x, y = pyautogui.position()
        
        if enable_scaling and scale_func:
            scaled_x, scaled_y = scale_func(x, y)
            return {
                "success": True,
                "raw_position": {"x": x, "y": y},
                "scaled_position": {"x": scaled_x, "y": scaled_y},
                "message": f"Cursor raw position: ({x}, {y}), scaled: ({scaled_x}, {scaled_y})"
            }
        
        return {
            "success": True,
            "position": {"x": x, "y": y},
            "message": f"Cursor position: ({x}, {y})"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting cursor position: {str(e)}"
        }
