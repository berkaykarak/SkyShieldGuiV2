# controllers/Rasberrypi_Controller.py
import requests
import json
import time

class RaspberryController:
    """
    HTTP tabanlı Raspberry Pi kontrolcüsü
    """
    
    def __init__(self, raspberry_ip: str = "localhost", port: int = 8000):
        self.raspberry_ip = raspberry_ip
        self.port = port
        self.base_url = f"http://{raspberry_ip}:{port}"
        self.connected = False
        
        print(f"[RASPBERRY] Controller oluşturuldu: {self.base_url}")
    
    def start_connection(self):
        """Bağlantıyı başlat"""
        print(f"[RASPBERRY] Bağlantı test ediliyor: {self.base_url}")
        self.connected = self.test_connection()
        
        if self.connected:
            print("[RASPBERRY] ✅ HTTP server'a bağlanıldı")
            # İlk durum gönder
            self.send_command({
                "system_mode": 0,
                "system_active": False,
                "message": "GUI başlatıldı"
            })
        else:
            print(f"[RASPBERRY] ❌ HTTP server bulunamadı: {self.base_url}")
            print("[RASPBERRY] Server'ın çalıştığından emin ol!")
    
    def stop_connection(self):
        """Bağlantıyı durdur"""
        print("[RASPBERRY] Bağlantı kapatıldı")
    
    def test_connection(self):
        """Bağlantı testi"""
        try:
            print(f"[RASPBERRY] Ping gönderiliyor: {self.base_url}/ping")
            response = requests.get(f"{self.base_url}/ping", timeout=0.5)
            success = response.status_code == 200
            print(f"[RASPBERRY] Ping sonucu: {success} (Status: {response.status_code})")
            return success
        except requests.exceptions.ConnectionError:
            print(f"[RASPBERRY] Bağlantı hatası: Server çalışmıyor olabilir")
            return False
        except Exception as e:
            print(f"[RASPBERRY] Test hatası: {e}")
            return False
    
    def send_command(self, data):
        """JSON komutu gönder"""
        try:
            print(f"[RASPBERRY] 📤 Komut gönderiliyor:")
            print(f"   URL: {self.base_url}/command")
            print(f"   Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            response = requests.post(
                f"{self.base_url}/command", 
                json=data, 
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"[RASPBERRY] HTTP Response: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[RASPBERRY] ✅ Başarılı! Server yanıtı: {response_data.get('message', 'OK')}")
                self.connected = True
                return True
            else:
                print(f"[RASPBERRY] ❌ HTTP hatası: {response.status_code}")
                print(f"[RASPBERRY] Response text: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"[RASPBERRY] ❌ Bağlantı hatası! Server çalışıyor mu?")
            self.connected = False
            return False
        except requests.exceptions.Timeout:
            print(f"[RASPBERRY] ❌ Timeout hatası!")
            return False
        except Exception as e:
            print(f"[RASPBERRY] ❌ Beklenmeyen hata: {e}")
            return False
    
    # Ana GUI'den çağrılan fonksiyonlar
    def update_system_mode(self, mode):
        """Sistem modunu güncelle"""
        return self.send_command({
            "system_mode": mode,
            "action": f"Sistem modu {mode} olarak değiştirildi"
        })
    
    def update_system_active(self, active):
        """Sistem aktif/pasif durumu"""
        return self.send_command({
            "system_active": active,
            "action": "Sistem başlatıldı" if active else "Sistem durduruldu"
        })
    
    def update_emergency_stop(self, emergency):
        """Acil durdur"""
        return self.send_command({
            "emergency_stop": emergency,
            "system_active": False,
            "action": "ACİL DURDUR AKTİVE!" if emergency else "Acil durdur iptal edildi"
        })
    
    def send_phase_command(self, phase):
        """Aşama komutu"""
        return self.send_command({
            "system_mode": phase,
            "fire_gui_flag": True,
            "engagement_started_flag": True,
            "action": f"Aşama {phase} başlatıldı"
        })
    
    def send_emergency_command(self):
        """Acil durdur komutu"""
        return self.send_command({
            "emergency_stop": True,
            "system_active": False,
            "fire_gui_flag": False,
            "engagement_started_flag": False,
            "action": "ACİL DURDUR KOMUTU"
        })
    
    def update_target_position(self, x, y):
        """Hedef pozisyonu güncelle"""
        return self.send_command({
            "target_x": x,
            "target_y": y,
            "action": f"Hedef pozisyonu: X={x:.1f}, Y={y:.1f}"
        })

# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 Raspberry Controller HTTP Test")
    
    controller = RaspberryController()
    controller.start_connection()
    
    if controller.connected:
        print("✅ Bağlantı başarılı, test komutları gönderiliyor...")
        
        controller.update_system_mode(1)
        time.sleep(1)
        
        controller.update_system_active(True)
        time.sleep(1)
        
        controller.send_emergency_command()
        
        print("📊 Test tamamlandı!")
    else:
        print("❌ Bağlantı başarısız!")
        print("Server'ı başlat: python test_http_server.py")