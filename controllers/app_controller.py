# gui/controllers/app_controller.py - UPDATED VERSION
import queue
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Communication Manager'ı import et
from communication.communication_manager import CommunicationManager

class SystemMode(Enum):
    """Sistem modları"""
    MANUAL = 0
    STAGE_1 = 1  # Tüm hedefler
    STAGE_2 = 2  # Dost-düşman ayrımı
    STAGE_3 = 3  # Angajman emri

class WeaponType(Enum):
    """Mühimmat türleri"""
    NONE = "None"
    LASER = "Laser"
    AIRGUN = "Airgun"
    AUTO = "Auto"

@dataclass
class TargetData:
    """Hedef verisi"""
    x: float = 0.0
    y: float = 0.0
    distance: float = 0.0
    speed: float = 0.0
    size: float = 0.0
    locked: bool = False
    type: str = "Unknown"
    confidence: float = 0.0

@dataclass
class SystemState:
    """Sistem durumu"""
    mode: SystemMode = SystemMode.MANUAL
    active: bool = False
    emergency_stop: bool = False
    
    # Hedef bilgileri
    target: TargetData = None
    targets_detected: int = 0
    targets_destroyed: int = 0
    
    # Motor pozisyonları
    pan_angle: float = 0.0
    tilt_angle: float = 0.0
    
    # Mühimmat
    selected_weapon: WeaponType = WeaponType.NONE
    weapon_ready: bool = False
    
    # Zaman bilgileri
    start_time: datetime = None
    last_update: datetime = None
    
    # Raspberry Pi bağlantı durumu
    raspberry_connected: bool = False
    camera_connected: bool = False
    
    def __post_init__(self):
        if self.target is None:
            self.target = TargetData()
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.last_update is None:
            self.last_update = datetime.now()

class AppController:
    """
    Uygulama mantığını yöneten ana kontrolcü sınıfı
    GUI ve Raspberry Pi arasındaki köprü görevi görür
    HTTP iletişimi ile entegre edildi
    """
    
    def __init__(self, raspberry_ip: str = "localhost"):
        # İletişim kuyruğu (legacy support için)
        self.command_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # Sistem durumu
        self.state = SystemState()
        
        # Communication Manager
        self.comm_manager = CommunicationManager(raspberry_ip)
        
        # Callback'ler
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # Thread kontrolü
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        
        # Loglar
        self.logs: List[str] = []
        self.max_logs = 1000
        
        # İstatistikler
        self.stats = {
            'commands_sent': 0,
            'updates_received': 0,
            'frames_received': 0,
            'errors': 0,
            'uptime': timedelta(0)
        }
        
        # Communication Manager callback'lerini kur
        self._setup_communication_callbacks()
        
        print("[APP CONTROLLER] HTTP Communication ile oluşturuldu")
    
    def _setup_communication_callbacks(self):
        """Communication Manager callback'lerini kur"""
        self.comm_manager.register_data_callback(self._on_raspberry_data_received)
        self.comm_manager.register_frame_callback(self._on_raspberry_frame_received)
        self.comm_manager.register_connection_callback(self._on_raspberry_connection_changed)
        self.comm_manager.register_error_callback(self._on_raspberry_error)
    
    def start(self) -> None:
        """Kontrolcüyü başlat"""
        if not self.running:
            self.running = True
            self.state.start_time = datetime.now()
            
            # Communication Manager'ı başlat
            raspberry_connected = self.comm_manager.start_communication()
            self.state.raspberry_connected = raspberry_connected
            
            # Update thread'ini başlat
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            log_msg = "App Controller başlatıldı"
            if raspberry_connected:
                log_msg += " (Raspberry Pi bağlı)"
            else:
                log_msg += " (Raspberry Pi bağlantısı yok)"
            
            self.add_log(log_msg)
    
    def stop(self) -> None:
        """Kontrolcüyü durdur"""
        self.running = False
        
        # Communication Manager'ı durdur
        self.comm_manager.stop_communication()
        
        # Update thread'ini bekle
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
        
        self.add_log("App Controller durduruldu")
    
    def send_command(self, command: str, data: Any = None) -> None:
        """
        Komut gönder - Hem local hem Raspberry Pi'ye
        Args:
            command: Komut adı
            data: Komut verisi
        """
        command_data = {
            'command': command,
            'data': data,
            'timestamp': datetime.now(),
            'id': self.stats['commands_sent']
        }
        
        # Legacy queue'ya ekle
        self.command_queue.put(command_data)
        
        # Local olarak işle
        self._process_command(command, data)
        
        # Raspberry Pi'ye gönder
        raspberry_success = self._send_command_to_raspberry(command, data)
        
        self.stats['commands_sent'] += 1
        
        log_msg = f"Komut gönderildi: {command}"
        if raspberry_success:
            log_msg += " (Raspberry Pi'ye gönderildi)"
        else:
            log_msg += " (Sadece local)"
        
        self.add_log(log_msg)
    
    def _send_command_to_raspberry(self, command: str, data: Any) -> bool:
        """Komutu Raspberry Pi'ye gönder"""
        if not self.state.raspberry_connected:
            return False
        
        try:
            # Komuta göre uygun Raspberry format oluştur
            raspberry_data = self._convert_command_to_raspberry_format(command, data)
            
            if raspberry_data:
                return self.comm_manager.send_command(raspberry_data)
            
            return False
            
        except Exception as e:
            self.add_log(f"Raspberry komut gönderme hatası: {e}", "ERROR")
            return False
    
    def _convert_command_to_raspberry_format(self, command: str, data: Any) -> Optional[Dict[str, Any]]:
        """GUI komutunu Raspberry formatına çevir"""
        raspberry_data = {}
        
        if command == "change_mode":
            raspberry_data = {"system_mode": data}
            
        elif command == "start_system":
            raspberry_data = {"system_active": True}
            
        elif command == "stop_system":
            raspberry_data = {"system_active": False}
            
        elif command == "emergency_stop":
            raspberry_data = {
                "emergency_stop": True,
                "system_active": False,
                "fire_gui_flag": False,
                "engagement_started_flag": False
            }
            
        elif command == "fire_weapon":
            raspberry_data = {
                "fire_gui_flag": True,
                "engagement_started_flag": True
            }
            
        elif command == "start_scan":
            raspberry_data = {
                "scanning_target_flag": True,
                "system_active": True
            }
            
        elif command == "select_weapon":
            weapon_map = {
                WeaponType.LASER: "L",
                WeaponType.AIRGUN: "A", 
                WeaponType.AUTO: "Auto"
            }
            raspberry_data = {"weapon": weapon_map.get(data, "E")}
            
        elif command == "calibrate_joystick":
            raspberry_data = {"calibration_flag": True}
            
        elif command == "update_target_position":
            if isinstance(data, dict) and 'x' in data and 'y' in data:
                raspberry_data = {
                    "x_target": data['x'],
                    "y_target": data['y']
                }
        
        return raspberry_data if raspberry_data else None
    
    def _process_command(self, command: str, data: Any) -> None:
        """Komutları local olarak işle"""
        try:
            if command == "change_mode":
                self.state.mode = SystemMode(data)
                self.trigger_event("mode_changed", self.state.mode)
                
            elif command == "start_system":
                self.state.active = True
                self.trigger_event("system_started")
                
            elif command == "stop_system":
                self.state.active = False
                self.trigger_event("system_stopped")
                
            elif command == "emergency_stop":
                self.state.emergency_stop = True
                self.state.active = False
                self.trigger_event("emergency_stop")
                
            elif command == "fire_weapon":
                if self.state.target.locked and self.state.weapon_ready:
                    self.trigger_event("weapon_fired", self.state.selected_weapon)
                    
            elif command == "start_scan":
                if self.state.active:
                    self.trigger_event("scan_started")
                    
            elif command == "select_weapon":
                if isinstance(data, WeaponType):
                    self.state.selected_weapon = data
                elif isinstance(data, str):
                    # String'den WeaponType'a dönüştür
                    weapon_map = {
                        "Laser": WeaponType.LASER,
                        "Airgun": WeaponType.AIRGUN,
                        "Auto": WeaponType.AUTO
                    }
                    self.state.selected_weapon = weapon_map.get(data, WeaponType.NONE)
                
                self.trigger_event("weapon_selected", self.state.selected_weapon)
                
        except Exception as e:
            self.stats['errors'] += 1
            self.add_log(f"Komut işleme hatası: {e}", "ERROR")
    
    def _on_raspberry_data_received(self, data: Dict[str, Any]):
        """Raspberry Pi'den veri alındığında"""
        try:
            # Raspberry formatını GUI formatına çevir
            gui_data = self._convert_raspberry_data_to_gui_format(data)
            
            # Sistem durumunu güncelle
            self.update_target_data(gui_data)
            
            self.stats['updates_received'] += 1
            self.add_log(f"Raspberry'den veri alındı", "DEBUG")
            
        except Exception as e:
            self.add_log(f"Raspberry veri işleme hatası: {e}", "ERROR")
    
    def _on_raspberry_frame_received(self, frame):
        """Raspberry Pi'den frame alındığında"""
        try:
            self.stats['frames_received'] += 1
            
            # Frame'i GUI'ye aktar
            self.trigger_event("frame_received", frame)
            
        except Exception as e:
            self.add_log(f"Frame işleme hatası: {e}", "ERROR")
    
    def _on_raspberry_connection_changed(self, connected: bool, details: Dict[str, Any]):
        """Raspberry Pi bağlantı durumu değiştiğinde"""
        self.state.raspberry_connected = details.get('data_connected', False)
        self.state.camera_connected = details.get('camera_connected', False)
        
        status = "bağlandı" if connected else "bağlantı kesildi"
        self.add_log(f"Raspberry Pi {status}")
        
        self.trigger_event("raspberry_connection_changed", {
            'connected': connected,
            'details': details
        })
    
    def _on_raspberry_error(self, error_message: str):
        """Raspberry Pi hata oluştuğunda"""
        self.stats['errors'] += 1
        self.add_log(f"Raspberry Pi hatası: {error_message}", "ERROR")
        self.trigger_event("raspberry_error", error_message)
    
    def _convert_raspberry_data_to_gui_format(self, raspberry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raspberry formatını GUI formatına çevir"""
        gui_data = {}
        
        # Hedef pozisyonu
        if 'x_target' in raspberry_data:
            gui_data['target_x'] = float(raspberry_data['x_target'])
        if 'y_target' in raspberry_data:
            gui_data['target_y'] = float(raspberry_data['y_target'])
        
        # Motor açıları
        if 'global_angle' in raspberry_data:
            gui_data['pan_angle'] = float(raspberry_data['global_angle'])
        if 'global_tilt_angle' in raspberry_data:
            gui_data['tilt_angle'] = float(raspberry_data['global_tilt_angle'])
        
        # Sistem durumu
        if 'system_mode' in raspberry_data:
            gui_data['mode'] = int(raspberry_data['system_mode'])
        if 'target_destroyed_flag' in raspberry_data:
            gui_data['target_destroyed'] = bool(raspberry_data['target_destroyed_flag'])
        if 'scanning_target_flag' in raspberry_data:
            gui_data['scanning'] = bool(raspberry_data['scanning_target_flag'])
        if 'target_detected_flag' in raspberry_data:
            gui_data['target_locked'] = bool(raspberry_data['target_detected_flag'])
        
        # Mühimmat
        if 'weapon' in raspberry_data:
            weapon_map = {
                'L': 'Laser',
                'A': 'Airgun',
                'E': 'None'
            }
            gui_data['weapon'] = weapon_map.get(raspberry_data['weapon'], 'Auto')
        
        return gui_data
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Olay dinleyicisi kaydet"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def trigger_event(self, event: str, data: Any = None) -> None:
        """Olay tetikle"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    self.add_log(f"Callback hatası [{event}]: {e}", "ERROR")
    
    def update_target_data(self, target_data: Dict[str, Any]) -> None:
        """Hedef verilerini güncelle"""
        if not target_data:
            return
            
        # Hedef bilgilerini güncelle
        if 'target_x' in target_data:
            self.state.target.x = target_data['target_x']
        if 'target_y' in target_data:
            self.state.target.y = target_data['target_y']
        if 'distance' in target_data:
            self.state.target.distance = target_data['distance']
        if 'speed' in target_data:
            self.state.target.speed = target_data['speed']
        if 'target_locked' in target_data:
            self.state.target.locked = target_data['target_locked']
        if 'weapon' in target_data:
            weapon_map = {
                'Laser': WeaponType.LASER,
                'Airgun': WeaponType.AIRGUN,
                'Auto': WeaponType.AUTO,
                'None': WeaponType.NONE
            }
            self.state.selected_weapon = weapon_map.get(target_data['weapon'], WeaponType.NONE)
        
        # Motor pozisyonları
        if 'pan_angle' in target_data:
            self.state.pan_angle = target_data['pan_angle']
        if 'tilt_angle' in target_data:
            self.state.tilt_angle = target_data['tilt_angle']
        
        # İstatistik güncellemeleri
        if 'target_destroyed' in target_data and target_data['target_destroyed']:
            self.state.targets_destroyed += 1
        
        self.state.last_update = datetime.now()
        
        # GUI'yi güncelle
        self.trigger_event("data_updated", self.get_state_dict())
    
    def get_current_frame_for_gui(self, width: int = None, height: int = None):
        """GUI için mevcut kamera frame'ini al"""
        return self.comm_manager.get_current_frame_for_gui(width, height)
    
    def save_current_frame(self, filename: str) -> bool:
        """Mevcut frame'i kaydet"""
        return self.comm_manager.save_current_frame(filename)
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Sistem durumunu sözlük olarak döndür"""
        uptime = datetime.now() - self.state.start_time if self.state.start_time else timedelta(0)
        
        success_rate = 0
        if self.state.targets_detected > 0:
            success_rate = (self.state.targets_destroyed / self.state.targets_detected) * 100
        
        return {
            # Sistem durumu
            'mode': self.state.mode.value,
            'mode_name': self.state.mode.name,
            'active': self.state.active,
            'emergency_stop': self.state.emergency_stop,
            
            # Bağlantı durumu
            'raspberry_connected': self.state.raspberry_connected,
            'camera_connected': self.state.camera_connected,
            
            # Hedef bilgileri
            'target_locked': self.state.target.locked,
            'target_x': self.state.target.x,
            'target_y': self.state.target.y,
            'distance': self.state.target.distance,
            'speed': self.state.target.speed,
            'target_type': self.state.target.type,
            
            # Motor pozisyonları
            'pan_angle': self.state.pan_angle,
            'tilt_angle': self.state.tilt_angle,
            
            # Mühimmat
            'weapon': self.state.selected_weapon.value,
            'weapon_ready': self.state.weapon_ready,
            
            # İstatistikler
            'targets_detected': self.state.targets_detected,
            'targets_destroyed': self.state.targets_destroyed,
            'success_rate': success_rate,
            'uptime': str(uptime).split('.')[0],
            
            # Sistem bilgileri
            'last_update': self.state.last_update.strftime("%H:%M:%S"),
            'commands_sent': self.stats['commands_sent'],
            'updates_received': self.stats['updates_received'],
            'frames_received': self.stats['frames_received'],
            'errors': self.stats['errors']
        }
    
    def add_log(self, message: str, level: str = "INFO") -> None:
        """Log mesajı ekle"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        self.logs.append(log_entry)
        
        # Max log sayısını aş
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Log callback'ini tetikle
        self.trigger_event("log_added", log_entry)
    
    def get_recent_logs(self, count: int = 50) -> List[str]:
        """Son N log mesajını döndür"""
        return self.logs[-count:] if self.logs else []
    
    def _update_loop(self) -> None:
        """Ana güncelleme döngüsü"""
        while self.running:
            try:
                # Sistem durumunu güncelle
                self._update_system_status()
                
                # İstatistikleri güncelle
                self._update_statistics()
                
                time.sleep(0.1)  # 10 Hz güncelleme
                
            except Exception as e:
                self.stats['errors'] += 1
                self.add_log(f"Update loop hatası: {e}", "ERROR")
                time.sleep(0.5)
    
    def _update_system_status(self) -> None:
        """Sistem durumunu güncelle"""
        # Uptime güncelle
        if self.state.start_time:
            self.stats['uptime'] = datetime.now() - self.state.start_time
        
        # Acil durdurma kontrolü
        if self.state.emergency_stop:
            self.state.active = False
            self.state.target.locked = False
    
    def _update_statistics(self) -> None:
        """İstatistikleri güncelle"""
        # Communication Manager istatistikleri al
        comm_status = self.comm_manager.get_system_status()
        comm_stats = comm_status.get('stats', {})
        
        # Kendi istatistiklerimizi güncelle
        self.stats['commands_sent'] = comm_stats.get('commands_sent', self.stats['commands_sent'])
        self.stats['frames_received'] = comm_stats.get('frames_received', self.stats['frames_received'])
    
    def get_communication_status(self) -> Dict[str, Any]:
        """İletişim durumu detayları"""
        return self.comm_manager.get_system_status()
    
    # Kolay kullanım için kısayol metodlar
    def set_raspberry_ip(self, ip: str):
        """Raspberry Pi IP adresini değiştir"""
        # Mevcut bağlantıyı durdur
        self.comm_manager.stop_communication()
        
        # Yeni IP ile yeni Communication Manager oluştur
        self.comm_manager = CommunicationManager(ip)
        self._setup_communication_callbacks()
        
        # Yeniden bağlan
        if self.running:
            raspberry_connected = self.comm_manager.start_communication()
            self.state.raspberry_connected = raspberry_connected
            
            self.add_log(f"Raspberry Pi IP değiştirildi: {ip}")
    
    def simulate_data(self) -> None:
        """Test için veri simülasyonu (Raspberry Pi bağlı değilse)"""
        if self.state.raspberry_connected:
            return  # Gerçek veri varsa simülasyon yapma
            
        import random
        
        if not self.state.active:
            return
            
        # Rastgele hedef verisi
        simulated_data = {
            'target_x': random.randint(300, 400),
            'target_y': random.randint(350, 450),
            'distance': random.uniform(50, 500),
            'speed': random.uniform(0, 25),
            'target_locked': random.choice([True, False]),
            'weapon': random.choice(['Laser', 'Airgun', 'Auto']),
            'pan_angle': random.uniform(-180, 180),
            'tilt_angle': random.uniform(-75, 75)
        }