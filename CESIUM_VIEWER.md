# CesiumJS 3D Viewer Integration

## Overview

The DJI Video to 3D Map Pipeline now includes an integrated CesiumJS-based 3D viewer that automatically launches after WebODM processing completes. This provides an immediate, interactive way to visualize your 3D reconstructions without needing external software.

## Features

### Automatic Launch
- Viewer automatically opens in your default web browser after 3D processing
- No manual configuration required
- Runs on a local web server (default port: 8080)

### Interactive Controls
- **Rotate**: Left-click and drag
- **Pan**: Right-click and drag  
- **Zoom**: Scroll wheel
- **Tilt**: Middle-click and drag

### Visualization Options
- **3D Models**: View textured meshes (OBJ format) or point clouds (PLY format)
- **Terrain Integration**: Toggle between world terrain and flat ellipsoid
- **Orthophoto Overlay**: Support for orthophoto layers (when available)
- **Camera Controls**: Reset view, home button, and scene mode picker

## Technical Details

### Architecture

The CesiumJS viewer integration consists of:

1. **cesium_viewer.py** - Main viewer module
   - `CesiumViewer` class: Manages the viewer lifecycle
   - `convert_webodm_to_3dtiles()`: Utility for finding 3D models in WebODM output

2. **Local Web Server**
   - Python `http.server.SimpleHTTPRequestHandler`
   - Serves HTML viewer and 3D assets
   - Runs in background thread
   - Automatically cleaned up on application exit

3. **HTML Viewer Template**
   - CesiumJS library loaded via CDN (version 1.109)
   - Responsive design
   - Toolbar with controls
   - Information panel with keyboard shortcuts

### Workflow

```
WebODM Processing Complete
          ↓
Download 3D Model (OBJ/PLY)
          ↓
Download Orthophoto (optional)
          ↓
Create Viewer Directory
          ↓
Copy Assets to Viewer Directory
          ↓
Generate HTML Viewer Page
          ↓
Start Local HTTP Server
          ↓
Open Browser to http://localhost:8080
          ↓
User Interacts with 3D Model
          ↓
Server Cleaned Up on App Exit
```

## Usage

### Automatic Usage (Recommended)

1. Process your DJI video through the pipeline
2. Click "Create 3D Map" in the WebODM tab
3. Wait for processing to complete
4. **Viewer automatically opens** in your browser
5. Interact with your 3D model

The viewer runs until you close the application.

### Manual Control

If you need to access the viewer later:

1. Navigate to the viewer directory:
   ```
   %USERPROFILE%/DJI_3D_Viewer/project_<id>_task_<uuid>/
   ```

2. Look for the generated viewer files:
   - `index.html` - Main viewer page
   - `odm_textured_model_geo.obj` - 3D model
   - `odm_orthophoto.tif` - Orthophoto (if available)

3. You can open `index.html` directly in a web browser, but you'll need to serve it via HTTP for the 3D model to load properly due to CORS restrictions.

## Supported Formats

### 3D Models
- **OBJ**: Textured mesh with materials (preferred)
- **PLY**: Point cloud or mesh
- **3D Tiles**: Future support planned for better performance

### Orthophotos
- **GeoTIFF**: `.tif` format
- Note: Full orthophoto integration requires tile service setup

## Configuration

### Default Settings

```python
# Default viewer port
port = 8080

# Viewer directory
viewer_dir = "%USERPROFILE%/DJI_3D_Viewer"

# CesiumJS CDN version
cesium_version = "1.109"
```

### Customization

To customize the viewer, you can modify `cesium_viewer.py`:

1. **Change Port**:
   ```python
   viewer = CesiumViewer(port=9000)
   ```

2. **Custom Viewer Directory**:
   ```python
   viewer.prepare_viewer_directory(
       output_dir="/custom/path",
       model_path=model_path
   )
   ```

3. **Disable Auto-Launch**:
   Modify `main_app.py` and comment out the `_launch_cesium_viewer()` call

## Troubleshooting

### Viewer Doesn't Open

**Problem**: Browser doesn't open after processing

**Solutions**:
1. Check if port 8080 is already in use
2. Look for error messages in the application log
3. Manually navigate to `http://localhost:8080`
4. Check your firewall settings

### 3D Model Not Visible

**Problem**: Viewer opens but model isn't shown

**Solutions**:
1. Check browser console for errors (F12)
2. Verify the model file was downloaded successfully
3. Ensure you're accessing via HTTP, not file:// protocol
4. Check that WebODM processing completed successfully

### Port Already in Use

**Problem**: "Address already in use" error

**Solutions**:
1. The viewer will automatically try port 8081 if 8080 is busy
2. Close other applications using port 8080
3. Restart the application
4. Check for other running viewer instances

### Performance Issues

**Problem**: Viewer is slow or laggy

**Solutions**:
1. Use a modern browser (Chrome, Firefox, Edge)
2. Close other browser tabs
3. Reduce the number of images in your reconstruction
4. Consider using lower quality settings in WebODM

### CORS Errors

**Problem**: CORS policy errors in browser console

**Solutions**:
1. Always access the viewer via the HTTP server (http://localhost:8080)
2. Don't open index.html directly from file system
3. Ensure the server is running (check application log)

## Advanced Features

### 3D Tiles Conversion (Future)

For better performance with large datasets, you can convert models to 3D Tiles format:

```python
from cesium_viewer import convert_webodm_to_3dtiles

success, tileset_path = convert_webodm_to_3dtiles(
    webodm_output_dir="/path/to/webodm/output",
    output_dir="/path/to/3dtiles/output"
)
```

Currently, this function locates existing models. Future versions will include actual 3D Tiles conversion.

### Custom HTML Template

To customize the viewer appearance, modify the `create_viewer_html()` method in `cesium_viewer.py`. The template includes:

- CSS styling
- JavaScript initialization
- Cesium configuration
- UI controls

## API Reference

### CesiumViewer Class

```python
class CesiumViewer:
    def __init__(self, port: int = 8080)
    def create_viewer_html(self, model_path: str, orthophoto_path: Optional[str] = None) -> str
    def prepare_viewer_directory(self, output_dir: str, model_path: str, orthophoto_path: Optional[str] = None) -> Tuple[bool, str]
    def start_server(self) -> Tuple[bool, str]
    def open_viewer(self) -> Tuple[bool, str]
    def stop_server(self) -> None
    def launch_viewer(self, model_path: str, orthophoto_path: Optional[str] = None, output_dir: Optional[str] = None) -> Tuple[bool, str]
```

### Key Methods

**launch_viewer()**
- Complete workflow: prepare directory, start server, open browser
- Returns: `(success: bool, message: str)`

**stop_server()**
- Clean shutdown of HTTP server
- Called automatically on application exit

## Integration with Main Application

The viewer is integrated into `main_app.py`:

1. **Initialization**: `self.cesium_viewer = CesiumViewer()`
2. **Launch**: Called after WebODM processing in `_webodm_pipeline()`
3. **Cleanup**: Automatic via `atexit.register(self._cleanup)`

## Security Considerations

### Local Server Only
- Server binds to localhost only
- Not accessible from external networks
- Automatically stops when application closes

### Asset Management
- Assets stored in user's home directory
- Temporary files cleaned up appropriately
- No external data transmission

### Browser Security
- Uses standard CORS policies
- No sensitive data in viewer
- Standard HTTP (not HTTPS) for localhost

## Performance Tips

1. **Browser Choice**: Use Chrome or Edge for best performance
2. **Model Size**: Smaller models load faster
3. **Texture Quality**: Lower texture resolution improves loading
4. **RAM**: Ensure sufficient RAM for large models
5. **Close Other Apps**: Free up resources for the viewer

## Future Enhancements

Planned improvements for the CesiumJS viewer:

- [ ] Full 3D Tiles conversion support
- [ ] Better orthophoto integration with tile services
- [ ] Multiple viewer instances for comparison
- [ ] Measurement tools
- [ ] Export camera positions
- [ ] Animation/flythrough support
- [ ] Point cloud classification visualization
- [ ] Custom base maps
- [ ] Save/load viewer state

## Resources

- **CesiumJS Documentation**: https://cesium.com/learn/cesiumjs-learn/
- **CesiumJS API Reference**: https://cesium.com/learn/cesiumjs/ref-doc/
- **WebODM Output Formats**: https://docs.opendronemap.org/outputs/
- **3D Tiles Specification**: https://github.com/CesiumGS/3d-tiles

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs for errors
3. Open an issue on GitHub with:
   - Browser and version
   - Error messages from browser console
   - Application log output
   - Description of the problem

## License

The CesiumJS library is licensed under the Apache License 2.0.
This integration code follows the project's open-source license.
