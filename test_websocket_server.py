# test_websocket_server.py - FRESH START - İHTİYACA YÖNELIK
import asyncio
import websockets
import json
import logging
import time
from datetime import datetime

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SimpleTestWebSocketServer:
    """
    Basit ve etkili WebSocket test server'ı
    Aşama-spesifik veriler 1'den başlayıp her saniye 1 artır
    """
    
    def __init__(self, host="localhost", port=9000):
        self.host = host
        self.port = port
        self.clients = set()
        
        # BAŞLANGIÇ VERİLERİ - HEPSİ 1'DEN BAŞLIYOR
        self.shared_data = {
            # ========== ORTAK SİSTEM VERİLERİ ==========
            "system_mode": -1,
            "phase_mode": -1,
            "system_active": False,
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
            
            # Joystick
            "controller_connected": True,
            
            # GUI bayrakları
            "calibration_flag": False,
            "fire_gui_flag": False,
            "engagement_started_flag": False,
            
            # ========== AŞAMA 1 VERİLERİ - 1'DEN BAŞLA ==========
            "targets_detected": 1,       # 1'den başla
            "targets_destroyed": 1,      # 1'den başla
            "balloon_count": 1,          # 1'den başla
            
            # ========== AŞAMA 2 VERİLERİ - 1'DEN BAŞLA ==========
            "friend_targets": 1,         # 1'den başla
            "enemy_targets": 1,          # 1'den başla
            "enemy_destroyed": 1,        # 1'den başla
            "classification_accuracy": 90.0,  # 90%'dan başla
            
            # ========== AŞAMA 3 VERİLERİ - SABİT ==========
            "target_color": "red",       # Başlangıç: kırmızı
            "target_shape": "circle",    # Başlangıç: daire
            "current_platform": "A",     # Başlangıç: A platformu
            "qr_code_detected": True,    # Başlangıç: tespit edilmiş
            "engagement_authorized": True,  # Başlangıç: yetkili
        }
        
        self.start_time = time.time()
        self.update_counter = 0
        
    async def handle_client(self, websocket):
        """Client bağlantısını yönet"""
        client_ip = websocket.remote_address[0]
        self.clients.add(websocket)
        
        logging.info(f"🟢 YENİ BAĞLANTI: {client_ip} (Toplam: {len(self.clients)})")
        
        try:
            # Hoş geldin mesajı
            welcome = {
                "status": "connected",
                "message": "Simple Test WebSocket Server",
                "server_time": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(welcome))
            
            # Paralel işlemler
            await asyncio.gather(
                self.receive_commands(websocket),
                self.send_updates(websocket)
            )
            
        except websockets.exceptions.ConnectionClosed:
            logging.info(f"🔴 Bağlantı kapandı: {client_ip}")
        except Exception as e:
            logging.error(f"❌ Client hatası: {e}")
        finally:
            self.clients.discard(websocket)
            logging.info(f"📊 Kalan bağlantı: {len(self.clients)}")
    
    async def receive_commands(self, websocket):
        """GUI'den gelen komutları dinle"""
        async for message in websocket:
            try:
                data = json.loads(message)
                logging.info(f"📥 KOMUT ALINDI: {data}")
                
                # Komutları işle
                self.process_command(data)
                
            except json.JSONDecodeError as e:
                logging.error(f"❌ JSON hatası: {e}")
            except Exception as e:
                logging.error(f"❌ Komut hatası: {e}")
    
    async def send_updates(self, websocket):
        """Her saniye veri gönder ve artır"""
        logging.info("📡 Veri gönderimi başladı (1 saniyede 1 kez)")
        
        while True:
            try:
                # VERİLERİ ARTTIR (Her saniye +1)
                self.update_data()
                
                # Timestamp ekle
                current_data = self.shared_data.copy()
                current_data["timestamp"] = datetime.now().isoformat()
                current_data["server_uptime"] = time.time() - self.start_time
                
                # Gönder
                await websocket.send(json.dumps(current_data))
                
                # Log (Her 5 saniyede bir detay göster)
                if self.update_counter % 5 == 0:
                    logging.info(f"📊 Veri gönderildi #{self.update_counter}")
                    logging.info(f"   Aşama 1: Tespit={current_data['targets_detected']}, İmha={current_data['targets_destroyed']}")
                    logging.info(f"   Aşama 2: Dost={current_data['friend_targets']}, Düşman={current_data['enemy_targets']}")
                    logging.info(f"   Aşama 3: Renk={current_data['target_color']}, Şekil={current_data['target_shape']}")
                
                await asyncio.sleep(1.0)  # 1 saniye bekle
                
            except websockets.exceptions.ConnectionClosed:
                logging.info("📡 Veri gönderimi durduruldu")
                break
            except Exception as e:
                logging.error(f"❌ Veri gönderme hatası: {e}")
                break
    
    def update_data(self):
        """Verileri güncelle - HER SANİYE +1"""
        self.update_counter += 1
        
        # ========== AŞAMA 1 VERİLERİ +1 ==========
        self.shared_data["targets_detected"] += 1
        self.shared_data["targets_destroyed"] += 1
        self.shared_data["balloon_count"] += 1
        
        # ========== AŞAMA 2 VERİLERİ +1 ==========
        self.shared_data["friend_targets"] += 1
        self.shared_data["enemy_targets"] += 1
        self.shared_data["enemy_destroyed"] += 1
        
        # Classification accuracy yavaş artır (her 10 saniyede +1)
        if self.update_counter % 10 == 0:
            self.shared_data["classification_accuracy"] += 1.0
            if self.shared_data["classification_accuracy"] > 99.0:
                self.shared_data["classification_accuracy"] = 90.0  # Reset
        
        # ========== AŞAMA 3 VERİLERİ DÖNGÜ ==========
        # Her 10 saniyede değişen döngü
        cycle = (self.update_counter // 10) % 4
        
        if cycle == 0:
            self.shared_data["target_color"] = "red"
            self.shared_data["target_shape"] = "circle"
            self.shared_data["qr_code_detected"] = True
            self.shared_data["engagement_authorized"] = True
        elif cycle == 1:
            self.shared_data["target_color"] = "blue"
            self.shared_data["target_shape"] = "square"
            self.shared_data["qr_code_detected"] = True
            self.shared_data["engagement_authorized"] = False
        elif cycle == 2:
            self.shared_data["target_color"] = "green"
            self.shared_data["target_shape"] = "triangle"
            self.shared_data["qr_code_detected"] = True
            self.shared_data["engagement_authorized"] = True
        else:
            self.shared_data["target_color"] = "unknown"
            self.shared_data["target_shape"] = "unknown"
            self.shared_data["qr_code_detected"] = False
            self.shared_data["engagement_authorized"] = False
        
        # Platform değişimi (her 15 saniyede)
        platform_cycle = (self.update_counter // 15) % 2
        self.shared_data["current_platform"] = "A" if platform_cycle == 0 else "B"
        
        # ========== ORTAK VERİLER ==========
        # Controller her zaman bağlı
        self.shared_data["controller_connected"] = True
        
        # Hedef tespiti döngüsü (her 5 saniyede)
        if (self.update_counter % 5) < 3:
            self.shared_data["target_detected_flag"] = True
            weapon_cycle = self.update_counter % 3
            if weapon_cycle == 0:
                self.shared_data["weapon"] = "L"  # Laser
            elif weapon_cycle == 1:
                self.shared_data["weapon"] = "A"  # Airgun
            else:
                self.shared_data["weapon"] = "E"  # None
        else:
            self.shared_data["target_detected_flag"] = False
            self.shared_data["weapon"] = "E"
        
        # Hedef pozisyonu (yavaş hareket)
        import math
        angle = self.update_counter * 0.1
        self.shared_data["x_target"] = int(320 + 100 * math.cos(angle))
        self.shared_data["y_target"] = int(240 + 50 * math.sin(angle))
        
        # Motor açıları
        self.shared_data["global_angle"] = 30 * math.sin(angle)
        self.shared_data["global_tilt_angle"] = 15 * math.cos(angle * 0.7)
    
    def process_command(self, data):
        """Gelen komutları işle"""
        if "change_phase" in data:
            phase = int(data["change_phase"])
            self.shared_data["phase_mode"] = phase
            logging.info(f"🔄 Aşama değişti: {phase}")
        
        if "start_system" in data:
            self.shared_data["system_active"] = True
            self.shared_data["scanning_target_flag"] = True
            logging.info("🚀 Sistem başlatıldı")
        
        if "stop_system" in data:
            self.shared_data["system_active"] = False
            self.shared_data["scanning_target_flag"] = False
            logging.info("⏸️ Sistem durduruldu")
        
        if "fire_gui_flag" in data and data["fire_gui_flag"]:
            logging.info("💥 ATEŞ KOMUTİ!")
            # Fire flag'i işaretle
            self.shared_data["fire_gui_flag"] = True
            # 2 saniye sonra reset et
            asyncio.create_task(self.reset_fire_flag())
    
    async def reset_fire_flag(self):
        """Fire flag'ini 2 saniye sonra sıfırla"""
        await asyncio.sleep(2)
        self.shared_data["fire_gui_flag"] = False
    
    async def start_server(self):
        """Server'ı başlat"""
        logging.info("🚀 Simple Test WebSocket Server Başlatılıyor...")
        logging.info(f"🌐 Adres: ws://{self.host}:{self.port}")
        logging.info("📊 Başlangıç değerleri:")
        
        # Sadece önemli başlangıç değerlerini göster
        important_keys = [
            "targets_detected", "targets_destroyed", "balloon_count",
            "friend_targets", "enemy_targets", "enemy_destroyed",
            "target_color", "target_shape", "controller_connected"
        ]
        
        for key in important_keys:
            logging.info(f"   {key}: {self.shared_data[key]}")
        
        logging.info("=" * 60)
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logging.info("✅ Server başlatıldı! GUI'yi başlatabilirsin.")
            logging.info("🔄 Veriler her saniye +1 artacak (Ctrl+C ile durdur)")
            await asyncio.Future()  # Sonsuz bekle


def main():
    """Ana fonksiyon"""
    server = SimpleTestWebSocketServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logging.info("\n🛑 Server durduruldu (Ctrl+C)")
    except Exception as e:
        logging.error(f"❌ Server hatası: {e}")


if __name__ == "__main__":
    main()