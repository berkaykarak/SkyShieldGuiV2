# gui/communication/communication_manager.py
from typing import Dict, Any, Optional, Callable
import time
import threading
from datetime import datetime

from .http_client import HTTPCommunicationClient
from .camera_stream_client import CameraStreamClient

class CommunicationManager:
    """
    HTTP Client ve Camera Stream Client'ı yöneten ana koordinatör
    GUI ile Raspberry Pi arasındaki tüm iletişimi organize eder
    """
    
    def __init__(self, raspberry_ip: str = "localhost", 
                 command_port: int = 8000, 
                 stream_port: int = 9001):
        
        # Client'ları oluştur
        self.http_client = HTTPCommunicationClient(raspberry_ip, command_port, stream_port)
        self.camera_client = CameraStreamClient(raspberry_ip, stream_port)
        
        # Durum takibi
        self.connected = False
        self.data_connected = False
        self.camera_connected = False
        
        # Son alınan veri
        self.last_system_data = {}
        self.last_frame = None
        
        # Callback fonksiyonları
        self.data_callback: Optional[Callable] = None
        self.frame_callback: Optional[Callable] = None
        self.connection_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        
        # İstatistikler
        self.stats = {
            'commands_sent': 0,
            'data_received': 0,
            'frames_received': 0,
            'connection_attempts': 0,
            'last_command_time': None,
            'last_data_time': None,
            'last_frame_time': None
        }
        
        self._setup_client_callbacks()
        
        print(f"[COMM MANAGER] Oluşturuldu: {raspberry_ip}:{command_port}")
    
    def _setup_client_callbacks(self):
        """Client callback'lerini kur"""
        # HTTP Client callbacks
        self.http_client.register_data_callback(self._on_data_received)
        self.http_client.register_connection_callback(self._on_data_connection_changed)
        self.http_client.register_error_callback(self._on_error)
        
        # Camera Client callbacks
        self.camera_client.register_frame_callback(self._on_frame_received)
        self.camera_client.register_connection_callback(self._on_camera_connection_changed)
        self.camera_client.register_error_callback(self._on_error)
    
    def start_communication(self) -> bool:
        """Tüm iletişimi başlat"""
        print("[COMM MANAGER] İletişim başlatılıyor...")
        self.stats['connection_attempts'] += 1
        
        # HTTP bağlantısını başlat
        data_success = self.http_client.start_connection()
        
        # Kamera stream'ini başlat
        camera_success = self.camera_client.start_stream()
        
        # Genel bağlantı durumunu güncelle
        self._update_overall_connection_status()
        
        success = data_success or camera_success  # En az biri başarılı olmalı
        
        if success:
            print("[COMM MANAGER] ✅ İletişim başlatıldı")
        else:
            print("[COMM MANAGER] ❌ İletişim başlatılamadı")
        
        return success
    
    def stop_communication(self):
        """Tüm iletişimi durdur"""
        print("[COMM MANAGER] İletişim durduruluyor...")
        
        # Client'ları durdur
        self.http_client.stop_connection()
        self.camera_client.stop_stream()
        
        # Durumu güncelle
        self.connected = False
        self.data_connected = False
        self.camera_connected = False
        
        if self.connection_callback:
            self.connection_callback(False, self._get_connection_details())
        
        print("[COMM MANAGER] İletişim durduruldu")
    
    def send_command(self, command_data: Dict[str, Any]) -> bool:
        """Raspberry Pi'ye komut gönder"""
        if not self.data_connected:
            print("[COMM MANAGER] ⚠️ HTTP bağlantısı yok, komut gönderilemiyor")
            return False
        
        success = self.http_client.send_command(command_data)
        
        if success:
            self.stats['commands_sent'] += 1
            self.stats['last_command_time'] = datetime.now()
        
        return success
    
    def get_current_frame_for_gui(self, width: int = None, height: int = None):
        """GUI için mevcut frame'i al"""
        return self.camera_client.get_current_frame_as_tkinter(width, height)
    
    def save_current_frame(self, filename: str) -> bool:
        """Mevcut frame'i kaydet"""
        return self.camera_client.save_current_frame(filename)
    
    def _on_data_received(self, data: Dict[str, Any]):
        """HTTP client'tan veri alındığında"""
        self.last_system_data = data
        self.stats['data_received'] += 1
        self.stats['last_data_time'] = datetime.now()
        
        # Veri callback'ini tetikle
        if self.data_callback:
            self.data_callback(data)
    
    def _on_frame_received(self, frame):
        """Camera client'tan frame alındığında"""
        self.last_frame = frame
        self.stats['frames_received'] += 1
        self.stats['last_frame_time'] = datetime.now()
        
        # Frame callback'ini tetikle
        if self.frame_callback:
            self.frame_callback(frame)
    
    def _on_data_connection_changed(self, connected: bool):
        """HTTP bağlantı durumu değiştiğinde"""
        self.data_connected = connected
        self._update_overall_connection_status()
        print(f"[COMM MANAGER] HTTP bağlantısı: {'Aktif' if connected else 'Kesildi'}")
    
    def _on_camera_connection_changed(self, connected: bool):
        """Kamera bağlantı durumu değiştiğinde"""
        self.camera_connected = connected
        self._update_overall_connection_status()
        print(f"[COMM MANAGER] Kamera stream'i: {'Aktif' if connected else 'Kesildi'}")
    
    def _update_overall_connection_status(self):
        """Genel bağlantı durumunu güncelle"""
        old_status = self.connected
        self.connected = self.data_connected or self.camera_connected
        
        # Durum değişti mi?
        if old_status != self.connected:
            if self.connection_callback:
                self.connection_callback(self.connected, self._get_connection_details())
    
    def _get_connection_details(self) -> Dict[str, Any]:
        """Detaylı bağlantı bilgisi"""
        return {
            'overall_connected': self.connected,
            'data_connected': self.data_connected,
            'camera_connected': self.camera_connected,
            'raspberry_ip': self.http_client.raspberry_ip,
            'command_port': self.http_client.command_port,
            'stream_port': self.camera_client.stream_port
        }
    
    def _on_error(self, error_message: str):
        """Hata oluştuğunda"""
        print(f"[COMM MANAGER] ❌ Hata: {error_message}")
        if self.error_callback:
            self.error_callback(error_message)
    
    def register_data_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Sistem verisi callback'i kaydet"""
        self.data_callback = callback
    
    def register_frame_callback(self, callback: Callable[[Any], None]):
        """Frame callback'i kaydet"""
        self.frame_callback = callback
    
    def register_connection_callback(self, callback: Callable[[bool, Dict[str, Any]], None]):
        """Bağlantı durumu callback'i kaydet"""
        self.connection_callback = callback
    
    def register_error_callback(self, callback: Callable[[str], None]):
        """Hata callback'i kaydet"""
        self.error_callback = callback
    
    def get_system_status(self) -> Dict[str, Any]:
        """Sistem durumu özeti"""
        return {
            'communication': {
                'connected': self.connected,
                'data_connected': self.data_connected,
                'camera_connected': self.camera_connected,
                'raspberry_ip': self.http_client.raspberry_ip
            },
            'stats': self.stats.copy(),
            'last_data': self.last_system_data.copy() if self.last_system_data else {},
            'camera_info': self.camera_client.get_stream_info(),
            'http_info': self.http_client.get_connection_status()
        }
    
    # Kolay kullanım için kısayol fonksiyonlar
    def send_system_mode(self, mode: int) -> bool:
        """Sistem modu gönder"""
        return self.send_command({"system_mode": mode})
    
    def send_system_active(self, active: bool) -> bool:
        """Sistem aktif durumu gönder"""
        return self.send_command({"system_active": active})
    
    def send_emergency_stop(self) -> bool:
        """Acil durdur komutu gönder"""
        return self.send_command({
            "emergency_stop": True,
            "system_active": False,
            "fire_gui_flag": False,
            "engagement_started_flag": False
        })
    
    def send_fire_command(self) -> bool:
        """Ateş komutu gönder"""
        return self.send_command({
            "fire_gui_flag": True,
            "engagement_started_flag": True
        })
    
    def send_calibration_command(self) -> bool:
        """Kalibrasyon komutu gönder"""
        return self.send_command({"calibration_flag": True})
    
    def send_target_position(self, x: float, y: float) -> bool:
        """Hedef pozisyonu gönder"""
        return self.send_command({
            "target_x": x,
            "target_y": y
        })

# Test fonksiyonu
if __name__ == "__main__":
    def on_data_received(data):
        print(f"📊 Sistem verisi: {data}")
    
    def on_frame_received(frame):
        print(f"📷 Frame alındı: {frame.shape}")
    
    def on_connection_changed(connected, details):
        print(f"🔗 Bağlantı durumu: {'Aktif' if connected else 'Kesildi'}")
        print(f"   Detaylar: {details}")
    
    def on_error(error):
        print(f"❌ Hata: {error}")
    
    print("🧪 Communication Manager Test")
    
    # Manager oluştur
    comm = CommunicationManager()
    
    # Callback'leri kaydet
    comm.register_data_callback(on_data_received)
    comm.register_frame_callback(on_frame_received)
    comm.register_connection_callback(on_connection_changed)
    comm.register_error_callback(on_error)
    
    # İletişimi başlat
    if comm.start_communication():
        print("✅ İletişim başlatıldı")
        
        # Test komutları gönder
        test_commands = [
            ("Sistem Modu 1", lambda: comm.send_system_mode(1)),
            ("Sistem Aktif", lambda: comm.send_system_active(True)),
            ("Hedef Pozisyon", lambda: comm.send_target_position(150.5, 200.3)),
            ("Ateş Komutu", lambda: comm.send_fire_command()),
            ("Kalibrasyon", lambda: comm.send_calibration_command()),
            ("Acil Durdur", lambda: comm.send_emergency_stop())
        ]
        
        for desc, cmd in test_commands:
            print(f"\n📤 Test: {desc}")
            success = cmd()
            print(f"   Sonuç: {'✅' if success else '❌'}")
            time.sleep(2)
        
        # Durum bilgisini göster
        print("\n📊 Sistem Durumu:")
        status = comm.get_system_status()
        print(f"   Bağlantı: {status['communication']['connected']}")
        print(f"   Gönderilen komut: {status['stats']['commands_sent']}")
        print(f"   Alınan veri: {status['stats']['data_received']}")
        print(f"   Alınan frame: {status['stats']['frames_received']}")
        
        # 5 saniye daha bekle
        print("\n⏱️ 5 saniye daha test...")
        time.sleep(5)
    
    # İletişimi durdur
    comm.stop_communication()
    print("\nTest tamamlandı!")