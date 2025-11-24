"""
Tests for WebODM Manager
"""

import pytest
import os
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
        # In this repository, webodm should exist
        assert result is True
    
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
