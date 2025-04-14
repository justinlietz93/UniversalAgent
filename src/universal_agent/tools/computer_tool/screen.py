"""
Screen handling utilities for the ComputerTool module.
"""

import base64
import io
import platform
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Optional
from uuid import uuid4

import pyautogui
from PIL import Image, ImageGrab
from screeninfo import get_monitors

# Import platform-specific modules
if platform.system() == "Darwin":  # macOS
    try:
        import Quartz
    except ImportError:
        pass  # Will handle gracefully in the code


def get_screen_size(selected_screen: int = 0) -> Tuple[int, int]:
    """
    Get the dimensions of the selected screen.
    
    Args:
        selected_screen (int): Index of the screen to get dimensions for.
        
    Returns:
        Tuple[int, int]: The width and height of the selected screen.
    """
    if platform.system() == "Windows":
        # Windows: Use screeninfo
        screens = get_monitors()
        sorted_screens = sorted(screens, key=lambda s: s.x)
        
        if selected_screen < 0 or selected_screen >= len(screens):
            # Fall back to primary screen
            for i, screen in enumerate(screens):
                if screen.is_primary:
                    return screen.width, screen.height
            # If no primary screen found, use first screen
            return sorted_screens[0].width, sorted_screens[0].height
        
        screen = sorted_screens[selected_screen]
        return screen.width, screen.height
        
    elif platform.system() == "Darwin":  # macOS
        # macOS: Use Quartz if available
        if 'Quartz' in globals():
            max_displays = 32
            active_displays = Quartz.CGGetActiveDisplayList(max_displays, None, None)[1]
            
            screens = []
            for display_id in active_displays:
                bounds = Quartz.CGDisplayBounds(display_id)
                is_primary = Quartz.CGDisplayIsMain(display_id)
                screens.append({
                    'id': display_id,
                    'x': int(bounds.origin.x),
                    'y': int(bounds.origin.y),
                    'width': int(bounds.size.width),
                    'height': int(bounds.size.height),
                    'is_primary': is_primary
                })
            
            sorted_screens = sorted(screens, key=lambda s: s['x'])
            
            if selected_screen < 0 or selected_screen >= len(screens):
                # Fall back to primary screen
                for screen in screens:
                    if screen['is_primary']:
                        return screen['width'], screen['height']
                # If no primary screen found, use first screen
                return sorted_screens[0]['width'], sorted_screens[0]['height']
            
            screen = sorted_screens[selected_screen]
            return screen['width'], screen['height']
        
        # Fallback if Quartz not available
        return pyautogui.size()
        
    else:  # Linux or other
        # Try using xrandr command
        try:
            cmd = "xrandr | grep ' connected' | head -n1 | awk '{print $3}' | cut -d'+' -f1"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            if 'x' in output:
                width, height = map(int, output.split('x'))
                return width, height
        except Exception:
            pass
        
        # Fallback
        return pyautogui.size()


def get_screen_offset_and_bbox(selected_screen: int = 0) -> Tuple[int, int, Tuple[int, int, int, int]]:
    """
    Get the screen offset and bounding box for the selected screen.
    
    Args:
        selected_screen (int): Index of the screen to get offset and bbox for.
        
    Returns:
        Tuple[int, int, Tuple[int, int, int, int]]: The x and y offset and the bounding box.
    """
    if platform.system() == "Windows":
        # Windows: Use screeninfo
        screens = get_monitors()
        sorted_screens = sorted(screens, key=lambda s: s.x)
        
        if selected_screen < 0 or selected_screen >= len(screens):
            # Fall back to primary screen
            for i, screen in enumerate(screens):
                if screen.is_primary:
                    return (screen.x, screen.y, 
                            (screen.x, screen.y, screen.x + screen.width, screen.y + screen.height))
            # If no primary screen found, use first screen
            screen = sorted_screens[0]
            return (screen.x, screen.y, 
                    (screen.x, screen.y, screen.x + screen.width, screen.y + screen.height))
        
        screen = sorted_screens[selected_screen]
        return (screen.x, screen.y, 
                (screen.x, screen.y, screen.x + screen.width, screen.y + screen.height))
        
    elif platform.system() == "Darwin":  # macOS
        # macOS: Use Quartz if available
        if 'Quartz' in globals():
            max_displays = 32
            active_displays = Quartz.CGGetActiveDisplayList(max_displays, None, None)[1]
            
            screens = []
            for display_id in active_displays:
                bounds = Quartz.CGDisplayBounds(display_id)
                is_primary = Quartz.CGDisplayIsMain(display_id)
                screens.append({
                    'id': display_id,
                    'x': int(bounds.origin.x),
                    'y': int(bounds.origin.y),
                    'width': int(bounds.size.width),
                    'height': int(bounds.size.height),
                    'is_primary': is_primary
                })
            
            sorted_screens = sorted(screens, key=lambda s: s['x'])
            
            if selected_screen < 0 or selected_screen >= len(screens):
                # Fall back to primary screen
                for screen in screens:
                    if screen['is_primary']:
                        return (screen['x'], screen['y'], 
                                (screen['x'], screen['y'], 
                                 screen['x'] + screen['width'], screen['y'] + screen['height']))
                # If no primary screen found, use first screen
                screen = sorted_screens[0]
                return (screen['x'], screen['y'], 
                        (screen['x'], screen['y'], 
                         screen['x'] + screen['width'], screen['y'] + screen['height']))
            
            screen = sorted_screens[selected_screen]
            return (screen['x'], screen['y'], 
                    (screen['x'], screen['y'], 
                     screen['x'] + screen['width'], screen['y'] + screen['height']))
        
        # Fallback if Quartz not available
        return (0, 0, (0, 0, *pyautogui.size()))
        
    else:  # Linux or other
        # For simplicity, assume single screen or primary screen
        return (0, 0, (0, 0, *pyautogui.size()))


def take_screenshot(bbox: Optional[Tuple[int, int, int, int]] = None, 
                   target_dimensions: Optional[Dict[str, int]] = None) -> str:
    """
    Take a screenshot and return it as a base64 string.
    
    Args:
        bbox (Optional[Tuple[int, int, int, int]]): Bounding box for screenshot.
        target_dimensions (Optional[Dict[str, int]]): Target dimensions for scaling.
        
    Returns:
        str: Base64-encoded screenshot.
    """
    try:
        # Create temporary output directory if needed
        output_dir = Path("./tmp/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Take the screenshot
        if platform.system() == "Windows" or platform.system() == "Darwin":
            # Windows/macOS: Use PIL ImageGrab with bbox
            screenshot = ImageGrab.grab(bbox=bbox)
        else:  # Linux or other
            screenshot = pyautogui.screenshot()
        
        # Apply scaling if needed
        if target_dimensions:
            screenshot = screenshot.resize((target_dimensions["width"], target_dimensions["height"]))
        
        # Convert to base64
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
        
    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        # Fallback to pyautogui screenshot
        try:
            screenshot = pyautogui.screenshot()
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e2:
            print(f"Fallback screenshot also failed: {str(e2)}")
            raise e  # Re-raise the original error


def get_screen_details():
    """Get detailed information about all screens in the system."""
    screens = get_monitors()
    screen_details = []

    # Sort screens by x position to arrange from left to right
    sorted_screens = sorted(screens, key=lambda s: s.x)

    # Loop through sorted screens and assign positions
    primary_index = 0
    for i, screen in enumerate(sorted_screens):
        if i == 0:
            layout = "Left"
        elif i == len(sorted_screens) - 1:
            layout = "Right"
        else:
            layout = "Center"
        
        if screen.is_primary:
            position = "Primary" 
            primary_index = i
        else:
            position = "Secondary"
        screen_info = f"Screen {i + 1}: {screen.width}x{screen.height}, {layout}, {position}"
        screen_details.append(screen_info)

    return screen_details, primary_index
