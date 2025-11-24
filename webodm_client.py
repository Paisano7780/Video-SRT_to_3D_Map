"""
WebODM API Client
Interface for WebODM photogrammetry processing
"""

import requests
import time
import os
from typing import Optional, Dict, List
import json


class WebODMClient:
    """Client for WebODM API"""
    
    def __init__(self, host: str = "http://localhost:8000", 
                 username: str = "admin", password: str = "admin"):
        """
        Initialize WebODM client
        
        Args:
            host: WebODM server URL
            username: WebODM username
            password: WebODM password
        """
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        
    def authenticate(self) -> bool:
        """
        Authenticate with WebODM server
        
        Returns:
            True if authentication successful
        """
        try:
            url = f"{self.host}/api/token-auth/"
            response = self.session.post(
                url,
                json={'username': self.username, 'password': self.password}
            )
            response.raise_for_status()
            
            self.token = response.json()['token']
            self.session.headers.update({'Authorization': f'Token {self.token}'})
            
            print(f"✓ Authenticated with WebODM at {self.host}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def create_project(self, name: str, description: str = "") -> Optional[int]:
        """
        Create a new project in WebODM
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            url = f"{self.host}/api/projects/"
            response = self.session.post(
                url,
                json={'name': name, 'description': description}
            )
            response.raise_for_status()
            
            project_id = response.json()['id']
            print(f"✓ Created project '{name}' (ID: {project_id})")
            return project_id
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to create project: {e}")
            return None
    
    def upload_images(self, project_id: int, image_paths: List[str],
                     task_name: str = "3D Reconstruction",
                     options: Optional[Dict] = None) -> Optional[str]:
        """
        Upload images and create a processing task
        
        Args:
            project_id: WebODM project ID
            image_paths: List of image file paths
            task_name: Name for the processing task
            options: Processing options dictionary
            
        Returns:
            Task UUID if successful, None otherwise
        """
        try:
            url = f"{self.host}/api/projects/{project_id}/tasks/"
            
            # Prepare files for upload
            files = []
            file_handles = []
            try:
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        fh = open(img_path, 'rb')
                        file_handles.append(fh)
                        files.append(
                            ('images', (os.path.basename(img_path), fh, 'image/jpeg'))
                        )
            
            # Default processing options
            default_options = {
                'dsm': True,
                'dtm': True,
                'orthophoto-resolution': 2,
                'feature-quality': 'high',
                'pc-quality': 'high',
                'mesh-octree-depth': 11,
                'mesh-size': 200000,
            }
            
            if options:
                default_options.update(options)
            
            # Prepare form data
            data = {
                'name': task_name,
                'options': json.dumps([
                    {'name': k, 'value': v} 
                    for k, v in default_options.items()
                ])
            }
            
                print(f"⏳ Uploading {len(files)} images...")
                response = self.session.post(url, files=files, data=data)
                response.raise_for_status()
            finally:
                # Close file handles
                for fh in file_handles:
                    fh.close()
            
            task_uuid = response.json()['id']
            print(f"✓ Task created (UUID: {task_uuid})")
            return task_uuid
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to upload images: {e}")
            return None
    
    def get_task_status(self, project_id: int, task_uuid: str) -> Optional[Dict]:
        """
        Get task processing status
        
        Args:
            project_id: WebODM project ID
            task_uuid: Task UUID
            
        Returns:
            Task status dictionary
        """
        try:
            url = f"{self.host}/api/projects/{project_id}/tasks/{task_uuid}/"
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to get task status: {e}")
            return None
    
    def wait_for_completion(self, project_id: int, task_uuid: str,
                           timeout: int = 7200,
                           progress_callback=None) -> bool:
        """
        Wait for task to complete
        
        Args:
            project_id: WebODM project ID
            task_uuid: Task UUID
            timeout: Maximum wait time in seconds (default: 2 hours)
            progress_callback: Optional callback function(status, progress)
            
        Returns:
            True if completed successfully
        """
        start_time = time.time()
        last_status = None
        
        while (time.time() - start_time) < timeout:
            status_data = self.get_task_status(project_id, task_uuid)
            
            if not status_data:
                return False
            
            status = status_data.get('status', {}).get('code')
            progress = status_data.get('progress', 0)
            
            if status != last_status:
                print(f"Status: {status} ({progress}%)")
                last_status = status
            
            if progress_callback:
                progress_callback(status, progress)
            
            # Check if completed
            if status == 40:  # Completed
                print("✓ Processing completed successfully!")
                return True
            elif status == 30:  # Failed
                print("✗ Processing failed")
                return False
            elif status == 50:  # Canceled
                print("⚠ Processing was canceled")
                return False
            
            time.sleep(5)  # Check every 5 seconds
        
        print("✗ Timeout waiting for task completion")
        return False
    
    def download_results(self, project_id: int, task_uuid: str,
                        output_dir: str, asset_type: str = "all.zip") -> Optional[str]:
        """
        Download processing results
        
        Args:
            project_id: WebODM project ID
            task_uuid: Task UUID
            output_dir: Directory to save results
            asset_type: Type of asset to download (all.zip, orthophoto.tif, etc.)
            
        Returns:
            Path to downloaded file
        """
        try:
            url = f"{self.host}/api/projects/{project_id}/tasks/{task_uuid}/download/{asset_type}"
            
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, asset_type)
            
            print(f"⏳ Downloading {asset_type}...")
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✓ Downloaded to {output_path}")
            return output_path
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to download results: {e}")
            return None
