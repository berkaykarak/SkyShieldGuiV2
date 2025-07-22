# gui/communication/websocket_client.py - COMPLETE FIXED VERSION
import asyncio
import websockets
import json
import threading
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime

class WebSocketCommunicationClient:
    """
    Raspberry Pi WebSocket server ile iletişim - COMPLETE FIXED VERSION
    Threading ve connection timeout sorunları düzeltildi
    """
    
    def __init__(self, raspberry_ip: str = "localhost", ws_port: int = 9000):
        self.raspberry_ip = raspberry_ip
        self.ws_port = ws_port
        self.ws_url = f"ws://{raspberry_ip}:{ws_port}"
        
        # Bağlantı durumu
        self.connected = False
        self.websocket = None
        
        # Threading
        self.running = False
        self.ws_thread: Optional[threading.Thread] = None
        self.loop = None
        
        # Callback fonksiyonları
        self.data_callback: Optional[Callable] = None
        self.connection_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        
        # Son alınan veri ve istatistikler
        self.last_data = {}
        self.commands_sent = 0
        self.data_received = 0
        self.connection_attempts = 0
        
        print(f"[WS CLIENT] Oluşturuldu: {self.ws_url}")
    
    def start_connection(self) -> bool:
        """WebSocket bağlantısını başlat"""
        if self.running:
            print("[WS CLIENT] Zaten çalışıyor")
            return True
        
        print(f"[WS CLIENT] Bağlantı başlatılıyor: {self.ws_url}")
        
        self.running = True
        self.connection_attempts += 1
        
        # WebSocket thread'ini başlat
        self.ws_thread = threading.Thread(target=self._run_websocket_loop, daemon=True)
        self.ws_thread.start()
        
        # Bağlantı kurulana kadar bekle (max 3 saniye)
        for _ in range(30):
            if self.connected:
                return True
            time.sleep(0.1)
        
        return self.connected
    
    def stop_connection(self):
        """WebSocket bağlantısını durdur"""
        print("[WS CLIENT] Bağlantı durduruluyor...")
        self.running = False
        
        # WebSocket'i kapat
        if self.websocket and self.loop and not self.loop.is_closed():
            try:
                future = asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
                future.result(timeout=1)
            except:
                pass
        
        # Thread'i bekle
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=2)
        
        self.connected = False
        if self.connection_callback:
            # Thread-safe callback
            try:
                self.connection_callback(False)
            except:
                pass
        
        print("[WS CLIENT] Bağlantı durduruldu")
    
    def _run_websocket_loop(self):
        """WebSocket event loop'unu ayrı thread'de çalıştır - FIXED"""
        try:
            # Yeni event loop oluştur
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Handler'ı çalıştır
            self.loop.run_until_complete(self._websocket_handler())
            
        except Exception as e:
            print(f"[WS CLIENT] Loop hatası: {e}")
            if self.error_callback:
                try:
                    self.error_callback(f"WebSocket loop hatası: {e}")
                except:
                    pass
        finally:
            try:
                if self.loop and not self.loop.is_closed():
                    self.loop.close()
            except:
                pass
    
    async def _websocket_handler(self):
        """Ana WebSocket işleyicisi - FIXED"""
        reconnect_delay = 1
        max_delay = 30
        
        while self.running:
            try:
                print(f"[WS CLIENT] Bağlanmaya çalışıyor: {self.ws_url}")
                
                # FIXED: Timeout doğru kullanımı
                websocket = await asyncio.wait_for(
                    websockets.connect(
                        self.ws_url,
                        ping_interval=20,
                        ping_timeout=10,
                        close_timeout=5
                    ),
                    timeout=5.0
                )
                
                async with websocket:
                    self.websocket = websocket
                    self.connected = True
                    reconnect_delay = 1  # Reset delay
                    
                    print("[WS CLIENT] ✅ WebSocket bağlantısı kuruldu")
                    
                    # Thread-safe callback
                    if self.connection_callback:
                        try:
                            self.connection_callback(True)
                        except:
                            pass
                    
                    # Mesajları dinle
                    async for message in websocket:
                        try:
                            if not self.running:
                                break
                                
                            data = json.loads(message)
                            self.last_data = data
                            self.data_received += 1
                            
                            # Raspberry formatını GUI formatına çevir
                            gui_data = self._convert_raspberry_to_gui_format(data)
                            
                            # Thread-safe callback
                            if self.data_callback:
                                try:
                                    self.data_callback(gui_data)
                                except Exception as callback_error:
                                    print(f"[WS CLIENT] Callback hatası: {callback_error}")
                            
                        except json.JSONDecodeError as e:
                            print(f"[WS CLIENT] JSON parse hatası: {e}")
                        except Exception as e:
                            print(f"[WS CLIENT] Mesaj işleme hatası: {e}")
            
            except asyncio.TimeoutError:
                print(f"[WS CLIENT] ❌ Bağlantı timeout: {self.ws_url}")
                self.connected = False
                if self.connection_callback:
                    try:
                        self.connection_callback(False)
                    except:
                        pass
            
            except websockets.exceptions.ConnectionClosed:
                print("[WS CLIENT] 🔴 Bağlantı kapandı")
                self.connected = False
                if self.connection_callback:
                    try:
                        self.connection_callback(False)
                    except:
                        pass
            
            except websockets.exceptions.InvalidURI:
                print(f"[WS CLIENT] ❌ Geçersiz WebSocket URL: {self.ws_url}")
                self.connected = False
                break  # URL hatası için yeniden deneme yapma
            
            except Exception as e:
                print(f"[WS CLIENT] ❌ Bağlantı hatası: {e}")
                self.connected = False
                if self.connection_callback:
                    try:
                        self.connection_callback(False)
                    except:
                        pass
                if self.error_callback:
                    try:
                        self.error_callback(f"WebSocket hatası: {e}")
                    except:
                        pass
            
            # Yeniden bağlanmayı dene (exponential backoff)
            if self.running:
                print(f"[WS CLIENT] {reconnect_delay} saniye sonra yeniden bağlanılacak...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, max_delay)
    
    def send_command(self, data: Dict[str, Any]) -> bool:
        """WebSocket üzerinden komut gönder - FIXED"""
        if not self.connected or not self.websocket:
            print("[WS CLIENT] ⚠️ Bağlantı yok, komut gönderilemiyor")
            return False
        
        if not self.loop or self.loop.is_closed():
            print("[WS CLIENT] ⚠️ Event loop çalışmıyor")
            return False
        
        try:
            # Timestamp ve metadata ekle
            data_with_metadata = data.copy()
            data_with_metadata['timestamp'] = datetime.now().isoformat()
            data_with_metadata['source'] = 'gui'
            
            print(f"[WS CLIENT] 📤 Komut gönderiliyor: {data}")
            
            # FIXED: Thread-safe async işlem
            future = asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(data_with_metadata)), 
                self.loop
            )
            future.result(timeout=3)  # Max 3 saniye bekle
            
            self.commands_sent += 1
            print("[WS CLIENT] ✅ Komut gönderildi")
            return True
            
        except asyncio.TimeoutError:
            print("[WS CLIENT] ❌ Komut gönderme timeout")
            return False
        except Exception as e:
            print(f"[WS CLIENT] ❌ Komut gönderme hatası: {e}")
            if self.error_callback:
                try:
                    self.error_callback(f"Komut gönderme hatası: {e}")
                except:
                    pass
            return False
    
    def _convert_raspberry_to_gui_format(self, raspberry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raspberry Pi formatını GUI formatına çevir"""
        gui_data = {}
        
        try:
            # Sistem durumu
            if 'system_mode' in raspberry_data:
                mode = raspberry_data['system_mode']
                gui_data['mode'] = mode
                gui_data['mode_name'] = self._get_mode_name(mode)
                gui_data['active'] = mode != -1
                gui_data['system_active'] = mode != -1
            
            # Hedef bilgileri
            if 'target_detected_flag' in raspberry_data:
                gui_data['target_locked'] = raspberry_data['target_detected_flag']
            
            if 'x_target' in raspberry_data:
                gui_data['target_x'] = float(raspberry_data['x_target'])
            
            if 'y_target' in raspberry_data:
                gui_data['target_y'] = float(raspberry_data['y_target'])
            
            # Açı bilgileri
            if 'global_angle' in raspberry_data:
                gui_data['pan_angle'] = float(raspberry_data['global_angle'])
            
            if 'global_tilt_angle' in raspberry_data:
                gui_data['tilt_angle'] = float(raspberry_data['global_tilt_angle'])
            
            # Mühimmat dönüştürme
            if 'weapon' in raspberry_data:
                weapon_map = {
                    'L': 'Laser',
                    'A': 'Airgun', 
                    'E': 'None'
                }
                gui_data['weapon'] = weapon_map.get(raspberry_data['weapon'], 'Auto')
            
            # Durum bayrakları
            if 'scanning_target_flag' in raspberry_data:
                gui_data['scanning'] = raspberry_data['scanning_target_flag']
            
            if 'target_destroyed_flag' in raspberry_data:
                gui_data['target_destroyed'] = raspberry_data['target_destroyed_flag']
            
            # Hedef tarafı
            if 'target_side' in raspberry_data:
                gui_data['target_side'] = raspberry_data['target_side']
            
            # Hesaplanmış veriler
            gui_data['last_update'] = datetime.now().strftime("%H:%M:%S")
            
            # Dummy veriler (simülasyon için)
            gui_data['distance'] = 0.0
            gui_data['speed'] = 0.0
            gui_data['confidence'] = 95.0 if gui_data.get('target_locked') else 0.0
            
        except Exception as e:
            print(f"[WS CLIENT] Veri dönüştürme hatası: {e}")
        
        return gui_data
    
    def _get_mode_name(self, mode: int) -> str:
        """Mod numarasını isme çevir"""
        mode_names = {
            -1: "DURDUR",
            0: "MANUEL", 
            1: "AŞAMA 1",
            2: "AŞAMA 2",
            3: "AŞAMA 3"
        }
        return mode_names.get(mode, f"MOD {mode}")
    
    def ping_server(self) -> bool:
        """Server ping testi"""
        return self.connected
    
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
            'ws_port': self.ws_port,
            'ws_url': self.ws_url,
            'commands_sent': self.commands_sent,
            'data_received': self.data_received,
            'connection_attempts': self.connection_attempts,
            'last_data': self.last_data.copy()
        }
    
    def get_system_data(self) -> Optional[Dict[str, Any]]:
        """Son alınan sistem verisini döndür (HTTP client uyumluluğu için)"""
        return self.last_data if self.last_data else None

# Test fonksiyonu - FIXED
if __name__ == "__main__":
    import time
    
    def on_data_received(data):
        print(f"📥 Veri alındı: {data}")
    
    def on_connection_changed(connected):
        print(f"🔗 Bağlantı durumu: {'Bağlı' if connected else 'Kesildi'}")
    
    def on_error(error):
        print(f"❌ Hata: {error}")
    
    print("🧪 Fixed WebSocket Client Test")
    
    client = WebSocketCommunicationClient()
    client.register_data_callback(on_data_received)
    client.register_connection_callback(on_connection_changed)
    client.register_error_callback(on_error)
    
    if client.start_connection():
        print("✅ WebSocket bağlantısı başlatıldı")
        
        # Test komutları gönder
        test_commands = [
            {"system_mode": 1},
            {"calibration_flag": True},
            {"fire_gui_flag": True},
            {"engagement_started_flag": True}
        ]
        
        for cmd in test_commands:
            success = client.send_command(cmd)
            print(f"Komut: {cmd} → {'✅' if success else '❌'}")
            time.sleep(1)
        
        # 10 saniye dinle
        time.sleep(10)
    else:
        print("❌ WebSocket bağlantısı başarısız")
    
    client.stop_connection()
    print("Test tamamlandı!")