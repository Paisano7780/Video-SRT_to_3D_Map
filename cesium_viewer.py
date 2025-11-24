"""
CesiumJS Viewer Integration
Handles conversion of WebODM outputs to CesiumJS-compatible formats and serves the viewer
"""

import os
import sys
import http.server
import socketserver
import threading
import webbrowser
import time
import json
import shutil
from typing import Optional, Tuple
from pathlib import Path


class CesiumViewer:
    """Manager for CesiumJS 3D viewer"""
    
    def __init__(self, port: int = 8080):
        """
        Initialize CesiumJS viewer
        
        Args:
            port: Port for the local web server
        """
        self.port = port
        self.server = None
        self.server_thread = None
        self.viewer_dir = None
        
    def create_viewer_html(self, model_path: str, orthophoto_path: Optional[str] = None) -> str:
        """
        Create HTML viewer page with CesiumJS
        
        Args:
            model_path: Path to the 3D model file (textured mesh or point cloud)
            orthophoto_path: Optional path to orthophoto
            
        Returns:
            HTML content as string
        """
        # CesiumJS Ion token (using default development token - replace with your own for production)
        cesium_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYWE1OWUxNy1mMWZiLTQzYjYtYTQ0OS1kMWFjYmFkNjc5YzciLCJpZCI6NTc3MzMsImlhdCI6MTYyNzg0NTE4Mn0.XcKpgANiY19MC4bdFUXMVEBToBmqS8kuYpUlxJHYZxk"
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DJI 3D Map Viewer - CesiumJS</title>
    
    <!-- CesiumJS -->
    <script src="https://cesium.com/downloads/cesiumjs/releases/1.109/Build/Cesium/Cesium.js"></script>
    <link href="https://cesium.com/downloads/cesiumjs/releases/1.109/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
    
    <style>
        html, body, #cesiumContainer {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}
        
        #toolbar {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(42, 42, 42, 0.9);
            padding: 10px;
            border-radius: 5px;
            color: white;
            z-index: 1000;
        }}
        
        #toolbar h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
        }}
        
        #toolbar button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        #toolbar button:hover {{
            background: #45a049;
        }}
        
        #info {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(42, 42, 42, 0.8);
            padding: 10px;
            border-radius: 5px;
            color: white;
            font-size: 12px;
            max-width: 300px;
        }}
    </style>
</head>
<body>
    <div id="cesiumContainer"></div>
    
    <div id="toolbar">
        <h3>🗺️ DJI 3D Map Viewer</h3>
        <button onclick="resetView()">Reset View</button>
        <button onclick="toggleTerrain()">Toggle Terrain</button>
        <button onclick="toggleOrtho()">Toggle Orthophoto</button>
    </div>
    
    <div id="info">
        <strong>Controls:</strong><br>
        • Left click + drag: Rotate<br>
        • Right click + drag: Pan<br>
        • Scroll wheel: Zoom<br>
        • Middle click + drag: Tilt
    </div>

    <script>
        // Set Cesium Ion access token
        Cesium.Ion.defaultAccessToken = '{cesium_token}';
        
        // Initialize the Cesium Viewer
        const viewer = new Cesium.Viewer('cesiumContainer', {{
            terrainProvider: Cesium.createWorldTerrain(),
            animation: false,
            timeline: false,
            baseLayerPicker: true,
            geocoder: false,
            homeButton: true,
            navigationHelpButton: true,
            sceneModePicker: true,
            selectionIndicator: false,
            infoBox: false,
            fullscreenButton: true,
        }});
        
        let modelEntity = null;
        let orthoLayer = null;
        let initialCamera = null;
        
        // Load the 3D model if available
        const modelPath = '{os.path.basename(model_path) if model_path else ''}';
        if (modelPath) {{
            // For textured mesh (OBJ, PLY, or 3D Tiles)
            if (modelPath.endsWith('.obj') || modelPath.endsWith('.ply')) {{
                // Load as a 3D model
                const position = Cesium.Cartesian3.fromDegrees(0, 0, 0); // Will be updated
                const heading = Cesium.Math.toRadians(0);
                const pitch = 0;
                const roll = 0;
                const hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
                const orientation = Cesium.Transforms.headingPitchRollQuaternion(position, hpr);
                
                modelEntity = viewer.entities.add({{
                    name: '3D Model',
                    position: position,
                    orientation: orientation,
                    model: {{
                        uri: modelPath,
                        scale: 1.0,
                        minimumPixelSize: 128,
                        maximumScale: 20000
                    }}
                }});
            }} else if (modelPath.includes('tileset.json')) {{
                // Load as 3D Tiles
                const tileset = viewer.scene.primitives.add(
                    new Cesium.Cesium3DTileset({{
                        url: modelPath
                    }})
                );
                
                tileset.readyPromise.then(function(tileset) {{
                    viewer.zoomTo(tileset, new Cesium.HeadingPitchRange(0.0, -0.5, tileset.boundingSphere.radius * 2.0));
                    initialCamera = viewer.camera.clone();
                }}).otherwise(function(error) {{
                    console.error('Error loading tileset:', error);
                }});
            }}
        }}
        
        // Load orthophoto if available
        const orthoPath = '{os.path.basename(orthophoto_path) if orthophoto_path else ''}';
        if (orthoPath) {{
            // Note: This is a simplified approach. In production, you'd want to serve
            // the orthophoto as a proper tile service or convert it to GeoTIFF
            console.log('Orthophoto available at:', orthoPath);
        }}
        
        // Store initial camera position
        setTimeout(function() {{
            if (!initialCamera && modelEntity) {{
                viewer.zoomTo(modelEntity);
                setTimeout(function() {{
                    initialCamera = viewer.camera.clone();
                }}, 100);
            }}
        }}, 500);
        
        // Reset view function
        function resetView() {{
            if (initialCamera) {{
                viewer.camera.flyTo({{
                    destination: initialCamera.position,
                    orientation: {{
                        heading: initialCamera.heading,
                        pitch: initialCamera.pitch,
                        roll: initialCamera.roll
                    }},
                    duration: 2.0
                }});
            }} else if (modelEntity) {{
                viewer.zoomTo(modelEntity);
            }}
        }}
        
        // Toggle terrain
        let terrainEnabled = true;
        function toggleTerrain() {{
            terrainEnabled = !terrainEnabled;
            viewer.terrainProvider = terrainEnabled 
                ? Cesium.createWorldTerrain()
                : new Cesium.EllipsoidTerrainProvider();
        }}
        
        // Toggle orthophoto layer
        function toggleOrtho() {{
            if (orthoLayer) {{
                viewer.imageryLayers.remove(orthoLayer);
                orthoLayer = null;
            }} else if (orthoPath) {{
                alert('Orthophoto layer functionality requires proper tile service setup');
            }}
        }}
    </script>
</body>
</html>
"""
        return html_template
    
    def prepare_viewer_directory(self, output_dir: str, model_path: str, 
                                 orthophoto_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Prepare viewer directory with HTML and assets
        
        Args:
            output_dir: Directory to create viewer in
            model_path: Path to 3D model file
            orthophoto_path: Optional path to orthophoto
            
        Returns:
            Tuple of (success, viewer_directory_path)
        """
        try:
            # Create viewer directory
            self.viewer_dir = os.path.join(output_dir, "cesium_viewer")
            os.makedirs(self.viewer_dir, exist_ok=True)
            
            # Copy model file to viewer directory
            if model_path and os.path.exists(model_path):
                model_dest = os.path.join(self.viewer_dir, os.path.basename(model_path))
                shutil.copy2(model_path, model_dest)
            
            # Copy orthophoto if available
            ortho_dest = None
            if orthophoto_path and os.path.exists(orthophoto_path):
                ortho_dest = os.path.join(self.viewer_dir, os.path.basename(orthophoto_path))
                shutil.copy2(orthophoto_path, ortho_dest)
            
            # Create HTML viewer
            html_content = self.create_viewer_html(model_path, orthophoto_path)
            html_path = os.path.join(self.viewer_dir, "index.html")
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True, self.viewer_dir
            
        except Exception as e:
            return False, f"Failed to prepare viewer: {str(e)}"
    
    def start_server(self) -> Tuple[bool, str]:
        """
        Start local web server for viewer
        
        Returns:
            Tuple of (success, message)
        """
        if not self.viewer_dir:
            return False, "Viewer directory not prepared"
        
        original_dir = os.getcwd()
        
        try:
            # Change to viewer directory
            os.chdir(self.viewer_dir)
            
            # Create simple HTTP server
            Handler = http.server.SimpleHTTPRequestHandler
            
            # Try to bind to the port
            try:
                self.server = socketserver.TCPServer(("", self.port), Handler)
            except OSError as e:
                # Port might be in use, try next port
                self.port += 1
                self.server = socketserver.TCPServer(("", self.port), Handler)
            
            # Start server in separate thread
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True
            )
            self.server_thread.start()
            
            # Return to original directory
            os.chdir(original_dir)
            
            return True, f"Viewer server started at http://localhost:{self.port}"
            
        except Exception as e:
            try:
                os.chdir(original_dir)
            except (OSError, FileNotFoundError):
                # Original directory might not exist anymore
                pass
            return False, f"Failed to start server: {str(e)}"
    
    def open_viewer(self) -> Tuple[bool, str]:
        """
        Open the viewer in default web browser
        
        Returns:
            Tuple of (success, message)
        """
        try:
            url = f"http://localhost:{self.port}/index.html"
            webbrowser.open(url)
            return True, f"Viewer opened at {url}"
        except Exception as e:
            return False, f"Failed to open viewer: {str(e)}"
    
    def stop_server(self) -> None:
        """Stop the web server"""
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except (OSError, AttributeError) as e:
                # Server might already be closed or invalid
                print(f"Warning: Error stopping server: {e}")
            self.server = None
            self.server_thread = None
    
    def launch_viewer(self, model_path: str, orthophoto_path: Optional[str] = None,
                     output_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Complete workflow to launch viewer
        
        Args:
            model_path: Path to 3D model
            orthophoto_path: Optional path to orthophoto
            output_dir: Output directory (defaults to temp)
            
        Returns:
            Tuple of (success, message)
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.expanduser("~"), "DJI_3D_Viewer")
        
        # Prepare viewer directory
        success, result = self.prepare_viewer_directory(output_dir, model_path, orthophoto_path)
        if not success:
            return False, result
        
        # Start server
        success, message = self.start_server()
        if not success:
            return False, message
        
        # Wait a moment for server to be ready
        time.sleep(0.5)
        
        # Open viewer
        success, message = self.open_viewer()
        if not success:
            self.stop_server()
            return False, message
        
        return True, f"Viewer launched successfully at http://localhost:{self.port}"


def convert_webodm_to_3dtiles(webodm_output_dir: str, output_dir: str) -> Tuple[bool, str]:
    """
    Convert WebODM outputs to 3D Tiles format for CesiumJS
    
    Note: This is a placeholder for future implementation.
    Currently, CesiumJS can load OBJ/PLY models directly.
    For production use, consider using tools like:
    - py3dtiles for converting to 3D Tiles
    - PDAL for point cloud processing
    - Meshlab for mesh optimization
    
    Args:
        webodm_output_dir: Directory containing WebODM outputs
        output_dir: Directory for 3D Tiles output
        
    Returns:
        Tuple of (success, path_to_tileset_json)
    """
    # For now, we'll use the textured mesh directly
    # In future, implement conversion to 3D Tiles for better performance
    
    # Look for textured mesh
    potential_files = [
        'odm_texturing/odm_textured_model_geo.obj',
        'odm_texturing/odm_textured_model.obj',
        'odm_georeferencing/odm_georeferenced_model.ply',
    ]
    
    for file_path in potential_files:
        full_path = os.path.join(webodm_output_dir, file_path)
        if os.path.exists(full_path):
            return True, full_path
    
    return False, "No suitable 3D model found in WebODM output"
