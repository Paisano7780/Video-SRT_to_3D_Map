"""
Tests for CesiumJS Viewer Integration
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
from cesium_viewer import CesiumViewer, convert_webodm_to_3dtiles


class TestCesiumViewer(unittest.TestCase):
    """Test CesiumJS viewer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.viewer = CesiumViewer(port=8081)  # Use non-default port for testing
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'viewer') and self.viewer:
            self.viewer.stop_server()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test CesiumViewer initialization"""
        self.assertEqual(self.viewer.port, 8081)
        self.assertIsNone(self.viewer.server)
        self.assertIsNone(self.viewer.server_thread)
        self.assertIsNone(self.viewer.viewer_dir)
    
    def test_create_viewer_html(self):
        """Test HTML viewer creation"""
        model_path = "/path/to/model.obj"
        orthophoto_path = "/path/to/orthophoto.tif"
        
        html_content = self.viewer.create_viewer_html(model_path, orthophoto_path)
        
        # Check that HTML contains required elements
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('cesium.com', html_content)
        self.assertIn('DJI 3D Map Viewer', html_content)
        self.assertIn('model.obj', html_content)
        self.assertIn('orthophoto.tif', html_content)
        self.assertIn('Cesium.Viewer', html_content)
    
    def test_create_viewer_html_without_orthophoto(self):
        """Test HTML viewer creation without orthophoto"""
        model_path = "/path/to/model.obj"
        
        html_content = self.viewer.create_viewer_html(model_path, None)
        
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('model.obj', html_content)
        # Check that the orthoPath variable is empty when no orthophoto provided
        self.assertIn("const orthoPath = '';", html_content)
    
    def test_prepare_viewer_directory_without_files(self):
        """Test viewer directory preparation without existing files"""
        # This should fail gracefully since files don't exist
        success, result = self.viewer.prepare_viewer_directory(
            self.temp_dir,
            "/nonexistent/model.obj",
            None
        )
        
        # Should succeed in creating directory structure even if files don't exist
        self.assertTrue(success)
        self.assertTrue(os.path.exists(result))
        
        # Check that index.html was created
        index_path = os.path.join(result, "index.html")
        self.assertTrue(os.path.exists(index_path))
    
    def test_prepare_viewer_directory_with_model(self):
        """Test viewer directory preparation with actual model file"""
        # Create a dummy model file
        model_file = os.path.join(self.temp_dir, "test_model.obj")
        with open(model_file, 'w') as f:
            f.write("# Dummy OBJ file\n")
        
        success, result = self.viewer.prepare_viewer_directory(
            self.temp_dir,
            model_file,
            None
        )
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(result))
        
        # Check that model was copied
        copied_model = os.path.join(result, "test_model.obj")
        self.assertTrue(os.path.exists(copied_model))
        
        # Check that index.html was created
        index_path = os.path.join(result, "index.html")
        self.assertTrue(os.path.exists(index_path))
    
    def test_stop_server_when_not_started(self):
        """Test stopping server when it was never started"""
        # Should not raise exception
        self.viewer.stop_server()
        self.assertIsNone(self.viewer.server)
    
    def test_viewer_port_configuration(self):
        """Test custom port configuration"""
        custom_viewer = CesiumViewer(port=9999)
        self.assertEqual(custom_viewer.port, 9999)


class TestWebODMConversion(unittest.TestCase):
    """Test WebODM output conversion utilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_convert_webodm_to_3dtiles_no_files(self):
        """Test conversion when no model files exist"""
        success, message = convert_webodm_to_3dtiles(self.temp_dir, self.temp_dir)
        
        self.assertFalse(success)
        self.assertIn("No suitable 3D model found", message)
    
    def test_convert_webodm_to_3dtiles_with_obj(self):
        """Test conversion when OBJ file exists"""
        # Create dummy directory structure
        texture_dir = os.path.join(self.temp_dir, "odm_texturing")
        os.makedirs(texture_dir)
        
        # Create dummy OBJ file
        obj_file = os.path.join(texture_dir, "odm_textured_model_geo.obj")
        with open(obj_file, 'w') as f:
            f.write("# Dummy OBJ\n")
        
        success, model_path = convert_webodm_to_3dtiles(self.temp_dir, self.temp_dir)
        
        self.assertTrue(success)
        self.assertEqual(model_path, obj_file)
    
    def test_convert_webodm_to_3dtiles_with_ply(self):
        """Test conversion when PLY file exists"""
        # Create dummy directory structure
        geo_dir = os.path.join(self.temp_dir, "odm_georeferencing")
        os.makedirs(geo_dir)
        
        # Create dummy PLY file
        ply_file = os.path.join(geo_dir, "odm_georeferenced_model.ply")
        with open(ply_file, 'w') as f:
            f.write("ply\n")
        
        success, model_path = convert_webodm_to_3dtiles(self.temp_dir, self.temp_dir)
        
        self.assertTrue(success)
        self.assertEqual(model_path, ply_file)


if __name__ == '__main__':
    unittest.main()
