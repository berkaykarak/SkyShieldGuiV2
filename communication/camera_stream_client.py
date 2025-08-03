# gui/communication/camera_stream_client.py - FIXED VERSION
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
    Raspberry Pi'den kamera stream'ini alan client - FIXED VERSION
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
        """Ana stream döngüsü - FIXED VERSION"""
        try:
            response = requests.get(self.stream_url, stream=True, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            print("[CAMERA STREAM] MJPEG stream bağlantısı kuruldu")
            
            # Buffer ve değişkenler
            buffer = b""
            boundary = None
            
            for chunk in response.iter_content(chunk_size=4096):  # Daha büyük chunk
                if not self.streaming:
                    break
                
                buffer += chunk
                
                # Boundary'yi bul (ilk kez)
                if boundary is None:
                    # Boundary genelde --frame şeklinde
                    boundary_idx = buffer.find(b'--frame')
                    if boundary_idx != -1:
                        boundary = b'--frame'
                        print(f"[CAMERA STREAM] Boundary bulundu: {boundary}")
                
                # Frame'leri ayıkla
                while boundary and len(buffer) > 1024:
                    # Yeni frame başlangıcını bul
                    start_idx = buffer.find(boundary)
                    if start_idx == -1:
                        break
                    
                    # Bir sonraki boundary'yi bul
                    next_idx = buffer.find(boundary, start_idx + len(boundary))
                    
                    if next_idx == -1:
                        # Henüz tam frame yok, daha fazla veri bekle
                        break
                    
                    # Tam frame'i çıkar
                    frame_data = buffer[start_idx:next_idx]
                    
                    # JPEG verilerini ayıkla
                    jpeg_start = frame_data.find(b'\xff\xd8')
                    jpeg_end = frame_data.find(b'\xff\xd9')
                    
                    if jpeg_start != -1 and jpeg_end != -1 and jpeg_end > jpeg_start:
                        jpeg_data = frame_data[jpeg_start:jpeg_end + 2]
                        
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
                            
                            # Debug log - her 30 frame'de bir
                            if self.frame_count % 30 == 0:
                                print(f"[CAMERA STREAM] Frame {self.frame_count} alındı")
                    
                    # İşlenen kısmı buffer'dan çıkar
                    buffer = buffer[next_idx:]
                
                # Buffer'ı sınırla (memory leak önleme)
                if len(buffer) > 1024 * 1024:  # 1MB'dan büyükse
                    buffer = buffer[-1024*512:]  # Son 512KB'ı tut
        
        except requests.exceptions.Timeout:
            print("[CAMERA STREAM] ❌ Stream timeout")
        except requests.exceptions.ConnectionError:
            print("[CAMERA STREAM] ❌ Bağlantı hatası")
        except Exception as e:
            print(f"[CAMERA STREAM] ❌ Stream loop hatası: {e}")
        finally:
            self.connected = False
            if self.error_callback:
                self.error_callback("Stream bağlantısı kesildi")
            if self.connection_callback:
                self.connection_callback(False)
    
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
            self.fps_counter = self.frame_count - getattr(self, 'last_frame_count', 0)
            self.last_frame_count = self.frame_count
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
    from matplotlib.animation import FuncAnimation
    
    fig, ax = plt.subplots()
    im = None
    
    def on_frame_received(frame):
        global im
        print(f"📷 Frame alındı: {frame.shape}")
        
        # İlk frame
        if im is None:
            im = ax.imshow(frame)
            ax.axis('off')
            plt.show(block=False)
        else:
            # Frame'i güncelle
            im.set_data(frame)
            plt.draw()
            plt.pause(0.001)
    
    def on_connection_changed(connected):
        print(f"🔗 Stream bağlantısı: {'Aktif' if connected else 'Kesildi'}")
    
    def on_fps_update(fps):
        print(f"📊 FPS: {fps}")
    
    def on_error(error):
        print(f"❌ Hata: {error}")
    
    print("🧪 Camera Stream Client Test")
    print("Stream URL'yi değiştirmeyi unutmayın!")
    
    # Test için localhost kullan
    client = CameraStreamClient(raspberry_ip="localhost", stream_port=9001)
    
    client.register_frame_callback(on_frame_received)
    client.register_connection_callback(on_connection_changed)
    client.register_fps_callback(on_fps_update)
    client.register_error_callback(on_error)
    
    if client.start_stream():
        print("✅ Stream başlatıldı")
        print("Ctrl+C ile durdurun...")
        
        try:
            while True:
                time.sleep(0.1)
                
                # Stream durumunu kontrol et
                if not client.connected:
                    print("Stream bağlantısı kesildi, yeniden bağlanıyor...")
                    client.stop_stream()
                    time.sleep(2)
                    client.start_stream()
                    
        except KeyboardInterrupt:
            print("\n🛑 Durduruldu")
    else:
        print("❌ Stream başlatılamadı")
    
    client.stop_stream()
    print("Test tamamlandı!")