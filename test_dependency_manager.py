"""
Unit Tests for Dependency Manager
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Skip tests on non-Windows platforms
pytestmark = pytest.mark.skipif(
    sys.platform != 'win32',
    reason="Dependency manager is Windows-specific"
)


def test_import_dependency_manager():
    """Test that dependency_manager module can be imported"""
    from dependency_manager import DependencyManager
    assert DependencyManager is not None


def test_dependency_manager_initialization():
    """Test DependencyManager initialization"""
    from dependency_manager import DependencyManager
    
    # Test with default directory
    dm = DependencyManager()
    assert dm.app_dir is not None
    assert dm.deps_dir is not None
    assert os.path.exists(dm.deps_dir)
    
    # Test with custom directory
    test_dir = os.path.join(os.path.dirname(__file__), 'test_deps')
    dm = DependencyManager(app_dir=test_dir)
    assert dm.app_dir == test_dir
    assert os.path.exists(dm.deps_dir)
    
    # Cleanup
    import shutil
    shutil.rmtree(os.path.join(test_dir, 'dependencies'), ignore_errors=True)


@patch('subprocess.run')
def test_check_ffmpeg_installed(mock_run):
    """Test FFmpeg installation check"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Test when FFmpeg is installed
    mock_run.return_value = Mock(returncode=0)
    assert dm.check_ffmpeg_installed()
    
    # Test when FFmpeg is not installed
    mock_run.side_effect = FileNotFoundError()
    assert not dm.check_ffmpeg_installed()


@patch('subprocess.run')
def test_check_exiftool_installed(mock_run):
    """Test ExifTool installation check"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Test when ExifTool is installed
    mock_run.return_value = Mock(returncode=0)
    assert dm.check_exiftool_installed()
    
    # Test when ExifTool is not installed
    mock_run.side_effect = FileNotFoundError()
    assert not dm.check_exiftool_installed()


@patch('subprocess.run')
def test_check_docker_installed(mock_run):
    """Test Docker installation check"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Test when Docker is installed
    mock_run.return_value = Mock(returncode=0)
    assert dm.check_docker_installed()
    
    # Test when Docker is not installed
    mock_run.side_effect = FileNotFoundError()
    assert not dm.check_docker_installed()


def test_check_all_dependencies():
    """Test checking all dependencies"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    status = dm.check_all_dependencies()
    
    # Verify structure of returned status
    assert 'ffmpeg' in status
    assert 'exiftool' in status
    assert 'docker' in status
    
    assert 'installed' in status['ffmpeg']
    assert 'bundled' in status['ffmpeg']
    assert 'installed' in status['exiftool']
    assert 'bundled' in status['exiftool']
    assert 'installed' in status['docker']
    assert 'running' in status['docker']


@patch('urllib.request.urlretrieve')
def test_download_with_progress(mock_urlretrieve):
    """Test download with progress callback"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Mock successful download
    mock_urlretrieve.return_value = None
    
    result = dm.download_with_progress(
        'http://example.com/file.zip',
        '/tmp/test.zip'
    )
    
    assert result
    mock_urlretrieve.assert_called_once()
    
    # Test with progress callback
    progress_called = []
    
    def progress_callback(current, total, percentage):
        progress_called.append((current, total, percentage))
    
    result = dm.download_with_progress(
        'http://example.com/file.zip',
        '/tmp/test2.zip',
        progress_callback=progress_callback
    )
    
    assert result


def test_url_constants():
    """Test that URL constants are defined correctly"""
    from dependency_manager import DependencyManager
    
    # ExifTool now uses LATEST_64 URL
    assert "exiftool-LATEST_64.zip" in DependencyManager.EXIFTOOL_URL
    assert "ffmpeg" in DependencyManager.FFMPEG_URL.lower()
    
    # Verify URLs are using the correct format
    assert DependencyManager.EXIFTOOL_URL == "https://exiftool.org/exiftool-LATEST_64.zip"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
