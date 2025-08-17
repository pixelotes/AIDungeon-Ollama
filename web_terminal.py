#!/usr/bin/env python3
"""
Web Terminal Server for AI Dungeon Clover Edition
Runs the terminal app through a web interface using websockets.
"""
import asyncio
import json
import os
import signal
import sys
import threading
import time
import shutil
from pathlib import Path

import pexpect
import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
from urllib.parse import urlparse, parse_qs

class WebTerminalServer:
    def __init__(self, command="python launch.py", port=8080, ws_port=8765):
        self.command = command
        self.port = port
        self.ws_port = ws_port
        self.clients = set()
        self.process = None
        self.running = False
        
    def start_process(self):
        """Start the AI Dungeon process"""
        try:
            # Start the process with pseudo-terminal
            self.process = pexpect.spawn(
                self.command,
                timeout=None,
                encoding='utf-8',
                dimensions=(24, 80)
            )
            self.process.setwinsize(24, 80)
            print(f"Started process: {self.command}")
            return True
        except Exception as e:
            print(f"Failed to start process: {e}")
            return False
    
    def stop_process(self):
        """Stop the AI Dungeon process"""
        if self.process and self.process.isalive():
            self.process.terminate()
            self.process = None
    
    async def handle_websocket(self, websocket):
        """Handle websocket connections from web clients"""
        print(f"New client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        
        try:
            # Start the process if not already running
            if not self.process or not self.process.isalive():
                if not self.start_process():
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'data': 'Failed to start AI Dungeon process'
                    }))
                    return
            
            # Start reading from process in background
            read_task = asyncio.create_task(self.read_from_process(websocket))
            
            # Handle incoming messages from client
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data['type'] == 'input':
                        # Send input to the process
                        input_text = data['data']
                        if self.process and self.process.isalive():
                            self.process.send(input_text + '\n')
                    elif data['type'] == 'resize':
                        # Handle terminal resize
                        if self.process and self.process.isalive():
                            rows = data.get('rows', 24)
                            cols = data.get('cols', 80)
                            self.process.setwinsize(rows, cols)
                except json.JSONDecodeError:
                    print("Invalid JSON received from client")
                except Exception as e:
                    print(f"Error handling client message: {e}")
                    
        except (ConnectionClosedError, ConnectionClosedOK):
            print(f"Client disconnected: {websocket.remote_address}")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            self.clients.discard(websocket)
            if 'read_task' in locals():
                read_task.cancel()
            
    async def read_from_process(self, websocket):
        """Read output from the process and send to websocket"""
        try:
            while self.process and self.process.isalive():
                try:
                    # Read from process with timeout
                    output = self.process.read_nonblocking(size=1024, timeout=0.1)
                    if output:
                        await websocket.send(json.dumps({
                            'type': 'output',
                            'data': output
                        }))
                except pexpect.TIMEOUT:
                    # No output available, continue
                    await asyncio.sleep(0.01)
                except pexpect.EOF:
                    # Process ended
                    await websocket.send(json.dumps({
                        'type': 'output',
                        'data': '\n[Process ended]\n'
                    }))
                    break
                except Exception as e:
                    print(f"Error reading from process: {e}")
                    break
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in read_from_process: {e}")
    
    def start_http_server(self):
        """Start HTTP server for serving the web interface"""
        class CustomHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                # Get the directory where this script is located
                directory = str(Path(__file__).parent)
                super().__init__(*args, directory=directory, **kwargs)
            
            def log_message(self, format, *args):
                # Suppress HTTP server logs
                pass
            
            def end_headers(self):
                # Add CORS headers for development
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                super().end_headers()
        
        try:
            httpd = HTTPServer(('0.0.0.0', self.port), CustomHandler)
            print(f"HTTP server running on http://0.0.0.0:{self.port}")
            httpd.serve_forever()
        except Exception as e:
            print(f"Failed to start HTTP server: {e}")
    
    async def start_websocket_server(self):
        """Start WebSocket server"""
        print(f"WebSocket server starting on ws://0.0.0.0:{self.ws_port}")
        try:
            # Use the newer websockets API
            async with websockets.serve(
                self.handle_websocket, 
                '0.0.0.0', 
                self.ws_port,
                ping_interval=30,
                ping_timeout=10
            ):
                await asyncio.Future()  # Run forever
        except Exception as e:
            print(f"Failed to start WebSocket server: {e}")
            raise
    
    def run(self):
        """Run the web terminal server"""
        print("Starting AI Dungeon Web Terminal...")
        print(f"Web interface will be available at: http://localhost:{self.port}")
        print(f"WebSocket server at: ws://localhost:{self.ws_port}")
        
        # Check if index.html exists
        index_file = Path(__file__).parent / "index.html"
        if not index_file.exists():
            print("Warning: index.html not found in the current directory!")
            print(f"Looking for: {index_file}")
        
        # Start HTTP server in separate thread
        http_thread = threading.Thread(target=self.start_http_server, daemon=True)
        http_thread.start()
        
        # Wait a moment for HTTP server to start
        time.sleep(1)
        
        # Open browser automatically
        try:
            webbrowser.open(f"http://localhost:{self.port}")
            print("Opened browser automatically")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print(f"Please manually open: http://localhost:{self.port}")
        
        # Start WebSocket server
        try:
            asyncio.run(self.start_websocket_server())
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop_process()

def find_python_executable():
    """Find the correct Python executable"""
    import shutil
    
    # Try different Python executable names
    python_names = ['python3', 'python', 'python3.11', 'python3.12', 'python3.13']
    
    for name in python_names:
        if shutil.which(name):
            return name
    
    # Fallback to sys.executable (the current Python interpreter)
    return sys.executable

if __name__ == "__main__":
    # Find the correct Python executable
    python_exec = find_python_executable()
    
    # Parse command line arguments
    command = f"{python_exec} -m aidungeon"
    port = 8080
    ws_port = 8765
    
    if len(sys.argv) > 1:
        # If user provides custom command, use it as-is
        command = " ".join(sys.argv[1:])
    
    print(f"Using Python executable: {python_exec}")
    
    server = WebTerminalServer(command=command, port=port, ws_port=ws_port)
    server.run()