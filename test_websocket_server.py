# test_websocket_server.py - SADECE target_side (current_platform yok)
import asyncio
import websockets
import json
import logging
import time
import random
from datetime import datetime

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SimpleTestWebSocketServer:
    """
    Sadece target_side kullanan WebSocket test server'ı
    Şekiller: T(üçgen), C(daire), S(kare)
    Renkler: R(kırmızı), G(yeşil), B(mavi)
    target_side: A veya B (current_platform yok!)
    """
    
    def __init__(self, host="localhost", port=9000):
        self.host = host
        self.port = port
        self.clients = set()
        
        # BAŞLANGIÇ VERİLERİ - SADECE target_side
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
            "target_side": "A",          # ✅ BU VAR - KONTROL ET!
            "target_detected_flag": False,
            
            # Joystick
            "controller_connected": True,
            
            # GUI bayrakları
            "calibration_flag": False,
            "fire_gui_flag": False,
            "engagement_started_flag": False,
            
            # ========== AŞAMA 1 VERİLERİ ==========
            "targets_detected": 4,
            "targets_destroyed": 2,
            "balloon_count": 3,
            
            # ========== AŞAMA 2 VERİLERİ ==========
            "friend_targets": 8,
            "enemy_targets": 9,
            "enemy_destroyed": 12,
            "classification_accuracy": 90.0,
            
            # ========== AŞAMA 3 VERİLERİ - RASPBERRY Pİ FORMATI ==========
            "target_color": "R",         # R/G/B formatı
            "target_shape": "C",         # T/C/S formatı
            "qr_code_detected": True,
            "engagement_authorized": True,
        }
        
        print(f"[INIT] target_side başlangıç değeri: {self.shared_data['target_side']}")
        print(f"[INIT] shared_data keys: {list(self.shared_data.keys())}")

        # SADECE target_side KOMBİNASYONLARI (current_platform yok)
        self.phase3_combinations = [
            {"side": "A", "color": "R", "shape": "C", "qr": True, "auth": True},   # A - Kırmızı Daire
            {"side": "B", "color": "B", "shape": "S", "qr": True, "auth": False},  # B - Mavi Kare
            {"side": "A", "color": "G", "shape": "T", "qr": True, "auth": True},   # A - Yeşil Üçgen
            {"side": "B", "color": "R", "shape": "S", "qr": False, "auth": False}, # B - Kırmızı Kare
            {"side": "A", "color": "B", "shape": "C", "qr": True, "auth": True},   # A - Mavi Daire
            {"side": "B", "color": "G", "shape": "S", "qr": False, "auth": True},  # B - Yeşil Kare
            {"side": "A", "color": "R", "shape": "T", "qr": False, "auth": False}, # A - Kırmızı Üçgen
            {"side": "B", "color": "B", "shape": "T", "qr": True, "auth": True},   # B - Mavi Üçgen
            {"side": "A", "color": "G", "shape": "C", "qr": True, "auth": False},  # A - Yeşil Daire
            {"side": "B", "color": "R", "shape": "C", "qr": False, "auth": True},  # B - Kırmızı Daire
            {"side": "A", "color": "B", "shape": "T", "qr": True, "auth": True},   # A - Mavi Üçgen
            {"side": "B", "color": "G", "shape": "T", "qr": False, "auth": False}, # B - Yeşil Üçgen
        ]
        
        # ÇEVR İM TABLOSU - GUI'de göstermek için
        self.color_names = {"R": "Kırmızı", "G": "Yeşil", "B": "Mavi"}
        self.shape_names = {"T": "Üçgen", "C": "Daire", "S": "Kare"}
        
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
                "message": "SADECE target_side WebSocket Server",
                "server_time": datetime.now().isoformat(),
                "format_info": {
                    "colors": "R=Kırmızı, G=Yeşil, B=Mavi",
                    "shapes": "T=Üçgen, C=Daire, S=Kare",
                    "note": "current_platform yok, sadece target_side var!"
                }
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
        logging.info("📡 Veri gönderimi başladı (SADECE target_side)")
        
        while True:
            try:
                # VERİLERİ ARTTIR
                self.update_data()
                
                # Timestamp ekle
                current_data = self.shared_data.copy()
                current_data["timestamp"] = datetime.now().isoformat()
                current_data["server_uptime"] = time.time() - self.start_time
                
                # ✅ SORUN BURADA: target_side'ı current_data'ya ekle!
                # Eğer shared_data'da target_side varsa, current_data'ya da ekle
                if "target_side" in self.shared_data:
                    current_data["target_side"] = self.shared_data["target_side"]
                    print(f"[WS SERVER] target_side gönderiliyor: {current_data['target_side']}")
                else:
                    print(f"[WS SERVER] HATA: shared_data'da target_side yok!")
                    print(f"[WS SERVER] shared_data keys: {list(self.shared_data.keys())}")
                
                # Gönder
                await websocket.send(json.dumps(current_data))
                
                # HER SANİYE target_side + Raspberry formatını göster
                color_name = self.color_names.get(current_data['target_color'], current_data['target_color'])
                shape_name = self.shape_names.get(current_data['target_shape'], current_data['target_shape'])
                
                # target_side'ı da logla
                target_side = current_data.get('target_side', 'UNDEFINED')
                
                logging.info(f"📡 #{self.update_counter} - target_side: {target_side} | "
                        f"Renk: {current_data['target_color']}({color_name}) | "
                        f"Şekil: {current_data['target_shape']}({shape_name})")
                
                # Her 5 saniyede detaylı bilgi
                if self.update_counter % 5 == 0:
                    logging.info(f"📊 Detaylı veri #{self.update_counter}")
                    logging.info(f"   Aşama 1: Tespit={current_data['targets_detected']}, İmha={current_data['targets_destroyed']}")
                    logging.info(f"   Aşama 2: Dost={current_data['friend_targets']}, Düşman={current_data['enemy_targets']}")
                    logging.info(f"   Aşama 3: target_side={current_data.get('target_side', 'UNDEFINED')}")
                
                await asyncio.sleep(1.0)
                
            except websockets.exceptions.ConnectionClosed:
                logging.info("📡 Veri gönderimi durduruldu")
                break
            except Exception as e:
                logging.error(f"❌ Veri gönderme hatası: {e}")
                break
    
    def update_data(self):
        """Verileri güncelle - SADECE target_side"""
        self.update_counter += 1
        
        # ========== AŞAMA 1 VERİLERİ +1 ==========
        self.shared_data["targets_detected"] += 1
        self.shared_data["targets_destroyed"] += 1
        self.shared_data["balloon_count"] += 1
        
        # ========== AŞAMA 2 VERİLERİ +1 ==========
        self.shared_data["friend_targets"] += 1
        self.shared_data["enemy_targets"] += 1
        self.shared_data["enemy_destroyed"] += 1
        
        # Classification accuracy
        if self.update_counter % 10 == 0:
            self.shared_data["classification_accuracy"] += 1.0
            if self.shared_data["classification_accuracy"] > 99.0:
                self.shared_data["classification_accuracy"] = 90.0
        
        # ========== AŞAMA 3 VERİLERİ - SADECE target_side ==========
        # Her 6 saniyede bir kombinasyon değişir
        if self.update_counter % 6 == 0:
            combination_index = (self.update_counter // 6) % len(self.phase3_combinations)
            current_combo = self.phase3_combinations[combination_index]
            
            # Eski değerleri sakla
            old_color = self.shared_data["target_color"]
            old_shape = self.shared_data["target_shape"]
            old_side = self.shared_data["target_side"]
            
            # Sadece target_side formatında güncelle
            self.shared_data["target_color"] = current_combo["color"]      # R/G/B
            self.shared_data["target_shape"] = current_combo["shape"]      # T/C/S
            self.shared_data["target_side"] = current_combo["side"]        # A/B (sadece bu!)
            self.shared_data["qr_code_detected"] = current_combo["qr"]
            self.shared_data["engagement_authorized"] = current_combo["auth"]
            
            # Değişimi logla
            old_color_name = self.color_names.get(old_color, old_color)
            new_color_name = self.color_names.get(current_combo["color"], current_combo["color"])
            old_shape_name = self.shape_names.get(old_shape, old_shape)
            new_shape_name = self.shape_names.get(current_combo["shape"], current_combo["shape"])
            
            logging.info(f"🔄 AŞAMA 3 DEĞİŞİMİ (SADECE target_side):")
            logging.info(f"   Target Side: {old_side} → {current_combo['side']}")
            logging.info(f"   Renk: {old_color}({old_color_name}) → {current_combo['color']}({new_color_name})")
            logging.info(f"   Şekil: {old_shape}({old_shape_name}) → {current_combo['shape']}({new_shape_name})")
            logging.info(f"   QR: {current_combo['qr']}, Angajman: {current_combo['auth']}")
        
        # ========== ORTAK VERİLER ==========
        self.shared_data["controller_connected"] = True
        
        # Hedef tespiti döngüsü
        if (self.update_counter % 5) < 3:
            self.shared_data["target_detected_flag"] = True
            weapon_cycle = self.update_counter % 3
            if weapon_cycle == 0:
                self.shared_data["weapon"] = "L"
            elif weapon_cycle == 1:
                self.shared_data["weapon"] = "A"
            else:
                self.shared_data["weapon"] = "E"
        else:
            self.shared_data["target_detected_flag"] = False
            self.shared_data["weapon"] = "E"
        
        # Hedef pozisyonu ve motor açıları
        import math
        angle = self.update_counter * 0.1
        self.shared_data["x_target"] = int(320 + 100 * math.cos(angle))
        self.shared_data["y_target"] = int(240 + 50 * math.sin(angle))
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
            self.shared_data["fire_gui_flag"] = True
            asyncio.create_task(self.reset_fire_flag())
        
        if "switch_platform" in data and data["switch_platform"]:
            # Manuel target_side değiştirme
            current_index = 0
            for i, combo in enumerate(self.phase3_combinations):
                if (combo["color"] == self.shared_data["target_color"] and
                    combo["shape"] == self.shared_data["target_shape"] and
                    combo["side"] == self.shared_data["target_side"]):
                    current_index = i
                    break
            
            # Sonraki kombinasyona geç
            next_index = (current_index + 1) % len(self.phase3_combinations)
            next_combo = self.phase3_combinations[next_index]
            
            old_color = self.shared_data["target_color"]
            old_shape = self.shared_data["target_shape"]
            old_side = self.shared_data["target_side"]
            
            self.shared_data["target_color"] = next_combo["color"]
            self.shared_data["target_shape"] = next_combo["shape"]
            self.shared_data["target_side"] = next_combo["side"]
            self.shared_data["qr_code_detected"] = next_combo["qr"]
            self.shared_data["engagement_authorized"] = next_combo["auth"]
            
            # Log ile göster
            old_color_name = self.color_names.get(old_color, old_color)
            new_color_name = self.color_names.get(next_combo["color"], next_combo["color"])
            old_shape_name = self.shape_names.get(old_shape, old_shape)
            new_shape_name = self.shape_names.get(next_combo["shape"], next_combo["shape"])
            
            logging.info(f"🔄 MANUEL target_side DEĞİŞİMİ:")
            logging.info(f"   Target Side: {old_side} → {next_combo['side']}")
            logging.info(f"   Renk: {old_color}({old_color_name}) → {next_combo['color']}({new_color_name})")
            logging.info(f"   Şekil: {old_shape}({old_shape_name}) → {next_combo['shape']}({new_shape_name})")
    
    async def reset_fire_flag(self):
        """Fire flag'ini 2 saniye sonra sıfırla"""
        await asyncio.sleep(2)
        self.shared_data["fire_gui_flag"] = False
    
    async def start_server(self):
        """Server'ı başlat"""
        logging.info("🚀 SADECE target_side WebSocket Server Başlatılıyor...")
        logging.info(f"🌐 Adres: ws://{self.host}:{self.port}")
        logging.info("📊 FORMAT AÇIKLAMASI:")
        logging.info("   Renkler: R=Kırmızı, G=Yeşil, B=Mavi")
        logging.info("   Şekiller: T=Üçgen, C=Daire, S=Kare")
        logging.info("   SADECE target_side: A veya B (current_platform YOK!)")
        
        logging.info("📊 Başlangıç değerleri:")
        important_keys = ["target_color", "target_shape", "target_side"]
        for key in important_keys:
            value = self.shared_data[key]
            if key == "target_color":
                name = self.color_names.get(value, value)
                logging.info(f"   {key}: {value} ({name})")
            elif key == "target_shape":
                name = self.shape_names.get(value, value)
                logging.info(f"   {key}: {value} ({name})")
            else:
                logging.info(f"   {key}: {value}")
        
        logging.info("🔗 AŞAMA 3 KOMBİNASYONLARI:")
        for i, combo in enumerate(self.phase3_combinations):
            color_name = self.color_names.get(combo["color"], combo["color"])
            shape_name = self.shape_names.get(combo["shape"], combo["shape"])
            logging.info(f"   {i+1}. Side:{combo['side']}, Renk:{combo['color']}({color_name}), Şekil:{combo['shape']}({shape_name})")
        
        logging.info("=" * 80)
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logging.info("✅ SADECE target_side Server başlatıldı!")
            logging.info("🔄 Her saniye target_side değerini göreceksiniz")
            logging.info("🎯 Örnek: target_side: A | Renk: R(Kırmızı) | Şekil: C(Daire)")
            await asyncio.Future()


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