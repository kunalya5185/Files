#!/usr/bin/env python3
"""
Simple Web File Server with Upload/Download/Delete GUI
Run directly to start server on 0.0.0.0:1234
Always serves from C:\ drive
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import urllib.parse
import html
import mimetypes
from pathlib import Path
import json
import zipfile
import io

# Base directory - always C drive
BASE_DIR = Path("C:/")

# Embedded HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Server</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #2a2a2a;
            border: 1px solid #444;
        }}
        .header {{
            background: #333;
            color: #fff;
            padding: 20px;
            border-bottom: 2px solid #555;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 24px;
        }}
        .current-path {{
            background: #444;
            padding: 8px 12px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 14px;
        }}
        .upload-section {{
            padding: 20px;
            background: #333;
            border-bottom: 1px solid #444;
        }}
        .upload-form {{
            display: flex;
            gap: 10px;
        }}
        input[type="file"] {{
            flex: 1;
            padding: 8px;
            background: #444;
            color: #e0e0e0;
            border: 1px solid #666;
        }}
        .upload-btn {{
            padding: 8px 20px;
            background: #0066cc;
            color: white;
            border: none;
            cursor: pointer;
        }}
        .upload-btn:hover {{
            background: #0052a3;
        }}
        .files-section {{
            padding: 20px;
        }}
        .files-section h2 {{
            margin: 0 0 15px 0;
            font-size: 18px;
            border-bottom: 2px solid #444;
            padding-bottom: 8px;
        }}
        .file-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .file-item {{
            display: flex;
            align-items: center;
            padding: 10px;
            margin-bottom: 5px;
            background: #333;
            border: 1px solid #444;
        }}
        .file-item:hover {{
            background: #3a3a3a;
        }}
        .file-name {{
            flex: 1;
            color: #88c0d0;
            text-decoration: none;
        }}
        .file-name:hover {{
            color: #a3d5e8;
        }}
        .file-size {{
            color: #888;
            margin-left: 15px;
            font-size: 13px;
        }}
        .delete-btn {{
            padding: 5px 12px;
            background: #cc3333;
            color: white;
            border: none;
            cursor: pointer;
            margin-left: 10px;
            font-size: 12px;
        }}
        .delete-btn:hover {{
            background: #aa0000;
        }}
        .empty-message {{
            text-align: center;
            padding: 30px;
            color: #666;
        }}
        .message {{
            padding: 12px;
            margin: 15px 20px;
            text-align: center;
        }}
        .success {{
            background: #1a4d2e;
            color: #90ee90;
        }}
        .error {{
            background: #4d1a1a;
            color: #ff6b6b;
        }}
    </style>
    <script>
        function deleteFile(path) {{
            if (!confirm('Delete: ' + path + '?')) return;
            fetch(window.location.pathname, {{
                method: 'DELETE',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{path: path}})
            }})
            .then(r => r.json())
            .then(d => d.success ? location.reload() : alert('Error: ' + d.error))
            .catch(e => alert('Error: ' + e));
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📁 File Server</h1>
            <div class="current-path">Current Directory: {current_path}</div>
        </div>
        
        {message}
        
        <div class="upload-section">
            <form method="POST" enctype="multipart/form-data" class="upload-form">
                <div class="file-input-wrapper">
                    <input type="file" name="file" required multiple>
                </div>
                <button type="submit" class="upload-btn">⬆ Upload Files</button>
            </form>
        </div>
        
        <div class="files-section">
            <h2>📂 Files & Folders</h2>
            {files_html}
        </div>
    </div>
</body>
</html>
"""


class FileServerHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler for file server"""
    
    def do_GET(self):
        """Handle GET requests - show files or download"""
        # Parse the URL
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        path = urllib.parse.unquote(parsed_path.path)
        
        # Get the file path relative to server root
        file_path = self._get_safe_path(path)
        
        if file_path is None:
            self.send_error(403, "Access denied")
            return
        
        # If download parameter is present, serve the file or folder as ZIP
        if 'download' in query_params:
            if file_path.is_file():
                self._serve_file(file_path)
            elif file_path.is_dir():
                self._serve_directory_as_zip(file_path)
            else:
                self.send_error(404, "File not found")
        elif file_path.is_dir():
            self._list_directory(file_path)
        elif file_path.is_file():
            self._serve_file(file_path)
        else:
            self.send_error(404, "File not found")
    
    def do_DELETE(self):
        """Handle DELETE requests - delete files"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
            path = data.get('path', '')
            
            # Get the safe file path
            file_path = self._get_safe_path(path)
            
            if file_path is None:
                self._send_json_response({'success': False, 'error': 'Access denied'})
                return
            
            # Don't allow deleting the base directory
            if file_path == BASE_DIR:
                self._send_json_response({'success': False, 'error': 'Cannot delete base directory'})
                return
            
            # Delete the file or directory
            if file_path.is_file():
                file_path.unlink()
                self._send_json_response({'success': True, 'message': f'Deleted {file_path.name}'})
            elif file_path.is_dir():
                # Delete directory and contents
                import shutil
                shutil.rmtree(file_path)
                self._send_json_response({'success': True, 'message': f'Deleted directory {file_path.name}'})
            else:
                self._send_json_response({'success': False, 'error': 'File not found'})
        
        except Exception as e:
            self._send_json_response({'success': False, 'error': str(e)})
    
    def _send_json_response(self, data):
        """Send JSON response"""
        response = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
    
    def do_POST(self):
        """Handle POST requests - file upload"""
        content_type = self.headers.get('content-type', '')
        if not content_type.startswith('multipart/form-data'):
            self.send_error(400, "Expected multipart/form-data")
            return
        
        # Extract boundary
        boundary = content_type.split('boundary=')[1].encode()
        
        # Read the body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        # Parse multipart data
        uploaded_files = []
        parts = body.split(b'--' + boundary)
        
        for part in parts:
            if b'Content-Disposition' in part:
                # Extract filename
                if b'filename="' in part:
                    try:
                        filename_start = part.find(b'filename="') + 10
                        filename_end = part.find(b'"', filename_start)
                        filename = part[filename_start:filename_end].decode('utf-8')
                        
                        if filename:
                            # Extract file content
                            content_start = part.find(b'\r\n\r\n') + 4
                            content_end = part.rfind(b'\r\n')
                            file_content = part[content_start:content_end]
                            
                            # Save file
                            filename = os.path.basename(filename)
                            filepath = os.path.join(str(BASE_DIR), filename)
                            
                            with open(filepath, 'wb') as f:
                                f.write(file_content)
                            uploaded_files.append(filename)
                    except Exception as e:
                        print(f"Error processing file: {e}")
        
        # Redirect back with success message
        if uploaded_files:
            message = f"Uploaded: {', '.join(uploaded_files)}"
        else:
            message = "No files uploaded"
        
        self._list_directory(BASE_DIR, message, 'success' if uploaded_files else 'error')
    
    def _get_safe_path(self, url_path):
        """Get safe file path, preventing directory traversal"""
        # Remove leading slash and decode
        if url_path.startswith('/'):
            url_path = url_path[1:]
        
        # If empty, use base directory
        if not url_path:
            return BASE_DIR
        
        # Resolve the path
        requested_path = (BASE_DIR / url_path).resolve()
        
        # Make sure it's within the base directory
        try:
            requested_path.relative_to(BASE_DIR)
            return requested_path
        except ValueError:
            return None
    
    def _list_directory(self, dir_path, message=None, message_type=None):
        """List directory contents with HTML interface"""
        try:
            entries = os.listdir(dir_path)
        except OSError:
            self.send_error(404, "Cannot list directory")
            return
        
        # Separate directories and files
        directories = []
        files = []
        
        for entry in entries:
            entry_path = dir_path / entry
            if entry_path.is_dir():
                directories.append(entry)
            else:
                files.append(entry)
        
        # Sort each list alphabetically (case-insensitive)
        directories.sort(key=str.lower)
        files.sort(key=str.lower)
        
        # Build file list HTML
        files_html = []
        
        # Add parent directory link if not in root
        if dir_path != BASE_DIR:
            parent = dir_path.parent.relative_to(BASE_DIR)
            parent_path = f"/{parent}" if str(parent) != "." else "/"
            files_html.append(
                f'<li class="file-item">'
                f'📁 <a href="{parent_path}" class="file-name">..</a>'
                f'</li>'
            )
        
        # Add directories first
        for entry in directories:
            entry_path = dir_path / entry
            rel_path = entry_path.relative_to(BASE_DIR)
            url_path = '/' + str(rel_path).replace('\\', '/')
            
            files_html.append(
                f'<li class="file-item">'
                f'📁 <a href="{urllib.parse.quote(url_path)}" class="file-name">{html.escape(entry)}</a>'
                f'<a href="{urllib.parse.quote(url_path)}?download=1" class="delete-btn" style="background:#0066cc;text-decoration:none;">Download ZIP</a>'
                f'<button class="delete-btn" onclick="deleteFile(\'{url_path.replace(chr(39), chr(92)+chr(39))}\'); event.preventDefault();">Delete</button>'
                f'</li>'
            )
        
        # Then add files
        for entry in files:
            entry_path = dir_path / entry
            rel_path = entry_path.relative_to(BASE_DIR)
            url_path = '/' + str(rel_path).replace('\\', '/')
            
            size = entry_path.stat().st_size
            size_str = self._format_size(size)
            files_html.append(
                f'<li class="file-item">'
                f'📄 <a href="{urllib.parse.quote(url_path)}?download=1" class="file-name">{html.escape(entry)}</a>'
                f'<span class="file-size">{size_str}</span>'
                f'<button class="delete-btn" onclick="deleteFile(\'{url_path.replace(chr(39), chr(92)+chr(39))}\'); event.preventDefault();">Delete</button>'
                f'</li>'
            )
        
        if not files_html:
            files_html = ['<div class="empty-message">No files or folders</div>']
        
        # Build message HTML
        message_html = ''
        if message:
            message_html = f'<div class="message {message_type}">{html.escape(message)}</div>'
        
        # Render HTML
        current_path_display = str(dir_path)
        html_content = HTML_TEMPLATE.format(
            current_path=html.escape(current_path_display),
            message=message_html,
            files_html='<ul class="file-list">' + ''.join(files_html) + '</ul>'
        )
        
        # Send response
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(html_content.encode('utf-8')))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def _serve_file(self, file_path):
        """Serve a file for download"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Guess content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.send_header("Content-Length", len(content))
            self.send_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def _serve_directory_as_zip(self, dir_path):
        """Serve a directory as a ZIP file"""
        try:
            # Calculate total size first to check if it's too large
            total_size = 0
            file_count = 0
            MAX_SIZE = 500 * 1024 * 1024  # 500 MB limit
            MAX_FILES = 10000  # Max 10k files
            
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_count += 1
                    if file_count > MAX_FILES:
                        self.send_error(400, f"Directory has too many files (>{MAX_FILES}). Cannot create ZIP.")
                        return
                    
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        if total_size > MAX_SIZE:
                            self.send_error(400, f"Directory too large (>500MB). Cannot create ZIP.")
                            return
                    except:
                        continue
            
            # Create ZIP in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Walk through directory
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Calculate relative path for ZIP
                            arcname = os.path.relpath(file_path, dir_path)
                            zip_file.write(file_path, arcname)
                        except Exception as e:
                            # Skip files that can't be read (permission issues, etc.)
                            print(f"Skipping {file_path}: {e}")
                            continue
            
            # Get ZIP content
            zip_content = zip_buffer.getvalue()
            
            # Send response
            self.send_response(200)
            self.send_header("Content-type", "application/zip")
            self.send_header("Content-Length", len(zip_content))
            self.send_header("Content-Disposition", f'attachment; filename="{dir_path.name}.zip"')
            self.end_headers()
            self.wfile.write(zip_content)
        except ConnectionAbortedError:
            # Browser closed connection - just log and ignore
            print(f"Connection aborted while creating ZIP for {dir_path.name}")
        except Exception as e:
            print(f"Error creating ZIP: {str(e)}")
            try:
                self.send_error(500, f"Error creating ZIP: {str(e)}")
            except:
                pass
    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the file server"""
    host = "0.0.0.0"
    port = 1234
    
    server = HTTPServer((host, port), FileServerHandler)
    
    print("=" * 60)
    print(f"🚀 File Server Starting")
    print(f"📂 Serving directory: {BASE_DIR}")
    print(f"🌐 Server running on http://{host}:{port}/")
    print(f"💡 Access from this machine: http://localhost:{port}/")
    print(f"⚠️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        server.shutdown()


if __name__ == "__main__":
    main()
