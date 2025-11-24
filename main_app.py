"""
Main GUI Application for DJI Video to 3D Map Pipeline
Windows 10 Application with drag-drop support and Google Drive integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from typing import Optional
import shutil

from srt_parser import SRTParser
from frame_extractor import FrameExtractor
from telemetry_sync import TelemetrySynchronizer
from exif_injector import ExifInjector
from webodm_client import WebODMClient


class PhotogrammetryApp:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DJI Video to 3D Map Pipeline")
        self.root.geometry("900x700")
        
        # Variables
        self.video_path = tk.StringVar()
        self.srt_path = tk.StringVar()
        self.buffer_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "DroneBuffer"))
        self.output_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "DroneOutput"))
        self.webodm_url = tk.StringVar(value="http://localhost:8000")
        self.webodm_username = tk.StringVar(value="admin")
        self.webodm_password = tk.StringVar(value="admin")
        self.frame_rate = tk.DoubleVar(value=1.0)
        
        # State
        self.processing = False
        self.geotagged_images = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface"""
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Input
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="1. Input Files")
        self._setup_input_tab(input_frame)
        
        # Tab 2: Processing
        process_frame = ttk.Frame(notebook)
        notebook.add(process_frame, text="2. Processing")
        self._setup_process_tab(process_frame)
        
        # Tab 3: WebODM
        webodm_frame = ttk.Frame(notebook)
        notebook.add(webodm_frame, text="3. WebODM")
        self._setup_webodm_tab(webodm_frame)
        
        # Tab 4: Output
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="4. Output")
        self._setup_output_tab(output_frame)
        
        # Log console at bottom
        log_label = ttk.Label(self.root, text="Processing Log:")
        log_label.pack(anchor='w', padx=10)
        
        self.log_text = scrolledtext.ScrolledText(
            self.root, height=10, wrap=tk.WORD, 
            state='disabled', bg='black', fg='lime'
        )
        self.log_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
    def _setup_input_tab(self, parent):
        """Setup input file selection tab"""
        # Video file
        video_frame = ttk.LabelFrame(parent, text="Video File (.MP4)", padding=10)
        video_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Entry(video_frame, textvariable=self.video_path, width=60).pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(video_frame, text="Browse", command=self._browse_video).pack(side='left')
        
        # SRT file
        srt_frame = ttk.LabelFrame(parent, text="SRT File (Telemetry)", padding=10)
        srt_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Entry(srt_frame, textvariable=self.srt_path, width=60).pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(srt_frame, text="Browse", command=self._browse_srt).pack(side='left')
        
        # Buffer directory
        buffer_frame = ttk.LabelFrame(parent, text="Buffer Directory (Geotagged Images)", padding=10)
        buffer_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Entry(buffer_frame, textvariable=self.buffer_path, width=60).pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(buffer_frame, text="Browse", command=self._browse_buffer).pack(side='left')
        
        # Instructions
        instructions = ttk.Label(
            parent,
            text="Select video and SRT files from your DJI Mini 3 drone.\n"
                 "Choose a buffer directory to store geotagged images.",
            justify='left', foreground='gray'
        )
        instructions.pack(padx=10, pady=10, anchor='w')
        
    def _setup_process_tab(self, parent):
        """Setup processing options tab"""
        # Frame rate
        rate_frame = ttk.LabelFrame(parent, text="Frame Extraction Settings", padding=10)
        rate_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(rate_frame, text="Frames per second:").pack(side='left', padx=(0, 5))
        ttk.Spinbox(
            rate_frame, textvariable=self.frame_rate,
            from_=0.1, to=5.0, increment=0.1, width=10
        ).pack(side='left')
        ttk.Label(rate_frame, text="(Recommended: 1.0 fps)", foreground='gray').pack(side='left', padx=(5, 0))
        
        # Process button
        process_btn = ttk.Button(
            parent, text="Start Processing Pipeline",
            command=self._start_processing,
            style='Accent.TButton'
        )
        process_btn.pack(pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            parent, variable=self.progress_var,
            maximum=100, length=400
        )
        self.progress_bar.pack(pady=10)
        
        self.progress_label = ttk.Label(parent, text="Ready to process")
        self.progress_label.pack()
        
    def _setup_webodm_tab(self, parent):
        """Setup WebODM integration tab"""
        # Connection settings
        conn_frame = ttk.LabelFrame(parent, text="WebODM Connection", padding=10)
        conn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(conn_frame, text="URL:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        ttk.Entry(conn_frame, textvariable=self.webodm_url, width=40).grid(row=0, column=1, sticky='ew')
        
        ttk.Label(conn_frame, text="Username:").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(5, 0))
        ttk.Entry(conn_frame, textvariable=self.webodm_username, width=40).grid(row=1, column=1, sticky='ew', pady=(5, 0))
        
        ttk.Label(conn_frame, text="Password:").grid(row=2, column=0, sticky='w', padx=(0, 5), pady=(5, 0))
        ttk.Entry(conn_frame, textvariable=self.webodm_password, width=40, show='*').grid(row=2, column=1, sticky='ew', pady=(5, 0))
        
        conn_frame.columnconfigure(1, weight=1)
        
        # Test connection button
        ttk.Button(
            parent, text="Test Connection",
            command=self._test_webodm_connection
        ).pack(pady=10)
        
        # Create 3D map button
        self.create_map_btn = ttk.Button(
            parent, text="Create 3D Map",
            command=self._create_3d_map,
            state='disabled'
        )
        self.create_map_btn.pack(pady=10)
        
        self.webodm_progress_label = ttk.Label(parent, text="")
        self.webodm_progress_label.pack()
        
    def _setup_output_tab(self, parent):
        """Setup output options tab"""
        # Output directory
        output_frame = ttk.LabelFrame(parent, text="Output Directory", padding=10)
        output_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=60).pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self._browse_output).pack(side='left')
        
        # Export button
        self.export_btn = ttk.Button(
            parent, text="Export Results",
            command=self._export_results,
            state='disabled'
        )
        self.export_btn.pack(pady=20)
        
        # Status
        self.export_status = ttk.Label(parent, text="")
        self.export_status.pack()
        
    def _browse_video(self):
        """Browse for video file"""
        filename = filedialog.askopenfilename(
            title="Select DJI Video File",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if filename:
            self.video_path.set(filename)
            # Try to auto-find SRT file
            srt_file = os.path.splitext(filename)[0] + ".SRT"
            if os.path.exists(srt_file):
                self.srt_path.set(srt_file)
                self.log("Auto-detected SRT file: " + srt_file)
    
    def _browse_srt(self):
        """Browse for SRT file"""
        filename = filedialog.askopenfilename(
            title="Select SRT Telemetry File",
            filetypes=[("SRT files", "*.SRT *.srt"), ("All files", "*.*")]
        )
        if filename:
            self.srt_path.set(filename)
    
    def _browse_buffer(self):
        """Browse for buffer directory"""
        dirname = filedialog.askdirectory(title="Select Buffer Directory")
        if dirname:
            self.buffer_path.set(dirname)
    
    def _browse_output(self):
        """Browse for output directory"""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_path.set(dirname)
    
    def _test_webodm_connection(self):
        """Test WebODM connection"""
        self.log("Testing WebODM connection...")
        
        try:
            client = WebODMClient(
                host=self.webodm_url.get(),
                username=self.webodm_username.get(),
                password=self.webodm_password.get()
            )
            
            if client.authenticate():
                self.log("✓ WebODM connection successful!")
                messagebox.showinfo("Success", "Connected to WebODM successfully!")
            else:
                self.log("✗ WebODM connection failed")
                messagebox.showerror("Error", "Failed to connect to WebODM")
        except Exception as e:
            self.log(f"✗ Error: {e}")
            messagebox.showerror("Error", f"Connection error: {e}")
    
    def _start_processing(self):
        """Start the processing pipeline"""
        if self.processing:
            messagebox.showwarning("Warning", "Processing already in progress")
            return
        
        # Validate inputs
        if not self.video_path.get() or not os.path.exists(self.video_path.get()):
            messagebox.showerror("Error", "Please select a valid video file")
            return
        
        if not self.srt_path.get() or not os.path.exists(self.srt_path.get()):
            messagebox.showerror("Error", "Please select a valid SRT file")
            return
        
        # Start processing in separate thread
        self.processing = True
        thread = threading.Thread(target=self._process_pipeline, daemon=True)
        thread.start()
    
    def _process_pipeline(self):
        """Main processing pipeline"""
        try:
            self.log("=" * 60)
            self.log("Starting DJI Video Processing Pipeline")
            self.log("=" * 60)
            
            # Step 1: Extract video information
            self.update_progress(5, "Analyzing video...")
            extractor = FrameExtractor(self.video_path.get())
            video_info = extractor.get_video_info()
            self.log(f"Video: {video_info['duration']:.2f}s, {video_info['fps']:.2f} fps")
            
            # Step 2: Parse SRT
            self.update_progress(10, "Parsing SRT telemetry...")
            parser = SRTParser(self.srt_path.get())
            telemetry_df = parser.parse()
            self.log(f"Parsed {len(telemetry_df)} telemetry records")
            
            # Validate duration
            if not parser.validate_duration(telemetry_df, video_info['duration']):
                if not messagebox.askyesno(
                    "Warning",
                    "SRT duration doesn't match video duration. Continue anyway?"
                ):
                    self.log("Processing canceled by user")
                    return
            
            # Step 3: Extract frames
            self.update_progress(20, "Extracting video frames...")
            temp_frames_dir = os.path.join(self.buffer_path.get(), "temp_frames")
            os.makedirs(temp_frames_dir, exist_ok=True)
            
            frame_paths = extractor.extract_frames(
                temp_frames_dir,
                frame_rate=self.frame_rate.get()
            )
            self.log(f"Extracted {len(frame_paths)} frames")
            
            # Step 4: Synchronize and interpolate
            self.update_progress(40, "Synchronizing telemetry with frames...")
            frame_timestamps = extractor.calculate_frame_timestamps(
                len(frame_paths),
                self.frame_rate.get()
            )
            
            synchronizer = TelemetrySynchronizer(telemetry_df)
            frame_telemetry = synchronizer.synchronize_and_interpolate(frame_timestamps)
            
            # Classify flight type
            flight_type = synchronizer.classify_flight_type(frame_telemetry)
            self.log(f"Flight type: {flight_type}")
            
            # Step 5: Inject EXIF metadata
            self.update_progress(60, "Injecting GPS metadata...")
            injector = ExifInjector()
            
            telemetry_records = frame_telemetry.to_dict('records')
            success_count = injector.batch_inject(
                frame_paths,
                telemetry_records,
                progress_callback=lambda curr, total: self.update_progress(
                    60 + (curr / total) * 30,
                    f"Geotagging image {curr}/{total}"
                )
            )
            
            self.log(f"✓ Successfully geotagged {success_count}/{len(frame_paths)} images")
            
            # Save geotagged images list
            self.geotagged_images = frame_paths
            
            # Enable WebODM button
            self.create_map_btn.config(state='normal')
            
            self.update_progress(100, "Processing complete!")
            self.log("=" * 60)
            self.log("✓ Pipeline completed successfully!")
            self.log(f"Geotagged images saved to: {temp_frames_dir}")
            self.log("=" * 60)
            
            messagebox.showinfo(
                "Success",
                f"Processing complete!\n\n"
                f"Processed {len(frame_paths)} frames\n"
                f"Flight type: {flight_type}\n\n"
                f"Ready for 3D map creation in WebODM tab."
            )
            
        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Processing failed:\n{str(e)}")
        finally:
            self.processing = False
    
    def _create_3d_map(self):
        """Create 3D map using WebODM"""
        if not self.geotagged_images:
            messagebox.showerror("Error", "No geotagged images available. Run processing first.")
            return
        
        # Start in separate thread
        thread = threading.Thread(target=self._webodm_pipeline, daemon=True)
        thread.start()
    
    def _webodm_pipeline(self):
        """WebODM processing pipeline"""
        try:
            self.log("=" * 60)
            self.log("Starting WebODM 3D Reconstruction")
            self.log("=" * 60)
            
            # Connect to WebODM
            self.webodm_progress_label.config(text="Connecting to WebODM...")
            client = WebODMClient(
                host=self.webodm_url.get(),
                username=self.webodm_username.get(),
                password=self.webodm_password.get()
            )
            
            if not client.authenticate():
                raise Exception("Failed to authenticate with WebODM")
            
            # Create project
            self.webodm_progress_label.config(text="Creating project...")
            project_name = f"DJI_Reconstruction_{os.path.basename(self.video_path.get())}"
            project_id = client.create_project(project_name, "DJI Mini 3 photogrammetry")
            
            if not project_id:
                raise Exception("Failed to create WebODM project")
            
            # Upload images
            self.webodm_progress_label.config(text="Uploading images...")
            task_uuid = client.upload_images(
                project_id,
                self.geotagged_images,
                task_name="3D Map Generation"
            )
            
            if not task_uuid:
                raise Exception("Failed to upload images")
            
            # Wait for processing
            self.webodm_progress_label.config(text="Processing (this may take a while)...")
            
            def update_webodm_progress(status, progress):
                """Update WebODM processing progress"""
                self.webodm_progress_label.config(text=f"Processing: {status} ({progress}%)")
            
            success = client.wait_for_completion(
                project_id,
                task_uuid,
                timeout=7200,  # 2 hours
                progress_callback=update_webodm_progress
            )
            
            if success:
                self.log("✓ 3D reconstruction completed!")
                self.webodm_progress_label.config(text="✓ Processing complete!")
                self.export_btn.config(state='normal')
                
                # Store task info for export
                self.current_project_id = project_id
                self.current_task_uuid = task_uuid
                
                messagebox.showinfo(
                    "Success",
                    "3D map created successfully!\n\n"
                    "Go to Output tab to export results."
                )
            else:
                raise Exception("WebODM processing failed or timed out")
            
        except Exception as e:
            self.log(f"✗ WebODM Error: {str(e)}")
            self.webodm_progress_label.config(text="✗ Processing failed")
            messagebox.showerror("Error", f"WebODM processing failed:\n{str(e)}")
    
    def _export_results(self):
        """Export WebODM results"""
        if not hasattr(self, 'current_project_id') or not hasattr(self, 'current_task_uuid'):
            messagebox.showerror("Error", "No results available to export")
            return
        
        try:
            self.export_status.config(text="Exporting...")
            
            client = WebODMClient(
                host=self.webodm_url.get(),
                username=self.webodm_username.get(),
                password=self.webodm_password.get()
            )
            
            client.authenticate()
            
            # Download all results
            output_path = client.download_results(
                self.current_project_id,
                self.current_task_uuid,
                self.output_path.get(),
                asset_type="all.zip"
            )
            
            if output_path:
                self.export_status.config(text=f"✓ Exported to {output_path}")
                messagebox.showinfo(
                    "Success",
                    f"Results exported successfully!\n\n{output_path}"
                )
            else:
                raise Exception("Download failed")
                
        except Exception as e:
            self.export_status.config(text="✗ Export failed")
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def log(self, message):
        """Add message to log console"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        print(message)  # Also print to console
    
    def update_progress(self, value, message=""):
        """Update progress bar and label"""
        self.progress_var.set(value)
        if message:
            self.progress_label.config(text=message)
        self.root.update_idletasks()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = PhotogrammetryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
