# gui/controllers/app_controller.py
import queue
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum

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
    GUI ve sistem arasındaki köprü görevi görür
    """
    
    def __init__(self):
        # İletişim kuyruğu
        self.command_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.target_queue = queue.Queue()  # PUC process ile iletişim
        
        # Sistem durumu
        self.state = SystemState()
        
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
            'errors': 0,
            'uptime': timedelta(0)
        }
    
    def start(self) -> None:
        """Kontrolcüyü başlat"""
        if not self.running:
            self.running = True
            self.state.start_time = datetime.now()
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            self.add_log("App Controller başlatıldı")
    
    def stop(self) -> None:
        """Kontrolcüyü durdur"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
        self.add_log("App Controller durduruldu")
    
    def send_command(self, command: str, data: Any = None) -> None:
        """
        Komut gönder
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
        
        self.command_queue.put(command_data)
        self.stats['commands_sent'] += 1
        
        # Komut işle
        self._process_command(command, data)
        
        self.add_log(f"Komut gönderildi: {command}")
    
    def _process_command(self, command: str, data: Any) -> None:
        """Komutları işle"""
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
                self.state.selected_weapon = WeaponType(data)
                self.trigger_event("weapon_selected", self.state.selected_weapon)
                
        except Exception as e:
            self.stats['errors'] += 1
            self.add_log(f"Komut işleme hatası: {e}")
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Olay dinleyicisi kaydet
        Args:
            event: Olay adı
            callback: Çağırılacak fonksiyon
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def trigger_event(self, event: str, data: Any = None) -> None:
        """
        Olay tetikle
        Args:
            event: Olay adı
            data: Olay verisi
        """
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    self.add_log(f"Callback hatası [{event}]: {e}")
    
    def update_target_data(self, target_data: Dict[str, Any]) -> None:
        """
        Hedef verilerini güncelle (PUC process'ten gelir)
        Args:
            target_data: Hedef veri sözlüğü
        """
        if not target_data:
            return
            
        # Hedef bilgilerini güncelle
        if 'x_target' in target_data:
            self.state.target.x = target_data['x_target']
        if 'y_target' in target_data:
            self.state.target.y = target_data['y_target']
        if 'distance' in target_data:
            self.state.target.distance = target_data['distance']
        if 'speed' in target_data:
            self.state.target.speed = target_data['speed']
        if 'target_locked' in target_data:
            self.state.target.locked = target_data['target_locked']
        if 'weapon' in target_data:
            self.state.selected_weapon = WeaponType(target_data['weapon'])
        
        # Motor pozisyonları
        if 'pan_angle' in target_data:
            self.state.pan_angle = target_data['pan_angle']
        if 'tilt_angle' in target_data:
            self.state.tilt_angle = target_data['tilt_angle']
        
        self.state.last_update = datetime.now()
        self.stats['updates_received'] += 1
        
        # GUI'yi güncelle
        self.trigger_event("data_updated", self.get_state_dict())
    
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
            'uptime': str(uptime).split('.')[0],  # Mikrosaniye kısmını kaldır
            
            # Sistem bilgileri
            'last_update': self.state.last_update.strftime("%H:%M:%S"),
            'commands_sent': self.stats['commands_sent'],
            'updates_received': self.stats['updates_received'],
            'errors': self.stats['errors']
        }
    
    def add_log(self, message: str, level: str = "INFO") -> None:
        """
        Log mesajı ekle
        Args:
            message: Log mesajı
            level: Log seviyesi (INFO, WARNING, ERROR)
        """
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
                # PUC process'ten veri kontrolü
                self._check_target_queue()
                
                # Sistem durumunu güncelle
                self._update_system_status()
                
                # İstatistikleri güncelle
                self._update_statistics()
                
                time.sleep(0.1)  # 10 Hz güncelleme
                
            except Exception as e:
                self.stats['errors'] += 1
                self.add_log(f"Update loop hatası: {e}", "ERROR")
                time.sleep(0.5)
    
    def _check_target_queue(self) -> None:
        """Hedef kuyruğunu kontrol et"""
        try:
            while not self.target_queue.empty():
                target_data = self.target_queue.get_nowait()
                self.update_target_data(target_data)
        except queue.Empty:
            pass
    
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
        # Bu metot gerçek sistemde daha karmaşık olabilir
        pass
    
    def connect_to_puc_process(self, target_queue_ref, system_mode_ref, target_destroyed_flag_ref):
        """
        PUC process ile bağlantı kur
        Args:
            target_queue_ref: PUC process'in target_queue referansı
            system_mode_ref: Sistem modu shared variable referansı
            target_destroyed_flag_ref: Hedef imha flag referansı
        """
        self.target_queue = target_queue_ref
        self.system_mode_ref = system_mode_ref
        self.target_destroyed_flag_ref = target_destroyed_flag_ref
        
        self.add_log("PUC Process ile bağlantı kuruldu")
    
    def simulate_data(self) -> None:
        """Test için veri simülasyonu"""
        import random
        
        if not self.state.active:
            return
            
        # Rastgele hedef verisi
        simulated_data = {
            'x_target': random.randint(300, 400),
            'y_target': random.randint(350, 450),
            'distance': random.uniform(50, 500),
            'speed': random.uniform(0, 25),
            'target_locked': random.choice([True, False]),
            'weapon': random.choice(['Laser', 'Airgun', 'Auto']),
            'pan_angle': random.uniform(-180, 180),
            'tilt_angle': random.uniform(-75, 75)
        }
        
        self.update_target_data(simulated_data)