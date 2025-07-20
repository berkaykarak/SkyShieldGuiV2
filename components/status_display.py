# gui/components/status_display.py
import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading
import time
from .base_component import BaseGUIComponent

class StatusDisplay(BaseGUIComponent):
    """
    Sağ taraftaki ana durum gösterge ekranı
    Hedef bilgileri, sistem durumu, loglar ve grafikler
    """
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, app_controller)
        
        # Log sistemi
        self.logs: List[str] = []
        self.max_logs = 100
        
        # Grafik verileri
        self.target_history = []
        self.performance_data = []
        
        # UI referansları
        self.status_label: Optional[ctk.CTkLabel] = None
        self.time_label: Optional[ctk.CTkLabel] = None
        self.log_text: Optional[ctk.CTkTextbox] = None
        self.target_labels: Dict[str, ctk.CTkLabel] = {}
        self.system_labels: Dict[str, ctk.CTkLabel] = {}
        self.progress_bars: Dict[str, ctk.CTkProgressBar] = {}
        
        # Animasyon ve güncellemeler
        self.animation_running = False
        self.last_update = datetime.now()
        
        self.setup_ui()
        self._start_time_update()
    
    def setup_ui(self) -> None:
        """Ana durum ekranı UI'ını oluştur"""
        # Ana frame
        self.frame = ctk.CTkFrame(self.parent, corner_radius=10)
        self.frame.grid(row=0, column=1, sticky="nsew", padx=(0,10), pady=10)
        
        # Üst durum çubuğu
        self._create_status_header()
        
        # Ana içerik alanı (scrollable)
        self._create_main_content()
        
        # Alt durum çubuğu
        self._create_bottom_status()
    
    def _create_status_header(self) -> None:
        """Üst durum çubuğunu oluştur"""
        header_frame = ctk.CTkFrame(self.frame, height=80)
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        # Sol taraf - Ana durum
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
        
        self.status_label = ctk.CTkLabel(
            left_frame,
            text="⚪ SİSTEM HAZIR",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=15, pady=10)
        
        # Durum animasyon noktası
        self.status_indicator = ctk.CTkFrame(left_frame, width=15, height=15, corner_radius=8)
        self.status_indicator.pack(side="left", padx=(0,15), pady=10)
        
        # Orta - Hızlı bilgiler
        center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        center_frame.pack(side="left", padx=20)
        
        # Hedef sayacı
        target_info_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        target_info_frame.pack()
        
        ctk.CTkLabel(
            target_info_frame,
            text="🎯",
            font=ctk.CTkFont(size=16)
        ).pack(side="left")
        
        self.target_counter = ctk.CTkLabel(
            target_info_frame,
            text="0/0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.target_counter.pack(side="left", padx=(5,0))
        
        # Sağ taraf - Zaman ve mod
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=15)
        
        self.time_label = ctk.CTkLabel(
            right_frame,
            text=datetime.now().strftime("%H:%M:%S"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.time_label.pack(pady=(10,5))
        
        self.mode_indicator = ctk.CTkLabel(
            right_frame,
            text="MANUEL",
            font=ctk.CTkFont(size=10),
            text_color=("#888888", "#888888")
        )
        self.mode_indicator.pack()
    
    def _create_main_content(self) -> None:
        """Ana içerik alanını oluştur"""
        # Scrollable frame
        main_scroll = ctk.CTkScrollableFrame(self.frame)
        main_scroll.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        # Hedef bilgileri bölümü
        self._create_target_section(main_scroll)
        
        # Sistem performans bölümü
        self._create_performance_section(main_scroll)
        
        # Detaylı sistem bilgileri
        self._create_detailed_info_section(main_scroll)
        
        # Log bölümü
        self._create_log_section(main_scroll)
    
    def _create_target_section(self, parent) -> None:
        """Hedef bilgileri bölümünü oluştur"""
        target_frame = ctk.CTkFrame(parent)
        target_frame.pack(fill="x", pady=(0,15))
        
        # Başlık
        title_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(15,10))
        
        ctk.CTkLabel(
            title_frame,
            text="🎯 HEDEF BİLGİLERİ",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Hedef durumu göstergesi
        self.target_status_frame = ctk.CTkFrame(title_frame, width=100, height=25)
        self.target_status_frame.pack(side="right")
        self.target_status_frame.pack_propagate(False)
        
        self.target_status_text = ctk.CTkLabel(
            self.target_status_frame,
            text="ARANIYOR",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("#ffffff", "#ffffff")
        )
        self.target_status_text.pack(expand=True)
        
        # Bilgi grid'i
        info_container = ctk.CTkFrame(target_frame, fg_color="transparent")
        info_container.pack(fill="x", padx=20, pady=(0,20))
        
        # Sol kolon
        left_col = ctk.CTkFrame(info_container)
        left_col.pack(side="left", fill="both", expand=True, padx=(0,10))
        
        # Sağ kolon
        right_col = ctk.CTkFrame(info_container)
        right_col.pack(side="right", fill="both", expand=True, padx=(10,0))
        
        # Sol kolon bilgileri
        left_info = [
            ("📍 Konum (X,Y):", "position", "-- , --"),
            ("📏 Mesafe:", "distance", "-- m"),
            ("⚡ Hız:", "speed", "-- m/s"),
            ("📐 Boyut:", "size", "-- cm")
        ]
        
        for label_text, key, default in left_info:
            info_row = ctk.CTkFrame(left_col, fg_color="transparent")
            info_row.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(
                info_row,
                text=label_text,
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).pack(side="left")
            
            value_label = ctk.CTkLabel(
                info_row,
                text=default,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="e"
            )
            value_label.pack(side="right")
            self.target_labels[key] = value_label
        
        # Sağ kolon bilgileri
        right_info = [
            ("🧭 Pan Açısı:", "pan_angle", "-- °"),
            ("📐 Tilt Açısı:", "tilt_angle", "-- °"),
            ("🎯 Mühimmat:", "weapon", "--"),
            ("🎯 Güven:", "confidence", "-- %")
        ]
        
        for label_text, key, default in right_info:
            info_row = ctk.CTkFrame(right_col, fg_color="transparent")
            info_row.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(
                info_row,
                text=label_text,
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).pack(side="left")
            
            value_label = ctk.CTkLabel(
                info_row,
                text=default,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="e"
            )
            value_label.pack(side="right")
            self.target_labels[key] = value_label
    
    def _create_performance_section(self, parent) -> None:
        """Sistem performans bölümünü oluştur"""
        perf_frame = ctk.CTkFrame(parent)
        perf_frame.pack(fill="x", pady=(0,15))
        
        # Başlık
        ctk.CTkLabel(
            perf_frame,
            text="📊 SİSTEM PERFORMANSI",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15,10))
        
        # Progress barlar
        progress_container = ctk.CTkFrame(perf_frame, fg_color="transparent")
        progress_container.pack(fill="x", padx=20, pady=(0,20))
        
        progress_items = [
            ("İşlemci Kullanımı", "cpu", "#3b82f6"),
            ("Bellek Kullanımı", "memory", "#10b981"),
            ("Hedef Doğruluğu", "accuracy", "#f59e0b"),
            ("Sistem Sağlığı", "health", "#ef4444")
        ]
        
        for i, (label, key, color) in enumerate(progress_items):
            if i % 2 == 0:
                row_frame = ctk.CTkFrame(progress_container, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)
            
            col_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            col_frame.pack(side="left" if i % 2 == 0 else "right", fill="x", expand=True, padx=10)
            
            ctk.CTkLabel(
                col_frame,
                text=label,
                font=ctk.CTkFont(size=11),
                anchor="w"
            ).pack(fill="x")
            
            progress_bar = ctk.CTkProgressBar(
                col_frame,
                height=15,
                progress_color=color
            )
            progress_bar.pack(fill="x", pady=(5,0))
            progress_bar.set(0)
            self.progress_bars[key] = progress_bar
    
    def _create_detailed_info_section(self, parent) -> None:
        """Detaylı sistem bilgileri bölümünü oluştur"""
        detail_frame = ctk.CTkFrame(parent)
        detail_frame.pack(fill="x", pady=(0,15))
        
        # Başlık
        ctk.CTkLabel(
            detail_frame,
            text="⚙️ DETAYLI BİLGİLER",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15,10))
        
        # Bilgi tablosu
        info_grid = ctk.CTkFrame(detail_frame, fg_color="transparent")
        info_grid.pack(fill="x", padx=20, pady=(0,20))
        
        # Grid içeriği
        detailed_info = [
            ("Tespit Edilen Hedefler:", "targets_detected", "0"),
            ("İmha Edilen Hedefler:", "targets_destroyed", "0"),
            ("Başarı Oranı:", "success_rate", "0%"),
            ("Çalışma Süresi:", "uptime", "00:00:00"),
            ("Son Güncelleme:", "last_update", "--"),
            ("Sistem Modu:", "system_mode", "Manuel")
        ]
        
        for i, (label_text, key, default) in enumerate(detailed_info):
            row = i // 2
            col = (i % 2) * 2
            
            if col == 0:  # Yeni satır başlangıcı
                row_container = ctk.CTkFrame(info_grid, fg_color="transparent")
                row_container.pack(fill="x", pady=2)
            
            # Label
            ctk.CTkLabel(
                row_container if col == 0 else row_container,
                text=label_text,
                font=ctk.CTkFont(size=11),
                anchor="w"
            ).pack(side="left", padx=(10 if col == 0 else 50, 5))
            
            # Value
            value_label = ctk.CTkLabel(
                row_container,
                text=default,
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            )
            value_label.pack(side="left", padx=(5, 20 if col == 2 else 0))
            self.system_labels[key] = value_label
    
    def _create_log_section(self, parent) -> None:
        """Log bölümünü oluştur"""
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(fill="both", expand=True)
        
        # Başlık ve kontroller
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=(15,10))
        
        ctk.CTkLabel(
            log_header,
            text="📋 SİSTEM LOGLARI",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Log kontrolleri
        log_controls = ctk.CTkFrame(log_header, fg_color="transparent")
        log_controls.pack(side="right")
        
        self.clear_logs_btn = ctk.CTkButton(
            log_controls,
            text="🗑️ Temizle",
            command=self._clear_logs,
            width=80,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        self.clear_logs_btn.pack(side="right", padx=(5,0))
        
        self.export_logs_btn = ctk.CTkButton(
            log_controls,
            text="💾 Dışa Aktar",
            command=self._export_logs,
            width=90,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        self.export_logs_btn.pack(side="right")
        
        # Log text alanı
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        # İlk log mesajı
        self.add_log("Sistem başlatıldı", "INFO")
    
    def _create_bottom_status(self) -> None:
        """Alt durum çubuğunu oluştur"""
        bottom_frame = ctk.CTkFrame(self.frame, height=40)
        bottom_frame.pack(fill="x", padx=20, pady=(0,20))
        bottom_frame.pack_propagate(False)
        
        # Sol - Bağlantı durumu
        self.connection_status = ctk.CTkLabel(
            bottom_frame,
            text="🔗 PUC Process: Bağlı",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.connection_status.pack(side="left", padx=15, pady=10)
        
        # Orta - Versiyon bilgisi
        version_label = ctk.CTkLabel(
            bottom_frame,
            text="Sky Shield v2.0",
            font=ctk.CTkFont(size=10),
            text_color=("#888888", "#888888")
        )
        version_label.pack(expand=True, pady=10)
        
        # Sağ - FPS göstergesi
        self.fps_label = ctk.CTkLabel(
            bottom_frame,
            text="FPS: --",
            font=ctk.CTkFont(size=11),
            anchor="e"
        )
        self.fps_label.pack(side="right", padx=15, pady=10)
    
    def _start_time_update(self) -> None:
        """Zaman güncelleme thread'ini başlat"""
        def update_time():
            while True:
                if self.time_label:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    self.time_label.configure(text=current_time)
                time.sleep(1)
        
        time_thread = threading.Thread(target=update_time, daemon=True)
        time_thread.start()
    
    def add_log(self, message: str, level: str = "INFO") -> None:
        """
        Log mesajı ekle
        Args:
            message: Log mesajı
            level: Log seviyesi (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Renk kodları
        colors = {
            "INFO": "#ffffff",
            "WARNING": "#fbbf24",
            "ERROR": "#ef4444",
            "SUCCESS": "#10b981",
            "DEBUG": "#8b5cf6"
        }
        
        # Emoji'ler
        emojis = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "DEBUG": "🔧"
        }
        
        emoji = emojis.get(level, "ℹ️")
        log_entry = f"[{timestamp}] {emoji} [{level}] {message}\n"
        
        # Log listesine ekle
        self.logs.append(log_entry)
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # UI'a ekle
        if self.log_text:
            self.log_text.insert("end", log_entry)
            self.log_text.see("end")
    
    def _clear_logs(self) -> None:
        """Logları temizle"""
        self.logs.clear()
        if self.log_text:
            self.log_text.delete("1.0", "end")
        self.add_log("Loglar temizlendi", "INFO")
    
    def _export_logs(self) -> None:
        """Logları dosyaya aktar"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sky_shield_logs_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("SKY SHIELD SYSTEM LOGS\n")
                f.write("=" * 50 + "\n")
                f.write(f"Export Time: {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                
                for log in self.logs:
                    f.write(log)
            
            self.add_log(f"Loglar dışa aktarıldı: {filename}", "SUCCESS")
            
        except Exception as e:
            self.add_log(f"Log dışa aktarma hatası: {e}", "ERROR")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """Durum ekranını güncelle"""
        try:
            # Ana durum güncelleme
            self._update_main_status(data)
            
            # Hedef bilgileri güncelleme
            self._update_target_info(data)
            
            # Sistem bilgileri güncelleme
            self._update_system_info(data)
            
            # Performans göstergelerini güncelle
            self._update_performance_indicators(data)
            
            # Son güncelleme zamanı
            self.last_update = datetime.now()
            
        except Exception as e:
            self.add_log(f"Veri güncelleme hatası: {e}", "ERROR")
    
    def _update_main_status(self, data: Dict[str, Any]) -> None:
        """Ana durum göstergesini güncelle"""
        if not self.status_label:
            return
        
        # Sistem durumu
        if data.get('emergency_stop'):
            self.status_label.configure(text="🔴 ACİL DURDURMA")
            self.status_indicator.configure(fg_color="red")
            self.target_status_frame.configure(fg_color="red")
            self.target_status_text.configure(text="DURDURULDU")
            
        elif data.get('target_locked'):
            self.status_label.configure(text="🟢 HEDEF KİLİTLİ")
            self.status_indicator.configure(fg_color="green")
            self.target_status_frame.configure(fg_color="green")
            self.target_status_text.configure(text="KİLİTLİ")
            
        elif data.get('active'):
            self.status_label.configure(text="🟡 HEDEF ARANIYOR")
            self.status_indicator.configure(fg_color="orange")
            self.target_status_frame.configure(fg_color="orange")
            self.target_status_text.configure(text="ARANIYOR")
            
        else:
            self.status_label.configure(text="⚪ SİSTEM HAZIR")
            self.status_indicator.configure(fg_color="gray")
            self.target_status_frame.configure(fg_color="gray")
            self.target_status_text.configure(text="BEKLEMEDE")
        
        # Mod göstergesi
        mode_names = {
            0: "MANUEL",
            1: "AŞAMA 1",
            2: "AŞAMA 2", 
            3: "AŞAMA 3"
        }
        mode = data.get('mode', 0)
        if self.mode_indicator:
            self.mode_indicator.configure(text=mode_names.get(mode, "BİLİNMEYEN"))
        
        # Hedef sayacı
        detected = data.get('targets_detected', 0)
        destroyed = data.get('targets_destroyed', 0)
        if self.target_counter:
            self.target_counter.configure(text=f"{destroyed}/{detected}")
    
    def _update_target_info(self, data: Dict[str, Any]) -> None:
        """Hedef bilgilerini güncelle"""
        # Pozisyon
        x = data.get('target_x', 0)
        y = data.get('target_y', 0)
        if 'position' in self.target_labels:
            self.target_labels['position'].configure(text=f"{x:.0f}, {y:.0f}")
        
        # Mesafe
        if 'distance' in data and 'distance' in self.target_labels:
            self.target_labels['distance'].configure(text=f"{data['distance']:.1f} m")
        
        # Hız
        if 'speed' in data and 'speed' in self.target_labels:
            self.target_labels['speed'].configure(text=f"{data['speed']:.1f} m/s")
        
        # Açılar
        if 'pan_angle' in data and 'pan_angle' in self.target_labels:
            self.target_labels['pan_angle'].configure(text=f"{data['pan_angle']:.1f}°")
        
        if 'tilt_angle' in data and 'tilt_angle' in self.target_labels:
            self.target_labels['tilt_angle'].configure(text=f"{data['tilt_angle']:.1f}°")
        
        # Mühimmat
        if 'weapon' in data and 'weapon' in self.target_labels:
            weapon_display = {
                'Laser': '🔴 Lazer',
                'Airgun': '🔵 Gazlı İtki',
                'Auto': '🤖 Otomatik',
                'None': '--'
            }
            weapon = data['weapon']
            self.target_labels['weapon'].configure(text=weapon_display.get(weapon, weapon))
        
        # Boyut (hesaplanabilirse)
        if 'target_size' in data and 'size' in self.target_labels:
            self.target_labels['size'].configure(text=f"{data['target_size']:.1f} cm")
        
        # Güven seviyesi
        if 'confidence' in data and 'confidence' in self.target_labels:
            self.target_labels['confidence'].configure(text=f"{data['confidence']:.1f}%")
    
    def _update_system_info(self, data: Dict[str, Any]) -> None:
        """Sistem bilgilerini güncelle"""
        # İstatistikler
        stats_mapping = [
            ('targets_detected', 'targets_detected'),
            ('targets_destroyed', 'targets_destroyed'),
            ('success_rate', 'success_rate'),
            ('uptime', 'uptime'),
            ('last_update', 'last_update')
        ]
        
        for data_key, label_key in stats_mapping:
            if data_key in data and label_key in self.system_labels:
                value = data[data_key]
                if data_key == 'success_rate':
                    self.system_labels[label_key].configure(text=f"{value}%")
                else:
                    self.system_labels[label_key].configure(text=str(value))
        
        # Sistem modu
        if 'mode_name' in data and 'system_mode' in self.system_labels:
            self.system_labels['system_mode'].configure(text=data['mode_name'])
    
    def _update_performance_indicators(self, data: Dict[str, Any]) -> None:
        """Performans göstergelerini güncelle"""
        # CPU kullanımı
        if 'cpu_usage' in data and 'cpu' in self.progress_bars:
            cpu_usage = min(data['cpu_usage'] / 100.0, 1.0)
            self.progress_bars['cpu'].set(cpu_usage)
        
        # Bellek kullanımı
        if 'memory_usage' in data and 'memory' in self.progress_bars:
            memory_usage = min(data['memory_usage'] / 100.0, 1.0)
            self.progress_bars['memory'].set(memory_usage)
        
        # Hedef doğruluğu
        detected = data.get('targets_detected', 0)
        destroyed = data.get('targets_destroyed', 0)
        if detected > 0 and 'accuracy' in self.progress_bars:
            accuracy = destroyed / detected
            self.progress_bars['accuracy'].set(accuracy)
        
        # Sistem sağlığı (örnek hesaplama)
        if 'system_health' in data and 'health' in self.progress_bars:
            health = min(data['system_health'] / 100.0, 1.0)
            self.progress_bars['health'].set(health)
        elif 'cpu_usage' in data and 'memory_usage' in data:
            # Basit sağlık hesaplaması
            cpu = data['cpu_usage']
            memory = data['memory_usage']
            health = 1.0 - ((cpu + memory) / 200.0)
            health = max(0.0, min(1.0, health))
            if 'health' in self.progress_bars:
                self.progress_bars['health'].set(health)
        
        # FPS güncelleme
        if 'fps' in data and self.fps_label:
            self.fps_label.configure(text=f"FPS: {data['fps']:.1f}")
    
    def update_connection_status(self, connected: bool) -> None:
        """
    Bağlantı durumunu güncelle
    
    Args:
        status_dict: RaspberryConnectionManager'dan bağlantı durumu sözlüğü
    """
        if self.connection_status:
            if connected:
                self.connection_status.configure(
                    text="🔗 PUC Process: Bağlı",
                    text_color=("green", "green")
                )
            else:
                self.connection_status.configure(
                    text="🔗 PUC Process: Bağlantı Yok",
                    text_color=("red", "red")
        
                )
    def update_raspberry_connection(self, status_dict: Dict[str, bool]) -> None:
        """
        Raspberry Pi bağlantı durumunu güncelle
        
        Args:
            status_dict: RaspberryConnectionManager'dan bağlantı durumu sözlüğü
        """
        if self.connection_status:
            websocket = status_dict.get("websocket_connected", False)
            stream = status_dict.get("stream_connected", False)
            
            if websocket and stream:
                self.connection_status.configure(
                    text="🔗 Raspberry Pi: Tam Bağlantı",
                    text_color=("green", "green")
                )
            elif websocket:
                self.connection_status.configure(
                    text="🔗 Raspberry Pi: Sadece Veri",
                    text_color=("#ffa500", "#ffa500")  # Turuncu
                )
            elif stream:
                self.connection_status.configure(
                    text="🔗 Raspberry Pi: Sadece Video",
                    text_color=("#ffa500", "#ffa500")  # Turuncu
                )
            else:
                self.connection_status.configure(
                    text="🔗 Raspberry Pi: Bağlantı Yok",
                    text_color=("red", "red")
                )             
    
    def get_data(self) -> Dict[str, Any]:
        """Durum ekranı verilerini döndür"""
        return {
            'logs_count': len(self.logs),
            'last_update': self.last_update.isoformat(),
            'target_history': self.target_history[-10:],  # Son 10 hedef
            'performance_data': self.performance_data[-50:]  # Son 50 veri noktası
        }
    
    def reset(self) -> None:
        """Durum ekranını sıfırla"""
        # Logları temizle
        self._clear_logs()
        
        # Tüm label'ları sıfırla
        for label in self.target_labels.values():
            label.configure(text="--")
        
        for label in self.system_labels.values():
            label.configure(text="0" if "count" in str(label) else "--")
        
        # Progress bar'ları sıfırla
        for progress in self.progress_bars.values():
            progress.set(0)
        
        # Ana durumu sıfırla
        if self.status_label:
            self.status_label.configure(text="⚪ SİSTEM HAZIR")
        
        if self.status_indicator:
            self.status_indicator.configure(fg_color="gray")
        
        if self.target_counter:
            self.target_counter.configure(text="0/0")
        
        # Veri listelerini temizle
        self.target_history.clear()
        self.performance_data.clear()
        
        self.add_log("Durum ekranı sıfırlandı", "INFO")