import customtkinter as ctk
import tkinter as tk
import threading  # YENİ: Threading fix için
import time

from controllers.app_controller import AppController 
import numpy as np  

from PIL import Image, ImageTk
from datetime import datetime
from PIL import Image, ImageTk
import os                   

# CustomTkinter ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PhaseSelectionWindow:
    """Başlangıç aşama seçim penceresi"""
    def __init__(self):
        self.selected_phase = None
        self.root = ctk.CTk()
        self.root.title("Sky Shield - Aşama Seçimi")
        self.root.geometry("1400x900")
        self.root.resizable(False, False)
        
        # Pencereyi merkeze al - GÜNCELLENMIŞ YÖNTEMİ
        self.center_window()
        
        self.setup_phase_selection()

    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        # Pencere boyutları
        window_width = 1400
        window_height = 900
        
        # Ekran boyutlarını al
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Orta pozisyonu hesapla
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # Pencereyi ortala
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        print(f"[WINDOW] Pencere ortalandı: {center_x}x{center_y}")
    
        
    def setup_phase_selection(self):
        
        # Ana çerçeve
        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık bölümü
        self._create_header(main_frame)
        
        # Aşama kartları
        self._create_phase_cards(main_frame)
        
        # Alt bilgi
        self._create_footer(main_frame)
    
    def _create_header(self, parent):
        """Başlık bölümünü (kompakt logo + başlık) oluştur"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(15, 15))  # Daha az padding
        header_frame.pack_propagate(True)

        # ──────────── ORTA BOY SkyShield Logosu ────────────
        logo_paths = [
            os.path.join("assets", "skyshield_logo.png"),
            os.path.join("assets", "skyshield_logo.jpg"),
            "skyshield_logo.png", 
            "skyshield_logo.jpg"
        ]
        
        logo_loaded = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    img = Image.open(logo_path).resize((280, 280))   # Daha büyük logo
                    self.header_big_logo = ImageTk.PhotoImage(img)
                    logo_lbl = ctk.CTkLabel(header_frame, image=self.header_big_logo, text="")
                    logo_lbl.pack(side="top", pady=(0, 15))  # Biraz daha boşluk
                    logo_loaded = True
                    print(f"[LOGO] Logo yüklendi: {logo_path}")
                    break
                except Exception as e:
                    print(f"[LOGO] Logo yükleme hatası ({logo_path}): {e}")
                    continue
        
        # Logo bulunamazsa emoji logo göster
        if not logo_loaded:
            emoji_logo = ctk.CTkLabel(
                header_frame,
                text="🛡️",
                font=ctk.CTkFont(size=100),  # Emoji de büyük
                text_color="#00ff88"
            )
            emoji_logo.pack(side="top", pady=(0, 10))
            print("[LOGO] Dosya bulunamadı, emoji logo gösteriliyor")

        # ──────────── Kompakt Başlık ────────────
        title_label = ctk.CTkLabel(
            header_frame,
            text="Aşama Seçimi",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#cccccc"
        )
        title_label.pack(side="top", pady=(0, 5))

    def _create_footer(self, parent):
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", padx=30, pady=(5, 15))  # Daha az padding

        # ──────────── Sadece Uyarı Yazısı (kompakt) ────────────
        warning_label = ctk.CTkLabel(
            footer_frame,
            text="⚠️ Seçilen aşama doğrultusunda sistem konfigürasyonu değişecektir.",
            font=ctk.CTkFont(size=11),  # Daha küçük font
            text_color="#ff9800"
        )
        warning_label.pack(pady=(0, 0))


    def _create_phase_cards(self, parent):
        """
        Aşama kartlarını 2×2 grid şeklinde oluşturur.
        Kartlar alt alta değil, iki sütun × iki satır olarak dizilir.
        """
        # Grid çerçevesi
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # 2 sütunlu grid ayarı
        cards_frame.grid_columnconfigure(0, weight=1, uniform="col")
        cards_frame.grid_columnconfigure(1, weight=1, uniform="col")

        # Aşama verileri
        phase_data = [
            {"id": 0, "title": "AŞAMA 0", "icon": "🎮", "color": "#6b46c1", "hover": "#553c9a"},
            {"id": 1, "title": "AŞAMA 1", "icon": "🎯", "color": "#4CAF50", "hover": "#388E3C"},
            {"id": 2, "title": "AŞAMA 2", "icon": "🔍", "color": "#FF9800", "hover": "#F57C00"},
            {"id": 3, "title": "AŞAMA 3", "icon": "⚡", "color": "#F44336", "hover": "#D32F2F"},
        ]

        for idx, info in enumerate(phase_data):
            row, col = divmod(idx, 2)
            self._create_phase_card(cards_frame, info, row, col)

    def _create_phase_card(self, parent, phase_info, row, column):
        """
        Tek bir aşama kartını grid içinde (row,col) pozisyonunda oluşturur.
        Kartın altındaki uzun açıklamalar kaldırıldı; sadece ikon, başlık ve buton var.
        """
        # Kart çerçevesini grid ile yerleştir
        card = ctk.CTkFrame(
            parent,
            fg_color="#2a2a2a",  # İç koyu renk KALSIN
            corner_radius=12,
            border_width=2,
            border_color="#3399ff"  # SkyShield mavisi (kenar çizgisi)
        )

        card.grid(
            row=row, column=column,
            padx=20, pady=20,
            sticky="nsew"
        )
        card.grid_propagate(False)

        # Kart içi düzen
        # 1) İkon
        ico = ctk.CTkLabel(
            card,
            text=phase_info["icon"],
            font=ctk.CTkFont(size=36),
            text_color=phase_info["color"]  # Her aşamanın kendi rengi
        )

        ico.pack(pady=(20, 5))

        # 2) Başlık
        title = ctk.CTkLabel(
            card,
            text=phase_info["title"],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=phase_info["color"]
        )
        title.pack(pady=(0, 15))

        # 3) SEÇ butonu
        btn = ctk.CTkButton(
            card,
            text="SEÇ",
            fg_color=phase_info["color"],
            hover_color=phase_info["hover"],
            width=100, height=35,
            command=lambda p=phase_info["id"]: self.select_phase(p)
        )
        btn.pack(side="bottom", pady=(0, 20))
    
    

    def select_phase(self, phase):
        self.selected_phase = phase
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()
        return self.selected_phase

class BaseModule:
    """Temel modül sınıfı"""
    def __init__(self, parent, title):
        self.parent = parent
        self.title = title
        self.frame = ctk.CTkFrame(parent)
        
    def create_title(self):
        title_label = ctk.CTkLabel(
            self.frame,
            text=self.title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

class SystemStatusModule(BaseModule):
    """Sistem durumu modülü"""
    def __init__(self, parent):
        super().__init__(parent, "SİSTEM DURUMU")
        self.setup_module()
        
    def setup_module(self):
        self.create_title()
        
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Sistem Hazır",
            font=ctk.CTkFont(size=14),
            text_color="#00ff88"
        )
        self.status_label.pack(pady=5)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.frame)
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.set(0.0)
        
    def update_status(self, status, color="#00ff88"):
        self.status_label.configure(text=status, text_color=color)
        
    def update_progress(self, value):
        self.progress.set(value)

class TargetInfoModule(BaseModule):
    """Hedef bilgileri modülü"""
    def __init__(self, parent, phase):
        super().__init__(parent, "HEDEF BİLGİLERİ")
        self.phase = phase
        self.setup_module()
        
    def setup_module(self):
        self.create_title()
        
        if self.phase == 0:  
            self.create_manual_mode_info()
        # Aşamaya göre özel bilgiler
        elif self.phase == 1:
            self.create_phase1_info()
        elif self.phase == 2:
            self.create_phase2_info()
        elif self.phase == 3:
            self.create_phase3_info()
    def create_manual_mode_info(self):
        """Aşama 0: Manuel mod bilgileri"""
        self.controller_status = ctk.CTkLabel(
            self.frame,
            text="🎮 Controller: Bağlı Değil",
            font=ctk.CTkFont(size=12),
            text_color="#ff6b6b"
        )
        self.controller_status.pack(pady=2)
        
        self.control_mode = ctk.CTkLabel(
            self.frame,
            text="Kontrol: Manuel",
            font=ctk.CTkFont(size=12),
            text_color="#00ccff"
        )
        self.control_mode.pack(pady=2)
        
        self.sensitivity_label = ctk.CTkLabel(
            self.frame,
            text="Hassasiyet: Normal",
            font=ctk.CTkFont(size=12)
        )
        self.sensitivity_label.pack(pady=2)
        
        self.safety_status = ctk.CTkLabel(
            self.frame,
            text="Güvenlik: Aktif",
            font=ctk.CTkFont(size=12),
            text_color="#00ff88"
        )
        self.safety_status.pack(pady=2)        
            
    def create_phase1_info(self):
        """Aşama 1: Temel hedef bilgileri"""
        self.target_count_label = ctk.CTkLabel(
            self.frame,
            text="Tespit Edilen Balon: 0",
            font=ctk.CTkFont(size=12)
        )
        self.target_count_label.pack(pady=2)
        
        self.destroyed_label = ctk.CTkLabel(
            self.frame,
            text="İmha Edilen: 0",
            font=ctk.CTkFont(size=12),
            text_color="#00ff88"
        )
        self.destroyed_label.pack(pady=2)
        
    def create_phase2_info(self):
        """Aşama 2: Düşman/Dost ayrımı"""
        self.friend_label = ctk.CTkLabel(
            self.frame,
            text="Dost Hedef: 0",
            font=ctk.CTkFont(size=12),
            text_color="#00ff88"
        )
        self.friend_label.pack(pady=2)
        
        self.enemy_label = ctk.CTkLabel(
            self.frame,
            text="Düşman Hedef: 0",
            font=ctk.CTkFont(size=12),
            text_color="#ff4444"
        )
        self.enemy_label.pack(pady=2)
        
        self.destroyed_label = ctk.CTkLabel(
            self.frame,
            text="İmha Edilen Düşman: 0",
            font=ctk.CTkFont(size=12),
            text_color="#ffaa00"
        )
        self.destroyed_label.pack(pady=2)
        
    def create_phase3_info(self):
        """Aşama 3: QR kod ve angajman bilgileri"""
        self.qr_status_label = ctk.CTkLabel(
            self.frame,
            text="QR Kod: Okunmadı",
            font=ctk.CTkFont(size=12),
            text_color="#ff6666"
        )
        self.qr_status_label.pack(pady=2)
        
        self.target_color_label = ctk.CTkLabel(
            self.frame,
            text="Hedef Renk: --",
            font=ctk.CTkFont(size=12)
        )
        self.target_color_label.pack(pady=2)
        
        self.target_shape_label = ctk.CTkLabel(
            self.frame,
            text="Hedef Şekil: --",
            font=ctk.CTkFont(size=12)
        )
        self.target_shape_label.pack(pady=2)
        
        self.platform_label = ctk.CTkLabel(
            self.frame,
            text="Platform: A",
            font=ctk.CTkFont(size=12),
            text_color="#00ccff"
        )
        self.platform_label.pack(pady=2)

class CoordinatesModule(BaseModule):
    """Koordinat bilgileri modülü"""
    def __init__(self, parent):
        super().__init__(parent, "KOORDİNATLAR")
        self.setup_module()
        
    def setup_module(self):
        self.create_title()
        
        self.coord_labels = {}
        coord_data = [
            ("Mesafe", "-- m"),
            ("Açı (Pan)", "0°"),
            ("Açı (Tilt)", "0°"),
            ("Hız", "-- m/s")
        ]
        
        for label, value in coord_data:
            row_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=2)
            
            ctk.CTkLabel(
                row_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=12)
            ).pack(side="left")
            
            self.coord_labels[label] = ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#00ccff"
            )
            self.coord_labels[label].pack(side="right")
            
    def update_coordinates(self, distance=None, pan=None, tilt=None, speed=None):
        if distance is not None:
            self.coord_labels["Mesafe"].configure(text=f"{distance} m")
        if pan is not None:
            self.coord_labels["Açı (Pan)"].configure(text=f"{pan}°")
        if tilt is not None:
            self.coord_labels["Açı (Tilt)"].configure(text=f"{tilt}°")
        if speed is not None:
            self.coord_labels["Hız"].configure(text=f"{speed} m/s")

class WeaponModule(BaseModule):
    """Mühimmat modülü"""

    def __init__(self, parent):
        super().__init__(parent, "MÜHİMMAT SİSTEMİ")
        self.control_mode = "Otomatik"
        self.selected_weapon = "Lazer"
        self.setup_module()

    def setup_module(self):
        self.create_title()

        # Üst kontrol çubuğu: Otomatik / Manuel ve Seçili gösterimi
        control_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        control_row.pack(fill="x", padx=10, pady=(5, 0))

        self.control_mode_selector = ctk.CTkSegmentedButton(
            control_row,
            values=["Otomatik", "Manuel"],
            command=self.change_control_mode,
            width=140
        )
        self.control_mode_selector.pack(side="left")
        self.control_mode_selector.set("Otomatik")

        self.weapon_label = ctk.CTkLabel(
            control_row,
            text="Seçili: Lazer",
            font=ctk.CTkFont(size=12),
            text_color="#ffaa00"
        )
        self.weapon_label.pack(side="right", padx=(10, 0))

        # Mühimmat durum çerçevesi
        weapon_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        weapon_frame.pack(fill="x", padx=10, pady=(5, 10), anchor="n")

        # Lazer durumu (tıklanabilir nokta)
        laser_frame = ctk.CTkFrame(weapon_frame, fg_color="transparent")
        laser_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(laser_frame, text="Lazer:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.laser_status_btn = ctk.CTkButton(
            laser_frame,
            text="●",
            width=10,
            fg_color="transparent",
            hover=False,
            font=ctk.CTkFont(size=16),
            text_color="#00ff88",
            command=lambda: self.set_manual_weapon("Lazer")
        )
        self.laser_status_btn.pack(side="right")

        # Boncuk durumu (tıklanabilir nokta)
        pellet_frame = ctk.CTkFrame(weapon_frame, fg_color="transparent")
        pellet_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(pellet_frame, text="Boncuk:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.pellet_status_btn = ctk.CTkButton(
            pellet_frame,
            text="●",
            width=10,
            fg_color="transparent",
            hover=False,
            font=ctk.CTkFont(size=16),
            text_color="#888888",
            command=lambda: self.set_manual_weapon("Boncuk")
        )
        self.pellet_status_btn.pack(side="right")

    def change_control_mode(self, mode):
        self.control_mode = mode
        if mode == "Otomatik":
            self.selected_weapon = "Lazer"
        self.update_weapon_selection(self.selected_weapon)
        self.update_weapon_status()

    def set_manual_weapon(self, weapon):
        if self.control_mode == "Manuel":
            self.selected_weapon = weapon
            self.update_weapon_selection(weapon)
            self.update_weapon_status()

    def update_weapon_selection(self, weapon_type):
        self.weapon_label.configure(text=f"Seçili: {weapon_type}")

    def update_weapon_status(self):
        laser_active = self.selected_weapon == "Lazer"
        pellet_active = self.selected_weapon == "Boncuk"

        self.laser_status_btn.configure(text_color="#00ff88" if laser_active else "#888888")
        self.pellet_status_btn.configure(text_color="#00ff88" if pellet_active else "#888888")




class UpdatedCameraModule:
    """
    Raspberry Pi'den gerçek kamera akışı alan kamera modülü
    AppController ile entegre edildi
    """
    
    def __init__(self, parent, app_controller, phase):
        self.parent = parent
        self.app = app_controller
        self.phase = phase
        
        # Kamera durumu
        self.camera_active = True
        self.target_locked = False
        self.recording = False
        
        # Hedef pozisyonu (simülasyon + gerçek veri)
        self.target_x = 320
        self.target_y = 240
        
        # UI referansları
        self.camera_container = None
        self.camera_label = None
        self.status_text = None
        self.status_icon = None
        self.record_button = None
        self.snapshot_button = None
        self.lock_button = None
        
        # Frame yönetimi
        self.current_frame = None
        self.default_frame_created = False
        
        self.setup_ui()
        self._register_app_callbacks()
        
        print(f"[CAMERA MODULE] Oluşturuldu - Aşama {phase}")
    
    def setup_ui(self):
        """Kamera modülü UI'ını oluştur"""
        # Ana kamera container
        self.camera_container = ctk.CTkFrame(
            self.parent, 
            fg_color="#000000",
            corner_radius=0,
            border_width=2,
            border_color="#ffff00"
        )
        self.camera_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Kamera görüntü alanı
        self.camera_label = ctk.CTkLabel(
            self.camera_container,
            text="",
            width=500,
            height=350
        )
        self.camera_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        # İlk başta default frame göster
        self._create_default_frame()
        
        # Alt durum çubuğu
        self._create_status_bar()
        
        # Kamera kontrolleri
        self._create_camera_controls()
        
        print("[CAMERA MODULE] UI oluşturuldu")
    
    def _register_app_callbacks(self):
        """AppController callback'lerini kaydet"""
        # Frame alındığında
        self.app.register_callback("frame_received", self._on_frame_received)
        
        # Raspberry Pi bağlantı durumu değiştiğinde
        self.app.register_callback("raspberry_connection_changed", self._on_connection_changed)
        
        # Veri güncellendiğinde
        self.app.register_callback("data_updated", self._on_data_updated)
        
        print("[CAMERA MODULE] Callback'ler kaydedildi")
    
    def _create_default_frame(self):
        """Varsayılan kamera frame'i oluştur"""
        try:
            # Siyah arka plan ile targeting sistemi
            img = Image.new('RGB', (500, 350), color='black')
            
            # PIL Image'ı Tkinter PhotoImage'a çevir
            self.current_frame = ImageTk.PhotoImage(img)
            self.camera_label.configure(image=self.current_frame)
            
            # Targeting overlay'ini canvas ile ekle
            self._create_targeting_overlay()
            
            self.default_frame_created = True
            print("[CAMERA MODULE] Varsayılan frame oluşturuldu")
            
        except Exception as e:
            print(f"[CAMERA MODULE] Varsayılan frame oluşturma hatası: {e}")
            self.camera_label.configure(text="📷 KAMERA HAZIR")
    
    def _create_targeting_overlay(self):
        """Targeting sistemi overlay'i (Canvas ile)"""
        try:
            # Eğer zaten canvas varsa kaldır
            if hasattr(self, 'targeting_canvas'):
                self.targeting_canvas.destroy()
            
            # Targeting canvas oluştur
            self.targeting_canvas = tk.Canvas(
                self.camera_container,
                bg='black',
                highlightthickness=0,
                width=500,
                height=350
            )
            self.targeting_canvas.place(x=10, y=10, width=500, height=350)
            
            # Crosshair çiz
            self._draw_targeting_elements()
            
        except Exception as e:
            print(f"[CAMERA MODULE] Targeting overlay hatası: {e}")
    
    def _draw_targeting_elements(self):
        """Targeting elementlerini çiz"""
        if not hasattr(self, 'targeting_canvas'):
            return
            
        canvas = self.targeting_canvas
        canvas.delete("all")  # Önceki çizimleri temizle
        
        # Merkez crosshair
        canvas.create_line(250, 160, 250, 190, fill="#ffff00", width=2, tags="crosshair")
        canvas.create_line(235, 175, 265, 175, fill="#ffff00", width=2, tags="crosshair")
        
        # Köşe çerçeveleri
        # Sol üst
        canvas.create_line(50, 50, 80, 50, fill="#ffff00", width=3, tags="brackets")
        canvas.create_line(50, 50, 50, 80, fill="#ffff00", width=3, tags="brackets")
        
        # Sağ üst  
        canvas.create_line(420, 50, 450, 50, fill="#ffff00", width=3, tags="brackets")
        canvas.create_line(450, 50, 450, 80, fill="#ffff00", width=3, tags="brackets")
        
        # Sol alt
        canvas.create_line(50, 270, 80, 270, fill="#ffff00", width=3, tags="brackets")
        canvas.create_line(50, 270, 50, 300, fill="#ffff00", width=3, tags="brackets")
        
        # Sağ alt
        canvas.create_line(420, 270, 450, 270, fill="#ffff00", width=3, tags="brackets")
        canvas.create_line(450, 270, 450, 300, fill="#ffff00", width=3, tags="brackets")
        
        # Grid çizgileri
        for i in range(100, 400, 50):
            canvas.create_line(i, 0, i, 350, fill="#333333", width=1, tags="grid")
        for i in range(50, 300, 50):
            canvas.create_line(0, i, 500, i, fill="#333333", width=1, tags="grid")
        
        # Hedef göstergesi
        self._draw_target_indicator()
    
    def _draw_target_indicator(self):
        """Hedef göstergesini çiz"""
        if not hasattr(self, 'targeting_canvas'):
            return
            
        canvas = self.targeting_canvas
        
        # Önceki hedef göstergelerini temizle
        canvas.delete("target")
        
        # Hedef noktası
        canvas.create_oval(
            self.target_x - 10, self.target_y - 10,
            self.target_x + 10, self.target_y + 10,
            outline="#ff0000", width=2, tags="target"
        )
        
        # Hedef kilidi çerçevesi
        if self.target_locked:
            canvas.create_rectangle(
                self.target_x - 30, self.target_y - 30,
                self.target_x + 30, self.target_y + 30,
                outline="#ff0000", width=2, tags="target"
            )
            canvas.create_text(
                self.target_x, self.target_y - 40,
                text="LOCKED", fill="#ff0000", 
                font=("Arial", 10, "bold"), tags="target"
            )
    
    def _on_frame_received(self, frame_data):
        """Raspberry Pi'den frame alındığında"""
        try:
            if isinstance(frame_data, np.ndarray):
                # NumPy array'i PIL Image'a çevir
                pil_image = Image.fromarray(frame_data)
                
                # Boyutlandır
                pil_image = pil_image.resize((500, 350), Image.Resampling.LANCZOS)
                
                # Tkinter PhotoImage'a çevir
                self.current_frame = ImageTk.PhotoImage(pil_image)
                
                # Label'ı güncelle
                self.camera_label.configure(image=self.current_frame)
                
                # Targeting overlay'ini güncelle
                self._draw_targeting_elements()
                
                print("[CAMERA MODULE] Frame güncellendi")
                
        except Exception as e:
            print(f"[CAMERA MODULE] Frame işleme hatası: {e}")
    
    def _on_connection_changed(self, connection_data):
        """Raspberry Pi bağlantı durumu değiştiğinde"""
        try:
            connected = connection_data.get('connected', False) if connection_data else False
            details = connection_data.get('details', {}) if connection_data else {}
            camera_connected = details.get('camera_connected', False)
            
            if camera_connected:
                self.status_text.configure(text="SİSTEM DURUMU: Kamera Bağlı")
                self.status_icon.configure(text="📹")
            elif connected:
                self.status_text.configure(text="SİSTEM DURUMU: Veri Bağlı (Kamera Yok)")
                self.status_icon.configure(text="📡")
            else:
                self.status_text.configure(text="SİSTEM DURUMU: Bağlantı Yok")
                self.status_icon.configure(text="❌")
                # Varsayılan frame'e dön
                if self.default_frame_created:
                    self._create_default_frame()
            
            print(f"[CAMERA MODULE] Bağlantı durumu: {connected}, Kamera: {camera_connected}")
            
        except Exception as e:
            print(f"[CAMERA MODULE] Bağlantı durumu güncelleme hatası: {e}")
    
    def _on_data_updated(self, data):
        """Veri güncellendiğinde GUI modüllerini güncelle"""
        try:
            # Threading hatalarını önlemek için kontrol
            pass
            
        except Exception as e:
            # Threading hatalarını bastır
            pass
    
    def _create_status_bar(self):
        """Alt durum çubuğu"""
        status_frame = ctk.CTkFrame(
            self.camera_container,
            fg_color="#1a1a1a",
            height=40
        )
        status_frame.pack(fill="x", side="bottom", padx=5, pady=5)
        status_frame.pack_propagate(False)
        
        # Sol taraf - Sistem durumu
        left_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=10)
        
        self.status_icon = ctk.CTkLabel(
            left_frame,
            text="📷",
            font=ctk.CTkFont(size=16),
            text_color="#ffff00"
        )
        self.status_icon.pack(side="left", padx=5)
        
        self.status_text = ctk.CTkLabel(
            left_frame,
            text="SİSTEM DURUMU: Hazır",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffff00"
        )
        self.status_text.pack(side="left")
        
        # Sağ taraf - Zaman ve mod
        right_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=10)
        
        current_time = datetime.now().strftime("%H:%M")
        
        self.time_label = ctk.CTkLabel(
            right_frame,
            text=current_time,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.time_label.pack(side="right", padx=10)
        
        phase_label = ctk.CTkLabel(
            right_frame,
            text=f"AŞAMA {self.phase}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffff00"
        )
        phase_label.pack(side="right", padx=10)
        
        # Zaman güncelleme thread'i
        self._start_time_update()
    
    def _start_time_update(self):
        """Zaman güncelleme thread'ini başlat"""
        def update_time():
            while True:
                try:
                    if self.time_label:
                        current_time = datetime.now().strftime("%H:%M:%S")
                        self.time_label.configure(text=current_time)
                except:
                    break
                time.sleep(1)
        
        time_thread = threading.Thread(target=update_time, daemon=True)
        time_thread.start()
    
    def _create_camera_controls(self):
        """Kamera kontrol butonları"""
        controls_frame = ctk.CTkFrame(self.camera_container, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Kayıt butonu
        self.record_button = ctk.CTkButton(
            controls_frame,
            text="🔴 KAYIT BAŞLAT",
            width=120,
            height=30,
            fg_color="#cc0000",
            hover_color="#990000",
            command=self._toggle_recording
        )
        self.record_button.pack(side="left", padx=5)
        
        # Anlık görüntü
        self.snapshot_button = ctk.CTkButton(
            controls_frame,
            text="📸 SNAPSHOT",
            width=100,
            height=30,
            fg_color="#1f538d",
            command=self._take_snapshot
        )
        self.snapshot_button.pack(side="left", padx=5)
        
        # Hedef kilidi
        self.lock_button = ctk.CTkButton(
            controls_frame,
            text="🎯 TARGETİNG",
            width=100,
            height=30,
            fg_color="#ff9800",
            hover_color="#f57c00",
            command=self._toggle_target_lock
        )
        self.lock_button.pack(side="right", padx=5)
    
    def _toggle_recording(self):
        """Kayıt başlat/durdur"""
        self.recording = not self.recording
        
        if self.recording:
            self.record_button.configure(
                text="⏹️ KAYIT DURDUR", 
                fg_color="#ff0000"
            )
            self.status_text.configure(text="SİSTEM DURUMU: 🔴 KAYIT AKTİF")
            self.status_icon.configure(text="🔴")
            
            # AppController'a log ekle
            if hasattr(self.app, 'add_log'):
                self.app.add_log("📹 Video kaydı başlatıldı")
            
        else:
            self.record_button.configure(
                text="🔴 KAYIT BAŞLAT", 
                fg_color="#cc0000"
            )
            self.status_text.configure(text="SİSTEM DURUMU: Hazır")
            self.status_icon.configure(text="📷")
            
            # AppController'a log ekle
            if hasattr(self.app, 'add_log'):
                self.app.add_log("⏹️ Video kaydı durduruldu")
    
    def _take_snapshot(self):
        """Anlık görüntü al"""
        try:
            # Buton animasyonu
            self.snapshot_button.configure(text="📸 KAYDEDILIYOR...", fg_color="#ff9800")
            
            # AppController üzerinden frame kaydet
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/skyshield_snapshot_{timestamp}.png"
            
            success = self.app.save_current_frame(filename)
            
            if success:
                # AppController'a log ekle
                if hasattr(self.app, 'add_log'):
                    self.app.add_log(f"📸 Anlık görüntü alındı: {filename}")
                
                # Başarı animasyonu
                self.snapshot_button.configure(text="📸 SAVED! ✓", fg_color="#00cc44")
                self.camera_container.after(2000, lambda: self.snapshot_button.configure(
                    text="📸 SNAPSHOT", fg_color="#1f538d"
                ))
            else:
                # Hata durumu
                if hasattr(self.app, 'add_log'):
                    self.app.add_log("❌ Anlık görüntü alınamadı", "ERROR")
                
                self.snapshot_button.configure(text="❌ HATA", fg_color="#cc0000")
                self.camera_container.after(2000, lambda: self.snapshot_button.configure(
                    text="📸 SNAPSHOT", fg_color="#1f538d"
                ))
            
        except Exception as e:
            print(f"[CAMERA MODULE] Snapshot hatası: {e}")
            if hasattr(self.app, 'add_log'):
                self.app.add_log(f"❌ Snapshot hatası: {e}", "ERROR")
    
    def _toggle_target_lock(self):
        """Hedef kilidi aç/kapat"""
        # AppController'a komut gönder
        if self.target_locked:
            # Unlock
            self.app.send_command("unlock_target")
        else:
            # Lock
            self.app.send_command("lock_target")
        
        # UI güncellemesi data_updated callback'i ile gelecek
    
    def stop_camera(self):
        """Kamera modülünü durdur"""
        self.camera_active = False
        
        # Targeting canvas'ını temizle
        if hasattr(self, 'targeting_canvas'):
            self.targeting_canvas.delete("all")
            self.targeting_canvas.create_text(250, 175, text="KAMERA DURDURULDU", 
                                            fill="#ff0000", font=("Arial", 20, "bold"))
        
        # Durum güncelle
        self.status_text.configure(text="SİSTEM DURUMU: Durduruldu")
        self.status_icon.configure(text="⏹️")
        
        print("[CAMERA MODULE] Kamera durduruldu")
    
    def restart_camera(self):
        """Kamera modülünü yeniden başlat"""
        self.camera_active = True
        
        # Targeting overlay'ini yeniden oluştur
        self._draw_targeting_elements()
        
        # Durum güncelle
        self.status_text.configure(text="SİSTEM DURUMU: Hazır")
        self.status_icon.configure(text="📷")
        
        print("[CAMERA MODULE] Kamera yeniden başlatıldı")
    
    def get_module_info(self) -> dict:
        """Modül bilgilerini döndür"""
        return {
            'active': self.camera_active,
            'recording': self.recording,
            'target_locked': self.target_locked,
            'target_position': {'x': self.target_x, 'y': self.target_y},
            'phase': self.phase,
            'has_current_frame': self.current_frame is not None
        }

class LogModule(BaseModule):
    """Log modülü"""
    def __init__(self, parent):
        super().__init__(parent, "SİSTEM KAYITLARI")
        self.setup_module()
        
    def setup_module(self):
        self.create_title()
        
        self.log_text = ctk.CTkTextbox(self.frame, height=200)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Clear butonu
        clear_button = ctk.CTkButton(
            self.frame,
            text="TEMİZLE",
            width=80,
            height=25,
            command=self.clear_logs
        )
        clear_button.pack(pady=5)
        
        # İlk log mesajı
        self.add_log("Sistem başlatıldı...")
        
    def add_log(self, message):
        current_time = time.strftime("%H:%M:%S")
        log_message = f"[{current_time}] {message}\n"
        self.log_text.insert("end", log_message)
        self.log_text.see("end")
        
    def clear_logs(self):
        self.log_text.delete("0.0", "end")

class ControlModule(BaseModule):
    """Kontrol modülü"""
    def __init__(self, parent, phase):
        super().__init__(parent, "SİSTEM KONTROLLERİ")
        self.phase = phase
        self.setup_module()
        
    def setup_module(self):
        self.create_title()
        
        # Aşamaya özel kontroller
        if self.phase == 1:
            self.create_phase1_controls()
        elif self.phase == 2:
            self.create_phase2_controls()
        elif self.phase == 3:
            self.create_phase3_controls()
            
        # Ortak kontroller
        self.create_common_controls()
        
    def create_phase1_controls(self):
        """Aşama 1 kontrolleri"""
        self.auto_button = ctk.CTkButton(
            self.frame,
            text="OTOMATIK TARAMA BAŞLAT",
            fg_color="#4CAF50",
            hover_color="#388E3C",
            height=40,
            command=self.start_auto_scan
        )
        self.auto_button.pack(fill="x", padx=10, pady=5)
        
    def create_phase2_controls(self):
        """Aşama 2 kontrolleri"""
        self.auto_button = ctk.CTkButton(
            self.frame,
            text="DÜŞMAN TESPİT BAŞLAT",
            fg_color="#FF9800",
            hover_color="#F57C00",
            height=40,
            command=self.start_enemy_detection
        )
        self.auto_button.pack(fill="x", padx=10, pady=5)
        
    def create_phase3_controls(self):
        """Aşama 3 kontrolleri"""
        # QR okuma
        qr_button = ctk.CTkButton(
            self.frame,
            text="QR KOD OKU",
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            height=35,
            command=self.read_qr_code
        )
        qr_button.pack(fill="x", padx=10, pady=2)
        
        # Angajman başlat
        self.auto_button = ctk.CTkButton(
            self.frame,
            text="ANGAJMAN BAŞLAT",
            fg_color="#F44336",
            hover_color="#D32F2F",
            height=40,
            command=self.start_engagement
        )
        self.auto_button.pack(fill="x", padx=10, pady=5)
        
    def create_common_controls(self):
        """Ortak kontroller"""
        # Ateş butonu
        self.fire_button = ctk.CTkButton(
            self.frame,
            text="ATEŞ!",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#ff4444",
            hover_color="#cc3333",
            height=50,
            command=self.fire_weapon
        )
        self.fire_button.pack(fill="x", padx=10, pady=10)
        
        # Kalibrasyon
        calibrate_button = ctk.CTkButton(
            self.frame,
            text="KALİBRASYON",
            fg_color="#4499ff",
            hover_color="#3377cc",
            height=35,
            command=self.calibrate
        )
        calibrate_button.pack(fill="x", padx=10, pady=2)
        
    def start_auto_scan(self):
        # Aşama 1 otomatik tarama
        pass
        
    def start_enemy_detection(self):
        # Aşama 2 düşman tespiti
        pass
        
    def start_engagement(self):
        # Aşama 3 angajman
        pass
        
    def read_qr_code(self):
        # QR kod okuma
        pass
        
    def fire_weapon(self):
        # Ateş etme
        pass
        
    def calibrate(self):
        # Kalibrasyon
        pass

class SkyShieldMainGUI:
    """Ana GUI sınıfı"""
    def __init__(self, phase):
        self.phase = phase
        self.root = ctk.CTk()
        self.root.title(f"Sky Shield - Aşama {phase}")
        self.root.geometry("1400x900")
        self.root.resizable(False, False)

        # Temaya uygun renkler
        self.phase_colors = {
            0: "#9b59b6",  # Mor
            1: "#2ecc71",  # Yeşil
            2: "#f39c12",  # Turuncu
            3: "#e74c3c",  # Kırmızı
        }
        self.theme_color = self.phase_colors.get(self.phase, "#00ff88")

        self.center_window()
        self.emergency_active = False
        self.emergency_countdown = 15

        # -------- YENİ: AppController entegrasyonu + GERÇEK IP --------
       # raspberry_ip = "192.168.0.22"  # ✅ KENDİ IP'NİZİ YAZIN!
        raspberry_ip = "localhost"      # ❌ Bu yavaş
        
        self.app_controller = AppController(raspberry_ip)

        # 1. WebSocket bağlantısını kur
        self.app_controller.start()
        

        print(f"[MAIN GUI] Phase değeri GUI içinden: {self.phase}")

        # 2. Raspberry’ye seçilen aşamayı gönder
        self.app_controller.send_command("change_mode", self.phase)

        # 3. Callback’leri kur ve GUI’yi başlat
        self._register_app_callbacks()
        self.setup_main_gui()
        self.setup_modules()

        print(f"[MAIN GUI] Raspberry Pi IP: {raspberry_ip}")

    def center_window(self):
        """Ana GUI penceresini ekranın ortasına yerleştir"""
        # Pencere boyutları
        window_width = 1400
        window_height = 900
        
        # Ekran boyutlarını al
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Orta pozisyonu hesapla
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # Pencereyi ortala
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        print(f"[MAIN GUI] Pencere ortalandı: {center_x}x{center_y}")

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", padx=10, pady=(0, 0))
        header_frame.pack_propagate(True)

        header_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        header_frame.grid_rowconfigure(0, weight=1)

        # -------- YENİ: CTkImage kullan --------
        logo_paths = [
            os.path.join("assets", "skyshield_logo.jpg"),
            os.path.join("assets", "skyshield_logo.png"),
            "skyshield_logo.jpg", 
            "skyshield_logo.png"
        ]
        
        logo_loaded = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    # PIL Image'ı CTkImage'a çevir
                    pil_image = Image.open(logo_path)
                    self.small_logo_img = ctk.CTkImage(
                        light_image=pil_image,
                        dark_image=pil_image,
                        size=(100, 100)
                    )
                    
                    logo_lbl = ctk.CTkLabel(
                        header_frame, 
                        image=self.small_logo_img, 
                        text=""
                    )
                    logo_lbl.grid(row=0, column=2, sticky="ne", padx=5, pady=5)
                    
                    logo_loaded = True
                    print(f"[LOGO] Logo yüklendi: {logo_path}")
                    break
                    
                except Exception as e:
                    print(f"[LOGO] Logo yükleme hatası ({logo_path}): {e}")
                    continue
        
        # Logo bulunamazsa emoji logo göster
        if not logo_loaded:
            emoji_logo = ctk.CTkLabel(
                header_frame,
                text="🛡️",
                font=ctk.CTkFont(size=50),
                text_color=self.theme_color
            )
            emoji_logo.grid(row=0, column=2, sticky="ne", padx=5, pady=5)
            print("[LOGO] Dosya bulunamadı, emoji logo gösteriliyor")

        # Orta kısım - Başlık
        middle = ctk.CTkFrame(header_frame, fg_color="transparent")
        middle.grid(row=0, column=1, sticky="n", pady=(5, 0))

        title_lbl = ctk.CTkLabel(
            middle,
            text=f"SKY SHIELD - AŞAMA {self.phase}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.theme_color
        )
        title_lbl.pack(side="top", pady=(0, 0))

        phase_descs = {
            0: "Manuel Kontrol Modu",
            1: "Temel Hedef Tespiti ve İmha",
            2: "Düşman Tespiti ve Hedef İmha",
            3: "Görsel Angajman ile Çift Platform"
        }
        desc_lbl = ctk.CTkLabel(
            middle,
            text=phase_descs[self.phase],
            font=ctk.CTkFont(size=14),
            text_color="#cccccc"
        )
        desc_lbl.pack(side="top", pady=(0, 0))

    def _darker(self, hex_color, factor=0.85):
        """Verilen hex rengin daha koyu tonunu döndür"""
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(int(c * factor) for c in rgb)
        return "#%02x%02x%02x" % darker_rgb

    def setup_main_gui(self):
        # Ana çerçeve
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        self.create_header()
        
        # Ana içerik alanı
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Alt panel - Acil durum
        self.create_bottom_panel()
        
        # Geri dönme butonu
        self.back_button = ctk.CTkButton(
            self.root,
            text="←",
            command=self._return_to_menu,
            width=35,
            height=30,
            fg_color=self.theme_color,
            hover_color=self._darker(self.theme_color),
            font=ctk.CTkFont(size=16)
        )
        self.back_button.place(x=10, y=10)
        
    def setup_modules(self):
        # Sol panel - Durum ve bilgiler (Askeri tema)
        left_frame = ctk.CTkFrame(self.content_frame, width=280, fg_color="#1a1a1a")
        left_frame.pack(side="left", fill="y", padx=5)
        left_frame.pack_propagate(False)
        
        # Sistem durumu modülü
        self.status_module = SystemStatusModule(left_frame)
        self.status_module.pack(fill="x", padx=10, pady=10)
        
        # Hedef bilgileri modülü
        self.target_module = TargetInfoModule(left_frame, self.phase)
        self.target_module.pack(fill="x", padx=10, pady=5)
        
        # Koordinatlar modülü
        self.coords_module = CoordinatesModule(left_frame)
        self.coords_module.pack(fill="x", padx=10, pady=5)
        
        # Mühimmat modülü
        self.weapon_module = WeaponModule(left_frame)
        self.weapon_module.pack(fill="x", padx=10, pady=5)
        
        # -------- YENİ: Orta panel - Gerçek Kamera Modülü --------
        center_frame = ctk.CTkFrame(self.content_frame, fg_color="#000000")
        center_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        # ESKİ CameraModule yerine UpdatedCameraModule kullan
        self.camera_module = UpdatedCameraModule(center_frame, self.app_controller, self.phase)
        
        # Sağ panel - Kontroller ve log (Askeri tema)
        right_frame = ctk.CTkFrame(self.content_frame, width=250, fg_color="#1a1a1a")
        right_frame.pack(side="right", fill="y", padx=5)
        right_frame.pack_propagate(False)
        
        # Kontroller
        self.control_module = ControlModule(right_frame, self.phase)
        self.control_module.pack(fill="x", padx=10, pady=5)
        
        # Log
        self.log_module = LogModule(right_frame)
        self.log_module.pack(fill="both", expand=True, padx=10, pady=5)

    def start_system(self):
        """Sistem başlat - AppController ile"""
        # AppController'a komut gönder
        self.app_controller.send_command("start_system")
        self.app_controller.send_command("change_mode", self.phase)
        
        # UI güncellemeleri callback'ler ile gelecek
        if hasattr(self, 'log_module'):
            self.log_module.add_log(f"Sistem başlatıldı - Aşama {self.phase}")

    def stop_system(self):
        """Sistem durdur - AppController ile"""
        # AppController'a komut gönder
        self.app_controller.send_command("stop_system")
        
        # UI güncellemeleri callback'ler ile gelecek
        if hasattr(self, 'log_module'):
            self.log_module.add_log("Sistem durduruldu")

    def emergency_stop(self):
        """Acil durdur - AppController ile"""
        # Acil durdur butonu titreme efekti
        self.emergency_button.configure(fg_color="#ff0000", text="🚨 ACTİVE! 🚨")
        
        # AppController'a acil durdur komutu gönder
        self.app_controller.send_command("emergency_stop")
        
        # TÜM SİSTEMLERİ DURDUR
        self._stop_all_systems()
        
        # Uyarı popup'ı oluştur
        self.create_emergency_popup()
        
        # 15 saniye geri sayım başlat
        self.start_emergency_countdown()

    def _stop_all_systems(self):
        """Acil durdurma - Tüm sistemleri durdur"""
        try:
            # Kamera modülünü durdur
            if hasattr(self, 'camera_module'):
                self.camera_module.stop_camera()
            
            # AppController'a acil durdur gönder
            self.app_controller.send_command("emergency_stop")
            
            # Log ekle
            if hasattr(self, 'log_module'):
                self.log_module.add_log("🛑 ACİL DURDUR - Tüm sistemler durduruldu")
            
        except Exception as e:
            print(f"[EMERGENCY] Sistem durdurma hatası: {e}")

    def _restart_all_systems(self):
        """Acil durumdan sonra sistemleri yeniden başlat"""
        try:
            # Kamera modülünü yeniden başlat
            if hasattr(self, 'camera_module'):
                self.camera_module.restart_camera()
            
            # Log ekle
            if hasattr(self, 'log_module'):
                self.log_module.add_log("🟢 Sistemler yeniden başlatıldı")
            
        except Exception as e:
            print(f"[RESTART] Sistem yeniden başlatma hatası: {e}")

    def create_bottom_panel(self):
        bottom_frame = ctk.CTkFrame(self.main_frame, height=80)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        bottom_frame.pack_propagate(False)
        
        # Sol taraf - Sistem kontrolleri
        left_controls = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        left_controls.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Sistem butonları
        start_button = ctk.CTkButton(
            left_controls,
            text="SİSTEM BAŞLAT",
            fg_color="#00cc44",
            hover_color="#009933",
            width=120,
            height=40,
            command=self.start_system
        )
        start_button.pack(side="left", padx=5)
        
        stop_button = ctk.CTkButton(
            left_controls,
            text="SİSTEM DURDUR",
            fg_color="#ff6600",
            hover_color="#cc5500",
            width=120,
            height=40,
            command=self.stop_system
        )
        stop_button.pack(side="left", padx=5)
        
        # Sağ taraf - Acil durum
        emergency_frame = ctk.CTkFrame(bottom_frame)
        emergency_frame.pack(side="right", padx=10, pady=10)
        
        self.emergency_button = ctk.CTkButton(
            emergency_frame,
            text="ACİL DURDUR",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#cc0000",
            hover_color="#990000",
            width=150,
            height=60,
            command=self.emergency_stop
        )
        self.emergency_button.pack(padx=10, pady=10)
        
    def create_emergency_popup(self):
        """Acil durdur uyarı popup'ı"""
        # Popup penceresi
        self.emergency_popup = ctk.CTkToplevel(self.root)
        self.emergency_popup.title("⚠️ ACİL DURDUR")
        self.emergency_popup.geometry("400x250")
        self.emergency_popup.resizable(False, False)
        
        # Pencereyi üstte tut
        self.emergency_popup.attributes('-topmost', True)
        self.emergency_popup.grab_set()
        
        # Ortalama
        self.emergency_popup.update_idletasks()
        x = (self.emergency_popup.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.emergency_popup.winfo_screenheight() // 2) - (250 // 2)
        self.emergency_popup.geometry(f"400x250+{x}+{y}")
        
        # Ana frame
        main_frame = ctk.CTkFrame(self.emergency_popup, fg_color="#cc0000")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Uyarı başlığı
        warning_label = ctk.CTkLabel(
            main_frame,
            text="🚨 ACİL DURDUR AKTİVE! 🚨",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        warning_label.pack(pady=20)
        
        # Açıklama
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Sistem güvenlik protokolü aktivasyon!\nTüm operasyonlar durduruldu.",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff"
        )
        desc_label.pack(pady=10)
        
        # Geri sayım
        self.countdown_label = ctk.CTkLabel(
            main_frame,
            text="Sistem 15 saniye içinde kapanacak...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffff00"
        )
        self.countdown_label.pack(pady=20)
        
        # İptal butonu
        cancel_button = ctk.CTkButton(
            main_frame,
            text="İPTAL ET",
            command=self.cancel_emergency,
            fg_color="#ffffff",
            text_color="#cc0000",
            hover_color="#f0f0f0",
            width=100,
            height=35
        )
        cancel_button.pack(pady=10)
    
    def start_emergency_countdown(self):
        """15 saniye geri sayım"""
        self.emergency_countdown = 15
        self.emergency_active = True
        self.update_countdown()
    
    def update_countdown(self):
        """Geri sayım güncellemesi"""
        if hasattr(self, 'emergency_active') and self.emergency_active:
            if self.emergency_countdown > 0:
                # Countdown labelını güncelle
                if hasattr(self, 'countdown_label'):
                    self.countdown_label.configure(
                        text=f"Sistem {self.emergency_countdown} saniye içinde kapanacak..."
                    )
                
                # Emergency butonu yanıp sönme efekti
                if self.emergency_countdown % 2 == 0:
                    self.emergency_button.configure(fg_color="#ff0000", text="🚨 ACTİVE! 🚨")
                else:
                    self.emergency_button.configure(fg_color="#990000", text="⚠️ DURDUR ⚠️")
                
                # Log güncelleme
                self.log_module.add_log(f"⏰ Kapanmaya {self.emergency_countdown} saniye...")
                
                self.emergency_countdown -= 1
                
                # 1 saniye sonra tekrar çağır
                self.root.after(1000, self.update_countdown)
            else:
                # Sistem kapanması
                self.log_module.add_log("🔴 SİSTEM KAPATILIYOR...")
                self.root.after(1000, self.force_close)
    
    def cancel_emergency(self):
        """Acil durduru iptal et"""
        self.emergency_active = False
        
        # Popup'ı kapat
        if hasattr(self, 'emergency_popup'):
            self.emergency_popup.destroy()
        
        # Butonu normale döndür
        self.emergency_button.configure(
            fg_color="#cc0000",
            text="ACİL DURDUR"
        )
        
        # SİSTEMLERİ YENİDEN BAŞLAT
        self._restart_all_systems()
        
        # Sistem durumunu güncelle
        self.status_module.update_status("Sistem Hazır", "#00ff88")
        self.log_module.add_log("✅ Acil durdur iptal edildi - Sistem normale döndü")
    
    def force_close(self):
        """Zorla kapat"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        
    def _return_to_menu(self):
        """Ana menüye dön"""
        self.root.destroy()
        # Ana menüyü yeniden başlat
        main()

    def __del__(self):
        """GUI kapatılırken temizlik"""
        try:
            if hasattr(self, 'app_controller'):
                self.app_controller.stop()
        except:
            pass

    # ================================
    # YENİ THREADING FİX METODLARI  
    # ================================
    
    def _register_app_callbacks(self):
        """AppController callback'lerini kaydet - THREAD SAFE VERSION"""
        # Thread-safe wrapper fonksiyonlar
        def safe_data_callback(data):
            try:
                if hasattr(self, 'root') and self.root and self.root.winfo_exists():
                    self.root.after_idle(lambda: self._safe_update_gui(data))
            except:
                pass
        
        def safe_log_callback(log_entry):
            try:
                if hasattr(self, 'root') and self.root and self.root.winfo_exists():
                    self.root.after_idle(lambda: self._safe_add_log(log_entry))
            except:
                pass
        
        def safe_connection_callback(connection_data):
            try:
                if hasattr(self, 'root') and self.root and self.root.winfo_exists():
                    self.root.after_idle(lambda: self._safe_connection_update(connection_data))
            except:
                pass
        
        def safe_error_callback(error_message):
            try:
                if hasattr(self, 'root') and self.root and self.root.winfo_exists():
                    self.root.after_idle(lambda: self._safe_error_update(error_message))
            except:
                pass
        
        # Callback'leri kaydet
        self.app_controller.register_callback("data_updated", safe_data_callback)
        self.app_controller.register_callback("log_added", safe_log_callback)
        self.app_controller.register_callback("raspberry_connection_changed", safe_connection_callback)
        self.app_controller.register_callback("raspberry_error", safe_error_callback)

    def _safe_update_gui(self, data):
        """Thread-safe GUI güncellemesi"""
        try:
            if hasattr(self, 'coords_module') and data:
                if 'pan_angle' in data and 'tilt_angle' in data:
                    self.coords_module.update_coordinates(
                        distance=data.get('distance', '--'),
                        pan=f"{data['pan_angle']:.1f}",
                        tilt=f"{data['tilt_angle']:.1f}",
                        speed=data.get('speed', '--')
                    )
            
            if hasattr(self, 'status_module') and data:
                if data.get('target_locked'):
                    self.status_module.update_status("Hedef Kilitli", "#00ff88")
                    self.status_module.update_progress(1.0)
                elif data.get('active'):
                    self.status_module.update_status("Sistem Aktif", "#ffaa00")
                    self.status_module.update_progress(0.5)
                else:
                    self.status_module.update_status("Sistem Hazır", "#cccccc")
                    self.status_module.update_progress(0.0)
            
        except Exception as e:
            print(f"[MAIN GUI] GUI güncelleme hatası: {e}")

    def _safe_add_log(self, log_entry):
        """Thread-safe log ekleme"""
        try:
            if hasattr(self, 'log_module'):
                parts = log_entry.split('] ', 2)
                if len(parts) >= 3:
                    message = parts[2]
                    self.log_module.add_log(message)
                else:
                    self.log_module.add_log(log_entry)
        except Exception as e:
            print(f"[MAIN GUI] Log ekleme hatası: {e}")

    def _safe_connection_update(self, connection_data):
        """Thread-safe bağlantı güncellemesi"""
        try:
            connected = connection_data.get('connected', False) if connection_data else False
            if hasattr(self, 'status_module'):
                if connected:
                    self.status_module.update_status("Raspberry Pi Bağlı", "#00ff88")
                else:
                    self.status_module.update_status("Raspberry Pi Bağlantısı Yok", "#ff6666")
                    
            status = "bağlandı" if connected else "bağlantı kesildi"
            if hasattr(self, 'log_module'):
                self.log_module.add_log(f"Raspberry Pi {status}")
                
        except Exception as e:
            print(f"[MAIN GUI] Bağlantı durumu güncelleme hatası: {e}")

    def _safe_error_update(self, error_message):
        """Thread-safe hata güncellemesi"""
        try:
            if hasattr(self, 'log_module'):
                self.log_module.add_log(f"HATA: {error_message}")
            if hasattr(self, 'status_module'):
                self.status_module.update_status("Raspberry Pi Hatası", "#ff0000")
        except Exception as e:
            print(f"[MAIN GUI] Hata işleme hatası: {e}")

    # ESKİ METODLARI DEVRE DIŞI BIRAK
    def _on_data_updated(self, data):
        """ESKİ VERSİYON - Artık kullanılmıyor"""
        pass

    def _on_log_added(self, log_entry):
        """ESKİ VERSİYON - Artık kullanılmıyor"""
        pass

    def _on_raspberry_connection_changed(self, connection_data):
        """ESKİ VERSİYON - Artık kullanılmıyor"""
        pass

    def _on_raspberry_error(self, error_message):
        """ESKİ VERSİYON - Artık kullanılmıyor"""
        pass
        
    def run(self):
        self.root.mainloop()

def main():
    """Ana uygulama"""
    try:
        # Aşama seçim penceresi
        phase_window = PhaseSelectionWindow()
        selected_phase = phase_window.run()
        
        # BURADA SORUN VAR - Düzeltme yapıldı
        if selected_phase is not None:  # None kontrolü eklendi
            print(f"[MAIN] Seçilen aşama: {selected_phase}")
            # Ana GUI'yi seçilen aşama ile başlat
            main_gui = SkyShieldMainGUI(selected_phase)
            main_gui.run()
        else:
            print("[MAIN] Aşama seçilmedi, uygulama kapatılıyor...")
    except KeyboardInterrupt:
        print("[MAIN] Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"[MAIN] Hata: {e}")
        import traceback
        traceback.print_exc()  # Detaylı hata mesajı

if __name__ == "__main__":
    main()