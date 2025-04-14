"""
Main ComputerTool implementation for the Universal Agent framework.
"""

import platform
from typing import Dict, Any, List, Optional, Tuple

from src.universal_agent.interfaces.types import ToolParams, ToolResult
from src.universal_agent.tools.base_tool import BaseTool

from .actions import Action, ScrollDirection, ScalingSource
from .coordinates import scale_coordinates, validate_coordinates
from .input import (
    handle_mouse_movement, handle_mouse_click, handle_mouse_drag,
    handle_scroll, handle_key_press, handle_typing, get_cursor_position
)
from .screen import (
    get_screen_size, get_screen_offset_and_bbox, 
    take_screenshot, get_screen_details
)
from .windows import (
    find_window_by_title, get_window_info,
    move_window, set_window_focus
)


class ComputerTool(BaseTool):
    """
    A cross-platform tool for interacting with the computer's screen, keyboard, and mouse.
    
    Supports:
    - Mouse actions (move, click, drag, scroll)
    - Keyboard actions (type text, key combinations)
    - Screenshot capture (whole screen or specific monitor)
    - Window management (Windows only: find, move, focus, get info)
    
    Has special handling for multi-monitor setups and can scale coordinates between
    different resolution spaces (useful for vision-language model integrations).
    """
    
    def __init__(self, id: str = "computer", name: str = "Computer Control", 
                 description: str = None, selected_screen: int = 0, 
                 enable_scaling: bool = True):
        """
        Initialize the computer tool.
        
        Args:
            id (str): Unique identifier for the tool.
            name (str): Human-readable name for the tool.
            description (str): Description of the tool's functionality (auto-generated if None).
            selected_screen (int): Index of screen to use (0 = primary/first screen).
            enable_scaling (bool): Whether to enable coordinate scaling.
        """
        # Generate description if not provided
        if description is None:
            description = self._generate_description()
        
        super().__init__(id=id, name=name, description=description)
        
        # Tool configuration
        self.selected_screen = selected_screen
        self.enable_scaling = enable_scaling
        self._screenshot_delay = 0.5  # Delay before taking screenshot (seconds)
        
        # Screen properties
        self.screen_width, self.screen_height = get_screen_size(self.selected_screen)
        self.offset_x, self.offset_y, self.bbox = get_screen_offset_and_bbox(self.selected_screen)
        
        # For coordinate scaling with VLMs
        self.scaled_width = 1280  # Default target width for scaling
        self.scaled_height = 800  # Default target height for scaling
        self.target_scaling = {"width": self.scaled_width, "height": self.scaled_height}
    
    def _generate_description(self) -> str:
        """Generate a detailed description of the tool."""
        return """A tool for controlling the computer's mouse, keyboard, windows, and capturing screenshots.
        
Available actions:

1. Mouse Movement:
   - action: "mouse_move"
   - coordinate: [x, y] (required)
   Example: {"action": "mouse_move", "coordinate": [500, 500]}

2. Mouse Clicks:
   - action: "left_click", "right_click", "middle_click", or "double_click"
   - coordinate: [x, y] (optional, if not provided uses current position)
   Example: {"action": "left_click", "coordinate": [500, 500]}

3. Mouse Drag:
   - action: "left_click_drag"
   - coordinate: [x, y] (required - destination coordinates)
   Example: {"action": "left_click_drag", "coordinate": [600, 600]}

4. Scroll:
   - action: "scroll"
   - scroll_direction: "up", "down", "left", "right" (required)
   - scroll_amount: integer (optional, default 10)
   - coordinate: [x, y] (optional, if not provided uses current position)
   Example: {"action": "scroll", "scroll_direction": "down", "scroll_amount": 5}

5. Keyboard Input:
   - action: "type" for text, "key" for key combinations
   - text: string (required)
   Examples: 
     {"action": "type", "text": "Hello World"}
     {"action": "key", "text": "ctrl+c"}

6. Screen Capture:
   - action: "screenshot"
   Example: {"action": "screenshot"}

7. Cursor Position:
   - action: "cursor_position"
   Example: {"action": "cursor_position"}

8. Window Control (Windows only):
   - action: "find_window"
   - window_title: window title to find (required)
   Example: {"action": "find_window", "window_title": "Notepad"}

   - action: "move_window"
   - window_title: title of window to move (required)
   - position: [x, y] (required)
   - size: [width, height] (optional)
   Example: {"action": "move_window", "window_title": "Notepad", "position": [0, 0], "size": [800, 600]}

   - action: "set_window_focus"
   - window_title: title of window to focus (required)
   Example: {"action": "set_window_focus", "window_title": "Notepad"}

   - action: "get_window_info"
   - window_title: title of window to get info for (required)
   Example: {"action": "get_window_info", "window_title": "Notepad"}"""
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Get the input schema for the tool."""
        schema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [e.value for e in Action],
                    "description": "The action to perform"
                },
                "text": {
                    "type": "string",
                    "description": "Text to type or key command to send"
                },
                "coordinate": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Screen coordinates [x, y]"
                },
                "scroll_direction": {
                    "type": "string",
                    "enum": [e.value for e in ScrollDirection],
                    "description": "Direction to scroll (up, down, left, right)"
                },
                "scroll_amount": {
                    "type": "integer",
                    "description": "Amount to scroll (positive integer)"
                },
                "window_title": {
                    "type": "string",
                    "description": "Title of window to control (Windows only)"
                },
                "position": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Window position [x, y] (Windows only)"
                },
                "size": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Window size [width, height] (Windows only)"
                }
            },
            "required": ["action"],
            "additionalProperties": False,
        }
        
        # Add action-specific required parameters
        schema["allOf"] = [
            {
                "if": {"properties": {"action": {"enum": ["mouse_move", "left_click_drag"]}}},
                "then": {"required": ["coordinate"]}
            },
            {
                "if": {"properties": {"action": {"enum": ["key", "type"]}}},
                "then": {"required": ["text"]}
            },
            {
                "if": {"properties": {"action": {"enum": ["scroll"]}}},
                "then": {"required": ["scroll_direction"]}
            },
            {
                "if": {"properties": {"action": {"enum": ["find_window", "move_window", "set_window_focus", "get_window_info"]}}},
                "then": {"required": ["window_title"]}
            },
            {
                "if": {"properties": {"action": {"enum": ["move_window"]}}},
                "then": {"required": ["position"]}
            }
        ]
        
        return schema
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """
        Execute the computer tool with the given parameters.
        
        Args:
            params (ToolParams): The parameters for the action.
            
        Returns:
            ToolResult: The result of the action.
        """
        try:
            # Validate parameters
            validation_error = self.validate_parameters(params)
            if validation_error:
                return self.create_error_result(validation_error)
            
            # Extract parameters
            action = Action(params["action"])
            text = params.get("text")
            coordinate = params.get("coordinate")
            scroll_direction = params.get("scroll_direction")
            scroll_amount = params.get("scroll_amount", 10)
            window_title = params.get("window_title")
            position = params.get("position")
            size = params.get("size")
            
            # Dispatch to the appropriate action handler
            if action == Action.MOUSE_MOVE:
                return await self._handle_mouse_move(coordinate)
                
            elif action == Action.LEFT_CLICK_DRAG:
                return await self._handle_click_drag(coordinate)
                
            elif action in [Action.KEY, Action.TYPE]:
                return await self._handle_keyboard_action(action, text)
                
            elif action == Action.SCROLL:
                return await self._handle_scroll(scroll_direction, scroll_amount, coordinate)
                
            elif action == Action.SCREENSHOT:
                return await self._handle_screenshot()
                
            elif action == Action.CURSOR_POSITION:
                return await self._handle_cursor_position()
                
            elif action in [Action.LEFT_CLICK, Action.RIGHT_CLICK, Action.MIDDLE_CLICK, Action.DOUBLE_CLICK]:
                return await self._handle_click(action, coordinate)
                
            # Windows-specific window management actions
            elif platform.system() == "Windows":
                if action == Action.FIND_WINDOW:
                    return await self._handle_find_window(window_title)
                    
                elif action == Action.MOVE_WINDOW:
                    return await self._handle_move_window(window_title, position, size)
                    
                elif action == Action.SET_WINDOW_FOCUS:
                    return await self._handle_set_window_focus(window_title)
                    
                elif action == Action.GET_WINDOW_INFO:
                    return await self._handle_get_window_info(window_title)
            
            # If we get here with a Windows-only action on non-Windows platform
            if action in [Action.FIND_WINDOW, Action.MOVE_WINDOW, Action.SET_WINDOW_FOCUS, Action.GET_WINDOW_INFO]:
                return self.create_error_result(f"Action '{action}' is only supported on Windows")
                
            return self.create_error_result(f"Unsupported action: {action}")
            
        except Exception as e:
            return self.create_error_result(f"Error executing computer action: {str(e)}")
    
    # Action handler methods
    
    async def _handle_mouse_move(self, coordinate: List[int]) -> ToolResult:
        """Handle mouse movement."""
        try:
            x, y = validate_coordinates(
                coordinate, 
                self.enable_scaling,
                self.screen_width,
                self.screen_height,
                self.offset_x,
                self.offset_y,
                self.target_scaling
            )
            
            result = handle_mouse_movement(x, y, duration=0.1)
            
            if result["success"]:
                return self.create_success_result(result)
            else:
                return self.create_error_result(result["error"])
                
        except Exception as e:
            return self.create_error_result(f"Error moving mouse: {str(e)}")
    
    async def _handle_click_drag(self, coordinate: List[int]) -> ToolResult:
        """Handle click and drag."""
        try:
            x, y = validate_coordinates(
                coordinate, 
                self.enable_scaling,
                self.screen_width,
                self.screen_height,
                self.offset_x,
                self.offset_y,
                self.target_scaling
            )
            
            result = handle_mouse_drag(x, y, duration=0.5)
            
            if result["success"]:
                return self.create_success_result(result)
            else:
                return self.create_error_result(result["error"])
                
        except Exception as e:
            return self.create_error_result(f"Error dragging mouse: {str(e)}")
    
    async def _handle_keyboard_action(self, action: Action, text: str) -> ToolResult:
        """Handle keyboard actions (key, type)."""
        try:
            if action == Action.KEY:
                result = handle_key_press(text)
            else:  # TYPE
                result = handle_typing(text, interval=0.01)
                
            if result["success"]:
                return self.create_success_result(result)
            else:
                return self.create_error_result(result["error"])
                
        except Exception as e:
            return self.create_error_result(f"Error with keyboard action: {str(e)}")
    
    async def _handle_scroll(self, direction: str, amount: int, coordinate: Optional[List[int]] = None) -> ToolResult:
        """Handle scrolling."""
        try:
            if coordinate:
                x, y = validate_coordinates(
                    coordinate, 
                    self.enable_scaling,
                    self.screen_width,
                    self.screen_height,
                    self.offset_x,
                    self.offset_y,
                    self.target_scaling
                )
                result = handle_scroll(direction, amount, x, y)
            else:
                result = handle_scroll(direction, amount)
                
            if result["success"]:
                return self.create_success_result(result)
            else:
                return self.create_error_result(result["error"])
                
        except Exception as e:
            return self.create_error_result(f"Error scrolling: {str(e)}")
    
    async def _handle_click(self, action: Action, coordinate: Optional[List[int]] = None) -> ToolResult:
        """Handle various click actions."""
        try:
            button = "left"
            clicks = 1
            interval = 0.0
            
            if action == Action.RIGHT_CLICK:
                button = "right"
            elif action == Action.MIDDLE_CLICK:
                button = "middle"
            elif action == Action.DOUBLE_CLICK:
                clicks = 2
                interval = 0.1
                
            if coordinate:
                x, y = validate_coordinates(
                    coordinate, 
                    self.enable_scaling,
                    self.screen_width,
                    self.screen_height,
                    self.offset_x,
                    self.offset_y,
                    self.target_scaling
                )
                result = handle_mouse_click(button, clicks, interval, (x, y))
            else:
                result = handle_mouse_click(button, clicks, interval)
                
            if result["success"]:
                result["action"] = action.value  # Override with the original action name
                return self.create_success_result(result)
            else:
                return self.create_error_result(result["error"])
                
        except Exception as e:
            return self.create_error_result(f"Error clicking: {str(e)}")
    
    async def _handle_screenshot(self) -> ToolResult:
        """Handle taking a screenshot."""
        try:
            # Take screenshot
            screenshot_base64 = take_screenshot(
                bbox=self.bbox,
                target_dimensions=self.target_scaling if self.enable_scaling else None
            )
            
            # Return the screenshot as base64
            return self.create_success_result({
                "action": Action.SCREENSHOT.value,
                "type": "image",
                "format": "base64",
                "data": screenshot_base64
            })
                
        except Exception as e:
            return self.create_error_result(f"Error taking screenshot: {str(e)}")
    
    async def _handle_cursor_position(self) -> ToolResult:
        """Handle getting cursor position."""
        try:
            if self.enable_scaling:
                # Define a scaling function for cursor position
                def scale_func(x, y):
                    x_adj, y_adj = x - self.offset_x, y - self.offset_y
                    return scale_coordinates(
                        ScalingSource.COMPUTER, 
                        x_adj, 
                        y_adj,
                        self.screen_width,
                        self.screen_height,
                        self.target_scaling
                    )
                    
                result = get_cursor_position(enable_scaling=True, scale_func=scale_func)
            else:
                result = get_cursor_position()
                
            if result["success"]:
                result["action"] = Action.CURSOR_POSITION.value
                return self.create_success_result(result)
            else:
                return self.create_error_result(result["error"])
                
        except Exception as e:
            return self.create_error_result(f"Error getting cursor position: {str(e)}")
    
    # Windows-specific window management handlers
    
    async def _handle_find_window(self, window_title: str) -> ToolResult:
        """Handle finding a window by title (Windows only)."""
        if platform.system() != "Windows":
            return self.create_error_result("Find window is only supported on Windows")
            
        try:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                window_info = get_window_info(hwnd)
                window_info["action"] = Action.FIND_WINDOW.value
                return self.create_success_result(window_info)
            return self.create_error_result(f"Window with title '{window_title}' not found")
        except Exception as e:
            return self.create_error_result(f"Error finding window: {str(e)}")
    
    async def _handle_move_window(self, window_title: str, position: List[int], size: Optional[List[int]] = None) -> ToolResult:
        """Handle moving a window (Windows only)."""
        if platform.system() != "Windows":
            return self.create_error_result("Move window is only supported on Windows")
            
        try:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                success = move_window(hwnd, position, size)
                if success:
                    size_info = f" with size ({size[0]}, {size[1]})" if size else ""
                    return self.create_success_result({
                        "action": Action.MOVE_WINDOW.value,
                        "window_title": window_title,
                        "position": position,
                        "size": size,
                        "message": f"Moved window '{window_title}' to ({position[0]}, {position[1]}){size_info}"
                    })
                return self.create_error_result(f"Failed to move window '{window_title}'")
            return self.create_error_result(f"Window with title '{window_title}' not found")
        except Exception as e:
            return self.create_error_result(f"Error moving window: {str(e)}")
    
    async def _handle_set_window_focus(self, window_title: str) -> ToolResult:
        """Handle setting focus to a window (Windows only)."""
        if platform.system() != "Windows":
            return self.create_error_result("Set window focus is only supported on Windows")
            
        try:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                success = set_window_focus(hwnd)
                if success:
                    return self.create_success_result({
                        "action": Action.SET_WINDOW_FOCUS.value,
                        "window_title": window_title,
                        "message": f"Set focus to window '{window_title}'"
                    })
                return self.create_error_result(f"Failed to set focus to window '{window_title}'")
            return self.create_error_result(f"Window with title '{window_title}' not found")
        except Exception as e:
            return self.create_error_result(f"Error setting window focus: {str(e)}")
    
    async def _handle_get_window_info(self, window_title: str) -> ToolResult:
        """Handle getting window information (Windows only)."""
        if platform.system() != "Windows":
            return self.create_error_result("Get window info is only supported on Windows")
            
        try:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                window_info = get_window_info(hwnd)
                window_info["action"] = Action.GET_WINDOW_INFO.value
                window_info["window_title"] = window_title
                return self.create_success_result(window_info)
            return self.create_error_result(f"Window with title '{window_title}' not found")
        except Exception as e:
            return self.create_error_result(f"Error getting window info: {str(e)}")
