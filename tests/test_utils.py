#!/usr/bin/env python3
"""
Unit tests for utility functions
"""
import unittest
import tempfile
import os
import logging
from pathlib import Path
from utils import get_logging_level, create_folders


class TestGetLoggingLevel(unittest.TestCase):
    """Test cases for get_logging_level function"""

    def test_info_level(self):
        """Test INFO level"""
        self.assertEqual(get_logging_level("INFO"), logging.INFO)
        self.assertEqual(get_logging_level("info"), logging.INFO)
        self.assertEqual(get_logging_level("InFo"), logging.INFO)

    def test_debug_level(self):
        """Test DEBUG level"""
        self.assertEqual(get_logging_level("DEBUG"), logging.DEBUG)
        self.assertEqual(get_logging_level("debug"), logging.DEBUG)

    def test_warning_level(self):
        """Test WARNING level"""
        self.assertEqual(get_logging_level("WARNING"), logging.WARNING)
        self.assertEqual(get_logging_level("warning"), logging.WARNING)

    def test_error_level(self):
        """Test ERROR level"""
        self.assertEqual(get_logging_level("ERROR"), logging.ERROR)
        self.assertEqual(get_logging_level("error"), logging.ERROR)

    def test_critical_level(self):
        """Test CRITICAL level"""
        self.assertEqual(get_logging_level("CRITICAL"), logging.CRITICAL)
        self.assertEqual(get_logging_level("critical"), logging.CRITICAL)

    def test_invalid_level(self):
        """Test invalid level returns default (DEBUG)"""
        self.assertEqual(get_logging_level("INVALID"), logging.DEBUG)
        self.assertEqual(get_logging_level(""), logging.DEBUG)
        self.assertEqual(get_logging_level("random"), logging.DEBUG)

    def test_non_string_input(self):
        """Test non-string input returns default (DEBUG)"""
        self.assertEqual(get_logging_level(123), logging.DEBUG)
        self.assertEqual(get_logging_level(None), logging.DEBUG)
        self.assertEqual(get_logging_level([]), logging.DEBUG)


class TestCreateFolders(unittest.TestCase):
    """Test cases for create_folders function"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up any created directories
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_single_folder(self):
        """Test creating a single folder"""
        test_path = os.path.join(self.temp_dir, "test_folder", "test_file.txt")
        result = create_folders(test_path)
        
        self.assertIsInstance(result, Path)
        self.assertTrue(os.path.exists(os.path.dirname(test_path)))

    def test_create_nested_folders(self):
        """Test creating nested folders"""
        test_path = os.path.join(self.temp_dir, "level1", "level2", "level3", "file.log")
        result = create_folders(test_path)
        
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "level1", "level2", "level3")))

    def test_create_folders_with_path_object(self):
        """Test creating folders with Path object"""
        test_path = Path(self.temp_dir) / "test" / "file.txt"
        result = create_folders(test_path)
        
        self.assertIsInstance(result, Path)
        self.assertTrue(test_path.parent.exists())

    def test_create_folders_already_exists(self):
        """Test creating folders when they already exist"""
        test_path = os.path.join(self.temp_dir, "existing", "file.txt")
        
        # Create first time
        create_folders(test_path)
        
        # Create again - should not raise exception
        result = create_folders(test_path)
        self.assertIsInstance(result, Path)

    def test_create_folders_returns_path(self):
        """Test that create_folders returns a Path object"""
        test_path = os.path.join(self.temp_dir, "test", "file.txt")
        result = create_folders(test_path)
        
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), test_path)

    def test_create_folders_string_input(self):
        """Test create_folders with string input"""
        test_path = os.path.join(self.temp_dir, "string_test", "file.log")
        result = create_folders(test_path)
        
        self.assertTrue(os.path.exists(os.path.dirname(test_path)))

    def test_create_folders_permission_error(self):
        """Test create_folders with permission error"""
        # Try to create folder in a protected location (should fail without sudo)
        if os.name != 'nt':  # Skip on Windows
            # On macOS/Linux, try to create in a system directory
            # macOS: /private/var/root is root's home and requires elevated permissions
            # Linux: /root is root's home
            import platform
            if platform.system() == 'Darwin':  # macOS
                test_path = "/private/var/root/test_vmnotification/file.txt"
            else:  # Linux
                test_path = "/root/test_vmnotification/file.txt"
            
            with self.assertRaises(SystemExit) as context:
                create_folders(test_path)
            self.assertEqual(context.exception.code, 1)


class TestUtilsIntegration(unittest.TestCase):
    """Integration tests for utility functions"""

    def test_logging_levels_are_distinct(self):
        """Test that all logging levels are distinct"""
        levels = [
            get_logging_level("DEBUG"),
            get_logging_level("INFO"),
            get_logging_level("WARNING"),
            get_logging_level("ERROR"),
            get_logging_level("CRITICAL")
        ]
        
        # All levels should be different
        self.assertEqual(len(levels), len(set(levels)))

    def test_logging_levels_are_ordered(self):
        """Test that logging levels are properly ordered"""
        debug = get_logging_level("DEBUG")
        info = get_logging_level("INFO")
        warning = get_logging_level("WARNING")
        error = get_logging_level("ERROR")
        critical = get_logging_level("CRITICAL")
        
        self.assertLess(debug, info)
        self.assertLess(info, warning)
        self.assertLess(warning, error)
        self.assertLess(error, critical)


if __name__ == '__main__':
    unittest.main()

