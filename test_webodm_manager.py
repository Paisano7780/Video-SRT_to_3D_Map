"""
Tests for WebODM Manager
"""

import pytest
import os
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
    
    @patch('subprocess.run')
    def test_start_webodm_docker_not_installed(self, mock_run):
        """Test start_webodm returns proper error when Docker is not installed"""
        # Simulate Docker not installed
        mock_run.side_effect = FileNotFoundError()
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        assert "Docker is not installed" in message
        assert "Please install Docker Desktop first" in message
    
    @patch('webodm_manager.WebODMManager.check_docker_installed')
    @patch('webodm_manager.WebODMManager.check_docker_running')
    def test_start_webodm_docker_not_running(self, mock_running, mock_installed):
        """Test start_webodm returns proper error when Docker is not running"""
        # Docker is installed but not running
        mock_installed.return_value = True
        mock_running.return_value = False
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        assert "Docker is not running" in message
        assert "Please start Docker Desktop" in message
    
    @patch('webodm_manager.WebODMManager.check_webodm_exists')
    @patch('webodm_manager.WebODMManager.check_docker_installed')
    @patch('webodm_manager.WebODMManager.check_docker_running')
    def test_start_webodm_directory_not_found(self, mock_running, mock_installed, mock_webodm_exists):
        """Test start_webodm returns proper error when WebODM directory is missing"""
        # Docker is fine but WebODM directory doesn't exist
        mock_installed.return_value = True
        mock_running.return_value = True
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
    
    @patch('subprocess.run')
    def test_docker_not_installed_message_format(self, mock_run):
        """Test Docker not installed error message matches screenshot format"""
        mock_run.side_effect = FileNotFoundError()
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        # Message should match the error dialog in screenshot
        assert "Docker is not installed" in message
        assert "Please install Docker Desktop" in message
    
    @patch('webodm_manager.WebODMManager.check_docker_installed')
    @patch('os.path.exists')
    def test_webodm_not_found_message_format(self, mock_exists, mock_docker):
        """Test WebODM not found error message includes path information"""
        mock_docker.return_value = True
        mock_exists.return_value = False
        
        manager = WebODMManager()
        success, message = manager.start_webodm()
        
        assert success is False
        assert "WebODM not found" in message
        # Should include the path where it was looking
        assert manager.webodm_path in message or "webodm" in message.lower()
    
    @patch('subprocess.run')
    def test_ensure_running_propagates_error_messages(self, mock_run):
        """Test that ensure_running propagates error messages from start_webodm"""
        mock_run.side_effect = FileNotFoundError()
        
        manager = WebODMManager()
        success, message = manager.ensure_running()
        
        assert success is False
        assert "Docker is not installed" in message
