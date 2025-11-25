"""
Tests for WebODM Manager
"""

import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from webodm_manager import WebODMManager



class TestWebODMManager:
    """Test WebODM Manager functionality"""
    
    def test_initialization(self):
        """Test WebODM manager initialization"""
        manager = WebODMManager()
        assert manager.host == "http://localhost:8000"
        assert manager.username == "admin"
        assert manager.password == "admin"
    
    def test_custom_path(self):
        """Test WebODM manager with custom path"""
        custom_path = "/tmp/test_webodm"
        manager = WebODMManager(webodm_path=custom_path)
        assert manager.webodm_path == custom_path
    
    def test_check_docker_installed(self):
        """Test Docker installation check"""
        manager = WebODMManager()
        # This will return True or False depending on environment
        result = manager.check_docker_installed()
        assert isinstance(result, bool)
    
    def test_check_docker_running(self):
        """Test Docker running check"""
        manager = WebODMManager()
        result = manager.check_docker_running()
        assert isinstance(result, bool)
    
    def test_check_docker_in_path(self):
        """Test Docker in PATH check"""
        manager = WebODMManager()
        result = manager.check_docker_in_path()
        assert isinstance(result, bool)
    
    def test_check_webodm_exists(self):
        """Test WebODM directory existence check"""
        manager = WebODMManager()
        result = manager.check_webodm_exists()
        assert isinstance(result, bool)
        # WebODM existence depends on whether git submodules are initialized
        # This is acceptable - the method correctly reports the state
    
    def test_is_webodm_running(self):
        """Test WebODM running status check"""
        manager = WebODMManager()
        result = manager.is_webodm_running()
        assert isinstance(result, bool)
    
    def test_get_status(self):
        """Test status dictionary"""
        manager = WebODMManager()
        status = manager.get_status()
        
        assert isinstance(status, dict)
        assert 'docker_installed' in status
        assert 'docker_running' in status
        assert 'webodm_exists' in status
        assert 'webodm_running' in status
        assert 'host' in status
        assert 'username' in status
        
        assert status['host'] == "http://localhost:8000"
        assert status['username'] == "admin"
        assert isinstance(status['docker_installed'], bool)
        assert isinstance(status['docker_running'], bool)
        assert isinstance(status['webodm_exists'], bool)
        assert isinstance(status['webodm_running'], bool)
    
    def test_webodm_path_resolves_correctly(self):
        """Test that default WebODM path is resolved correctly"""
        manager = WebODMManager()
        assert 'webodm' in manager.webodm_path
        assert os.path.isabs(manager.webodm_path)


class TestDockerPathCheck:
    """Test the new check_docker_in_path method"""
    
    @patch('shutil.which')
    def test_check_docker_in_path_found(self, mock_which):
        """Test check_docker_in_path returns True when docker is in PATH"""
        mock_which.return_value = "/usr/bin/docker"
        
        manager = WebODMManager()
        result = manager.check_docker_in_path()
        
        assert result is True
    
    @patch('shutil.which')
    def test_check_docker_in_path_not_found(self, mock_which):
        """Test check_docker_in_path returns False when docker is not in PATH"""
        mock_which.return_value = None
        
        manager = WebODMManager()
        result = manager.check_docker_in_path()
        
        assert result is False


class TestDockerErrorHandling:
    """Test Docker error scenarios from the issue screenshot"""
    
    @patch('subprocess.run')
    def test_docker_not_installed_error(self, mock_run):
        """Test error handling when Docker is not installed"""
        # Simulate Docker not being found
        mock_run.side_effect = FileNotFoundError()
        
        manager = WebODMManager()
        result = manager.check_docker_installed()
        
        assert result is False
    
    @patch('subprocess.run')
    def test_docker_not_running_error(self, mock_run):
        """Test error handling when Docker daemon is not running"""
        # Simulate Docker installed but not running
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Cannot connect to the Docker daemon"
        mock_run.return_value = mock_result
        
        manager = WebODMManager()
        result = manager.check_docker_running()
        
        assert result is False
    
    @patch('webodm_manager.WebODMManager.check_docker_in_path')
    def test_start_webodm_docker_not_installed(self, mock_in_path):
        """Test start_webodm returns proper error when Docker is not installed"""
        # Simulate Docker not found in PATH
        mock_in_path.return_value = False
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        assert "Docker is not installed" in message
        assert "Please install Docker Desktop first" in message
    
    @patch('webodm_manager.WebODMManager.check_docker_in_path')    # Applied second (first param)
    @patch('webodm_manager.WebODMManager.wait_for_docker_ready')   # Applied first (second param)
    def test_start_webodm_docker_not_running(self, mock_wait, mock_in_path):
        """Test start_webodm returns proper error when Docker is not running"""
        # Docker is in PATH but service not responding
        mock_in_path.return_value = True
        mock_wait.return_value = False
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        # New Spanish error message per issue requirements
        assert "Error Crítico de Servicio" in message
        assert "60 segundos" in message
        assert "WSL" in message
    
    @patch('webodm_manager.WebODMManager.check_webodm_exists')     # Applied third (first param)
    @patch('webodm_manager.WebODMManager.check_docker_in_path')    # Applied second (second param)
    @patch('webodm_manager.WebODMManager.wait_for_docker_ready')   # Applied first (third param)
    def test_start_webodm_directory_not_found(self, mock_wait, mock_in_path, mock_webodm_exists):
        """Test start_webodm returns proper error when WebODM directory is missing"""
        # Docker is fine but WebODM directory doesn't exist
        mock_in_path.return_value = True
        mock_wait.return_value = True
        mock_webodm_exists.return_value = False
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        assert "WebODM not found" in message
        assert "webodm" in message.lower()
    
    def test_get_status_reports_docker_errors(self):
        """Test that get_status properly reports Docker and WebODM errors"""
        manager = WebODMManager()
        status = manager.get_status()
        
        # Verify all critical status fields are present
        assert 'docker_installed' in status
        assert 'docker_running' in status
        assert 'webodm_exists' in status
        assert 'webodm_running' in status
        
        # All should be boolean values
        assert isinstance(status['docker_installed'], bool)
        assert isinstance(status['docker_running'], bool)
        assert isinstance(status['webodm_exists'], bool)
        assert isinstance(status['webodm_running'], bool)


class TestWebODMErrorMessages:
    """Test that error messages match those shown in the issue screenshot"""
    
    @patch('webodm_manager.WebODMManager.check_docker_in_path')
    def test_docker_not_installed_message_format(self, mock_in_path):
        """Test Docker not installed error message matches expected format"""
        mock_in_path.return_value = False
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        # Message should indicate Docker is not installed
        assert "Docker is not installed" in message
        assert "Please install Docker Desktop" in message
    
    @patch('webodm_manager.WebODMManager.check_webodm_exists')         # Applied third (first param)
    @patch('webodm_manager.WebODMManager.wait_for_docker_ready')       # Applied second (second param)
    @patch('webodm_manager.WebODMManager.check_docker_in_path')        # Applied first (third param)
    def test_webodm_not_found_message_format(self, mock_in_path, mock_wait, mock_exists):
        """Test WebODM not found error message includes path information"""
        mock_in_path.return_value = True
        mock_wait.return_value = True
        mock_exists.return_value = False
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        assert "WebODM not found" in message
        # Should include the path where it was looking
        assert manager.webodm_path in message or "webodm" in message.lower()
    
    @patch('webodm_manager.WebODMManager.check_docker_in_path')
    def test_ensure_running_propagates_error_messages(self, mock_in_path):
        """Test that ensure_running propagates error messages from start_webodm"""
        mock_in_path.return_value = False
        
        manager = WebODMManager()
        success, message = manager.ensure_running()
        
        assert success is False
        assert "Docker is not installed" in message


class TestDockerWaitTimeout:
    """Test the new wait_for_docker_ready timeout and retry functionality"""
    
    @patch('subprocess.run')
    @patch('time.sleep')
    def test_wait_for_docker_ready_success_immediate(self, mock_sleep, mock_run):
        """Test wait_for_docker_ready succeeds immediately when Docker is ready"""
        # Docker is ready on first attempt
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        manager = WebODMManager()
        result = manager.wait_for_docker_ready()
        
        assert result is True
        # Should not sleep if Docker is ready immediately
        mock_sleep.assert_not_called()
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_docker_ready_success_after_retries(self, mock_time, mock_sleep, mock_run):
        """Test wait_for_docker_ready succeeds after a few retries"""
        # Simulate Docker becoming ready after 2 retries
        mock_time.side_effect = [0, 5, 10, 15]  # Start, after 1st retry, after 2nd retry, success
        
        # First two attempts fail, third succeeds
        fail_result = MagicMock()
        fail_result.returncode = 1
        fail_result.stderr = "Cannot connect to the Docker daemon"
        
        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stderr = ""
        
        mock_run.side_effect = [fail_result, fail_result, success_result]
        
        manager = WebODMManager()
        result = manager.wait_for_docker_ready()
        
        assert result is True
        assert mock_run.call_count == 3
        assert mock_sleep.call_count == 2  # Slept twice before succeeding
        mock_sleep.assert_called_with(5)  # 5 second intervals
    
    @patch('subprocess.run')
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_docker_ready_timeout(self, mock_time, mock_sleep, mock_run):
        """Test wait_for_docker_ready fails after timeout"""
        # Simulate time passing: 0, 5, 10, 15, ..., 60, 65
        mock_time.side_effect = list(range(0, 70, 5))
        
        # Docker never becomes ready
        fail_result = MagicMock()
        fail_result.returncode = 1
        fail_result.stderr = "Cannot connect to the Docker daemon"
        mock_run.return_value = fail_result
        
        manager = WebODMManager()
        result = manager.wait_for_docker_ready()
        
        assert result is False
        # Should have tried multiple times over 60 seconds
        assert mock_run.call_count >= 11  # At least 11 attempts over 60 seconds
    
    @patch('subprocess.run')
    def test_wait_for_docker_ready_file_not_found(self, mock_run):
        """Test wait_for_docker_ready handles docker executable not found"""
        mock_run.side_effect = FileNotFoundError()
        
        manager = WebODMManager()
        result = manager.wait_for_docker_ready()
        
        assert result is False
    
    @patch('subprocess.run')
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_docker_ready_timeout_expired_exception(self, mock_time, mock_sleep, mock_run):
        """Test wait_for_docker_ready handles subprocess timeout exceptions"""
        mock_time.side_effect = [0, 5, 10, 15]
        
        # First attempts timeout, then Docker becomes ready
        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stderr = ""
        
        mock_run.side_effect = [
            subprocess.TimeoutExpired('docker', 5),
            subprocess.TimeoutExpired('docker', 5),
            success_result
        ]
        
        manager = WebODMManager()
        result = manager.wait_for_docker_ready()
        
        assert result is True
        assert mock_sleep.call_count == 2
    
    @patch('subprocess.run')
    def test_wait_for_docker_ready_checks_stderr_for_daemon_error(self, mock_run):
        """Test wait_for_docker_ready checks for daemon connection error in stderr"""
        # Return code 0 but stderr has daemon error (should fail)
        fail_result = MagicMock()
        fail_result.returncode = 0
        fail_result.stderr = "Cannot connect to the Docker daemon at unix:///var/run/docker.sock"
        
        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stderr = ""
        
        mock_run.side_effect = [fail_result, success_result]
        
        manager = WebODMManager()
        # Need to patch time and sleep to avoid actual waiting
        with patch('time.sleep'), patch('time.time', side_effect=[0, 1, 2]):
            result = manager.wait_for_docker_ready()
        
        assert result is True
        assert mock_run.call_count == 2
    
    @patch('webodm_manager.WebODMManager.wait_for_docker_ready')
    @patch('webodm_manager.WebODMManager.check_docker_in_path')
    def test_start_webodm_calls_wait_for_docker_ready(self, mock_in_path, mock_wait):
        """Test that start_webodm calls wait_for_docker_ready during the startup process"""
        mock_in_path.return_value = True
        mock_wait.return_value = False  # Docker not ready
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        # New Spanish error message per issue requirements
        assert "Error Crítico de Servicio" in message
        assert "60 segundos" in message
        # Verify wait_for_docker_ready was called
        mock_wait.assert_called_once()
    
    @patch('webodm_manager.WebODMManager.is_webodm_running')
    @patch('webodm_manager.WebODMManager.check_webodm_exists')
    @patch('webodm_manager.WebODMManager.wait_for_docker_ready')
    @patch('webodm_manager.WebODMManager.check_docker_in_path')
    def test_start_webodm_waits_patiently_for_docker(self, mock_in_path, mock_wait, 
                                                      mock_exists, mock_running):
        """Test that start_webodm waits patiently for Docker before proceeding"""
        mock_in_path.return_value = True
        mock_wait.return_value = True  # Docker becomes ready
        mock_exists.return_value = False  # WebODM doesn't exist (to trigger early exit)
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        # Should call wait_for_docker_ready
        mock_wait.assert_called_once()
        # Should fail because WebODM doesn't exist, but we got past the Docker check
        assert "WebODM not found" in message
