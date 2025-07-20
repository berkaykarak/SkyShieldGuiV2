# processors/raspberry_connection_manager.py
import asyncio
import websockets
import json
import threading
import logging
import time
import queue
from typing import Dict, Any, Optional, Callable

class RaspberryConnectionManager:
    """
    Raspberry Pi ile bağlantıları yöneten sınıf
    WebSocket ve video akışı bağlantılarını kurar ve yönetir
    """
    
    def __init__(self, app_controller, 
                 websocket_host="localhost", websocket_port=9000,
                 stream_host="localhost", stream_port=9001):
        """
        Bağlantı yöneticisini başlat
        
        Args:
            app_controller: Ana uygulama kontrolcüsü
            websocket_host: WebSocket sunucu adresi
            websocket_port: WebSocket sunucu portu
            stream_host: Video akışı sunucu adresi
            stream_port: Video akışı sunucu portu
        """
        self.app_controller = app_controller
        self.websocket_host = websocket_host
        self.websocket_port = websocket_port
        self.stream_host = stream_host
        self.stream_port = stream_port
        
        # Bağlantı durumu
        self.websocket_connected = False
        self.stream_connected = False
        
        # Veri alıcısını oluştur
        from .raspberry_data_receiver import RaspberryDataReceiver
        self.data_receiver = RaspberryDataReceiver(app_controller)
        
        # Frame kuyruğu
        self.frame_queue = queue.Queue(maxsize=5)
        
        # Bağlantı thread'leri
        self.websocket_thread = None
        self.stream_thread = None
        
        # Kontrol bayrakları
        self.running = False
        
        logging.info("[CONNECTION] Raspberry Pi bağlantı yöneticisi başlatıldı")
    
    def start(self) -> None:
        """Tüm bağlantıları ve işleme thread'lerini başlat"""
        if self.running:
            logging.warning("[CONNECTION] Zaten çalışıyor")
            return
            
        self.running = True
        
        # WebSocket bağlantısını ayrı bir thread'de başlat
        self.websocket_thread = threading.Thread(
            target=self._run_websocket_client,
            daemon=True
        )
        self.websocket_thread.start()
        
        # Video akışı bağlantısını ayrı bir thread'de başlat
        self.stream_thread = threading.Thread(
            target=self._run_stream_client,
            daemon=True
        )
        self.stream_thread.start()
        
        logging.info("[CONNECTION] Tüm bağlantı thread'leri başlatıldı")
    
    def stop(self) -> None:
        """Tüm bağlantıları ve işlemeyi durdur"""
        self.running = False
        
        # Thread'lerin bitmesini bekle
        if self.websocket_thread:
            self.websocket_thread.join(timeout=1.0)
        
        if self.stream_thread:
            self.stream_thread.join(timeout=1.0)
        
        logging.info("[CONNECTION] Tüm bağlantı thread'leri durduruldu")
    
    def _run_websocket_client(self) -> None:
        """WebSocket istemci ana döngüsü"""
        ws_uri = f"ws://{self.websocket_host}:{self.websocket_port}"
        reconnect_delay = 1.0  # İlk yeniden bağlanma gecikmesi (saniye)
        max_reconnect_delay = 30.0  # Maksimum yeniden bağlanma gecikmesi
        
        logging.info(f"[CONNECTION] WebSocket istemcisi başlatılıyor: {ws_uri}")
        
        while self.running:
            try:
                # Thread için yeni event loop oluştur
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # WebSocket istemcisini çalıştır
                loop.run_until_complete(self._websocket_client(ws_uri))
                
                # Buraya gelinirse, bağlantı kapanmış demektir
                if self.running:
                    logging.warning(f"[CONNECTION] WebSocket bağlantısı kapandı, {reconnect_delay}s sonra yeniden bağlanılacak...")
                    time.sleep(reconnect_delay)
                    
                    # Üstel artış ile yeniden bağlanma
                    reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
                
            except Exception as e:
                logging.error(f"[CONNECTION] WebSocket istemci hatası: {e}")
                
                if self.running:
                    logging.warning(f"[CONNECTION] WebSocket {reconnect_delay}s sonra yeniden bağlanılacak...")
                    time.sleep(reconnect_delay)
                    
                    # Üstel artış ile yeniden bağlanma
                    reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
        
        logging.info("[CONNECTION] WebSocket istemci thread'i durduruldu")
    
    async def _websocket_client(self, uri: str) -> None:
        """
        WebSocket istemci korutini
        
        Args:
            uri: Bağlanılacak WebSocket URI'si
        """
        try:
            async with websockets.connect(uri) as websocket:
                logging.info(f"[CONNECTION] WebSocket bağlandı: {uri}")
                self.websocket_connected = True
                
                # Başarılı bağlantıda yeniden bağlanma gecikmesini sıfırla
                reconnect_delay = 1.0
                
                # İlk sistem durumunu gönder
                await self._send_system_state(websocket)
                
                # Alma döngüsü
                while self.running:
                    try:
                        # Self.running'i periyodik olarak kontrol etmek için zamanaşımı belirle
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        
                        # Mesajı işle
                        data = json.loads(message)
                        logging.debug(f"[CONNECTION] WebSocket verisi alındı: {data}")
                        
                        # Veriyi işle
                        self.data_receiver.receive_json_data(data)
                        
                    except asyncio.TimeoutError:
                        # Mesaj alınmadığında beklenen durum
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        logging.warning("[CONNECTION] WebSocket bağlantısı kapandı")
                        self.websocket_connected = False
                        break
                    except json.JSONDecodeError as e:
                        logging.error(f"[CONNECTION] JSON ayrıştırma hatası: {e}, mesaj: {message}")
                    except Exception as e:
                        logging.error(f"[CONNECTION] WebSocket alım hatası: {e}")
                
        except Exception as e:
            logging.error(f"[CONNECTION] WebSocket bağlantı hatası: {e}")
            self.websocket_connected = False
    
    async def _send_system_state(self, websocket) -> None:
        """
        Mevcut sistem durumunu WebSocket sunucusuna gönder
        
        Args:
            websocket: WebSocket bağlantısı
        """
        try:
            # App kontrolcüsünden mevcut sistem durumunu al
            if self.app_controller:
                state_dict = self.app_controller.get_state_dict()
                
                # Raspberry Pi'nin beklediği formata dönüştür
                state_to_send = {
                    "system_mode": state_dict.get('mode', 0),
                    "fire_gui_flag": False,
                    "engagement_started_flag": state_dict.get('active', False),
                    "calibration_flag": False
                }
                
                # Durumu gönder
                await websocket.send(json.dumps(state_to_send))
                logging.debug(f"[CONNECTION] İlk durum gönderildi: {state_to_send}")
                
        except Exception as e:
            logging.error(f"[CONNECTION] Sistem durumu gönderme hatası: {e}")
    
    def _run_stream_client(self) -> None:
        """Video akışı istemcisi ana döngüsü"""
        import cv2
        stream_url = f"http://{self.stream_host}:{self.stream_port}"
        reconnect_delay = 1.0  # İlk yeniden bağlanma gecikmesi (saniye)
        max_reconnect_delay = 30.0  # Maksimum yeniden bağlanma gecikmesi
        
        logging.info(f"[CONNECTION] Video akışı istemcisi başlatılıyor: {stream_url}")
        
        while self.running:
            try:
                # OpenCV ile video akışına bağlan
                cap = cv2.VideoCapture(stream_url)
                
                if not cap.isOpened():
                    logging.error(f"[CONNECTION] Video akışı açılamadı: {stream_url}")
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
                    continue
                
                logging.info(f"[CONNECTION] Video akışına bağlandı: {stream_url}")
                self.stream_connected = True
                
                # Başarılı bağlantıda yeniden bağlanma gecikmesini sıfırla
                reconnect_delay = 1.0
                
                # Kareleri oku
                while self.running:
                    ret, frame = cap.read()
                    
                    if not ret:
                        logging.warning("[CONNECTION] Video akışından kare okunamadı")
                        break
                    
                    # Kareyi veri alıcıya gönder
                    self.data_receiver.receive_frame(frame)
                    
                    # GUI için kareyi sakla (istendiğinde verilecek)
                    try:
                        # Kuyruk doluysa, son öğeyi çıkar ve yenisini ekle
                        if self.frame_queue.full():
                            try:
                                self.frame_queue.get_nowait()
                            except queue.Empty:
                                pass
                        # Yeni kareyi kuyruğa ekle
                        self.frame_queue.put(frame, block=False)
                    except queue.Full:
                        # Kuyruk doluysa, kareyi atla
                        pass
                
                # Video yakalama nesnesini kapat
                cap.release()
                self.stream_connected = False
                
                if self.running:
                    logging.warning(f"[CONNECTION] Video akışı kesildi, {reconnect_delay}s sonra yeniden bağlanılacak...")
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
                
            except Exception as e:
                logging.error(f"[CONNECTION] Video akışı istemci hatası: {e}")
                self.stream_connected = False
                
                if self.running:
                    logging.warning(f"[CONNECTION] Video akışına {reconnect_delay}s sonra yeniden bağlanılacak...")
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
        
        logging.info("[CONNECTION] Video akışı istemci thread'i durduruldu")
    
    def get_latest_frame(self):
        """
        En son işlenmiş kareyi al
        
        Returns:
            En son kare veya None
        """
        try:
            # Kuyruğun en son öğesini al (beklemeden)
            return self.data_receiver.get_latest_frame()
        except:
            # Kare yoksa None döndür
            return None
    
    def get_connection_status(self) -> Dict[str, bool]:
        """
        Bağlantı durumunu al
        
        Returns:
            Bağlantı durumu içeren sözlük
        """
        return {
            "websocket_connected": self.websocket_connected,
            "stream_connected": self.stream_connected,
            "all_connected": self.websocket_connected and self.stream_connected
        }
    
    def send_command(self, command: Dict[str, Any]) -> None:
        """
        Raspberry Pi WebSocket sunucusuna komut gönder
        
        Args:
            command: Gönderilecek komut verisi
        """
        if not self.websocket_connected:
            logging.warning("[CONNECTION] Komut gönderilemiyor: WebSocket bağlı değil")
            return
        
        # Geçici bir event loop oluştur ve gönderme korutinini çalıştır
        async def send_async():
            try:
                # WebSocket bağlantısı oluştur
                uri = f"ws://{self.websocket_host}:{self.websocket_port}"
                async with websockets.connect(uri) as websocket:
                    # Komutu gönder
                    await websocket.send(json.dumps(command))
                    logging.debug(f"[CONNECTION] Komut gönderildi: {command}")
                    
                    # Yanıt bekle
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        logging.debug(f"[CONNECTION] Komut yanıtı: {response}")
                        return json.loads(response)
                    except asyncio.TimeoutError:
                        logging.warning("[CONNECTION] Komut yanıtı zaman aşımı")
                        return {"status": "timeout"}
                    
            except Exception as e:
                logging.error(f"[CONNECTION] Komut gönderme hatası: {e}")
                return {"status": "error", "message": str(e)}
        
        # Ayrı bir thread'de çalıştır
        threading.Thread(
            target=lambda: asyncio.run(send_async()),
            daemon=True
        ).start()