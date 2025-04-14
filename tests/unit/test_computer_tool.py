"""Unit tests for the ComputerTool."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import platform
import base64
from typing import Dict, Any, List, Tuple

from src.universal_agent.tools.computer_tool import ComputerTool, Action, ScrollDirection, ScalingSource


@pytest.fixture
def mock_computer_tool():
    """Create a mock ComputerTool instance for testing."""
    with patch('pyautogui.size', return_value=(1920, 1080)), \
         patch('screeninfo.get_monitors', return_value=[
             MagicMock(x=0, y=0, width=1920, height=1080, is_primary=True)
         ]):
        tool = ComputerTool()
        # Mock platform-specific functionality
        tool._take_screenshot = MagicMock(return_value="mocked_base64_image")
        
        # Mock pyautogui methods
        patch('pyautogui.moveTo', MagicMock()).start()
        patch('pyautogui.click', MagicMock()).start()
        patch('pyautogui.dragTo', MagicMock()).start()
        patch('pyautogui.scroll', MagicMock()).start()
        patch('pyautogui.hscroll', MagicMock()).start()
        patch('pyautogui.keyDown', MagicMock()).start()
        patch('pyautogui.keyUp', MagicMock()).start()
        patch('pyautogui.write', MagicMock()).start()
        patch('pyautogui.position', MagicMock(return_value=(100, 100))).start()
        
        # Mock Windows-specific features if on Windows
        if platform.system() == "Windows":
            patch('win32gui.FindWindow', MagicMock(return_value=12345)).start()
            patch('win32gui.GetWindowText', MagicMock(return_value="Test Window")).start()
            patch('win32gui.GetClassName', MagicMock(return_value="TestWindowClass")).start()
            patch('win32gui.GetWindowRect', MagicMock(return_value=(10, 20, 410, 320))).start()
            patch('win32gui.IsWindowVisible', MagicMock(return_value=True)).start()
            patch('win32gui.IsWindowEnabled', MagicMock(return_value=True)).start()
            patch('win32gui.IsIconic', MagicMock(return_value=False)).start()
            patch('win32gui.GetForegroundWindow', MagicMock(return_value=12345)).start()
            patch('win32gui.MoveWindow', MagicMock()).start()
            patch('win32gui.SetForegroundWindow', MagicMock()).start()
            patch('win32gui.ShowWindow', MagicMock()).start()
            
            # Mock the Windows-specific window finding
            tool._find_window_by_title = MagicMock(return_value=12345)
        
        yield tool


@pytest.mark.asyncio
async def test_get_parameter_schema(mock_computer_tool):
    """Test that parameter schema is properly defined."""
    schema = mock_computer_tool.get_parameter_schema()
    
    # Check basic schema structure
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "action" in schema["properties"]
    assert "required" in schema
    assert "action" in schema["required"]
    
    # Check action enum values
    actions = schema["properties"]["action"]["enum"]
    for action in [e.value for e in Action]:
        assert action in actions
    
    # Check conditionally required parameters
    assert "allOf" in schema
    # There should be conditions for required parameters based on action
    assert len(schema["allOf"]) > 0


@pytest.mark.asyncio
async def test_mouse_move(mock_computer_tool):
    """Test mouse movement."""
    with patch('pyautogui.moveTo') as mock_move:
        result = await mock_computer_tool.execute({
            "action": "mouse_move",
            "coordinate": [500, 300]
        })
        
        # Verify result
        assert result.success is True
        assert result.data["action"] == "mouse_move"
        assert "position" in result.data
        
        # Verify pyautogui call
        mock_move.assert_called_once()


@pytest.mark.asyncio
async def test_click_actions(mock_computer_tool):
    """Test mouse click actions."""
    click_actions = ["left_click", "right_click", "middle_click", "double_click"]
    
    for action in click_actions:
        with patch('pyautogui.click') as mock_click:
            result = await mock_computer_tool.execute({
                "action": action,
                "coordinate": [500, 300]
            })
            
            # Verify result
            assert result.success is True
            assert result.data["action"] == action
            assert "message" in result.data
            
            # Verify pyautogui call
            mock_click.assert_called_once()


@pytest.mark.asyncio
async def test_click_drag(mock_computer_tool):
    """Test click and drag."""
    with patch('pyautogui.dragTo') as mock_drag:
        result = await mock_computer_tool.execute({
            "action": "left_click_drag",
            "coordinate": [500, 300]
        })
        
        # Verify result
        assert result.success is True
        assert result.data["action"] == "left_click_drag"
        assert "from" in result.data
        assert "to" in result.data
        
        # Verify pyautogui call
        mock_drag.assert_called_once()


@pytest.mark.asyncio
async def test_scroll(mock_computer_tool):
    """Test scrolling."""
    scroll_directions = ["up", "down", "left", "right"]
    
    for direction in scroll_directions:
        with patch('pyautogui.scroll') as mock_scroll, \
             patch('pyautogui.hscroll') as mock_hscroll:
            
            result = await mock_computer_tool.execute({
                "action": "scroll",
                "scroll_direction": direction,
                "scroll_amount": 5
            })
            
            # Verify result
            assert result.success is True
            assert result.data["action"] == "scroll"
            assert result.data["direction"] == direction
            
            # Verify correct pyautogui call based on direction
            if direction in ["up", "down"]:
                mock_scroll.assert_called_once()
            else:
                mock_hscroll.assert_called_once()


@pytest.mark.asyncio
async def test_keyboard_actions(mock_computer_tool):
    """Test keyboard actions."""
    # Test key combination
    with patch('pyautogui.keyDown') as mock_key_down, \
         patch('pyautogui.keyUp') as mock_key_up:
        
        result = await mock_computer_tool.execute({
            "action": "key",
            "text": "ctrl+c"
        })
        
        # Verify result
        assert result.success is True
        assert result.data["action"] == "key"
        assert result.data["text"] == "ctrl+c"
        
        # Verify pyautogui calls (2 keys = 2 downs and 2 ups)
        assert mock_key_down.call_count == 2
        assert mock_key_up.call_count == 2
    
    # Test typing
    with patch('pyautogui.write') as mock_write:
        result = await mock_computer_tool.execute({
            "action": "type",
            "text": "Hello, world!"
        })
        
        # Verify result
        assert result.success is True
        assert result.data["action"] == "type"
        assert result.data["text"] == "Hello, world!"
        
        # Verify pyautogui call
        mock_write.assert_called_once_with("Hello, world!", interval=0.01)


@pytest.mark.asyncio
async def test_screenshot(mock_computer_tool):
    """Test screenshot functionality."""
    result = await mock_computer_tool.execute({"action": "screenshot"})
    
    # Verify result
    assert result.success is True
    assert result.data["action"] == "screenshot"
    assert result.data["type"] == "image"
    assert result.data["format"] == "base64"
    assert result.data["data"] == "mocked_base64_image"


@pytest.mark.asyncio
async def test_cursor_position(mock_computer_tool):
    """Test getting cursor position."""
    with patch('pyautogui.position', return_value=(100, 100)):
        result = await mock_computer_tool.execute({"action": "cursor_position"})
        
        # Verify result
        assert result.success is True
        assert result.data["action"] == "cursor_position"
        # With the default setup, we should get scaled position
        assert "scaled_position" in result.data or "position" in result.data


@pytest.mark.asyncio
async def test_coordinate_scaling(mock_computer_tool):
    """Test coordinate scaling functionality."""
    # Test API to computer scaling
    api_x, api_y = 500, 300  # Coordinates in API space
    screen_x, screen_y = mock_computer_tool._scale_coordinates(ScalingSource.API, api_x, api_y)
    
    # Verify scaling calculation
    expected_x = round(api_x / (mock_computer_tool.target_scaling["width"] / mock_computer_tool.screen_width))
    expected_y = round(api_y / (mock_computer_tool.target_scaling["height"] / mock_computer_tool.screen_height))
    assert screen_x == expected_x
    assert screen_y == expected_y
    
    # Test computer to API scaling
    api_x2, api_y2 = mock_computer_tool._scale_coordinates(ScalingSource.COMPUTER, screen_x, screen_y)
    
    # Verify reverse scaling is close to original (might have small rounding differences)
    assert abs(api_x2 - api_x) <= 1
    assert abs(api_y2 - api_y) <= 1


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific tests")
@pytest.mark.asyncio
async def test_windows_find_window(mock_computer_tool):
    """Test finding a window by title (Windows only)."""
    result = await mock_computer_tool.execute({
        "action": "find_window",
        "window_title": "Test Window"
    })
    
    # Verify result
    assert result.success is True
    assert result.data["action"] == "find_window"
    assert result.data["window_handle"] == 12345
    assert "position" in result.data
    assert "size" in result.data
    assert result.data["title"] == "Test Window"


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific tests")
@pytest.mark.asyncio
async def test_windows_move_window(mock_computer_tool):
    """Test moving a window (Windows only)."""
    with patch('win32gui.MoveWindow') as mock_move:
        result = await mock_computer_tool.execute({
            "action": "move_window",
            "window_title": "Test Window",
            "position": [100, 200],
            "size": [800, 600]
        })
        
        # Verify result
        assert result.success is True
        assert result.data["action"] == "move_window"
        assert result.data["position"] == [100, 200]
        assert result.data["size"] == [800, 600]
        
        # Verify win32gui call
        mock_move.assert_called_once_with(12345, 100, 200, 800, 600, True)


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific tests")
@pytest.mark.asyncio
async def test_windows_set_window_focus(mock_computer_tool):
    """Test setting window focus (Windows only)."""
    with patch('win32gui.SetForegroundWindow') as mock_focus:
        result = await mock_computer_tool.execute({
            "action": "set_window_focus",
            "window_title": "Test Window"
        })
        
        # Verify result
        assert result.success is True
        assert result.data["action"] == "set_window_focus"
        
        # Verify win32gui call
        mock_focus.assert_called_once_with(12345)


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific tests")
@pytest.mark.asyncio
async def test_windows_get_window_info(mock_computer_tool):
    """Test getting window information (Windows only)."""
    result = await mock_computer_tool.execute({
        "action": "get_window_info",
        "window_title": "Test Window"
    })
    
    # Verify result
    assert result.success is True
    assert result.data["action"] == "get_window_info"
    assert result.data["window_handle"] == 12345
    assert "position" in result.data
    assert "size" in result.data
    assert "title" in result.data
    assert "class" in result.data
    assert "visible" in result.data
    assert "enabled" in result.data
    assert "minimized" in result.data
    assert "foreground" in result.data


@pytest.mark.asyncio
async def test_validation_errors(mock_computer_tool):
    """Test parameter validation errors."""
    # Missing required parameter
    result = await mock_computer_tool.execute({
        "action": "mouse_move"
        # Missing required 'coordinate' parameter
    })
    assert result.success is False
    assert result.error is not None
    
    # Invalid action
    result = await mock_computer_tool.execute({
        "action": "invalid_action"
    })
    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_disable_scaling(mock_computer_tool):
    """Test with scaling disabled."""
    # Disable scaling
    mock_computer_tool.enable_scaling = False
    
    # Test mouse movement with scaling disabled
    with patch('pyautogui.moveTo') as mock_move:
        result = await mock_computer_tool.execute({
            "action": "mouse_move",
            "coordinate": [500, 300]
        })
        
        # Verify result
        assert result.success is True
        
        # With scaling disabled, coordinates should pass through unchanged (except for offset)
        mock_move.assert_called_once()
        args, _ = mock_move.call_args
        assert args[0] == 500 + mock_computer_tool.offset_x
        assert args[1] == 300 + mock_computer_tool.offset_y
