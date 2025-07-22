# test_websocket_server.py
import asyncio
import websockets
import json
import logging
import random
import time
from datetime import datetime

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class TestWebSocketServer:
    """
    Raspberry Pi WebSocket server'ını simüle eden test server'ı
    HTTP kaldırıldı, sadece WebSocket
    """
    
    def __init__(self, host="localhost", port=9000):
        self.host = host
        self.port = port
        self.clients = set()
        
        # Simüle edilen shared memory
        self.shared_data = {
            # Sistem durumu
            "system_mode": -1,
            "target_destroyed_flag": False,
            "scanning_target_flag": False,
            
            # Açı bilgileri
            "global_angle": 0.0,
            "global_tilt_angle": 0.0,
            
            # Hedef bilgileri
            "x_target": 320,
            "y_target": 240,
            "weapon": "E",
            "target_side": "O",
            "target_detected_flag": False,
            
            # PID çıktıları
            "correction_pan": 0,
            "correction_tilt": 0,
            "error_x": 0.0,
            "error_y": 0.0,
            
            # Joystick
            "pan": 0,
            "tilt": 0,
            "btn_thumb2": False,
            "btn_south": False,
            "btn_east": False,
            "btn_west": False,
            "fine_mode": False,
            
            # GUI bayrakları
            "calibration_flag": False,
            "fire_gui_flag": False,
            "engagement_started_flag": False
        }
        
        self.command_count = 0
        self.start_time = time.time()
    
    async def handle_client(self, websocket):
        """Yeni client bağlantısını yönet"""
        client_ip = websocket.remote_address[0]
        self.clients.add(websocket)
        
        logging.info(f"🟢 Yeni WebSocket bağlantısı: {client_ip} (Toplam: {len(self.clients)})")
        # path parametresi websockets 15.x'te handler'a gönderilmiyor
        
        try:
            # Hoş geldin mesajı
            welcome = {
                "status": "connected",
                "message": "Test WebSocket Server",
                "server_time": datetime.now().isoformat(),
                "uptime": time.time() - self.start_time
            }
            await websocket.send(json.dumps(welcome))
            
            # Paralel görevler
            await asyncio.gather(
                self.receive_commands(websocket),
                self.send_state_updates(websocket)
            )
            
        except websockets.exceptions.ConnectionClosed:
            logging.warning(f"🔴 Bağlantı kapandı: {client_ip}")
        except websockets.exceptions.ConnectionClosedError as e:
            logging.warning(f"🔴 Bağlantı zorla kapandı: {client_ip} - {e}")
        except websockets.exceptions.ConnectionClosedOK as e:
            logging.info(f"✅ Bağlantı normal kapandı: {client_ip}")
        except Exception as e:
            logging.error(f"❌ Client hatası ({type(e).__name__}): {e}")
            import traceback
            logging.error(f"📋 Traceback: {traceback.format_exc()}")
        finally:
            self.clients.discard(websocket)
            logging.info(f"📊 Kalan bağlantı sayısı: {len(self.clients)}")
    
    async def receive_commands(self, websocket):
        """GUI'den gelen komutları dinle"""
        async for message in websocket:
            try:
                data = json.loads(message)
                self.command_count += 1
                
                logging.info(f"📥 Komut #{self.command_count}: {json.dumps(data, indent=2)}")
                
                # Komutları işle
                changes = self.process_command(data)
                
                # Özel işlemler
                await self.simulate_command_effects(data)
                
                logging.info(f"✅ {len(changes)} değişken güncellendi")
                
            except json.JSONDecodeError as e:
                logging.error(f"❌ JSON parse hatası: {e}")
            except Exception as e:
                logging.error(f"❌ Komut işleme hatası: {e}")
    
    async def send_state_updates(self, websocket):
        """Sürekli sistem durumunu gönder"""
        logging.info("📡 Durum güncellemeleri başlatıldı (10 Hz)")
        previous_state = None
        
        while True:
            try:
                # Aktif sistemde simülasyon yap
                if self.shared_data["system_mode"] > 0:
                    self.update_simulation()
                
                # Durumu hazırla
                state = self.shared_data.copy()
                state["timestamp"] = datetime.now().isoformat()
                state["server_uptime"] = time.time() - self.start_time
                
                # Değişiklik kontrolü (timestamp hariç)
                state_without_timestamp = {k: v for k, v in state.items() 
                                         if k not in ["timestamp", "server_uptime"]}
                
                if previous_state != state_without_timestamp:
                    # Değişen alanları bul
                    if previous_state is not None:
                        changes = []
                        for key, value in state_without_timestamp.items():
                            if key not in previous_state or previous_state[key] != value:
                                old_val = previous_state.get(key, "N/A")
                                changes.append(f"{key}: {old_val} → {value}")
                        
                        if changes:
                            logging.info(f"📊 Veri değişikliği algılandı: {', '.join(changes[:3])}")
                            if len(changes) > 3:
                                logging.info(f"   ... ve {len(changes)-3} alan daha")
                    else:
                        logging.info("📊 İlk veri paketi gönderiliyor")
                    
                    previous_state = state_without_timestamp.copy()
                
                await websocket.send(json.dumps(state))
                await asyncio.sleep(0.1)  # 10 Hz
                
            except websockets.exceptions.ConnectionClosed:
                logging.info("📡 Durum güncellemeleri durduruldu (bağlantı kesildi)")
                break
            except Exception as e:
                logging.error(f"❌ Durum gönderme hatası: {e}")
                break
    
    def process_command(self, data):
        """Gelen komutları işle"""
        changes = []
        
        for key, value in data.items():
            if key in ["timestamp", "source"]:
                continue  # Metadata
            
            if key in self.shared_data:
                old_value = self.shared_data[key]
                
                # Tip uyumluluğu
                if isinstance(old_value, bool):
                    self.shared_data[key] = bool(value)
                elif isinstance(old_value, int):
                    self.shared_data[key] = int(value)
                elif isinstance(old_value, float):
                    self.shared_data[key] = float(value)
                else:
                    self.shared_data[key] = value
                
                changes.append(f"{key}: {old_value} → {self.shared_data[key]}")
            else:
                logging.warning(f"⚠️ Bilinmeyen alan: {key}")
        
        return changes
    
    async def simulate_command_effects(self, data):
        """Komut etkilerini simüle et"""
        
        # Sistem modu değişimi
        if "system_mode" in data:
            mode = data["system_mode"]
            mode_names = {-1: "DURDUR", 0: "MANUEL", 1: "AŞAMA 1", 2: "AŞAMA 2", 3: "AŞAMA 3"}
            logging.info(f"🎮 Sistem modu: {mode_names.get(mode, f'MOD {mode}')}")
            
            if mode > 0:
                logging.info("🚀 Sistem aktif, tarama başlıyor...")
                self.shared_data["scanning_target_flag"] = True
            else:
                logging.info("🛑 Sistem durduruldu")
                self.shared_data["scanning_target_flag"] = False
                self.shared_data["target_detected_flag"] = False
        
        # Ateş komutu
        if data.get("fire_gui_flag"):
            logging.info("💥 ATEŞ KOMUTİ AKTİVE!")
            await asyncio.sleep(0.5)
            if self.shared_data["target_detected_flag"]:
                logging.info("🎯 Hedef vuruldu!")
                self.shared_data["target_destroyed_flag"] = True
                await asyncio.sleep(1)
                self.shared_data["target_destroyed_flag"] = False
                self.shared_data["target_detected_flag"] = False
        
        # Kalibrasyon
        if data.get("calibration_flag"):
            logging.info("🔧 Kalibrasyon başlıyor...")
            for i in range(3):
                await asyncio.sleep(0.5)
                logging.info(f"📐 Kalibrasyon adım {i+1}/3")
            self.shared_data["calibration_flag"] = False
            logging.info("✅ Kalibrasyon tamamlandı!")
    
    def update_simulation(self):
        """Sistem aktifken simülasyon verileri üret"""
        import random
        
        # Hedef hareket simülasyonu
        self.shared_data["x_target"] += random.randint(-5, 5)
        self.shared_data["y_target"] += random.randint(-5, 5)
        
        # Sınırlar içinde tut
        self.shared_data["x_target"] = max(50, min(590, self.shared_data["x_target"]))
        self.shared_data["y_target"] = max(50, min(430, self.shared_data["y_target"]))
        
        # Motor açıları
        self.shared_data["global_angle"] += random.uniform(-2, 2)
        self.shared_data["global_tilt_angle"] += random.uniform(-1, 1)
        
        # Sınırlar
        self.shared_data["global_angle"] = max(-180, min(180, self.shared_data["global_angle"]))
        self.shared_data["global_tilt_angle"] = max(-90, min(90, self.shared_data["global_tilt_angle"]))
        
        # Hedef tespit simülasyonu
        if self.shared_data["scanning_target_flag"]:
            self.shared_data["target_detected_flag"] = random.choice([True, False, False])  # %33 şans
            if self.shared_data["target_detected_flag"]:
                self.shared_data["weapon"] = random.choice(["L", "A"])
            else:
                self.shared_data["weapon"] = "E"
    
    async def start_server(self):
        """WebSocket server'ı başlat"""
        logging.info("🚀 Test WebSocket Server Başlatılıyor...")
        logging.info(f"🌐 Adres: ws://{self.host}:{self.port}")
        logging.info("📊 Başlangıç durumu:")
        for key, value in self.shared_data.items():
            logging.info(f"   {key}: {value}")
        logging.info("=" * 60)
        
        # Use the new websockets 15.x API
        async with websockets.serve(self.handle_client, self.host, self.port):
            logging.info("✅ Server başlatıldı! GUI bağlantısı bekleniyor...")
            logging.info("🔄 GUI'yi başlatabilirsin (Ctrl+C ile durdur)")
            await asyncio.Future()  # Sonsuz bekle

def main():
    """Ana fonksiyon"""
    server = TestWebSocketServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logging.info("\n🛑 Server durduruldu (Ctrl+C)")
    except Exception as e:
        logging.error(f"❌ Server hatası: {e}")

if __name__ == "__main__":
    main()