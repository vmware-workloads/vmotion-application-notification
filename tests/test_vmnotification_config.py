#!/usr/bin/env python3
"""
Unit tests for VMNotificationConfig class
"""
import unittest
import tempfile
import os
from pathlib import Path
from vmnotification_config import VMNotificationConfig


class TestVMNotificationConfig(unittest.TestCase):
    """Test cases for VMNotificationConfig"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.conf")
        
        # Write a test configuration
        with open(self.config_file, 'w') as f:
            f.write("""[DEFAULT]
app_name = test_app
check_interval_seconds = 2
pre_vmotion_cmd = echo pre
post_vmotion_cmd = echo post

[Token]
token_file = /tmp/test_token
token_file_create = yes
token_obfuscate_logfile = no

[Logging]
service_logfile = /tmp/service.log
service_logfile_level = INFO
service_console_level = ERROR
service_logfile_maxsize_bytes = 2048
service_logfile_count = 5
vmotion_logfile = /tmp/vmotion.log
vmotion_logfile_maxsize_bytes = 2048
vmotion_logfile_count = 3
timeout_logfile = /tmp/timeout.log
timeout_logfile_maxsize_bytes = 2048
timeout_logfile_count = 3
""")

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)

    def test_config_file_loading(self):
        """Test that config file is loaded correctly"""
        config = VMNotificationConfig(self.config_file)
        self.assertEqual(config.app_name, "test_app")
        self.assertEqual(config.check_interval_seconds, 2)
        self.assertEqual(config.pre_vmotion_cmd, "echo pre")
        self.assertEqual(config.post_vmotion_cmd, "echo post")

    def test_token_section(self):
        """Test token configuration"""
        config = VMNotificationConfig(self.config_file)
        self.assertEqual(config.token_file, "/tmp/test_token")
        self.assertTrue(config.token_file_create)
        self.assertFalse(config.token_obfuscate_logfile)

    def test_logging_section(self):
        """Test logging configuration"""
        config = VMNotificationConfig(self.config_file)
        self.assertEqual(config.service_logfile, "/tmp/service.log")
        self.assertEqual(config.service_logfile_level, "INFO")
        self.assertEqual(config.service_console_level, "ERROR")
        self.assertEqual(config.service_logfile_maxsize_bytes, 2048)
        self.assertEqual(config.service_logfile_count, 5)

    def test_vmotion_logging_section(self):
        """Test vmotion logging configuration"""
        config = VMNotificationConfig(self.config_file)
        self.assertEqual(config.vmotion_logfile, "/tmp/vmotion.log")
        self.assertEqual(config.vmotion_logfile_maxsize_bytes, 2048)
        self.assertEqual(config.vmotion_logfile_count, 3)

    def test_timeout_logging_section(self):
        """Test timeout logging configuration"""
        config = VMNotificationConfig(self.config_file)
        self.assertEqual(config.timeout_logfile, "/tmp/timeout.log")
        self.assertEqual(config.timeout_logfile_maxsize_bytes, 2048)
        self.assertEqual(config.timeout_logfile_count, 3)

    def test_json_method(self):
        """Test json() method returns all config values"""
        config = VMNotificationConfig(self.config_file)
        json_data = config.json()
        
        self.assertIn("app_name", json_data)
        self.assertIn("check_interval_seconds", json_data)
        self.assertIn("pre_vmotion_cmd", json_data)
        self.assertIn("post_vmotion_cmd", json_data)
        self.assertIn("token_file", json_data)
        self.assertIn("timeout_logfile", json_data)
        self.assertIn("timeout_logfile_maxsize_bytes", json_data)
        self.assertIn("timeout_logfile_count", json_data)

    def test_app_name_validation_empty_string(self):
        """Test app_name validation rejects empty string"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.app_name = ""
        self.assertIn("at least 1 character", str(context.exception))

    def test_app_name_validation_non_string(self):
        """Test app_name validation rejects non-string"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.app_name = 123
        self.assertIn("must be a string", str(context.exception))

    def test_check_interval_validation_non_integer(self):
        """Test check_interval_seconds validation rejects non-integer"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.check_interval_seconds = "not_an_int"
        self.assertIn("must be an integer", str(context.exception))

    def test_check_interval_validation_zero(self):
        """Test check_interval_seconds validation rejects zero"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.check_interval_seconds = 0
        self.assertIn("greater than 0", str(context.exception))

    def test_token_file_create_validation(self):
        """Test token_file_create validation rejects non-boolean"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.token_file_create = "yes"
        self.assertIn("must be a boolean", str(context.exception))

    def test_token_obfuscate_logfile_validation(self):
        """Test token_obfuscate_logfile validation rejects non-boolean"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.token_obfuscate_logfile = "no"
        self.assertIn("must be a boolean", str(context.exception))

    def test_service_logfile_maxsize_validation_too_small(self):
        """Test service_logfile_maxsize_bytes validation rejects values < 1024"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.service_logfile_maxsize_bytes = 512
        self.assertIn("greater than or equal to 1024", str(context.exception))

    def test_service_logfile_maxsize_validation_non_integer(self):
        """Test service_logfile_maxsize_bytes validation rejects non-integer"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.service_logfile_maxsize_bytes = "2048"
        self.assertIn("must be an integer", str(context.exception))

    def test_service_logfile_count_validation_too_small(self):
        """Test service_logfile_count validation rejects values < 2"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.service_logfile_count = 1
        self.assertIn("greater than 1", str(context.exception))

    def test_service_logfile_count_validation_non_integer(self):
        """Test service_logfile_count validation rejects non-integer"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.service_logfile_count = "5"
        self.assertIn("must be an integer", str(context.exception))

    def test_vmotion_logfile_validation_empty_string(self):
        """Test vmotion_logfile validation rejects empty string"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.vmotion_logfile = ""
        self.assertIn("at least 1 character", str(context.exception))

    def test_timeout_logfile_validation_empty_string(self):
        """Test timeout_logfile validation rejects empty string"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.timeout_logfile = ""
        self.assertIn("at least 1 character", str(context.exception))

    def test_timeout_logfile_maxsize_validation(self):
        """Test timeout_logfile_maxsize_bytes validation"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.timeout_logfile_maxsize_bytes = 100
        self.assertIn("greater than or equal to 1024", str(context.exception))

    def test_timeout_logfile_count_validation(self):
        """Test timeout_logfile_count validation"""
        config = VMNotificationConfig(self.config_file)
        with self.assertRaises(ValueError) as context:
            config.timeout_logfile_count = 1
        self.assertIn("greater than 1", str(context.exception))

    def test_default_values(self):
        """Test that default values are used when config sections are missing"""
        # Create minimal config file
        minimal_config = os.path.join(self.temp_dir, "minimal.conf")
        with open(minimal_config, 'w') as f:
            f.write("""[DEFAULT]
pre_vmotion_cmd = echo pre
post_vmotion_cmd = echo post
""")
        
        config = VMNotificationConfig(minimal_config)
        self.assertEqual(config.app_name, "my_app")
        self.assertEqual(config.check_interval_seconds, 1)
        self.assertEqual(config.token_file, "/var/run/vmnotification/token_file")
        
        os.remove(minimal_config)

    def test_valid_property_assignments(self):
        """Test that valid property assignments work correctly"""
        config = VMNotificationConfig(self.config_file)
        
        # Test valid assignments
        config.app_name = "new_app"
        self.assertEqual(config.app_name, "new_app")
        
        config.check_interval_seconds = 5
        self.assertEqual(config.check_interval_seconds, 5)
        
        config.token_file_create = False
        self.assertFalse(config.token_file_create)
        
        config.service_logfile_maxsize_bytes = 4096
        self.assertEqual(config.service_logfile_maxsize_bytes, 4096)
        
        config.service_logfile_count = 10
        self.assertEqual(config.service_logfile_count, 10)


if __name__ == '__main__':
    unittest.main()

