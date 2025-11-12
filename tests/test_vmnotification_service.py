#!/usr/bin/env python3
"""
Unit tests for VMNotificationService class
"""
import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from vmnotification_service import VMNotificationService
from vmnotification_exception import VMNotificationException


class TestVMNotificationService(unittest.TestCase):
    """Test cases for VMNotificationService"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.token_file = os.path.join(self.temp_dir, "token_file")
        
        self.service = VMNotificationService(
            pre_vmotion_cmd="echo pre",
            post_vmotion_cmd="echo post",
            token_file=self.token_file,
            app_name="test_app",
            check_interval_seconds=1,
            token_file_create=True,
            token_obfuscate_logfile=False
        )

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        os.rmdir(self.temp_dir)

    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.service.pre_vmotion_cmd, "echo pre")
        self.assertEqual(self.service.post_vmotion_cmd, "echo post")
        self.assertEqual(self.service.token_file, self.token_file)
        self.assertEqual(self.service.app_name, "test_app")
        self.assertEqual(self.service.check_interval_seconds, 1)
        self.assertTrue(self.service.token_file_create)
        self.assertFalse(self.service.token_obfuscate_logfile)

    def test_command_splitting(self):
        """Test that commands are properly split"""
        service = VMNotificationService(
            pre_vmotion_cmd="echo 'hello world'",
            post_vmotion_cmd="ls -la /tmp",
            token_file=self.token_file
        )
        self.assertEqual(service.pre_vmotion_cmd_split, ["echo", "hello world"])
        self.assertEqual(service.post_vmotion_cmd_split, ["ls", "-la", "/tmp"])

    def test_write_token(self):
        """Test token writing to file"""
        test_token = "test-token-12345"
        self.service._VMNotificationService__token = test_token
        
        self.service.write_token()
        
        self.assertTrue(os.path.exists(self.token_file))
        with open(self.token_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, test_token)

    def test_read_token(self):
        """Test token reading from file"""
        test_token = "test-token-67890"
        with open(self.token_file, 'w') as f:
            f.write(test_token)
        
        self.service.read_token()
        
        self.assertEqual(self.service._VMNotificationService__token, test_token)

    def test_read_token_file_not_found(self):
        """Test reading token when file doesn't exist"""
        # Should not raise exception
        self.service.read_token()
        self.assertIsNone(self.service._VMNotificationService__token)

    def test_delete_token(self):
        """Test token deletion"""
        # Create token file
        with open(self.token_file, 'w') as f:
            f.write("test-token")
        
        self.assertTrue(os.path.exists(self.token_file))
        self.service.delete_token()
        self.assertFalse(os.path.exists(self.token_file))

    def test_delete_token_file_not_found(self):
        """Test deleting token when file doesn't exist"""
        # Should not raise exception
        self.service.delete_token()

    def test_obfuscate_msg_disabled(self):
        """Test message obfuscation when disabled"""
        self.service.token_obfuscate_logfile = False
        self.service._VMNotificationService__token = "secret-token-123"
        
        msg = "Token: secret-token-123"
        result = self.service._obfuscate_msg(msg)
        
        self.assertEqual(result, msg)

    def test_obfuscate_msg_enabled(self):
        """Test message obfuscation when enabled"""
        self.service.token_obfuscate_logfile = True
        self.service._VMNotificationService__token = "secret-token-123"
        
        msg = "Token: secret-token-123"
        result = self.service._obfuscate_msg(msg)
        
        self.assertIn("secret-t", result)
        self.assertIn("****", result)
        self.assertNotIn("secret-token-123", result)

    def test_obfuscate_msg_no_token(self):
        """Test message obfuscation when no token is set"""
        self.service.token_obfuscate_logfile = True
        self.service._VMNotificationService__token = None
        
        msg = "Some message"
        result = self.service._obfuscate_msg(msg)
        
        self.assertEqual(result, msg)

    @patch('vmnotification_service.Popen')
    def test_run_rpc_success(self, mock_popen):
        """Test successful RPC call"""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            json.dumps({"result": True, "data": "success"}).encode(),
            None
        )
        mock_popen.return_value = mock_process
        
        params = {"test": "value"}
        result = self.service.run_rpc("test.command", params)
        
        self.assertTrue(result["result"])
        self.assertEqual(result["data"], "success")

    @patch('vmnotification_service.Popen')
    def test_run_rpc_failure(self, mock_popen):
        """Test failed RPC call"""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            json.dumps({"result": False, "errorMessage": "Test error"}).encode(),
            None
        )
        mock_popen.return_value = mock_process
        
        params = {"test": "value"}
        
        with self.assertRaises(VMNotificationException) as context:
            self.service.run_rpc("test.command", params)
        
        self.assertIn("Test error", str(context.exception))

    @patch('vmnotification_service.Popen')
    def test_run_rpc_none_params(self, mock_popen):
        """Test RPC call with None params"""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            json.dumps({"result": True}).encode(),
            None
        )
        mock_popen.return_value = mock_process
        
        result = self.service.run_rpc("test.command", None)
        
        self.assertTrue(result["result"])

    @patch('vmnotification_service.Popen')
    def test_register_for_notification_success(self, mock_popen):
        """Test successful registration"""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            json.dumps({"result": True, "uniqueToken": "token-123"}).encode(),
            None
        )
        mock_popen.return_value = mock_process
        
        token = self.service.register_for_notification()
        
        self.assertEqual(token, "token-123")

    @patch('vmnotification_service.Popen')
    def test_register_for_notification_no_token(self, mock_popen):
        """Test registration when no token is returned"""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            json.dumps({"result": True}).encode(),
            None
        )
        mock_popen.return_value = mock_process
        
        with self.assertRaises(VMNotificationException) as context:
            self.service.register_for_notification()
        
        self.assertIn("No token was returned", str(context.exception))

    @patch('vmnotification_service.Popen')
    def test_unregister_for_notification_with_token(self, mock_popen):
        """Test unregistration with token"""
        self.service._VMNotificationService__token = "token-123"
        
        mock_process = Mock()
        mock_process.communicate.return_value = (
            json.dumps({"result": True}).encode(),
            None
        )
        mock_popen.return_value = mock_process
        
        # Should not raise exception
        self.service.unregister_for_notification()

    def test_unregister_for_notification_no_token(self):
        """Test unregistration without token"""
        self.service._VMNotificationService__token = None
        
        # Should return early without error
        self.service.unregister_for_notification()

    @patch('vmnotification_service.Popen')
    def test_ack_event(self, mock_popen):
        """Test event acknowledgment"""
        self.service._VMNotificationService__token = "token-123"
        
        mock_process = Mock()
        mock_process.communicate.return_value = (
            json.dumps({"result": True}).encode(),
            None
        )
        mock_popen.return_value = mock_process
        
        # Should not raise exception
        self.service.ack_event("op-id-123")

    @patch('vmnotification_service.Popen')
    def test_run_pre_vmotion(self, mock_popen):
        """Test pre-vmotion command execution"""
        mock_process = Mock()
        mock_process.stdout = [b"output line 1\n", b"output line 2\n"]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Should not raise exception
        self.service.run_pre_vmotion()
        
        mock_popen.assert_called_once()
        mock_process.wait.assert_called_once()

    @patch('vmnotification_service.Popen')
    def test_run_post_vmotion(self, mock_popen):
        """Test post-vmotion command execution"""
        mock_process = Mock()
        mock_process.stdout = [b"output line 1\n", b"output line 2\n"]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Should not raise exception
        self.service.run_post_vmotion()
        
        mock_popen.assert_called_once()
        mock_process.wait.assert_called_once()

    def test_stop_sets_run_flag(self):
        """Test that stop() sets the run flag to False"""
        import signal
        self.service._VMNotificationService__run = True
        
        self.service.stop(signal.SIGTERM, None)
        
        self.assertFalse(self.service._VMNotificationService__run)


class TestVMNotificationServiceIntegration(unittest.TestCase):
    """Integration tests for VMNotificationService"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.token_file = os.path.join(self.temp_dir, "token_file")

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        os.rmdir(self.temp_dir)

    def test_token_lifecycle(self):
        """Test complete token lifecycle: write, read, delete"""
        service = VMNotificationService(
            pre_vmotion_cmd="echo test",
            post_vmotion_cmd="echo test",
            token_file=self.token_file,
            token_file_create=True
        )
        
        # Write token
        test_token = "lifecycle-token-123"
        service._VMNotificationService__token = test_token
        service.write_token()
        self.assertTrue(os.path.exists(self.token_file))
        
        # Read token
        service2 = VMNotificationService(
            pre_vmotion_cmd="echo test",
            post_vmotion_cmd="echo test",
            token_file=self.token_file
        )
        service2.read_token()
        self.assertEqual(service2._VMNotificationService__token, test_token)
        
        # Delete token
        service2.delete_token()
        self.assertFalse(os.path.exists(self.token_file))


if __name__ == '__main__':
    unittest.main()

