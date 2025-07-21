# test_server.py - Raspberry Pi simülasyonu
import asyncio
import websockets
import json
from datetime import datetime

class FakeRaspberryServer:
    """Raspberry Pi WebSocket server simülasyonu"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        
        # Sahte global değişkenler
        self.globals = {
            "system_mode": 0,
            "calibration_flag": False,
            "fire_gui_flag": False,
            "engagement_started_flag": False,
            "emergency_stop": False,
            "system_active": False,
            "target_x": 0.0,
            "target_y": 0.0,
            "target_locked": False,
            "selected_weapon": "Auto",
            "pan_angle": 0.0,
            "tilt_angle": 0.0
        }
    
    async def handle_client(self, websocket, path):
        """Yeni client bağlantısı"""
        self.clients.add(websocket)
        client_ip = websocket.remote_address[0]
        
        print(f"🟢 Yeni bağlantı: {client_ip}")
        print(f"👥 Toplam bağlantı: {len(self.clients)}")
        
        try:
            # Hoş geldin mesajı gönder
            welcome_msg = {
                "status": "connected",
                "message": "Fake Raspberry Pi Server",
                "timestamp": datetime.now().isoformat(),
                "current_state": self.globals.copy()
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Mesajları dinle
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"🔴 Bağlantı kapandı: {client_ip}")
        except Exception as e:
            print(f"❌ Hata: {e}")
        finally:
            self.clients.remove(websocket)
    
    async def process_message(self, websocket, message):
        """Gelen mesajları işle"""
        try:
            data = json.loads(message)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n📥 [{timestamp}] Komut alındı:")
            print(f"   💾 Raw data: {message}")
            print(f"   📊 Parsed: {json.dumps(data, indent=6)}")
            
            # Global değişkenleri güncelle
            updated_vars = []
            for key, value in data.items():
                if key in self.globals:
                    old_value = self.globals[key]
                    self.globals[key] = value
                    updated_vars.append(f"{key}: {old_value} → {value}")
                    print(f"   🔄 {key}: {old_value} → {value}")
                else:
                    print(f"   ⚠️  Bilinmeyen değişken: {key}")
            
            # Yanıt mesajı oluştur
            response = {
                "status": "success",
                "message": f"{len(updated_vars)} değişken güncellendi",
                "updated_variables": updated_vars,
                "current_state": self.globals.copy(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Yanıt gönder
            await websocket.send(json.dumps(response))
            print(f"   📤 Yanıt gönderildi: {response['message']}")
            
            # Özel komutları simüle et
            await self.simulate_responses(data)
            
        except json.JSONDecodeError:
            error_response = {
                "status": "error",
                "message": "Geçersiz JSON formatı",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(error_response))
            print(f"   ❌ Geçersiz JSON: {message}")
        except Exception as e:
            print(f"   ❌ İşleme hatası: {e}")
    
    async def simulate_responses(self, data):
        """Özel komutlara özel yanıtlar simüle et"""
        
        # Sistem başlatma
        if data.get("system_active") == True:
            print("   🚀 SİSTEM BAŞLATILIYOR...")
            await asyncio.sleep(0.5)
            print("   ✅ Sistem aktif!")
        
        # Acil durdur
        if data.get("emergency_stop") == True:
            print("   🚨 ACİL DURDUR AKTİVE!")
            print("   🛑 Tüm sistemler durduruldu!")
        
        # Ateş komutu
        if data.get("fire_gui_flag") == True:
            print("   💥 ATEŞ KOMUTİ ALINDI!")
            print("   🎯 Hedef işaretlendi!")
        
        # Kalibrasyon
        if data.get("calibration_flag") == True:
            print("   🔧 KALİBRASYON BAŞLADI...")
            for i in range(3):
                await asyncio.sleep(0.3)
                print(f"   📐 Kalibrasyon adım {i+1}/3")
            print("   ✅ Kalibrasyon tamamlandı!")
        
        # Aşama değişimi
        if "system_mode" in data:
            mode = data["system_mode"]
            mode_names = {0: "Manuel", 1: "Aşama 1", 2: "Aşama 2", 3: "Aşama 3"}
            print(f"   🎮 Sistem modu değişti: {mode_names.get(mode, 'Bilinmeyen')}")
    
    def start_server(self):
        """Server'ı başlat"""
        print("🚀 Fake Raspberry Pi WebSocket Server Başlatılıyor...")
        print(f"🌐 Adres: ws://{self.host}:{self.port}")
        print(f"📊 İlk durum: {json.dumps(self.globals, indent=2)}")
        print("=" * 60)
        
        async def main():
            """Ana async fonksiyon"""
            async with websockets.serve(self.handle_client, self.host, self.port):
                print("✅ Server başlatıldı! Bağlantı bekleniyor...")
                print("🔄 GUI'yi başlatabilirsin (Ctrl+C ile durdur)")
                await asyncio.Future()  # Sonsuz bekle
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n🛑 Server durduruldu (Ctrl+C)")
        except Exception as e:
            print(f"❌ Server hatası: {e}")

# Test komutu
def test_client():
    """Test client - server'ı test etmek için"""
    import websocket
    import time
    import threading
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            print(f"📥 Yanıt: {data.get('message', 'Mesaj yok')}")
        except:
            print(f"📥 Ham yanıt: {message}")
    
    def on_error(ws, error):
        print(f"❌ Client hatası: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("🔴 Client bağlantısı kapandı")
    
    def on_open(ws):
        print("✅ Test client bağlandı")
        
        def send_commands():
            # Test komutları gönder
            test_commands = [
                {"system_mode": 1, "system_active": True},
                {"fire_gui_flag": True, "engagement_started_flag": True},
                {"target_x": 150.5, "target_y": 200.3},
                {"calibration_flag": True},
                {"emergency_stop": True}
            ]
            
            for i, cmd in enumerate(test_commands):
                time.sleep(2)
                if ws.sock and ws.sock.connected:
                    ws.send(json.dumps(cmd))
                    print(f"📤 Test komutu {i+1}: {cmd}")
                else:
                    print("❌ Bağlantı kesildi, komut gönderilemedi")
                    break
        
        # Komutları ayrı thread'de gönder
        threading.Thread(target=send_commands, daemon=True).start()
    
    print("🧪 Test client başlatılıyor...")
    print("🔗 ws://localhost:8765 adresine bağlanmaya çalışıyor...")
    
    ws = websocket.WebSocketApp(
        "ws://localhost:8765",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # 10 saniye test yap
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("🛑 Test client durduruldu")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test client çalıştır
        print("🧪 Test client başlatılıyor...")
        test_client()
    else:
        # Server çalıştır
        server = FakeRaspberryServer()
        server.start_server()