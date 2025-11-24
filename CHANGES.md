# Changes Summary - Fix Workflow and App Usability Issues

## Overview
This PR addresses multiple issues reported in the GitHub issue regarding workflow build errors and Windows application usability.

## Issues Fixed

### 1. Workflow Build Skipping on Pull Requests ✅
**Problem:** Build job was being skipped on pull_request events due to `if: github.event_name == 'push'` condition.

**Solution:** Removed the condition from line 39 of `.github/workflows/build.yml` so builds run on both push and pull_request events.

**Files Changed:**
- `.github/workflows/build.yml`

### 2. ExifTool Not Found Error ✅
**Problem:** Application shows error "ExifTool not found. Please install from: https://exiftool.org/" even though ExifTool was bundled with PyInstaller.

**Solution:** Updated `exif_injector.py` to properly detect ExifTool bundled in PyInstaller executables by checking `sys._MEIPASS` with proper exception handling.

**Files Changed:**
- `exif_injector.py`

**Implementation:**
```python
if getattr(sys, 'frozen', False):
    try:
        bundle_dir = sys._MEIPASS
        bundled_exiftool = os.path.join(bundle_dir, 'exiftool.exe')
        if os.path.exists(bundled_exiftool):
            return bundled_exiftool
    except AttributeError:
        pass
```

### 3. Missing Navigation Button on Tab 1 ✅
**Problem:** Tab 1 (Input Files) doesn't have a button to navigate to Tab 2 (Processing).

**Solution:** Added a "Next: Configure Processing →" button that navigates to the Processing tab when clicked.

**Files Changed:**
- `main_app.py`

### 4. Startup Console Warnings ✅
**Problem:** Console shows "Docker not installed" and "WebODM not found" errors on startup, which is confusing for users.

**Solution:** Modified `_check_webodm_status()` to not log warnings to console on initial startup (only updates UI). Also removed verbose Docker logging from `webodm_manager.py`.

**Files Changed:**
- `main_app.py`
- `webodm_manager.py`

### 5. Automatic Dependency Installation ✅
**Problem:** Users need to manually download and install FFmpeg and ExifTool.

**Solution:** Created a standalone installer that:
- Checks if FFmpeg and ExifTool are installed
- Downloads them if missing
- Extracts and installs to application directory
- Automatically adds to Windows PATH
- Shows download progress

**Files Created:**
- `install_dependencies.py` - Python installer script
- `installer.iss` - Inno Setup script (alternative)
- `INSTALLER_README.md` - User documentation

**Files Changed:**
- `build.py` - Build both main app and installer
- `.github/workflows/build.yml` - Build and upload installer

## Testing
- ✅ All 25 existing tests pass
- ✅ Python syntax validated
- ✅ YAML workflow validated
- ✅ Code review completed and issues addressed
- ✅ CodeQL security scan passed (0 alerts)

## Usage for End Users

### Installation
1. Download both files from the release:
   - `DJI_3D_Mapper.exe` - Main application
   - `Install_Dependencies.exe` - Dependency installer

2. Run `Install_Dependencies.exe` first
   - Automatically downloads and installs FFmpeg (~120MB)
   - Automatically downloads and installs ExifTool (~12MB)
   - Adds both to system PATH
   - Shows progress during installation

3. Run `DJI_3D_Mapper.exe`
   - No more "ExifTool not found" errors
   - No more confusing Docker warnings on startup
   - Easy navigation with Next button

## Security Summary
- No security vulnerabilities detected by CodeQL
- All downloads use official sources (exiftool.org, gyan.dev)
- No hardcoded credentials or secrets
- Proper exception handling throughout

## Breaking Changes
None - all changes are backward compatible and improve user experience.

## Future Improvements
- Could add auto-update functionality
- Could bundle FFmpeg in the main executable (would increase size significantly)
- Could add Docker Desktop auto-installation (complex, requires admin)
