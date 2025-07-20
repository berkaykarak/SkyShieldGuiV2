import customtkinter as ctk
import tkinter as tk
import threading
import time
import math
import random
from controllers.Rasberrypi_Controller import RaspberryController
try:
    import numpy as np
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("[WARNING] OpenCV veya NumPy bulunamadı. Basit simülasyon kullanılacak.")

from PIL import Image, ImageTk
from datetime import datetime
from PIL import Image, ImageTk
import os                    # ← SkyShield logosunu yüklemek için

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





class CameraModule(BaseModule):
    """Profesyonel askeri kamera modülü"""
    def __init__(self, parent, phase):
        super().__init__(parent, f"KAMERA GÖRÜNTÜSÜ - AŞAMA {phase}")
        self.phase = phase
        self.camera_active = False
        self.target_locked = False
        self.target_x = 320
        self.target_y = 240
        self.setup_module()
        
    def setup_module(self):
        # Başlık kaldırıldı, direkt kamera alanı
        
        # Ana kamera container - Siyah askeri tema
        self.camera_container = ctk.CTkFrame(
            self.frame, 
            fg_color="#000000",  # Siyah arka plan
            corner_radius=0,
            border_width=2,
            border_color="#ffff00"  # Sarı çerçeve
        )
        self.camera_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Kamera canvas - askeri targeting sistemi
        self.camera_canvas = tk.Canvas(
            self.camera_container,
            bg="#000000",
            width=500,
            height=350,
            highlightthickness=0,
            bd=0
        )
        self.camera_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # İLK AÇILIŞTA KAMERA AKTİF OLSUN
        self.camera_active = True
        
        # Targeting crosshair ve overlay'leri başlat
        self.setup_targeting_system()
        
        # Alt durum çubuğu
        self.create_status_bar()
        
        # Kamera kontrolleri
        self.create_camera_controls()
        
        # Animasyon başlat
        self.start_targeting_animation()
        
    def setup_targeting_system(self):
        """Askeri targeting sistemi kuruşu"""
        canvas = self.camera_canvas
        
        # Ana crosshair (artı işareti) - Merkez
        canvas.create_line(250, 160, 250, 190, fill="#ffff00", width=2, tags="crosshair")
        canvas.create_line(235, 175, 265, 175, fill="#ffff00", width=2, tags="crosshair")
        
        # Köşe çerçeveleri (targeting brackets)
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
            
        # Hedef simülasyonu - Drone/Uçak
        self.create_target_drone()
        
    def create_target_drone(self):
        """3D Drone/Uçak simülasyonu"""
        canvas = self.camera_canvas
        
        # Drone gövdesi
        canvas.create_oval(
            self.target_x-15, self.target_y-8, 
            self.target_x+15, self.target_y+8, 
            fill="#888888", outline="#ffffff", width=2, tags="drone"
        )
        
        # Drone kanatları
        canvas.create_line(
            self.target_x-25, self.target_y, self.target_x+25, self.target_y,
            fill="#666666", width=4, tags="drone"
        )
        canvas.create_line(
            self.target_x, self.target_y-15, self.target_x, self.target_y+15,
            fill="#666666", width=3, tags="drone"
        )
        
        # Hedef kilidi çerçevesi
        if self.target_locked:
            canvas.create_rectangle(
                self.target_x-30, self.target_y-25,
                self.target_x+30, self.target_y+25,
                outline="#ff0000", width=2, tags="target_lock"
            )
            canvas.create_text(
                self.target_x, self.target_y-35,
                text="LOCKED", fill="#ff0000", 
                font=("Arial", 10, "bold"), tags="target_lock"
            )
        
    def create_status_bar(self):
        """Alt durum çubuğu - askeri sistem"""
        status_frame = ctk.CTkFrame(
            self.camera_container,
            fg_color="#1a1a1a",
            height=40
        )
        status_frame.pack(fill="x", side="bottom", padx=5, pady=5)
        status_frame.pack_propagate(False)
        
        # Sol - Sistem durumu
        left_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=10)
        
        self.status_icon = ctk.CTkLabel(
            left_frame,
            text="⚠️",
            font=ctk.CTkFont(size=16),
            text_color="#ffff00"
        )
        self.status_icon.pack(side="left", padx=5)
        
        self.status_text = ctk.CTkLabel(
            left_frame,
            text="SİSTEM DURUMU: Hedefe Kilitlendi",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffff00"
        )
        self.status_text.pack(side="left")
        
        # Sağ - Zaman ve mod
        right_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=10)
        
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M")
        
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
        
    def create_camera_controls(self):
        """Kamera kontrol butonları"""
        controls_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Kayıt butonu
        self.record_button = ctk.CTkButton(
            controls_frame,
            text="🔴 KAYIT BAŞLAT",
            width=120,
            height=30,
            fg_color="#cc0000",
            hover_color="#990000",
            command=self.toggle_recording
        )
        self.record_button.pack(side="left", padx=5)
        
        # Anlık görüntü
        self.snapshot_button = ctk.CTkButton(
            controls_frame,
            text="📸 SNAPSHOT",
            width=100,
            height=30,
            fg_color="#1f538d",
            command=self.take_snapshot
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
            command=self.toggle_target_lock
        )
        self.lock_button.pack(side="right", padx=5)
        
        self.recording = False
        
    def start_targeting_animation(self):
        """Targeting sistemi animasyonu"""
        self.animate_targeting()
        
    def animate_targeting(self):
        """Crosshair ve hedef animasyonu"""
        # Acil durdur kontrolü - animasyonu durdur
        if not self.camera_active:
            return
            
        if hasattr(self, 'camera_canvas'):
            canvas = self.camera_canvas
            
            # Hedef hareketi (sinüs dalgası)
            import math
            t = time.time()
            self.target_x = 250 + 50 * math.sin(t * 0.5)
            self.target_y = 175 + 30 * math.cos(t * 0.3)
            
            # Eski drone'u temizle
            canvas.delete("drone")
            canvas.delete("target_lock")
            
            # Yeni drone pozisyonu
            self.create_target_drone()
            
            # Koordinat güncelleme
            self.update_coordinates()
            
            # 100ms sonra tekrar animate et (sadece kamera aktifse)
            if self.camera_active:
                self.frame.after(100, self.animate_targeting)
            
    def update_coordinates(self):
        """Koordinat bilgilerini güncelle (soldaki panel için)"""
        try:
            # Ana GUI'deki koordinat modülünü güncelle
            if hasattr(self.parent.master.master, 'coords_module'):
                coords = self.parent.master.master.coords_module
                distance = ((self.target_x - 250)**2 + (self.target_y - 175)**2)**0.5
                pan_angle = (self.target_x - 250) * 0.2
                tilt_angle = -(self.target_y - 175) * 0.2
                
                coords.update_coordinates(
                    distance=f"{distance:.1f}",
                    pan=f"{pan_angle:.1f}",
                    tilt=f"{tilt_angle:.1f}",
                    speed="12.5"
                )
        except:
            pass
            
    def toggle_recording(self):
        """Kayıt başlat/durdur - GERÇEK video kayıt sistemi"""
        self.recording = not self.recording
        if self.recording:
            self.record_button.configure(
                text="⏹️ KAYIT DURDUR", 
                fg_color="#ff0000"
            )
            self.status_text.configure(text="SİSTEM DURUMU: 🔴 KAYIT AKTİF")
            self.status_icon.configure(text="🔴")
            
            # GERÇEK VIDEO KAYIT BAŞLAT
            self.start_video_recording()
            
        else:
            self.record_button.configure(
                text="🔴 KAYIT BAŞLAT", 
                fg_color="#cc0000"
            )
            self.status_text.configure(text="SİSTEM DURUMU: Hazır")
            self.status_icon.configure(text="⚠️")
            
            # GERÇEK VIDEO KAYDI DURDUR
            self.stop_video_recording()
    
    def start_video_recording(self):
        """Gerçek video kaydını başlat"""
        try:
            import os
            
            # Kayıt klasörü oluştur
            if not os.path.exists("recordings"):
                os.makedirs("recordings")
            
            # Dosya adı oluştur
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.video_filename = f"recordings/skyshield_video_{timestamp}.mp4"
            
            # Video writer oluştur
            if OPENCV_AVAILABLE:
                # MP4 codec kullan (daha uyumlu)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, 10.0, (500, 350))
                
                if not self.video_writer.isOpened():
                    # Alternatif codec dene
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    self.video_filename = f"recordings/skyshield_video_{timestamp}.avi"
                    self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, 10.0, (500, 350))
            
            # Kayıt frame listesi oluştur
            self.recorded_frames = []
            
            # Log sistemine kayıt başladığını yaz
            if hasattr(self.parent.master.master, 'log_module'):
                self.parent.master.master.log_module.add_log("📹 Video kaydı başlatıldı")
                self.parent.master.master.log_module.add_log(f"📁 Dosya: {self.video_filename}")
            
            # Kayıt zamanını başlat
            self.recording_start_time = time.time()
            self.update_recording_time()
            self.capture_frames()
            
        except Exception as e:
            print(f"[RECORDING] Kayıt başlatma hatası: {e}")
            if hasattr(self.parent.master.master, 'log_module'):
                self.parent.master.master.log_module.add_log(f"❌ Kayıt hatası: {e}")
    
    def capture_frames(self):
        """Canvas'tan frame yakala ve kaydet"""
        if self.recording:
            try:
                # Canvas'ı bitmap olarak yakala (Windows uyumlu)
                x = self.camera_canvas.winfo_rootx()
                y = self.camera_canvas.winfo_rooty()
                width = self.camera_canvas.winfo_width()
                height = self.camera_canvas.winfo_height()
                
                # PIL ile ekran görüntüsü al
                from PIL import ImageGrab
                screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
                
                # Boyutu ayarla
                screenshot = screenshot.resize((500, 350))
                
                if OPENCV_AVAILABLE and hasattr(self, 'video_writer'):
                    # PIL'den OpenCV formatına çevir
                    import numpy as np
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Video'ya frame ekle
                    self.video_writer.write(frame)
                else:
                    # OpenCV yoksa frame'leri listeye kaydet
                    self.recorded_frames.append(screenshot)
                
                # 100ms sonra tekrar yakala (10 FPS)
                if self.recording:
                    self.frame.after(100, self.capture_frames)
                    
            except Exception as e:
                print(f"[RECORDING] Frame yakalama hatası: {e}")
                # Hata durumunda 200ms bekle ve tekrar dene
                if self.recording:
                    self.frame.after(200, self.capture_frames)
    
    def stop_video_recording(self):
        """Gerçek video kaydını durdur"""
        try:
            if OPENCV_AVAILABLE and hasattr(self, 'video_writer'):
                # OpenCV video writer'ı kapat
                self.video_writer.release()
                delattr(self, 'video_writer')
            elif hasattr(self, 'recorded_frames') and self.recorded_frames:
                # OpenCV yoksa GIF olarak kaydet
                self.video_filename = self.video_filename.replace('.mp4', '.gif').replace('.avi', '.gif')
                self.recorded_frames[0].save(
                    self.video_filename, 
                    save_all=True, 
                    append_images=self.recorded_frames[1:], 
                    duration=100, 
                    loop=0
                )
                self.recorded_frames.clear()
            
            # Log sistemine kayıt durdu yazısını yaz
            if hasattr(self.parent.master.master, 'log_module'):
                duration = int(time.time() - self.recording_start_time)
                self.parent.master.master.log_module.add_log(f"⏹️ Video kaydı durduruldu (Süre: {duration}s)")
                self.parent.master.master.log_module.add_log(f"💾 Video kaydedildi: {self.video_filename}")
                
                # Dosya boyutunu göster
                import os
                if os.path.exists(self.video_filename):
                    size_mb = os.path.getsize(self.video_filename) / (1024*1024)
                    self.parent.master.master.log_module.add_log(f"📊 Dosya boyutu: {size_mb:.2f} MB")
                
        except Exception as e:
            print(f"[RECORDING] Kayıt durdurma hatası: {e}")
            if hasattr(self.parent.master.master, 'log_module'):
                self.parent.master.master.log_module.add_log(f"❌ Kayıt durdurma hatası: {e}")
    
    def update_recording_time(self):
        """Kayıt süresini güncelle"""
        if self.recording and hasattr(self, 'recording_start_time'):
            duration = int(time.time() - self.recording_start_time)
            minutes = duration // 60
            seconds = duration % 60
            self.status_text.configure(text=f"SİSTEM DURUMU: 🔴 KAYIT {minutes:02d}:{seconds:02d}")
            
            # Her saniye güncelle
            self.frame.after(1000, self.update_recording_time)
            
    def take_snapshot(self):
        """Anlık görüntü al - GERÇEK PNG screenshot"""
        try:
            import os
            from PIL import ImageGrab
            
            # Screenshot klasörü oluştur
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            # Buton animasyonu
            self.snapshot_button.configure(text="📸 KAYDEDILIYOR...", fg_color="#ff9800")
            
            # Timestamp oluştur
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/skyshield_snapshot_{timestamp}.png"
            
            # Canvas'ın ekran pozisyonunu al
            x = self.camera_canvas.winfo_rootx()
            y = self.camera_canvas.winfo_rooty()
            width = self.camera_canvas.winfo_width()
            height = self.camera_canvas.winfo_height()
            
            # Ekran görüntüsü al
            screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
            screenshot.save(filename, "PNG")
            
            # Log sistemine ekle
            if hasattr(self.parent.master.master, 'log_module'):
                self.parent.master.master.log_module.add_log(f"📸 Anlık görüntü alındı")
                self.parent.master.master.log_module.add_log(f"💾 Dosya: {filename}")
                self.parent.master.master.log_module.add_log(f"📍 Hedef konumu: X:{self.target_x:.0f}, Y:{self.target_y:.0f}")
                
                # Dosya boyutunu göster
                if os.path.exists(filename):
                    size_kb = os.path.getsize(filename) / 1024
                    self.parent.master.master.log_module.add_log(f"📊 Dosya boyutu: {size_kb:.1f} KB")
            
            # Buton durumunu eski haline getir
            self.frame.after(1500, lambda: self.snapshot_button.configure(
                text="📸 SAVED! ✓", fg_color="#00cc44"
            ))
            self.frame.after(3000, lambda: self.snapshot_button.configure(
                text="📸 SNAPSHOT", fg_color="#1f538d"
            ))
            
        except Exception as e:
            print(f"[SNAPSHOT] Screenshot hatası: {e}")
            if hasattr(self.parent.master.master, 'log_module'):
                self.parent.master.master.log_module.add_log(f"❌ Screenshot hatası: {e}")
            
            # Hata durumunda buton durumunu eski haline getir
            self.frame.after(1000, lambda: self.snapshot_button.configure(
                text="📸 SNAPSHOT", fg_color="#1f538d"
            ))
        
    def toggle_target_lock(self):
        """Hedef kilidi aç/kapat"""
        self.target_locked = not self.target_locked
        if self.target_locked:
            self.lock_button.configure(
                text="🔓 UNLOCK", 
                fg_color="#00cc44"
            )
            self.status_text.configure(text="SİSTEM DURUMU: Hedefe Kilitlendi")
            self.status_icon.configure(text="🎯")
        else:
            self.lock_button.configure(
                text="🎯 TARGETİNG", 
                fg_color="#ff9800"
            )
            self.status_text.configure(text="SİSTEM DURUMU: Hedef Aranıyor")
            self.status_icon.configure(text="🔍")

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

   
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", padx=10, pady=(0, 0))
        header_frame.pack_propagate(True)

        header_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        header_frame.grid_rowconfigure(0, weight=1)

        logo_path = os.path.join("assets", "skyshield_logo.jpg")
        if os.path.exists(logo_path):
            img = Image.open(logo_path).resize((100, 100))
            self.small_logo_img = ImageTk.PhotoImage(img)
            logo_lbl = ctk.CTkLabel(header_frame, image=self.small_logo_img, text="")
            logo_lbl.grid(row=0, column=2, sticky="ne", padx=5, pady=5)

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

        self.setup_main_gui()
        self.setup_modules()
        # Raspberry Pi kontrolcüsü
        self.raspberry = RaspberryController()
        self.raspberry.start_connection()
        

        
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

    
    def _darker(self, hex_color, factor=0.85):
        """Verilen hex rengin daha koyu tonunu döndürür"""
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(int(c * factor) for c in rgb)
        return "#%02x%02x%02x" % darker_rgb    
    
        
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
        
        # Orta panel - Kamera (Askeri targeting sistemi)
        center_frame = ctk.CTkFrame(self.content_frame, fg_color="#000000")
        center_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.camera_module = CameraModule(center_frame, self.phase)
        self.camera_module.pack(fill="both", expand=True, padx=5, pady=5)
        
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
        
    def start_system(self):
            # İLK DEFA sistem modunu gönder
        self.raspberry.update_system_mode(self.phase)
        
        # Sistem aktif durumunu gönder
        self.raspberry.update_system_active(True)
        
        # Aşamaya göre özel komut
        if self.phase > 0:
            self.raspberry.send_phase_command(self.phase)
    
   
        self.status_module.update_status("Sistem Aktif", "#00ff88")
        self.log_module.add_log("Sistem başlatıldı")
        
    def stop_system(self):
        self.raspberry.update_system_active(False)
        self.status_module.update_status("Sistem Durduruldu", "#ff6666")
        self.log_module.add_log("Sistem durduruldu")
        
    def emergency_stop(self):
        # Acil durdur butonu titreme efekti
        self.emergency_button.configure(fg_color="#ff0000", text="🚨 ACTİVE! 🚨")
        
        # TÜM SİSTEMLERİ DURDUR
        self._stop_all_systems()
        
        # Uyarı popup'ı oluştur
        self.create_emergency_popup()
        
        # Sistem durumunu güncelle
        self.status_module.update_status("ACİL DURDUR AKTİVE!", "#ff0000")
        self.log_module.add_log("⚠️ ACİL DURDUR AKTİVE EDİLDİ!")
        
        # 15 saniye geri sayım başlat
        self.start_emergency_countdown()
    
    def _stop_all_systems(self):
        """Acil durdurma - Tüm sistemleri durdur"""
        try:
            # Kamera animasyonlarını durdur
            if hasattr(self, 'camera_module'):
                self.camera_module.camera_active = False
                self.camera_module.target_locked = False
                
                # Kamera canvas'ını temizle ve durduruldu mesajı göster
                if hasattr(self.camera_module, 'camera_canvas'):
                    canvas = self.camera_module.camera_canvas
                    canvas.delete("all")  # Tüm animasyonları temizle
                    
                    # ACİL DURDUR mesajı
                    canvas.create_rectangle(0, 0, 500, 350, fill="#ff0000", outline="#ffffff", width=3)
                    canvas.create_text(250, 150, text="🚨 ACİL DURDUR 🚨", 
                                     fill="#ffffff", font=("Arial", 24, "bold"))
                    canvas.create_text(250, 200, text="TÜM SİSTEMLER DURDURULDU", 
                                     fill="#ffffff", font=("Arial", 14, "bold"))
                
                # Kamera kontrollerini devre dışı bırak
                if hasattr(self.camera_module, 'record_button'):
                    self.camera_module.record_button.configure(state="disabled")
                if hasattr(self.camera_module, 'snapshot_button'):
                    self.camera_module.snapshot_button.configure(state="disabled")
                if hasattr(self.camera_module, 'lock_button'):
                    self.camera_module.lock_button.configure(state="disabled")
                
                # Durum çubuğunu güncelle
                if hasattr(self.camera_module, 'status_text'):
                    self.camera_module.status_text.configure(text="SİSTEM DURUMU: ACİL DURDUR AKTİVE")
                if hasattr(self.camera_module, 'status_icon'):
                    self.camera_module.status_icon.configure(text="🚨")
            
            # Sistem durumunu güncelle
            if hasattr(self, 'status_module'):
                self.status_module.update_progress(0.0)  # Progress bar'ı sıfırla
            
            self.log_module.add_log("🛑 Kamera sistemleri durduruldu")
            self.log_module.add_log("🛑 Hedef takip sistemleri devre dışı")
            self.log_module.add_log("🛑 Animasyonlar durduruldu")
            
        except Exception as e:
            print(f"[EMERGENCY] Sistem durdurma hatası: {e}")
            self.log_module.add_log(f"❌ Sistem durdurma hatası: {e}")
    
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
    
    def _restart_all_systems(self):
        """Acil durumdan sonra sistemleri yeniden başlat"""
        try:
            # Kamera sistemlerini yeniden başlat
            if hasattr(self, 'camera_module'):
                self.camera_module.camera_active = True
                
                # Canvas'ı temizle ve animasyonları yeniden başlat
                if hasattr(self.camera_module, 'camera_canvas'):
                    canvas = self.camera_module.camera_canvas
                    canvas.delete("all")
                    
                    # Targeting sistemini yeniden kur
                    self.camera_module.setup_targeting_system()
                    
                    # Animasyonu yeniden başlat
                    self.camera_module.start_targeting_animation()
                
                # Kamera kontrollerini yeniden etkinleştir
                if hasattr(self.camera_module, 'record_button'):
                    self.camera_module.record_button.configure(state="normal")
                if hasattr(self.camera_module, 'snapshot_button'):
                    self.camera_module.snapshot_button.configure(state="normal")
                if hasattr(self.camera_module, 'lock_button'):
                    self.camera_module.lock_button.configure(state="normal")
                
                # Durum çubuğunu güncelle
                if hasattr(self.camera_module, 'status_text'):
                    self.camera_module.status_text.configure(text="SİSTEM DURUMU: Hazır")
                if hasattr(self.camera_module, 'status_icon'):
                    self.camera_module.status_icon.configure(text="⚠️")
            
            self.log_module.add_log("🟢 Kamera sistemleri yeniden başlatıldı")
            self.log_module.add_log("🟢 Hedef takip sistemleri aktif")
            self.log_module.add_log("🟢 Animasyonlar yeniden başladı")
            
        except Exception as e:
            print(f"[RESTART] Sistem yeniden başlatma hatası: {e}")
            self.log_module.add_log(f"❌ Sistem yeniden başlatma hatası: {e}")
    
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