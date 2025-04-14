"""
Windows-specific utilities for the ComputerTool module.
"""

import platform
from typing import Dict, Any, Optional, List, Tuple

# Only import Windows-specific modules when on Windows
if platform.system() == "Windows":
    import win32api
    import win32con
    import win32gui


def find_window_by_title(title: str) -> Optional[int]:
    """
    Find a window by its title (Windows only).
    
    Args:
        title (str): Title of the window to find.
        
    Returns:
        Optional[int]: Window handle if found, None otherwise.
    """
    if platform.system() != "Windows":
        return None
        
    try:
        # First try exact match
        hwnd = win32gui.FindWindow(None, title)
        if hwnd and win32gui.IsWindowVisible(hwnd):
            return hwnd
        
        # If not found, try partial match
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title.lower() in window_title.lower():
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows[0] if windows else None
    except Exception as e:
        print(f"Error finding window: {str(e)}")
        return None


def get_window_info(hwnd: int) -> Dict[str, Any]:
    """
    Get information about a window (Windows only).
    
    Args:
        hwnd (int): Window handle.
        
    Returns:
        Dict[str, Any]: Window information.
    """
    if platform.system() != "Windows":
        return {}
        
    try:
        rect = win32gui.GetWindowRect(hwnd)
        return {
            "window_handle": hwnd,
            "position": [rect[0], rect[1]],
            "size": [rect[2] - rect[0], rect[3] - rect[1]],
            "title": win32gui.GetWindowText(hwnd),
            "class": win32gui.GetClassName(hwnd),
            "visible": win32gui.IsWindowVisible(hwnd),
            "enabled": win32gui.IsWindowEnabled(hwnd),
            "minimized": win32gui.IsIconic(hwnd),
            "foreground": hwnd == win32gui.GetForegroundWindow()
        }
    except Exception as e:
        print(f"Error getting window info: {str(e)}")
        return {}


def move_window(hwnd: int, position: List[int], size: Optional[List[int]] = None) -> bool:
    """
    Move and/or resize a window (Windows only).
    
    Args:
        hwnd (int): Window handle.
        position (List[int]): New position [x, y].
        size (Optional[List[int]]): New size [width, height].
        
    Returns:
        bool: Whether the operation was successful.
    """
    if platform.system() != "Windows":
        return False
        
    try:
        if not size:
            rect = win32gui.GetWindowRect(hwnd)
            size = [rect[2] - rect[0], rect[3] - rect[1]]
        win32gui.MoveWindow(hwnd, position[0], position[1], size[0], size[1], True)
        return True
    except Exception as e:
        print(f"Error moving window: {str(e)}")
        return False


def set_window_focus(hwnd: int) -> bool:
    """
    Set focus to a window (Windows only).
    
    Args:
        hwnd (int): Window handle.
        
    Returns:
        bool: Whether the operation was successful.
    """
    if platform.system() != "Windows":
        return False
        
    try:
        # Ensure window is not minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        # Set focus
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        print(f"Error setting window focus: {str(e)}")
        return False
