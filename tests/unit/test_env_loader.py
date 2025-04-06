"""
Unit tests for the env_loader module.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path to allow importing src modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Import the module ONCE at the top level
import src.env_loader as env_loader

# Attempt to import dotenv to check if it's installed for skipping tests
try:
    import dotenv
    dotenv_installed = True
except ImportError:
    dotenv_installed = False

class TestEnvLoader(unittest.TestCase):
    """Tests for environment variable loading and retrieval."""

    def setUp(self):
        """Set up environment variables for tests."""
        self.original_environ = os.environ.copy()
        os.environ["TEST_STRING"] = "hello world"
        os.environ["TEST_INT"] = "123"
        os.environ["TEST_FLOAT"] = "45.67"
        os.environ["TEST_BOOL_TRUE"] = "true"
        os.environ["TEST_BOOL_FALSE"] = "FALSE"
        os.environ["TEST_BOOL_YES"] = "yes"
        os.environ["TEST_BOOL_1"] = "1"
        os.environ["TEST_LIST"] = "item1, item2, item3"
        os.environ["TEST_EMPTY"] = ""
        # Clear potentially conflicting vars
        if "TEST_DEFAULT" in os.environ:
            del os.environ["TEST_DEFAULT"]
        if "TEST_INVALID_INT" in os.environ:
             os.environ["TEST_INVALID_INT"] = "not-an-int"
        if "TEST_INVALID_FLOAT" in os.environ:
             os.environ["TEST_INVALID_FLOAT"] = "not-a-float"
        if "TEST_INVALID_BOOL" in os.environ:
             os.environ["TEST_INVALID_BOOL"] = "maybe"

    def tearDown(self):
        """Clean up environment variables."""
        os.environ.clear()
        os.environ.update(self.original_environ)

    @patch.dict(sys.modules, {'dotenv': None}) # Simulate dotenv not installed
    @patch('src.env_loader.logger') # Mock logger to suppress warnings if needed
    def test_load_dotenv_without_dotenv(self, mock_logger):
        """Test loading .env file when python-dotenv is not installed."""
        # We need to reload the module because the import attempt happens at module level
        import importlib
        importlib.reload(env_loader)
        # Call the function directly
        loaded = env_loader.load_dotenv()
        self.assertFalse(loaded)
        # Check if the warning was logged (optional)
        # mock_logger.warning.assert_called_with("python-dotenv not installed, skipping .env file loading")

    # Skip this test if dotenv is not actually installed
    @unittest.skipUnless(dotenv_installed, "python-dotenv not installed")
    @patch('dotenv.load_dotenv') # Patch the actual function if the test runs
    @patch('src.env_loader.logger')
    def test_load_dotenv_with_dotenv(self, mock_logger, mock_actual_dotenv_load):
        """Test loading .env file when python-dotenv is installed."""
        # Reload env_loader to ensure it attempts the import within the test context
        # (This might be needed depending on how env_loader handles the optional import)
        import importlib
        importlib.reload(env_loader)

        # Simulate .env file found and loaded
        mock_actual_dotenv_load.return_value = True
        loaded = env_loader.load_dotenv(path=".env")
        self.assertTrue(loaded)
        mock_actual_dotenv_load.assert_called_once_with(dotenv_path=".env")
        # mock_logger.info.assert_called_with("Loaded environment variables from .env")

        # Simulate .env file not found
        mock_actual_dotenv_load.reset_mock()
        mock_logger.reset_mock()
        mock_actual_dotenv_load.return_value = False
        loaded = env_loader.load_dotenv(path=".env")
        self.assertFalse(loaded)
        mock_actual_dotenv_load.assert_called_once_with(dotenv_path=".env")
        # mock_logger.warning.assert_called_with("No .env file found at .env")

    # Removed the complex/redundant test_load_dotenv_with_dotenv_import_patch

    # Removed the duplicate/erroneous test_get_env_string method

    def test_get_env_string(self):
        """Test retrieving string environment variables using get_env."""
        self.assertEqual(env_loader.get_env("TEST_STRING"), "hello world")
        self.assertEqual(env_loader.get_env("TEST_EMPTY"), "")
        self.assertEqual(env_loader.get_env("TEST_DEFAULT", default="default_val"), "default_val")
        self.assertIsNone(env_loader.get_env("NON_EXISTENT")) # Test non-existent without default
        self.assertEqual(env_loader.get_env("NON_EXISTENT", default="fallback"), "fallback") # Test non-existent with default

    def test_get_env_int(self):
        """Test retrieving integer environment variables using get_env_int."""
        self.assertEqual(env_loader.get_env_int("TEST_INT"), 123)
        self.assertEqual(env_loader.get_env_int("TEST_DEFAULT", default=999), 999)
        self.assertIsNone(env_loader.get_env_int("NON_EXISTENT"))
        # Test invalid conversion - should return default
        self.assertEqual(env_loader.get_env_int("TEST_INVALID_INT", default=0), 0)

    def test_get_env_float(self):
        """Test retrieving float environment variables using get_env_float."""
        self.assertAlmostEqual(env_loader.get_env_float("TEST_FLOAT"), 45.67)
        self.assertAlmostEqual(env_loader.get_env_float("TEST_DEFAULT", default=1.23), 1.23)
        self.assertIsNone(env_loader.get_env_float("NON_EXISTENT"))
        # Test invalid conversion - should return default
        self.assertAlmostEqual(env_loader.get_env_float("TEST_INVALID_FLOAT", default=0.0), 0.0)

    def test_get_env_bool(self):
        """Test retrieving boolean environment variables using get_env_bool."""
        self.assertTrue(env_loader.get_env_bool("TEST_BOOL_TRUE"))
        self.assertFalse(env_loader.get_env_bool("TEST_BOOL_FALSE"))
        self.assertTrue(env_loader.get_env_bool("TEST_BOOL_YES"))
        self.assertTrue(env_loader.get_env_bool("TEST_BOOL_1"))
        self.assertFalse(env_loader.get_env_bool("TEST_EMPTY")) # Empty string should evaluate to False
        self.assertTrue(env_loader.get_env_bool("TEST_DEFAULT", default=True))
        self.assertFalse(env_loader.get_env_bool("TEST_DEFAULT", default=False)) # Test default False when var missing
        self.assertFalse(env_loader.get_env_bool("NON_EXISTENT")) # Default is False
        self.assertTrue(env_loader.get_env_bool("NON_EXISTENT", default=True)) # Test default True
         # Test invalid conversion - should evaluate to False based on ('true', 'yes', '1', 't', 'y') check
        self.assertFalse(env_loader.get_env_bool("TEST_INVALID_BOOL"))
        self.assertTrue(env_loader.get_env_bool("TEST_INVALID_BOOL", default=True)) # Should return default

    def test_get_env_list(self):
        """Test retrieving list environment variables using get_env_list."""
        expected_list = ["item1", "item2", "item3"]
        self.assertEqual(env_loader.get_env_list("TEST_LIST"), expected_list)
        self.assertEqual(env_loader.get_env_list("TEST_EMPTY"), []) # Empty string should become empty list
        self.assertEqual(env_loader.get_env_list("TEST_DEFAULT", default=["a", "b"]), ["a", "b"])
        self.assertEqual(env_loader.get_env_list("NON_EXISTENT"), []) # Default is empty list
        self.assertEqual(env_loader.get_env_list("NON_EXISTENT", default=['x']), ['x']) # Test default list
        # Test list with spaces
        os.environ["TEST_LIST_SPACES"] = " item 1 , item 2  ,item 3 "
        expected_list_spaces = ["item 1", "item 2", "item 3"]
        self.assertEqual(env_loader.get_env_list("TEST_LIST_SPACES"), expected_list_spaces)


if __name__ == '__main__':
    unittest.main()
