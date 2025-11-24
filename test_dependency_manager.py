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


@patch('os.path.exists')
def test_check_docker_desktop_exists(mock_exists):
    """Test Docker Desktop existence check"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Test when Docker Desktop exists
    mock_exists.return_value = True
    assert dm.check_docker_desktop_exists()
    
    # Test when Docker Desktop doesn't exist
    mock_exists.return_value = False
    assert not dm.check_docker_desktop_exists()


@patch('ctypes.windll.shell32.IsUserAnAdmin')
def test_is_admin(mock_is_admin):
    """Test admin privilege check"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Test when running as admin
    mock_is_admin.return_value = 1
    assert dm.is_admin()
    
    # Test when not running as admin
    mock_is_admin.return_value = 0
    assert not dm.is_admin()


@patch('dependency_manager.DependencyManager.download_with_progress')
@patch('os.path.exists')
def test_download_docker_installer(mock_exists, mock_download):
    """Test Docker installer download"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Test successful download
    mock_exists.return_value = False
    mock_download.return_value = True
    
    result = dm.download_docker_installer()
    
    assert result is not None
    assert 'DockerDesktopInstaller.exe' in result
    mock_download.assert_called_once()
    
    # Test when installer already exists
    mock_download.reset_mock()
    mock_exists.return_value = True
    
    result = dm.download_docker_installer()
    assert result is not None
    # Should not download again
    mock_download.assert_not_called()


@patch('subprocess.run')
@patch('os.path.exists')
@patch('dependency_manager.DependencyManager.is_admin')
def test_install_docker_desktop(mock_is_admin, mock_exists, mock_run):
    """Test Docker Desktop installation"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Test successful installation
    mock_is_admin.return_value = True
    mock_exists.return_value = True
    mock_run.return_value = Mock(returncode=0, stderr=b'')
    
    success, message = dm.install_docker_desktop('/tmp/DockerDesktopInstaller.exe')
    
    assert success
    assert "successfully" in message.lower()
    mock_run.assert_called_once()
    
    # Test installation without admin privileges
    mock_is_admin.return_value = False
    
    success, message = dm.install_docker_desktop('/tmp/DockerDesktopInstaller.exe')
    
    assert not success
    assert "administrator" in message.lower() or "admin" in message.lower()


@patch('tkinter.messagebox.showinfo')
def test_prompt_restart_for_docker(mock_showinfo):
    """Test restart prompt dialog"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    result = dm.prompt_restart_for_docker()
    
    assert result is True
    mock_showinfo.assert_called_once()
    
    # Verify message content
    call_args = mock_showinfo.call_args
    assert 'restart' in call_args[0][1].lower() or 'restart' in str(call_args[1]).lower()


@patch('dependency_manager.DependencyManager.check_docker_desktop_exists')
@patch('dependency_manager.DependencyManager.check_docker_installed')
@patch('dependency_manager.DependencyManager.check_docker_running')
def test_ensure_docker_is_installed_already_installed(mock_running, mock_installed, mock_exists):
    """Test ensure_docker_is_installed when Docker is already installed and running"""
    from dependency_manager import DependencyManager
    
    dm = DependencyManager()
    
    # Docker is already installed and running
    mock_exists.return_value = True
    mock_installed.return_value = True
    mock_running.return_value = True
    
    success, message = dm.ensure_docker_is_installed()
    
    assert success
    assert "running" in message.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
