# gui/communication/http_client.py
import requests
import json
import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime

class HTTPCommunicationClient:
    """
    GUI tarafından Raspberry Pi ile HTTP iletişimi
    Veri gönderme ve alma işlemlerini yönetir
    """
    
    def __init__(self, raspberry_ip: str = "localhost", 
                 command_port: int = 8000, 
                 stream_port: int = 9001):
        self.raspberry_ip = raspberry_ip
        self.command_port = command_port
        self.stream_port = stream_port
        
        # URL'ler
        self.command_url = f"http://{raspberry_ip}:{command_port}"
        self.stream_url = f"http://{raspberry_ip}:{stream_port}"
        
        # Bağlantı durumu
        self.connected = False
        self.last_ping_time = None
        
        # Callback fonksiyonları
        self.data_callback: Optional[Callable] = None
        self.connection_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        
        # Threading
        self.running = False
        self.data_thread: Optional[threading.Thread] = None
        self.ping_thread: Optional[threading.Thread] = None
        
        # Son alınan veri
        self.last_data = {}
        
        print(f"[HTTP CLIENT] Oluşturuldu: {self.command_url}")
    
    def start_connection(self) -> bool:
        """Bağlantıyı başlat ve test et"""
        print(f"[HTTP CLIENT] Bağlantı test ediliyor...")
        
        # İlk ping testi
        self.connected = self.ping_server()
        
        if self.connected:
            print("[HTTP CLIENT] ✅ Raspberry Pi'ye bağlanıldı")
            
            # Threading başlat
            self.running = True
            self.start_background_tasks()
            
            # Bağlantı callback'i tetikle
            if self.connection_callback:
                self.connection_callback(True)
                
            return True
        else:
            print("[HTTP CLIENT] ❌ Raspberry Pi'ye bağlanılamadı")
            if self.connection_callback:
                self.connection_callback(False)
            return False
    
    def stop_connection(self):
        """Bağlantıyı durdur"""
        print("[HTTP CLIENT] Bağlantı kapatılıyor...")
        self.running = False
        
        # Thread'leri bekle
        if self.data_thread and self.data_thread.is_alive():
            self.data_thread.join(timeout=2)
        if self.ping_thread and self.ping_thread.is_alive():
            self.ping_thread.join(timeout=2)
        
        self.connected = False
        if self.connection_callback:
            self.connection_callback(False)
        
        print("[HTTP CLIENT] Bağlantı kapatıldı")
    
    def ping_server(self) -> bool:
        """Server'a ping gönder"""
        try:
            response = requests.get(f"{self.command_url}/ping", timeout=2)
            success = response.status_code == 200
            self.last_ping_time = datetime.now()
            return success
        except Exception as e:
            print(f"[HTTP CLIENT] Ping hatası: {e}")
            return False
    
    def send_command(self, data: Dict[str, Any]) -> bool:
        """Raspberry Pi'ye komut gönder"""
        try:
            # Timestamp ekle
            data_with_timestamp = data.copy()
            data_with_timestamp['timestamp'] = datetime.now().isoformat()
            data_with_timestamp['source'] = 'gui'
            
            print(f"[HTTP CLIENT] 📤 Komut gönderiliyor:")
            print(f"   URL: {self.command_url}/command")
            print(f"   Data: {json.dumps(data_with_timestamp, indent=2)}")
            
            response = requests.post(
                f"{self.command_url}/command",
                json=data_with_timestamp,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[HTTP CLIENT] ✅ Başarılı: {response_data.get('message', 'OK')}")
                return True
            else:
                print(f"[HTTP CLIENT] ❌ HTTP hatası: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"[HTTP CLIENT] ❌ Bağlantı hatası!")
            self.connected = False
            if self.connection_callback:
                self.connection_callback(False)
            return False
        except Exception as e:
            print(f"[HTTP CLIENT] ❌ Komut gönderme hatası: {e}")
            if self.error_callback:
                self.error_callback(f"Komut gönderme hatası: {e}")
            return False
    
    def get_system_data(self) -> Optional[Dict[str, Any]]:
        """Sistem verilerini al"""
        try:
            response = requests.get(f"{self.command_url}/status", timeout=3)
            if response.status_code == 200:
                data = response.json()
                self.last_data = data
                return data
            else:
                print(f"[HTTP CLIENT] Status alma hatası: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[HTTP CLIENT] Veri alma hatası: {e}")
            return None
    
    def start_background_tasks(self):
        """Arka plan görevlerini başlat"""
        # Veri alma thread'i
        self.data_thread = threading.Thread(target=self._data_loop, daemon=True)
        self.data_thread.start()
        
        # Ping thread'i
        self.ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
        self.ping_thread.start()
    
    def _data_loop(self):
        """Sürekli veri alma döngüsü"""
        while self.running:
            try:
                if self.connected:
                    data = self.get_system_data()
                    if data and self.data_callback:
                        self.data_callback(data)
                
                time.sleep(0.1)  # 100ms aralıklarla
                
            except Exception as e:
                print(f"[HTTP CLIENT] Data loop hatası: {e}")
                time.sleep(1)
    
    def _ping_loop(self):
        """Sürekli ping döngüsü"""
        while self.running:
            try:
                was_connected = self.connected
                self.connected = self.ping_server()
                
                # Bağlantı durumu değişti mi?
                if was_connected != self.connected:
                    print(f"[HTTP CLIENT] Bağlantı durumu: {'Bağlı' if self.connected else 'Kesildi'}")
                    if self.connection_callback:
                        self.connection_callback(self.connected)
                
                time.sleep(5)  # 5 saniyede bir ping
                
            except Exception as e:
                print(f"[HTTP CLIENT] Ping loop hatası: {e}")
                time.sleep(5)
    
    def register_data_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Veri alma callback'i kaydet"""
        self.data_callback = callback
    
    def register_connection_callback(self, callback: Callable[[bool], None]):
        """Bağlantı durumu callback'i kaydet"""
        self.connection_callback = callback
    
    def register_error_callback(self, callback: Callable[[str], None]):
        """Hata callback'i kaydet"""
        self.error_callback = callback
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Bağlantı durumu bilgisi"""
        return {
            'connected': self.connected,
            'raspberry_ip': self.raspberry_ip,
            'command_port': self.command_port,
            'stream_port': self.stream_port,
            'last_ping': self.last_ping_time.isoformat() if self.last_ping_time else None,
            'last_data': self.last_data
        }

# Test fonksiyonu
if __name__ == "__main__":
    def on_data_received(data):
        print(f"📥 Veri alındı: {data}")
    
    def on_connection_changed(connected):
        print(f"🔗 Bağlantı durumu: {'Bağlı' if connected else 'Kesildi'}")
    
    def on_error(error):
        print(f"❌ Hata: {error}")
    
    print("🧪 HTTP Client Test")
    
    client = HTTPCommunicationClient()
    client.register_data_callback(on_data_received)
    client.register_connection_callback(on_connection_changed)
    client.register_error_callback(on_error)
    
    if client.start_connection():
        # Test komutları gönder
        test_commands = [
            {"system_mode": 1, "system_active": True},
            {"target_x": 150.5, "target_y": 200.3},
            {"fire_gui_flag": True},
            {"emergency_stop": True}
        ]
        
        for cmd in test_commands:
            client.send_command(cmd)
            time.sleep(2)
        
        # 10 saniye çalıştır
        time.sleep(10)
    
    client.stop_connection()
    print("Test tamamlandı!")