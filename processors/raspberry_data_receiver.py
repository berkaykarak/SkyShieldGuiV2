# processors/raspberry_data_receiver.py
import json
import logging
import numpy as np
from typing import Dict, Any, Optional

class RaspberryDataReceiver:
    """
    Raspberry Pi'dan gelen verileri alan ve GUI'ye ileten sınıf
    Görüntü işleme Raspberry Pi tarafında yapılıyor, 
    burada sadece alınan veriler GUI'ye aktarılıyor
    """
    
    def __init__(self, app_controller=None):
        """
        Veri alıcıyı başlat
        
        Args:
            app_controller: Verileri güncellemek için ana uygulama kontrolcüsü
        """
        self.app_controller = app_controller
        self.latest_json_data: Dict[str, Any] = {}
        self.latest_frame = None
        
        # İstatistikler
        self.packets_received = 0
        self.frames_received = 0
        
        logging.info("[RECEIVER] Raspberry Pi veri alıcısı başlatıldı")
    
    def receive_json_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Raspberry Pi'dan gelen JSON verisini al
        
        Args:
            data: Raspberry Pi'dan gelen JSON verisi
            
        Returns:
            İşlenmiş veri sözlüğü
        """
        try:
            self.latest_json_data = data
            self.packets_received += 1
            
            # Mod adını ekle (GUI için)
            if 'system_mode' in data:
                mode = data.get('system_mode', 0)
                mode_names = {0: "Manuel", 1: "Aşama 1", 2: "Aşama 2", 3: "Aşama 3"}
                data['mode_name'] = mode_names.get(mode, f"Mod {mode}")
            
            # App kontrolcüsünü güncelle
            if self.app_controller:
                self.app_controller.update_target_data(data)
            
            logging.debug(f"[RECEIVER] JSON verisi alındı: {data}")
            return data
            
        except Exception as e:
            logging.error(f"[RECEIVER] JSON alımı hatası: {e}")
            return data
    
    def receive_frame(self, frame) -> None:
        """
        Raspberry Pi'dan gelen video karesini al
        
        Args:
            frame: Raspberry Pi'dan gelen işlenmiş kamera karesi
        """
        try:
            self.latest_frame = frame
            self.frames_received += 1
            
            # Çok detaylı loglama gerektiğinde açılabilir
            #logging.debug(f"[RECEIVER] Kare alındı: {self.frames_received}")
            
        except Exception as e:
            logging.error(f"[RECEIVER] Kare alımı hatası: {e}")
    
    def get_latest_frame(self):
        """
        En son alınan kareyi döndür
        
        Returns:
            En son alınan kare veya None
        """
        return self.latest_frame
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        İstatistikleri döndür
        
        Returns:
            İstatistik verisi içeren sözlük
        """
        return {
            "packets_received": self.packets_received,
            "frames_received": self.frames_received,
            "latest_data_keys": list(self.latest_json_data.keys()) if self.latest_json_data else []
        }