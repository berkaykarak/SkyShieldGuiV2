# gui/controllers/app_controller.py - UPDATED VERSION
import queue
import threading
import time
from datetime import datetime, timedelta
import traceback
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
    NONE = 'E'
    LASER = 'L'
    AIRGUN = 'A'
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
    controller_connected: bool = False
 

    # ========== YENİ: EKSİK ALANLAR ==========
    
    # STAGE_1 - Balon Avı
    balloon_count: int = 0
    
    # STAGE_2 - Dost/Düşman Ayrımı
    friend_targets: int = 0
    enemy_targets: int = 0
    enemy_destroyed: int = 0
    classification_accuracy: float = 0.0

    # STAGE_3 - QR Kod ve Angajman
    target_color: str = "unknown"
    target_shape: str = "unknown"
    current_platform: str = "A"
    qr_code_detected: bool = False
    engagement_authorized: bool = False

    
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
        self.emergency_mode = False
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

    def set_emergency_mode(self, emergency: bool):
        """Acil durum modunu ayarla"""
        self.emergency_mode = emergency
        print(f"[APP CONTROLLER] Emergency mode: {emergency}")

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
            self.state.raspberry_connected = True
            
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
        }
        
        # ========== GÖNDERILEN KOMUT LOGU - HER ZAMAN GÖSTER ==========
        print(f"[APP CTRL] 📤 KOMUT GÖNDERİLİYOR: {command}")
        if data is not None:
            print(f"   📋 Veri: {data}")

        # Legacy queue'ya ekle
        self.command_queue.put(command_data)
        
        # Local olarak işle
        self._process_command(command, data)
        
        # Raspberry Pi'ye gönder
        raspberry_success = self._send_command_to_raspberry(command, data)
        
        self.stats['commands_sent'] += 1
        
        # Sonuç bildirimi
        if raspberry_success:
            print(f"   ✅ Raspberry Pi'ye gönderildi")
        else:
            print(f"   ⚠️ Sadece local işlendi (Raspberry Pi bağlantısı yok)")
        
        log_msg = f"Komut gönderildi: {command}"
        if raspberry_success:
            log_msg += " (Raspberry Pi'ye gönderildi)"
        else:
            log_msg += " (Sadece local)"
        
        self.add_log(log_msg)
    
    def _send_command_to_raspberry(self, command: str, data: Any) -> bool:
        """Komutu Raspberry Pi'ye gönder - CLEAN VERSION"""
        if not self.state.raspberry_connected:
            return False

        try:
            # Komuta göre uygun Raspberry format oluştur
            raspberry_data = self._convert_command_to_raspberry_format(command, data)
            
            if raspberry_data:
                print(f"   🔄 Raspberry formatı: {raspberry_data}")
                return self.comm_manager.send_command(raspberry_data)
            else:
                print(f"   ⚠️ Bu komut Raspberry Pi formatına çevrilemiyor: {command}")
                return False
                
        except Exception as e:
            print(f"   ❌ Raspberry komut gönderme hatası: {e}")
            self.add_log(f"Raspberry komut gönderme hatası: {e}", "ERROR")
            return False

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



    def _convert_command_to_raspberry_format(self, command: str, data: Any) -> Optional[Dict[str, Any]]:
        """GUI komutunu Raspberry WebSocket formatına çevir"""
        raspberry_data = {}

        if command == "change_mode":
            try:
                mode = data.value if isinstance(data, SystemMode) else int(data)
                raspberry_data["change_phase"] = mode
                # print(f"[COMMAND] Aşama değişikliği: {mode}")  # ← Bu satırı comment out
            except (ValueError, TypeError):
                pass

        elif command == "start_system":
            raspberry_data["start_system"] = True

        elif command == "stop_system":
            raspberry_data["stop_system"] = True

        elif command == "emergency_stop":
            raspberry_data["system_mode"] = True

        elif command == "fire_weapon":
            raspberry_data["fire_gui_flag"] = True
            raspberry_data["engagement_started_flag"] = True

        elif command == "switch_platform":
            raspberry_data["switch_platform"] = True
            # print("[COMMAND] Platform değiştirme komutu gönderiliyor")  # ← Comment out

        elif command == "start_scan":
            raspberry_data["scanning_target_flag"] = True

        # ========== ✅ WEAPON COMMAND - SADECE BU LOG'LAR KALDI ==========
        elif command == "select_weapon":
            weapon_value = str(data) if data else "Auto"
            
            weapon_map = {
                "Lazer": "L",
                "Boncuk": "A",
                "Otomatik": "L",
                "Auto": "L",
                "Laser": "L",
                "Airgun": "A",
                "None": "L"
            }
            
            raspberry_weapon = weapon_map.get(weapon_value, "L")
            raspberry_data["weapon"] = raspberry_weapon
            
            # ✅ SADECE WEAPON LOG'LARI - BÜYÜK VE GÖRÜNÜR
            print(f"\n{'='*60}")
            print(f"🔫 WEAPON COMMAND: '{weapon_value}' → '{raspberry_weapon}'")
            if weapon_value in ["Otomatik", "Auto"]:
                print(f"🎯 Otomatik modda varsayılan: Lazer (L)")
            print(f"📤 Raspberry'ye gönderilen: weapon = '{raspberry_weapon}'")
            print(f"{'='*60}\n")

        elif command == "calibrate_joystick":
            raspberry_data["calibration_flag"] = True

        elif command == "update_target_position":
            if isinstance(data, dict) and "x" in data and "y" in data:
                raspberry_data["x_target"] = int(data["x"])
                raspberry_data["y_target"] = int(data["y"])

        return raspberry_data if raspberry_data else None
    

    
    def _get_mode_name(self, mode: int) -> str:
        """Mod numarasını isme çevir"""
        mode_names = {
            0: "MANUEL", 
            1: "AŞAMA 1",
            2: "AŞAMA 2",
            3: "AŞAMA 3"
        }
        return mode_names.get(mode, f"MOD {mode}")


    
    def _on_raspberry_data_received(self, data: Dict[str, Any]):
        """Raspberry Pi'den veri alındığında - CONDITIONAL DEBUG"""
        try:
            if self.emergency_mode:
                print("[APP CONTROLLER] Emergency mode aktif - veri işlenmiyor")
                return
            
            # ✅ SADECE AŞAMA 3'TEYKEN DETAYLI DEBUG
            current_phase = data.get('phase_mode', 0)
            is_phase_3 = (current_phase == 3)
            
            if is_phase_3:
                # Sadece Aşama 3'te detaylı debug göster
                print(f"\n[APP CTRL] 📥 RAW DATA ALINDI (AŞAMA 3):")
                print(f"   target_color: {data.get('target_color', 'YOK')}")
                print(f"   target_shape: {data.get('target_shape', 'YOK')}")
                print(f"   target_side: {data.get('target_side', 'YOK')}")
            
            gui_data = self._convert_raspberry_data_to_gui_format(data)
            
            if is_phase_3:
                # Sadece Aşama 3'te converted data göster
                print(f"[APP CTRL] 🔄 CONVERTED DATA (AŞAMA 3):")
                print(f"   target_color: {gui_data.get('target_color', 'YOK')}")
                print(f"   target_shape: {gui_data.get('target_shape', 'YOK')}")
                print(f"   target_side: {gui_data.get('target_side', 'YOK')}")
            
            self.update_target_data(gui_data)
            self.stats['updates_received'] += 1
            
            if is_phase_3:
                # Sadece Aşama 3'te final state göster
                print(f"[APP CTRL] 📊 FINAL STATE (AŞAMA 3):")
                print(f"   state.target_color: {getattr(self.state, 'target_color', 'YOK')}")
                print(f"   state.target_shape: {getattr(self.state, 'target_shape', 'YOK')}")
                print(f"   state.current_platform: {getattr(self.state, 'current_platform', 'YOK')}")
            
            # Normal log (her zaman)
            self.add_log(f"Raspberry'den veri alındı", "DEBUG")
            
        except Exception as e:
            print(f"[APP CTRL] ❌ _on_raspberry_data_received hatası: {e}")
            import traceback
            traceback.print_exc()
            self.add_log(f"Raspberry veri işleme hatası: {e}", "ERROR")

    def _on_frame_received(self, frame):
        """Raspberry Pi'den frame alındığında"""
        try:
            # ✅ YENİ: Emergency modda frame işleme
            if self.emergency_mode:
                print("[APP CONTROLLER] Emergency mode aktif - frame işlenmiyor")
                return
            
            # Normal frame işleme
            self.stats['frames_received'] += 1
            self.trigger_event("frame_received", frame)
            
        except Exception as e:
            self.add_log(f"Frame işleme hatası: {e}", "ERROR")
    
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
        """CRITICAL FIX: Raspberry verisini GUI formatına çevir"""
        gui_data = {}
        
        try:
            # ========== RASPBERRY Pİ FORMAT DÖNÜŞTÜRME TABLOLARI ==========
            color_conversion = {
                'R': 'red',
                'G': 'green', 
                'B': 'blue'
            }
            
            shape_conversion = {
                'T': 'triangle',
                'C': 'circle',
                'S': 'square'
            }
            
            # ========== ORTAK SİSTEM VERİLERİ ==========
            if 'system_active' in raspberry_data:
                gui_data['system_active'] = raspberry_data['system_active']
                gui_data['active'] = raspberry_data['system_active']

            if 'phase_mode' in raspberry_data:
                gui_data['mode'] = raspberry_data['phase_mode']
                gui_data['mode_name'] = self._get_mode_name(raspberry_data['phase_mode'])

            if 'target_detected_flag' in raspberry_data:
                gui_data['target_locked'] = raspberry_data['target_detected_flag']
            if 'x_target' in raspberry_data:
                gui_data['target_x'] = float(raspberry_data['x_target'])
            if 'y_target' in raspberry_data:
                gui_data['target_y'] = float(raspberry_data['y_target'])

            # Motor açıları
            if 'pan_angle' in raspberry_data:
                gui_data['pan_angle'] = float(raspberry_data['pan_angle'])
            if 'tilt_angle' in raspberry_data:
                gui_data['tilt_angle'] = float(raspberry_data['tilt_angle'])
            if 'global_angle' in raspberry_data:
                gui_data['pan_angle'] = float(raspberry_data['global_angle'])
            if 'global_tilt_angle' in raspberry_data:
                gui_data['tilt_angle'] = float(raspberry_data['global_tilt_angle'])

            # Mühimmat
            if 'weapon' in raspberry_data:
                weapon_map = {'L': 'Laser', 'A': 'Airgun', 'E': 'None', 'None': 'Auto'}
                gui_data['weapon'] = weapon_map.get(raspberry_data['weapon'], 'Auto')

            # Controller durumu
            if 'controller_connected' in raspberry_data:
                gui_data['controller_connected'] = bool(raspberry_data['controller_connected'])

            # ========== AŞAMA 1 VERİLERİ ==========
            if 'targets_detected' in raspberry_data:
                gui_data['targets_detected'] = int(raspberry_data['targets_detected'])
            if 'targets_destroyed' in raspberry_data:
                gui_data['targets_destroyed'] = int(raspberry_data['targets_destroyed'])
            if 'balloon_count' in raspberry_data:
                gui_data['balloon_count'] = int(raspberry_data['balloon_count'])

            # ========== AŞAMA 2 VERİLERİ ==========
            if 'friend_targets' in raspberry_data:
                gui_data['friend_targets'] = int(raspberry_data['friend_targets'])
            if 'enemy_targets' in raspberry_data:
                gui_data['enemy_targets'] = int(raspberry_data['enemy_targets'])
            if 'enemy_destroyed' in raspberry_data:
                gui_data['enemy_destroyed'] = int(raspberry_data['enemy_destroyed'])
            if 'classification_accuracy' in raspberry_data:
                gui_data['classification_accuracy'] = float(raspberry_data['classification_accuracy'])

            # ========== AŞAMA 3 VERİLERİ - CONDITIONAL LOGGING ==========
            
            # ✅ SADECE AŞAMA 3'TEYKEN DEBUG LOG'LARI GÖSTER
            current_phase = raspberry_data.get('phase_mode', gui_data.get('mode', 0))
            is_phase_3 = (current_phase == 3)
            
            # Aşama 3 verilerini işle ama log'ları sadece Aşama 3'te göster
            if 'target_color' in raspberry_data:
                color_value = str(raspberry_data['target_color']).strip()
                
                if color_value.lower() in ['red', 'green', 'blue', 'yellow', 'orange', 'purple']:
                    gui_data['target_color'] = color_value.lower()
                    if is_phase_3:  # ✅ Sadece Aşama 3'te log göster
                        print(f"[FORMAT] Renk direkt kullanım (WebSocket'ten): {color_value} → {gui_data['target_color']}")
                elif len(color_value) == 1 and color_value.upper() in ['R', 'G', 'B']:
                    raspberry_color = color_value.upper()
                    gui_data['target_color'] = color_conversion.get(raspberry_color, 'unknown')
                    if is_phase_3:  # ✅ Sadece Aşama 3'te log göster
                        print(f"[FORMAT] Renk dönüştürme (R/G/B): {raspberry_color} → {gui_data['target_color']}")
                else:
                    gui_data['target_color'] = 'unknown'
                    if is_phase_3:  # ✅ Sadece Aşama 3'te log göster
                        print(f"[FORMAT] Bilinmeyen renk formatı: {color_value}")

            if 'target_shape' in raspberry_data:
                shape_value = str(raspberry_data['target_shape']).strip()
                
                if shape_value.lower() in ['triangle', 'circle', 'square', 'rectangle']:
                    gui_data['target_shape'] = shape_value.lower()
                    if is_phase_3:  # ✅ Sadece Aşama 3'te log göster
                        print(f"[FORMAT] Şekil direkt kullanım (WebSocket'ten): {shape_value} → {gui_data['target_shape']}")
                elif len(shape_value) == 1 and shape_value.upper() in ['T', 'C', 'S']:
                    raspberry_shape = shape_value.upper()
                    gui_data['target_shape'] = shape_conversion.get(raspberry_shape, 'unknown')
                    if is_phase_3:  # ✅ Sadece Aşama 3'te log göster
                        print(f"[FORMAT] Şekil dönüştürme (T/C/S): {raspberry_shape} → {gui_data['target_shape']}")
                else:
                    gui_data['target_shape'] = 'unknown'
                    if is_phase_3:  # ✅ Sadece Aşama 3'te log göster
                        print(f"[FORMAT] Bilinmeyen şekil formatı: {shape_value}")

            if 'target_side' in raspberry_data:
                target_side_value = str(raspberry_data['target_side']).upper().strip()
                gui_data['target_side'] = target_side_value
                if is_phase_3:  # ✅ Sadece Aşama 3'te log göster
                    print(f"[FORMAT] Target Side: {raspberry_data['target_side']} → {gui_data['target_side']}")

            if 'qr_code_detected' in raspberry_data:
                gui_data['qr_code_detected'] = bool(raspberry_data['qr_code_detected'])
            if 'engagement_authorized' in raspberry_data:
                gui_data['engagement_authorized'] = bool(raspberry_data['engagement_authorized'])

            # ========== AŞAMA 3 DEBUG ÇIKTISI - SADECE AŞAMA 3'TE ==========
            if is_phase_3 and any(key in raspberry_data for key in ['target_color', 'target_shape', 'target_side']):
                print(f"\n[CONVERT] 🎯 AŞAMA 3 VERİ DÖNÜŞTÜRME:")
                print(f"   Raspberry: color={raspberry_data.get('target_color', 'YOK')}, shape={raspberry_data.get('target_shape', 'YOK')}, side={raspberry_data.get('target_side', 'YOK')}")
                print(f"   GUI: color={gui_data.get('target_color', 'YOK')}, shape={gui_data.get('target_shape', 'YOK')}, side={gui_data.get('target_side', 'YOK')}")

        except Exception as e:
            print(f"[CONVERT] ❌ Veri dönüştürme hatası: {e}")
            import traceback
            traceback.print_exc()

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
        """CLEAN VERSION: Hedef verilerini güncelle - Sadece Aşama 3'te debug"""
        if not target_data:
            return

        try:
            # ✅ SADECE AŞAMA 3'TEYKEN DETAYLI DEBUG
            current_phase = target_data.get('mode', 0)
            is_phase_3 = (current_phase == 3)
            
            if is_phase_3:
                # Sadece Aşama 3'te input debug göster
                print(f"\n[UPDATE] 📥 TARGET_DATA ALINDI (AŞAMA 3):")
                print(f"   target_color: {target_data.get('target_color', 'YOK')}")
                print(f"   target_shape: {target_data.get('target_shape', 'YOK')}")
                print(f"   target_side: {target_data.get('target_side', 'YOK')}")

            # Mod güncellemesi
            if 'mode' in target_data:
                try:
                    self.state.mode = SystemMode(target_data['mode'])
                except ValueError:
                    pass

            # Genel hedef bilgileri
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
            if 'controller_connected' in target_data:
                self.state.controller_connected = target_data['controller_connected']
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

            # ========== AŞAMA 1 VERİLERİ ==========
            if 'targets_detected' in target_data:
                self.state.targets_detected = int(target_data['targets_detected'])
            if 'targets_destroyed' in target_data:
                self.state.targets_destroyed = int(target_data['targets_destroyed'])
            if 'balloon_count' in target_data:
                self.state.balloon_count = int(target_data['balloon_count'])

            # ========== AŞAMA 2 VERİLERİ ==========
            if 'friend_targets' in target_data:
                self.state.friend_targets = int(target_data['friend_targets'])
            if 'enemy_targets' in target_data:
                self.state.enemy_targets = int(target_data['enemy_targets'])
            if 'enemy_destroyed' in target_data:
                self.state.enemy_destroyed = int(target_data['enemy_destroyed'])
            if 'classification_accuracy' in target_data:
                self.state.classification_accuracy = float(target_data['classification_accuracy'])

            # ========== AŞAMA 3 VERİLERİ - CONDITIONAL LOGGING ==========
            
            # 🔴 target_color
            if 'target_color' in target_data:
                self.state.target_color = str(target_data['target_color'])
                if is_phase_3:  # ✅ Sadece Aşama 3'te log
                    print(f"[UPDATE] ✅ target_color güncellendi: '{self.state.target_color}'")
                
            # 🔵 target_shape
            if 'target_shape' in target_data:
                self.state.target_shape = str(target_data['target_shape'])
                if is_phase_3:  # ✅ Sadece Aşama 3'te log
                    print(f"[UPDATE] ✅ target_shape güncellendi: '{self.state.target_shape}'")
            
            # 🟢 target_side
            if 'target_side' in target_data:
                target_side = str(target_data['target_side']).strip()
                old_platform = getattr(self.state, 'current_platform', 'UNDEFINED')
                self.state.current_platform = target_side
                
                if is_phase_3:  # ✅ Sadece Aşama 3'te log
                    print(f"[UPDATE] ✅ target_side güncellendi: '{old_platform}' → '{target_side}'")
                    print(f"[UPDATE] 📊 state.current_platform şimdi: '{self.state.current_platform}'")
            else:
                if is_phase_3:  # ✅ Sadece Aşama 3'te log
                    print(f"[UPDATE] ❌ target_side target_data'da yok!")
            
            if 'qr_code_detected' in target_data:
                self.state.qr_code_detected = bool(target_data['qr_code_detected'])
            if 'engagement_authorized' in target_data:
                self.state.engagement_authorized = bool(target_data['engagement_authorized'])

            self.state.last_update = datetime.now()

            # ========== STATE AFTER UPDATE - CONDITIONAL ==========
            if is_phase_3:  # ✅ Sadece Aşama 3'te log
                print(f"[UPDATE] 🎯 STATE AFTER UPDATE (AŞAMA 3):")
                print(f"   state.target_color: {getattr(self.state, 'target_color', 'UNDEFINED')}")
                print(f"   state.target_shape: {getattr(self.state, 'target_shape', 'UNDEFINED')}")
                print(f"   state.current_platform: {getattr(self.state, 'current_platform', 'UNDEFINED')}")

            # GUI'yi güncelle
            gui_state_dict = self.get_state_dict()
            
            # ========== STATE_DICT DEBUG - CONDITIONAL ==========
            if is_phase_3:  # ✅ Sadece Aşama 3'te log
                print(f"[UPDATE] 📤 GUI'YE GÖNDERİLEN STATE_DICT (AŞAMA 3):")
                print(f"   target_color: {gui_state_dict.get('target_color', 'UNDEFINED')}")
                print(f"   target_shape: {gui_state_dict.get('target_shape', 'UNDEFINED')}")
                print(f"   target_side: {gui_state_dict.get('target_side', 'UNDEFINED')}")
            
            self.trigger_event("data_updated", gui_state_dict)
            
        except Exception as e:
            print(f"[UPDATE] ❌ update_target_data hatası: {e}")
            import traceback
            traceback.print_exc()


    def get_current_frame_for_gui(self, width: int = None, height: int = None):
        """GUI için mevcut kamera frame'ini al"""
        return self.comm_manager.get_current_frame_for_gui(width, height)
    
    def save_current_frame(self, filename: str) -> bool:
        """Mevcut frame'i kaydet"""
        return self.comm_manager.save_current_frame(filename)

    def get_state_dict(self) -> Dict[str, Any]:
        """CONDITIONAL LOGGING: target_side kesinlikle dönecek"""
        uptime = datetime.now() - self.state.start_time if self.state.start_time else timedelta(0)
        
        success_rate = 0
        if self.state.targets_detected > 0:
            success_rate = (self.state.targets_destroyed / self.state.targets_detected) * 100
        
        # ========== CONDITIONAL DEBUG ==========
        current_platform = getattr(self.state, 'current_platform', 'A')  # Varsayılan A
        current_phase = self.state.mode.value
        is_phase_3 = (current_phase == 3)
        
        # ✅ Sadece Aşama 3'te debug göster
        if is_phase_3:
            print(f"[STATE_DICT] 📊 current_platform: '{current_platform}'")
        
        state_dict = {
            # Sistem durumu
            'mode': self.state.mode.value,
            'mode_name': self.state.mode.name,
            'active': self.state.active,
            'emergency_stop': self.state.emergency_stop,
            
            # Bağlantı durumu
            'raspberry_connected': self.state.raspberry_connected,
            'camera_connected': self.state.camera_connected,
            'controller_connected': self.state.controller_connected,
            
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
            
            # ========== AŞAMA 1 VERİLERİ ==========
            'targets_detected': self.state.targets_detected,
            'targets_destroyed': self.state.targets_destroyed,
            'balloon_count': self.state.balloon_count,
            
            # ========== AŞAMA 2 VERİLERİ ==========
            'friend_targets': self.state.friend_targets,
            'enemy_targets': self.state.enemy_targets,
            'enemy_destroyed': self.state.enemy_destroyed,
            'classification_accuracy': self.state.classification_accuracy,
            
            # ========== AŞAMA 3 VERİLERİ - CRITICAL FIX ==========
            'target_color': getattr(self.state, 'target_color', 'unknown'),
            'target_shape': getattr(self.state, 'target_shape', 'unknown'),
            'target_side': current_platform,  # ✅ KESIN OLARAK target_side
            'qr_code_detected': getattr(self.state, 'qr_code_detected', False),
            'engagement_authorized': getattr(self.state, 'engagement_authorized', False),
            
            # İstatistikler
            'success_rate': success_rate,
            'uptime': str(uptime).split('.')[0],
            
            # Sistem bilgileri
            'last_update': self.state.last_update.strftime("%H:%M:%S"),
            'commands_sent': self.stats['commands_sent'],
            'updates_received': self.stats['updates_received'],
            'frames_received': self.stats['frames_received'],
            'errors': self.stats['errors']
        }
        
        # ========== CONDITIONAL DEBUG FINAL ==========
        # ✅ Sadece Aşama 3'te debug göster
        if is_phase_3:
            print(f"[STATE_DICT] ✅ target_side state_dict'te: '{state_dict.get('target_side', 'UNDEFINED')}'")
        
        return state_dict



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