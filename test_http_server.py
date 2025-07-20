# test_http_server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

class SimpleRaspberryServer(BaseHTTPRequestHandler):
    
    # Global değişkenler (sınıf değişkeni)
    globals_data = {
        "system_mode": 0,
        "calibration_flag": False,
        "fire_gui_flag": False,
        "engagement_started_flag": False,
        "emergency_stop": False,
        "system_active": False,
        "target_x": 0.0,
        "target_y": 0.0,
        "target_locked": False,
        "selected_weapon": "Auto"
    }
    
    def do_GET(self):
        """GET istekleri - ping için"""
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "ok", 
                "message": "Raspberry Pi Test Server",
                "timestamp": time.strftime("%H:%M:%S")
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_error(404, "Endpoint bulunamadı")
    
    def do_POST(self):
        """POST istekleri - komutlar için"""
        if self.path == '/command':
            try:
                # POST verisini al
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # Komutu ekrana yazdır
                print(f"\n📥 [{time.strftime('%H:%M:%S')}] Komut alındı:")
                print(f"   📊 Raw JSON: {json.dumps(data, indent=4)}")
                
                # Global değişkenleri güncelle
                updated_vars = []
                for key, value in data.items():
                    if key in self.globals_data:
                        old_value = self.globals_data[key]
                        self.globals_data[key] = value
                        updated_vars.append(f"{key}: {old_value} → {value}")
                        print(f"   🔄 {key}: {old_value} → {value}")
                    else:
                        print(f"   ⚠️  Bilinmeyen değişken: {key} = {value}")
                
                # Özel komut simülasyonları
                self.simulate_actions(data)
                
                # Başarı yanıtı gönder
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": f"{len(updated_vars)} değişken güncellendi",
                    "updated_variables": updated_vars,
                    "current_globals": self.globals_data.copy(),
                    "timestamp": time.strftime("%H:%M:%S")
                }
                
                self.wfile.write(json.dumps(response).encode())
                print(f"   📤 Yanıt gönderildi: {response['message']}")
                
            except json.JSONDecodeError:
                self.send_error(400, "Geçersiz JSON formatı")
                print("   ❌ Geçersiz JSON!")
            except Exception as e:
                self.send_error(500, f"Server hatası: {str(e)}")
                print(f"   ❌ Server hatası: {e}")
        else:
            self.send_error(404, "Endpoint bulunamadı")
    
    def simulate_actions(self, data):
        """Komutlara özel simülasyonlar"""
        # Sistem başlatma
        if data.get("system_active") == True:
            print("   🚀 SİSTEM BAŞLATILIYOR...")
            print("   ✅ Tüm sistemler aktif!")
        
        # Sistem durdurma
        if data.get("system_active") == False:
            print("   🛑 SİSTEM DURDURULDU")
        
        # Acil durdur
        if data.get("emergency_stop") == True:
            print("   🚨 ACİL DURDUR AKTİVE!")
            print("   🔴 TÜM OPERASYONLAR DURDURULDU!")
        
        # Ateş komutu
        if data.get("fire_gui_flag") == True:
            print("   💥 ATEŞ KOMUTİ ALINDI!")
            print("   🎯 Hedef işaretlendi ve ateş edildi!")
        
        # Aşama değişimi
        if "system_mode" in data:
            mode = data["system_mode"]
            mode_names = {0: "Manuel Mod", 1: "Aşama 1 - Temel Hedef", 2: "Aşama 2 - Düşman Tespiti", 3: "Aşama 3 - Angajman"}
            print(f"   🎮 Sistem modu: {mode_names.get(mode, f'Mod {mode}')}")
        
        # Hedef pozisyonu
        if "target_x" in data and "target_y" in data:
            x, y = data["target_x"], data["target_y"]
            print(f"   🎯 Hedef pozisyonu güncellendi: X={x:.1f}, Y={y:.1f}")
    
    def log_message(self, format, *args):
        """HTTP server loglarını bastır (sadece bizim mesajlarımız görünsün)"""
        pass

def start_test_server(port=8000):
    """Test server'ı başlat"""
    try:
        print("🚀 Raspberry Pi Test HTTP Server")
        print("=" * 50)
        print(f"🌐 Adres: http://localhost:{port}")
        print(f"📍 Endpoints:")
        print(f"   GET  /ping     → Bağlantı testi")
        print(f"   POST /command  → Komut gönder")
        print("=" * 50)
        print("✅ Server başlatıldı! GUI'yi çalıştırabilirsin...")
        print("🔄 Komutları bekleniyor... (Ctrl+C ile durdur)")
        print()
        
        server = HTTPServer(('localhost', port), SimpleRaspberryServer)
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server durduruldu (Ctrl+C)")
    except Exception as e:
        print(f"❌ Server hatası: {e}")

if __name__ == "__main__":
    start_test_server()