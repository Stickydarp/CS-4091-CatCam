# CatCam Server
# Receives images, performs basic CV detection, and issues commands

import socket
import os
import json
from datetime import datetime
from threading import Thread
import time

# Configuration
HOST = '0.0.0.0'
PORT = 8888
SAVE_DIR = 'received_images'
METADATA_DIR = 'metadata'
LOG_FILE = 'catcam_log.txt'

# Detection thresholds (placeholder for future CV implementation)
DETECTION_CONFIDENCE_THRESHOLD = 0.7
CONSECUTIVE_DETECTIONS_REQUIRED = 3

# Global state
device_states = {}
recent_detections = {}

class CatCamServer:
    def __init__(self):
        self.running = False
        self.frame_count = 0
        
        # Create directories
        os.makedirs(SAVE_DIR, exist_ok=True)
        os.makedirs(METADATA_DIR, exist_ok=True)
        
        self.log(f"Server initialized. Images will be saved to: {SAVE_DIR}")
        self.log(f"Server IP: {HOST}, Port: {PORT}")
    
    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_message + '\n')
    
    def process_cv_detection(self, image_path, metadata):
        """
        Placeholder for computer vision cat detection
        Returns: (detected: bool, confidence: float, bbox: dict or None)
        """
        # TODO: Implement actual CV detection here
        # For now, this is a simple placeholder that simulates detection
        
        # Simulate detection logic based on motion sensor
        motion_detected = metadata.get('sensor', {}).get('motion', False)
        
        if motion_detected:
            # Simulate higher probability of detection when motion is present
            # In real implementation, this would run actual CV model
            confidence = 0.8
            detected = True
            bbox = {"x": 100, "y": 80, "width": 120, "height": 100}
        else:
            confidence = 0.1
            detected = False
            bbox = None
        
        return detected, confidence, bbox
    
    def determine_next_mode(self, device_id, detection_result, metadata):
        """
        Determine what mode the device should be in based on detection results
        Returns: (next_mode: str, action: str, message: str)
        """
        detected, confidence, bbox = detection_result
        current_mode = metadata.get('mode', 'standby')
        
        # Track detection history for this device
        if device_id not in recent_detections:
            recent_detections[device_id] = []
        
        # Add current detection to history (keep last 5)
        recent_detections[device_id].append(detected)
        if len(recent_detections[device_id]) > 5:
            recent_detections[device_id].pop(0)
        
        # Count recent positive detections
        recent_positive = sum(recent_detections[device_id])
        
        # Decision logic
        if current_mode == "standby":
            if detected and confidence > DETECTION_CONFIDENCE_THRESHOLD:
                return "alert", "none", "Cat detected - entering alert mode"
            else:
                return "standby", "none", "No detection - remaining in standby"
        
        elif current_mode == "alert":
            if recent_positive >= CONSECUTIVE_DETECTIONS_REQUIRED:
                return "active", "start_stream", "Multiple detections - entering active mode"
            elif detected:
                return "remain_alert", "none", "Detection in progress - remaining in alert"
            else:
                # Let the device timeout naturally
                return "alert", "none", "Monitoring continues"
        
        elif current_mode == "active":
            if not detected and recent_positive < 2:
                return "standby", "stop_stream", "No recent detections - returning to standby"
            else:
                return "active", "none", "Continuing active monitoring"
        
        return "standby", "none", "Default response"
    
    def handle_client(self, client_sock, client_addr):
        """Handle incoming image upload from device"""
        try:
            # Receive metadata line
            metadata_bytes = b''
            while True:
                byte = client_sock.recv(1)
                if not byte or byte == b'\n':
                    break
                metadata_bytes += byte
            
            # Parse metadata
            meta_str = metadata_bytes.decode('utf-8').strip()
            parts = meta_str.split(',')
            
            if len(parts) < 2:
                self.log(f"Invalid metadata from {client_addr}")
                client_sock.close()
                return
            
            frame_num = parts[0]
            img_size = int(parts[1])
            
            self.log(f"Receiving frame {frame_num}: {img_size} bytes from {client_addr[0]}")
            
            # Receive image data
            img_data = b''
            remaining = img_size
            
            while remaining > 0:
                chunk = client_sock.recv(min(8192, remaining))
                if not chunk:
                    break
                img_data += chunk
                remaining -= len(chunk)
            
            # Verify we got all data
            if len(img_data) != img_size:
                self.log(f"ERROR: Expected {img_size} bytes, got {len(img_data)} bytes")
                client_sock.close()
                return
            
            # Save image
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"frame_{frame_num.zfill(4)}_{timestamp_str}.jpg"
            filepath = os.path.join(SAVE_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(img_data)
            
            self.frame_count += 1
            self.log(f"Saved to {filename}")
            
            # Try to receive JSON metadata if sent (optional extended protocol)
            try:
                client_sock.settimeout(0.5)
                json_data = client_sock.recv(2048)
                if json_data:
                    metadata = json.loads(json_data.decode())
                else:
                    metadata = self.create_basic_metadata(frame_num)
            except:
                metadata = self.create_basic_metadata(frame_num)
            
            # Save metadata
            metadata_file = os.path.join(METADATA_DIR, f"frame_{frame_num.zfill(4)}_{timestamp_str}.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Process CV detection
            detection_result = self.process_cv_detection(filepath, metadata)
            detected, confidence, bbox = detection_result
            
            device_id = metadata.get('device_id', 'unknown')
            
            # Determine next mode
            next_mode, action, message = self.determine_next_mode(
                device_id, detection_result, metadata
            )
            
            # Prepare response
            response = {
                "status": "ok",
                "frame": frame_num,
                "next_mode": next_mode,
                "action": action,
                "message": message,
                "detection": {
                    "cat_detected": detected,
                    "confidence": confidence,
                    "bbox": bbox
                }
            }
            
            # Send response back to device
            response_json = json.dumps(response) + '\n'
            try:
                client_sock.send(response_json.encode())
            except:
                pass  # Device may not be waiting for response
            
            # Log detection result
            if detected:
                self.log(f" Cat detected! Confidence: {confidence:.2f}, Next mode: {next_mode}")
            else:
                self.log(f"  No cat detected. Next mode: {next_mode}")
            
            # Update device state
            device_states[device_id] = {
                "last_seen": datetime.now().isoformat(),
                "mode": next_mode,
                "frame_count": frame_num,
                "last_detection": detected
            }
            
        except Exception as e:
            self.log(f"Error handling client: {e}")
        finally:
            client_sock.close()
    
    def create_basic_metadata(self, frame_num):
        """Create basic metadata when extended metadata is not available"""
        return {
            "device_id": "unknown",
            "timestamp_utc": datetime.now().isoformat(),
            "mode": "unknown",
            "seq": frame_num,
            "sensor": {
                "motion": False,
                "temperature_c": 0.0,
                "humidity": 0.0
            }
        }
    
    def start(self):
        """Start the server"""
        self.running = True
        
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(5)
        
        self.log("=" * 60)
        self.log("CatCam Server Started")
        self.log(f"Listening on {HOST}:{PORT}")
        self.log("Waiting for images from Nicla Vision...")
        self.log("=" * 60)
        
        try:
            while self.running:
                try:
                    server_sock.settimeout(1.0)
                    client_sock, client_addr = server_sock.accept()
                    
                    # Handle each client in a separate thread
                    client_thread = Thread(
                        target=self.handle_client,
                        args=(client_sock, client_addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    self.log(f"Accept error: {e}")
        
        except KeyboardInterrupt:
            self.log("\nShutdown requested...")
        finally:
            server_sock.close()
            self.log(f"Server stopped. Received {self.frame_count} images total")
    
    def stop(self):
        """Stop the server"""
        self.running = False

def main():
    server = CatCamServer()
    
    try:
        server.start()
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()
