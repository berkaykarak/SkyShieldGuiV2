# gui/communication/camera_stream_client.py
import requests
import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable
from PIL import Image, ImageTk
import io

class CameraStreamClient:
    """
    Raspberry Pi'den kamera stream'ini alan client
    MJPEG formatında görüntü akışını işler
    """
    
    def __init__(self, raspberry_ip: str = "localhost", stream_port: int = 9001):
        self.raspberry_ip = raspberry_ip
        self.stream_port = stream_port
        self.stream_url = f"http://{raspberry_ip}:{stream_port}"
        
        # Stream durumu
        self.streaming = False
        self.connected = False
        
        # Threading
        self.stream_thread: Optional[threading.Thread] = None
        
        # Callback fonksiyonları
        self.frame_callback: Optional[Callable] = None
        self.connection_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        
        # Son frame
        self.last_frame = None
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        print(f"[CAMERA STREAM] Client oluşturuldu: {self.stream_url}")
    
    def start_stream(self) -> bool:
        """Kamera stream'ini başlat"""
        if self.streaming:
            print("[CAMERA STREAM] Stream zaten aktif")
            return True
        
        print("[CAMERA STREAM] Stream başlatılıyor...")
        
        try:
            # İlk bağlantı testi
            response = requests.get(self.stream_url, timeout=5, stream=True)
            if response.status_code == 200:
                self.streaming = True
                self.connected = True
                
                # Stream thread'ini başlat
                self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
                self.stream_thread.start()
                
                print("[CAMERA STREAM] ✅ Stream başlatıldı")
                if self.connection_callback:
                    self.connection_callback(True)
                return True
            else:
                print(f"[CAMERA STREAM] ❌ Stream başlatılamadı: {response.status_code}")
                if self.connection_callback:
                    self.connection_callback(False)
                return False
                
        except Exception as e:
            print(f"[CAMERA STREAM] ❌ Stream başlatma hatası: {e}")
            if self.error_callback:
                self.error_callback(f"Stream başlatma hatası: {e}")
            if self.connection_callback:
                self.connection_callback(False)
            return False
    
    def stop_stream(self):
        """Kamera stream'ini durdur"""
        print("[CAMERA STREAM] Stream durduruluyor...")
        self.streaming = False
        self.connected = False
        
        # Thread'i bekle
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=3)
        
        if self.connection_callback:
            self.connection_callback(False)
        
        print("[CAMERA STREAM] Stream durduruldu")
    
    def _stream_loop(self):
        """Ana stream döngüsü"""
        try:
            response = requests.get(self.stream_url, stream=True, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            print("[CAMERA STREAM] MJPEG stream bağlantısı kuruldu")
            
            # MJPEG boundary parser
            boundary = None
            buffer = b""
            
            for chunk in response.iter_content(chunk_size=1024):
                if not self.streaming:
                    break
                
                buffer += chunk
                
                # Boundary bul
                if boundary is None:
                    boundary_pos = buffer.find(b'--')
                    if boundary_pos != -1:
                        boundary_end = buffer.find(b'\r\n', boundary_pos)
                        if boundary_end != -1:
                            boundary = buffer[boundary_pos:boundary_end]
                            print(f"[CAMERA STREAM] Boundary bulundu: {boundary}")
                
                # Frame'leri ayıkla
                if boundary:
                    self._parse_mjpeg_frames(buffer, boundary)
                    buffer = buffer[-1024:]  # Buffer'ı temiz tut
        
        except Exception as e:
            print(f"[CAMERA STREAM] ❌ Stream loop hatası: {e}")
            self.connected = False
            if self.error_callback:
                self.error_callback(f"Stream hatası: {e}")
            if self.connection_callback:
                self.connection_callback(False)
    
    def _parse_mjpeg_frames(self, buffer: bytes, boundary: bytes):
        """MJPEG frame'lerini parse et"""
        try:
            # Frame başlangıcını bul
            frame_start = buffer.find(b'\xff\xd8')  # JPEG start marker
            frame_end = buffer.find(b'\xff\xd9')    # JPEG end marker
            
            if frame_start != -1 and frame_end != -1 and frame_end > frame_start:
                # JPEG frame'i çıkar
                jpeg_data = buffer[frame_start:frame_end + 2]
                
                # Frame'i decode et
                frame = self._decode_jpeg_frame(jpeg_data)
                if frame is not None:
                    self.last_frame = frame
                    self.frame_count += 1
                    
                    # FPS hesapla
                    self._calculate_fps()
                    
                    # Callback'i tetikle
                    if self.frame_callback:
                        self.frame_callback(frame)
        
        except Exception as e:
            print(f"[CAMERA STREAM] Frame parsing hatası: {e}")
    
    def _decode_jpeg_frame(self, jpeg_data: bytes) -> Optional[np.ndarray]:
        """JPEG verisini OpenCV frame'ine çevir"""
        try:
            # Numpy array'e çevir
            nparr = np.frombuffer(jpeg_data, np.uint8)
            
            # OpenCV ile decode et
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # BGR'den RGB'ye çevir (GUI için)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame_rgb
            
            return None
            
        except Exception as e:
            print(f"[CAMERA STREAM] JPEG decode hatası: {e}")
            return None
    
    def _calculate_fps(self):
        """FPS hesapla"""
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:  # Her saniye
            self.fps_counter = self.frame_count - (self.fps_counter if hasattr(self, 'last_frame_count') else 0)
            self.last_fps_time = current_time
            if hasattr(self, 'fps_callback') and self.fps_callback:
                self.fps_callback(self.fps_counter)
    
    def get_current_frame_as_pil(self) -> Optional[Image.Image]:
        """Mevcut frame'i PIL Image olarak döndür"""
        if self.last_frame is not None:
            try:
                return Image.fromarray(self.last_frame)
            except Exception as e:
                print(f"[CAMERA STREAM] PIL dönüştürme hatası: {e}")
        return None
    
    def get_current_frame_as_tkinter(self, width: int = None, height: int = None) -> Optional[ImageTk.PhotoImage]:
        """Mevcut frame'i Tkinter PhotoImage olarak döndür"""
        pil_image = self.get_current_frame_as_pil()
        if pil_image:
            try:
                # Boyutlandır
                if width and height:
                    pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
                
                return ImageTk.PhotoImage(pil_image)
            except Exception as e:
                print(f"[CAMERA STREAM] Tkinter dönüştürme hatası: {e}")
        return None
    
    def save_current_frame(self, filename: str) -> bool:
        """Mevcut frame'i dosyaya kaydet"""
        pil_image = self.get_current_frame_as_pil()
        if pil_image:
            try:
                pil_image.save(filename)
                print(f"[CAMERA STREAM] Frame kaydedildi: {filename}")
                return True
            except Exception as e:
                print(f"[CAMERA STREAM] Frame kaydetme hatası: {e}")
        return False
    
    def register_frame_callback(self, callback: Callable[[np.ndarray], None]):
        """Frame callback'i kaydet"""
        self.frame_callback = callback
    
    def register_connection_callback(self, callback: Callable[[bool], None]):
        """Bağlantı durumu callback'i kaydet"""
        self.connection_callback = callback
    
    def register_error_callback(self, callback: Callable[[str], None]):
        """Hata callback'i kaydet"""
        self.error_callback = callback
    
    def register_fps_callback(self, callback: Callable[[int], None]):
        """FPS callback'i kaydet"""
        self.fps_callback = callback
    
    def get_stream_info(self) -> dict:
        """Stream bilgilerini döndür"""
        return {
            'streaming': self.streaming,
            'connected': self.connected,
            'stream_url': self.stream_url,
            'frame_count': self.frame_count,
            'fps': getattr(self, 'fps_counter', 0),
            'last_frame_shape': self.last_frame.shape if self.last_frame is not None else None
        }

# Test fonksiyonu
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    def on_frame_received(frame):
        print(f"📷 Frame alındı: {frame.shape}")
        # İlk frame'i göster
        if not hasattr(on_frame_received, 'shown'):
            plt.imshow(frame)
            plt.title("İlk Frame")
            plt.axis('off')
            plt.show()
            on_frame_received.shown = True
    
    def on_connection_changed(connected):
        print(f"🔗 Stream bağlantısı: {'Aktif' if connected else 'Kesildi'}")
    
    def on_fps_update(fps):
        print(f"📊 FPS: {fps}")
    
    print("🧪 Camera Stream Client Test")
    
    client = CameraStreamClient()
    client.register_frame_callback(on_frame_received)
    client.register_connection_callback(on_connection_changed)
    client.register_fps_callback(on_fps_update)
    
    if client.start_stream():
        print("Stream başlatıldı, 10 saniye test...")
        time.sleep(10)
        
        # Frame kaydet
        if client.save_current_frame("test_frame.jpg"):
            print("Test frame kaydedildi")
    
    client.stop_stream()
    print("Test tamamlandı!")