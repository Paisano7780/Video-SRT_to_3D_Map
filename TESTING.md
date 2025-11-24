# Testing Documentation

This document describes the testing strategy for the DJI Video to 3D Map Pipeline project.

## Test Structure

The project includes comprehensive unit tests for all major components:

- `test_srt_parser.py` - Tests for SRT file parsing and telemetry extraction
- `test_frame_extractor.py` - Tests for video frame extraction
- `test_telemetry_sync.py` - Tests for telemetry synchronization and interpolation
- `test_webodm_manager.py` - Tests for WebODM lifecycle management and error handling
- `test_dependency_manager.py` - Tests for dependency checking (Windows-specific)

## Running Tests

### Local Testing

Run all tests:
```bash
pytest test_*.py -v
```

Run specific test file:
```bash
pytest test_webodm_manager.py -v
```

Run with coverage:
```bash
pytest test_*.py --cov=. --cov-report=html
```

### CI/CD Testing

Tests run automatically in GitHub Actions on:
- Every push to `main` or `copilot/**` branches
- Every pull request to `main`

The workflow runs on Ubuntu (Linux) for the test job, ensuring cross-platform compatibility.

## WebODM and Docker Error Handling Tests

The `test_webodm_manager.py` file includes comprehensive tests for Docker and WebODM error scenarios, specifically addressing the issues shown in the application error dialogs:

### Test Classes

#### `TestWebODMManager`
Basic functionality tests for the WebODM manager:
- Initialization and configuration
- Status checking methods
- Path resolution

#### `TestDockerErrorHandling`
Tests for Docker-related error scenarios:

1. **`test_docker_not_installed_error`**
   - Verifies detection when Docker is not installed
   - Simulates `FileNotFoundError` when running `docker --version`
   - Ensures `check_docker_installed()` returns `False`

2. **`test_docker_not_running_error`**
   - Verifies detection when Docker daemon is not running
   - Simulates `docker ps` returning error code
   - Ensures `check_docker_running()` returns `False`

3. **`test_start_webodm_docker_not_installed`**
   - Verifies proper error message when trying to start WebODM without Docker
   - Checks that message includes: "Docker is not installed"
   - Checks that message includes: "Please install Docker Desktop first"

4. **`test_start_webodm_docker_not_running`**
   - Verifies proper error when Docker is installed but not running
   - Checks that message includes: "Docker is not running"
   - Checks that message includes: "Please start Docker Desktop"

5. **`test_start_webodm_directory_not_found`**
   - Verifies error when WebODM directory doesn't exist
   - Checks that message includes: "WebODM not found"
   - Useful when git submodules aren't initialized

6. **`test_get_status_reports_docker_errors`**
   - Verifies that `get_status()` correctly reports all error conditions
   - Ensures all boolean flags are present and properly typed

#### `TestWebODMErrorMessages`
Tests for error message formatting and propagation:

1. **`test_docker_not_installed_message_format`**
   - Verifies error message matches the format shown in the application UI
   - Ensures user-friendly messages are returned

2. **`test_webodm_not_found_message_format`**
   - Verifies WebODM path is included in error messages
   - Helps users understand where the application is looking for WebODM

3. **`test_ensure_running_propagates_error_messages`**
   - Verifies that `ensure_running()` correctly propagates errors from `start_webodm()`
   - Ensures consistent error reporting across different entry points

## Error Scenarios Covered

The tests specifically verify handling of the following error conditions shown in the issue screenshot:

### ❌ Docker is not installed
```
Docker is not installed. Please install Docker Desktop first.
```

### ❌ WebODM not found in ./webodm
```
WebODM not found at {path}. Please ensure the repository is cloned correctly.
```

### ❌ WebODM not running
```
WebODM not running
```

### ❌ Failed to start WebODM
```
WebODM processing failed:
Failed to start WebODM: Docker is not installed. Please install Docker Desktop first.
```

## Test Coverage

The test suite uses mocking to simulate error conditions without requiring:
- Docker to be installed
- Docker daemon to be running
- WebODM to be present
- Network connectivity

This allows the tests to run reliably in CI/CD environments and verify error handling logic independently of system state.

## Adding New Tests

When adding new tests for error handling:

1. Use `unittest.mock.patch` to simulate error conditions
2. Test both the return value (boolean success) and the error message
3. Ensure error messages are user-friendly and actionable
4. Add tests to the appropriate test class based on the component being tested

## Platform-Specific Tests

Some tests are skipped on non-Windows platforms:
- `test_dependency_manager.py` tests are Windows-specific and will be skipped on Linux/macOS

This is expected and normal behavior.
