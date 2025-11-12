#!/usr/bin/env python3
"""
Unit tests for VMNotificationException class
"""
import unittest
from vmnotification_exception import VMNotificationException


class TestVMNotificationException(unittest.TestCase):
    """Test cases for VMNotificationException"""

    def test_exception_creation(self):
        """Test creating exception with message"""
        msg = "Test error message"
        exception = VMNotificationException(msg)
        
        self.assertEqual(str(exception), msg)

    def test_exception_inheritance(self):
        """Test that VMNotificationException inherits from Exception"""
        exception = VMNotificationException("test")
        
        self.assertIsInstance(exception, Exception)
        self.assertIsInstance(exception, VMNotificationException)

    def test_exception_can_be_raised(self):
        """Test that exception can be raised and caught"""
        msg = "Test exception"
        
        with self.assertRaises(VMNotificationException) as context:
            raise VMNotificationException(msg)
        
        self.assertEqual(str(context.exception), msg)

    def test_exception_with_empty_message(self):
        """Test exception with empty message"""
        exception = VMNotificationException("")
        
        self.assertEqual(str(exception), "")

    def test_exception_with_special_characters(self):
        """Test exception with special characters"""
        msg = "Error: Failed to connect! @#$%^&*()"
        exception = VMNotificationException(msg)
        
        self.assertEqual(str(exception), msg)

    def test_exception_in_try_except(self):
        """Test exception handling in try-except block"""
        msg = "Caught exception"
        caught = False
        
        try:
            raise VMNotificationException(msg)
        except VMNotificationException as e:
            caught = True
            self.assertEqual(str(e), msg)
        
        self.assertTrue(caught)

    def test_exception_can_be_caught_as_base_exception(self):
        """Test that VMNotificationException can be caught as Exception"""
        msg = "Base exception test"
        caught = False
        
        try:
            raise VMNotificationException(msg)
        except Exception as e:
            caught = True
            self.assertIsInstance(e, VMNotificationException)
            self.assertEqual(str(e), msg)
        
        self.assertTrue(caught)


if __name__ == '__main__':
    unittest.main()

