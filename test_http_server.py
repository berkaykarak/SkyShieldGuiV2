# test_http_server.py - FIXED VERSION
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import threading
import random

class FixedRaspberryServer(BaseHTTPRequestHandler):
    
    # Global değişkenler
    server_data = {
        "system_mode": 0,
        "system_active": False,
        "fire_gui_flag": False,
        "engagement_started_flag": False,
        "emergency_stop": False,
        "calibration_flag": False,
        
        # Raspberry Pi'de oluşacak veriler (simülasyon)
        "x_target": 320,
        "y_target": 240,
        "global_angle": 0.0,
        "global_tilt_angle": 0.0,
        "target_detected_flag": False,
        "weapon": "E",
        "target_destroyed_flag": False,
        "scanning_target_flag": False
    }
    
    command_history = []
    
    def do_GET(self):
        """GET istekleri"""
        if self.path == '/ping':
            self._send_ping_response()
            
        elif self.path == '/status':
            self._send_status_response()
            
        elif self.path == '/commands':
            self._send_command_history()
            
        else:
            # Unicode hatasını önlemek için ASCII mesaj
            self.send_error(404, "Endpoint not found")
    
    def do_POST(self):
        """POST istekleri"""
        if self.path == '/command':
            self._handle_command()
        else:
            self.send_error(404, "Endpoint not found")
    
    def _send_ping_response(self):
        """Ping yanıtı"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "Raspberry Pi Test Server",
            "timestamp": time.strftime("%H:%M:%S"),
            "server_uptime": time.time(),
            "commands_received": len(self.command_history)
        }
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        print(f"📤 [{time.strftime('%H:%M:%S')}] Ping response sent")
    
    def _send_status_response(self):
        """Sistem durumu yanıtı - GUI'nin beklediği format"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Simülasyon verilerini güncelle
        self._update_simulation_data()
        
        # GUI'nin beklediği format
        response = {
            "timestamp": time.strftime("%H:%M:%S"),
            "status": "active",
            
            # Sistem durumu
            "system_mode": self.server_data["system_mode"],
            "system_active": self.server_data["system_active"],
            "emergency_stop": self.server_data["emergency_stop"],
            
            # Hedef bilgileri (simülasyon)
            "x_target": self.server_data["x_target"],
            "y_target": self.server_data["y_target"],
            "target_detected_flag": self.server_data["target_detected_flag"],
            "target_destroyed_flag": self.server_data["target_destroyed_flag"],
            "scanning_target_flag": self.server_data["scanning_target_flag"],
            
            # Motor açıları (simülasyon)
            "global_angle": self.server_data["global_angle"],
            "global_tilt_angle": self.server_data["global_tilt_angle"],
            
            # Mühimmat
            "weapon": self.server_data["weapon"],
            
            # Ek simülasyon verileri
            "distance": random.uniform(50, 300),
            "speed": random.uniform(5, 25),
            "target_locked": self.server_data["target_detected_flag"],
            "pan_angle": self.server_data["global_angle"],
            "tilt_angle": self.server_data["global_tilt_angle"]
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        print(f"📤 [{time.strftime('%H:%M:%S')}] Status sent - Mode: {response['system_mode']}")
    
    def _send_command_history(self):
        """Komut geçmişi"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "total_commands": len(self.command_history),
            "last_10_commands": self.command_history[-10:],
            "current_state": self.server_data.copy()
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def _handle_command(self):
        """Komut işleme"""
        try:
            # POST verisini al
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Timestamp ekle
            command_entry = {
                "timestamp": time.strftime("%H:%M:%S"),
                "received_data": data,
                "changes_made": []
            }
            
            print(f"\n📥 [{time.strftime('%H:%M:%S')}] KOMUT ALINDI:")
            print("=" * 50)
            print(f"📊 Raw JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
            print("=" * 50)
            
            # Veriyi işle
            changes = self._process_command_data(data)
            command_entry["changes_made"] = changes
            
            # Komut geçmişine ekle
            self.command_history.append(command_entry)
            if len(self.command_history) > 100:
                self.command_history = self.command_history[-100:]
            
            # Başarı yanıtı
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "success",
                "message": f"{len(changes)} variable updated",
                "changes_made": changes,
                "current_state": self.server_data.copy(),
                "timestamp": time.strftime("%H:%M:%S")
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            
            print(f"📤 Response sent: {len(changes)} changes made")
            print("=" * 50)
            
        except json.JSONDecodeError as e:
            self._send_error_response(400, f"Invalid JSON: {e}")
        except Exception as e:
            self._send_error_response(500, f"Server error: {e}")
    
    def _process_command_data(self, data):
        """Gelen veriyi işle ve değişiklikleri kaydet"""
        changes = []
        
        for key, value in data.items():
            if key in self.server_data:
                old_value = self.server_data[key]
                self.server_data[key] = value
                
                change_info = f"{key}: {old_value} -> {value}"
                changes.append(change_info)
                print(f"   🔄 {change_info}")
                
                # Özel işlemler
                self._handle_special_commands(key, value)
                
            elif key in ["timestamp", "source"]:
                # Metadata, işleme dahil etme
                print(f"   📝 Metadata: {key} = {value}")
            else:
                print(f"   ⚠️ Unknown field: {key} = {value}")
        
        return changes
    
    def _handle_special_commands(self, key, value):
        """Özel komut işlemleri"""
        if key == "system_mode":
            mode_names = {0: "Manuel", 1: "Stage 1", 2: "Stage 2", 3: "Stage 3"}
            print(f"   🎮 System mode: {mode_names.get(value, f'Mode {value}')}")
            
        elif key == "system_active" and value:
            print(f"   🚀 SYSTEM STARTING...")
            # Simülasyon: sistem başladığında tarama başlat
            self.server_data["scanning_target_flag"] = True
            
        elif key == "fire_gui_flag" and value:
            print(f"   💥 FIRE COMMAND ACTIVE!")
            
        elif key == "emergency_stop" and value:
            print(f"   🚨 EMERGENCY STOP ACTIVE!")
            # Simülasyon: tüm işlemleri durdur
            self.server_data["system_active"] = False
            self.server_data["fire_gui_flag"] = False
            self.server_data["scanning_target_flag"] = False
            
        elif key == "calibration_flag" and value:
            print(f"   🔧 CALIBRATION STARTING...")
    
    def _update_simulation_data(self):
        """Raspberry Pi verilerini simüle et"""
        if self.server_data["system_active"]:
            # Hedef pozisyonu simülasyonu
            self.server_data["x_target"] = random.randint(250, 450)
            self.server_data["y_target"] = random.randint(180, 320)
            
            # Açı simülasyonu
            self.server_data["global_angle"] = random.uniform(-90, 90)
            self.server_data["global_tilt_angle"] = random.uniform(-30, 30)
            
            # Hedef tespiti simülasyonu
            self.server_data["target_detected_flag"] = random.choice([True, False])
            
            # Mühimmat simülasyonu
            if self.server_data["target_detected_flag"]:
                self.server_data["weapon"] = random.choice(["L", "A"])
            else:
                self.server_data["weapon"] = "E"
    
    def _send_error_response(self, code, message):
        """Hata yanıtı"""
        self.send_error(code, message)
        print(f"❌ Error: {code} - {message}")
    
    def log_message(self, format, *args):
        """HTTP logları bastır"""
        pass

def start_fixed_test_server(port=8000):
    """Düzeltilmiş test server'ı başlat"""
    try:
        print("🚀 Fixed Raspberry Pi Test Server")
        print("=" * 60)
        print(f"🌐 Address: http://localhost:{port}")
        print(f"📍 Endpoints:")
        print(f"   GET  /ping      → Connection test")
        print(f"   GET  /status    → System status (simulation data)")
        print(f"   GET  /commands  → Command history")
        print(f"   POST /command   → Send command")
        print("=" * 60)
        print("✅ Server started!")
        print("📝 You will see detailed incoming commands...")
        print("🔄 You can start GUI now (Ctrl+C to stop)")
        print()
        
        server = HTTPServer(('localhost', port), FixedRaspberryServer)
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped (Ctrl+C)")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_fixed_test_server()