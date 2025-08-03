import traceback
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
        Her aşamanın kendi rengiyle çerçeve
        """
        # Kart çerçevesini grid ile yerleştir
        card = ctk.CTkFrame(
            parent,
            fg_color="#2a2a2a",  # İç koyu renk
            corner_radius=12,
            border_width=2,
            border_color=phase_info["color"]  # ← Her aşamanın kendi rengi
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
    """Hedef bilgileri modülü - PHASE-SPECIFIC DYNAMIC DATA"""
    def __init__(self, parent, phase):
        super().__init__(parent, "HEDEF BİLGİLERİ")
        self.phase = phase
        
        # Dinamik label'ları saklamak için
        self.dynamic_labels = {}
        
        self.setup_module()
        
    def setup_module(self):
        self.create_title()
        
        if self.phase == 0:  
            self.create_manual_mode_info()
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
            text="🎮 Controller: Kontrol Ediliyor...",
            font=ctk.CTkFont(size=12),
            text_color="#ffaa00"
        )
        self.controller_status.pack(pady=2)
        
        self.control_mode = ctk.CTkLabel(
            self.frame,
            text="Kontrol: Manuel",
            font=ctk.CTkFont(size=12),
            text_color="#00ccff"
        )
        self.control_mode.pack(pady=2)
    
    def create_phase1_info(self):
        """Aşama 1: Dinamik balon bilgileri"""
        # Tespit Edilen Balonlar
        self.dynamic_labels['targets_detected'] = ctk.CTkLabel(
            self.frame,
            text="Tespit Edilen Balon: 0",
            font=ctk.CTkFont(size=12)
        )
        self.dynamic_labels['targets_detected'].pack(pady=2)
        
        # İmha Edilen Balonlar
        self.dynamic_labels['targets_destroyed'] = ctk.CTkLabel(
            self.frame,
            text="İmha Edilen: 0",
            font=ctk.CTkFont(size=12),
            text_color="#00ff88"
        )
        self.dynamic_labels['targets_destroyed'].pack(pady=2)
        
        # Aktif Balon Sayısı
        self.dynamic_labels['balloon_count'] = ctk.CTkLabel(
            self.frame,
            text="Aktif Balon: 0",
            font=ctk.CTkFont(size=12),
            text_color="#ffaa00"
        )
        self.dynamic_labels['balloon_count'].pack(pady=2)
        
        # Başarı Oranı (hesaplanacak)
        self.dynamic_labels['success_rate'] = ctk.CTkLabel(
            self.frame,
            text="Başarı Oranı: 0%",
            font=ctk.CTkFont(size=12),
            text_color="#00ccff"
        )
        self.dynamic_labels['success_rate'].pack(pady=2)
        
    def create_phase2_info(self):
        """Aşama 2: Dinamik düşman/dost ayrımı bilgileri"""
        # Dost Hedefler
        self.dynamic_labels['friend_targets'] = ctk.CTkLabel(
            self.frame,
            text="Dost Hedef: 0",
            font=ctk.CTkFont(size=12),
            text_color="#00ff88"
        )
        self.dynamic_labels['friend_targets'].pack(pady=2)
        
        # Düşman Hedefler  
        self.dynamic_labels['enemy_targets'] = ctk.CTkLabel(
            self.frame,
            text="Düşman Hedef: 0",
            font=ctk.CTkFont(size=12),
            text_color="#ff4444"
        )
        self.dynamic_labels['enemy_targets'].pack(pady=2)
        
        # İmha Edilen Düşman
        self.dynamic_labels['enemy_destroyed'] = ctk.CTkLabel(
            self.frame,
            text="İmha Edilen Düşman: 0",
            font=ctk.CTkFont(size=12),
            text_color="#ffaa00"
        )
        self.dynamic_labels['enemy_destroyed'].pack(pady=2)
        
        
        
    # main_window.py'de TargetInfoModule içindeki değişiklikler - SADECE target_side

    
    def create_phase3_info(self):
        """Aşama 3: SADECE target_side kullan - current_platform kaldırıldı"""
        
        # Target Side (EN ÖNEMLİ - en üstte ve kalın)
        self.dynamic_labels['target_side'] = ctk.CTkLabel(
            self.frame,
            text="Platform: A",
            font=ctk.CTkFont(size=13, weight="bold"),  # Daha büyük ve kalın
            text_color="#00ccff"
        )
        self.dynamic_labels['target_side'].pack(pady=3)
        
        # Hedef Renk
        self.dynamic_labels['target_color'] = ctk.CTkLabel(
            self.frame,
            text="Hedef Renk: Bilinmiyor",
            font=ctk.CTkFont(size=12)
        )
        self.dynamic_labels['target_color'].pack(pady=2)
        
        # Hedef Şekil
        self.dynamic_labels['target_shape'] = ctk.CTkLabel(
            self.frame,
            text="Hedef Şekil: Bilinmiyor",
            font=ctk.CTkFont(size=12)
        )
        self.dynamic_labels['target_shape'].pack(pady=2)

        self.dynamic_labels['engagement_authorized'] = ctk.CTkLabel(
            self.frame,
            text="Angajman: ❌ Yetkisiz",
            font=ctk.CTkFont(size=12),
            text_color="#ff6b6b"
        )
        self.dynamic_labels['engagement_authorized'].pack(pady=2)

    def update_controller_status(self, data):
        """Controller bağlantı durumunu güncelle - Sadece Aşama 0 için"""
        if self.phase != 0:
            return
        
        if data.get('controller_connected') is True:
            self.controller_status.configure(
                text="🎮 Controller: Bağlı",
                text_color="#00ff88"
            )
        else:
            self.controller_status.configure(
                text="🎮 Controller: Bağlı Değil", 
                text_color="#ff6b6b"
            )
    
    # main_window.py içindeki TargetInfoModule.update_phase_data metodunda düzeltme

    def update_phase_data(self, data):
        """FIXED: Aşama-spesifik verileri güncelle - Color & Shape Display Fix"""
        try:
            
            if self.phase == 1:
                # AŞAMA 1 GÜNCELLEMELERİ
                if 'targets_detected' in data:
                    value = data['targets_detected']
                    if 'targets_detected' in self.dynamic_labels:
                        self.dynamic_labels['targets_detected'].configure(
                            text=f"Tespit Edilen Balon: {value}"
                        )
                
                if 'targets_destroyed' in data:
                    value = data['targets_destroyed']
                    if 'targets_destroyed' in self.dynamic_labels:
                        self.dynamic_labels['targets_destroyed'].configure(
                            text=f"İmha Edilen: {value}"
                        )
                    
                if 'balloon_count' in data:
                    value = data['balloon_count']
                    if 'balloon_count' in self.dynamic_labels:
                        self.dynamic_labels['balloon_count'].configure(
                            text=f"Aktif Balon: {value}"
                        )
                
                # Başarı oranını hesapla
                detected = data.get('targets_detected', 0)
                destroyed = data.get('targets_destroyed', 0)
                if detected > 0 and 'success_rate' in self.dynamic_labels:
                    success_rate = (destroyed / detected) * 100
                    self.dynamic_labels['success_rate'].configure(
                        text=f"Başarı Oranı: {success_rate:.1f}%"
                    )
            
            elif self.phase == 2:
                # AŞAMA 2 GÜNCELLEMELERİ
                if 'friend_targets' in data and 'friend_targets' in self.dynamic_labels:
                    value = data['friend_targets']
                    self.dynamic_labels['friend_targets'].configure(
                        text=f"Dost Hedef: {value}"
                    )
                
                if 'enemy_targets' in data and 'enemy_targets' in self.dynamic_labels:
                    value = data['enemy_targets']
                    self.dynamic_labels['enemy_targets'].configure(
                        text=f"Düşman Hedef: {value}"
                    )
                
                if 'enemy_destroyed' in data and 'enemy_destroyed' in self.dynamic_labels:
                    value = data['enemy_destroyed']
                    self.dynamic_labels['enemy_destroyed'].configure(
                        text=f"İmha Edilen Düşman: {value}"
                    )
                
                if 'classification_accuracy' in data and 'classification_accuracy' in self.dynamic_labels:
                    accuracy = data['classification_accuracy']
                    color = "#00ff88" if accuracy > 90 else "#ffaa00" if accuracy > 70 else "#ff6b6b"
                    self.dynamic_labels['classification_accuracy'].configure(
                        text=f"Tanıma Doğruluğu: {accuracy:.1f}%",
                        text_color=color
                    )
            
            elif self.phase == 3:
                # AŞAMA 3 GÜNCELLEMELERİ - COLOR & SHAPE FIX

                # 🅰️🅱️ Target Side güncelleme (çalışıyor)
                if 'target_side' in data and 'target_side' in self.dynamic_labels:
                    target_side = data['target_side']
                    side_display = {
                        'A': '🅰️ A Tarafı',
                        'B': '🅱️ B Tarafı'
                    }
                    side_color = {
                        'A': '#00ff88',  # Yeşil
                        'B': '#ff8844'   # Turuncu
                    }
                    
                    display_text = side_display.get(target_side, f"❓ {target_side}")
                    text_color = side_color.get(target_side, '#cccccc')
                    
                    self.dynamic_labels['target_side'].configure(
                        text=f"Platform: {display_text}",
                        text_color=text_color
                    )

                # 🔴 TARGET COLOR FIX - Hem WebSocket formatını hem GUI formatını destekle
                if 'target_color' in data and 'target_color' in self.dynamic_labels:
                    color_value = data['target_color']
                    
                    # ✅ ÇOKLU FORMAT DESTEĞİ
                    color_display_map = {
                        # WebSocket Server formatı (R/G/B)
                        'R': ('🔴 Kırmızı', '#ff4444'),
                        'G': ('🟢 Yeşil', '#44ff44'),
                        'B': ('🔵 Mavi', '#4488ff'),
                        
                        # GUI formatı (full names)
                        'red': ('🔴 Kırmızı', '#ff4444'),
                        'green': ('🟢 Yeşil', '#44ff44'),
                        'blue': ('🔵 Mavi', '#4488ff'),
                        
                        # Diğer renkler
                        'yellow': ('🟡 Sarı', '#ffff44'),
                        'orange': ('🟠 Turuncu', '#ff8844'),
                        'purple': ('🟣 Mor', '#8844ff'),
                        'unknown': ('❓ Bilinmiyor', '#cccccc')
                    }
                    
                    # Color mapping'i uygula
                    if color_value in color_display_map:
                        display_text, text_color = color_display_map[color_value]
                    else:
                        # Hiçbir format eşleşmezse, raw değeri göster
                        display_text = f"❓ {color_value}"
                        text_color = '#cccccc'
                    
                    self.dynamic_labels['target_color'].configure(
                        text=f"Hedef Renk: {display_text}",
                        text_color=text_color
                    )
                    
                    print(f"[GUI] Color güncellendi: '{color_value}' → '{display_text}'")
                
                # 🔵 TARGET SHAPE FIX - Hem WebSocket formatını hem GUI formatını destekle
                if 'target_shape' in data and 'target_shape' in self.dynamic_labels:
                    shape_value = data['target_shape']
                    
                    # ✅ ÇOKLU FORMAT DESTEĞİ
                    shape_display_map = {
                        # WebSocket Server formatı (T/C/S)
                        'T': '🔺 Üçgen',
                        'C': '⭕ Daire', 
                        'S': '🟫 Kare',
                        
                        # GUI formatı (full names)
                        'triangle': '🔺 Üçgen',
                        'circle': '⭕ Daire',
                        'square': '🟫 Kare',
                        
                        # Diğer şekiller
                        'rectangle': '🟫 Dikdörtgen',
                        'unknown': '❓ Bilinmiyor'
                    }
                    
                    # Shape mapping'i uygula
                    if shape_value in shape_display_map:
                        display_text = shape_display_map[shape_value]
                    else:
                        # Hiçbir format eşleşmezse, raw değeri göster
                        display_text = f"❓ {shape_value}"
                    
                    self.dynamic_labels['target_shape'].configure(
                        text=f"Hedef Şekil: {display_text}"
                    )
                    
                    print(f"[GUI] Shape güncellendi: '{shape_value}' → '{display_text}'")

                # QR kod ve angajman (bunlar çalışıyor)
                if 'qr_code_detected' in data and 'qr_code_detected' in self.dynamic_labels:
                    qr_detected = data['qr_code_detected']
                    if qr_detected:
                        self.dynamic_labels['qr_code_detected'].configure(
                            text="QR Kod: ✅ Tespit Edildi",
                            text_color="#00ff88"
                        )
                    else:
                        self.dynamic_labels['qr_code_detected'].configure(
                            text="QR Kod: ❌ Tespit Edilmedi",
                            text_color="#ff6b6b"
                        )
                
                if 'engagement_authorized' in data and 'engagement_authorized' in self.dynamic_labels:
                    authorized = data['engagement_authorized']
                    if authorized:
                        self.dynamic_labels['engagement_authorized'].configure(
                            text="Angajman: ✅ Yetkili",
                            text_color="#00ff88"
                        )
                    else:
                        self.dynamic_labels['engagement_authorized'].configure(
                            text="Angajman: ❌ Yetkisiz",
                            text_color="#ff6b6b"
                        )
            
        except Exception as e:
            print(f"[GUI] update_phase_data hatası: {e}")
            import traceback
            traceback.print_exc()


class CoordinatesModule(BaseModule):
    """Koordinat bilgileri modülü"""
    def __init__(self, parent):
        super().__init__(parent, "KOORDİNATLAR")
        self.setup_module()
        
    def setup_module(self):
        self.create_title()
        
        self.coord_labels = {}
        coord_data = [
            #("Mesafe", "-- m"),
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
        self.app_controller = None  # EKLE
        self.manual_locked = False  # YENİ: Manuel seçim kilidi

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
        """Kontrol modu değiştir - BIG LOGGING"""
        old_mode = getattr(self, 'control_mode', 'Unknown')
        self.control_mode = mode
        
        # ✅ BÜYÜK VE GÖRÜNÜR LOG
        print(f"\n{'+'*50}")
        print(f"🔄 MODE CHANGE: {old_mode} → {mode}")
        print(f"{'+'*50}")
        
        if mode == "Otomatik":
            self.selected_weapon = "Lazer"
            print(f"🎯 Otomatik mod: Varsayılan Lazer seçildi")
            
            if self.app_controller:
                self.app_controller.send_command("select_weapon", "Lazer")
                
        else:  # Manuel mod
            if not hasattr(self, 'selected_weapon') or not self.selected_weapon:
                self.selected_weapon = "Lazer"
                
            print(f"✋ Manuel mod: Seçili silah = {self.selected_weapon}")
            
            if self.app_controller:
                self.app_controller.send_command("select_weapon", self.selected_weapon)
        
        self.update_weapon_selection(self.selected_weapon)
        self.update_weapon_status()

    def set_manual_weapon(self, weapon):
        """Manuel silah seçimi - BIG LOGGING"""
        if self.control_mode == "Manuel":
            self.selected_weapon = weapon
            self.update_weapon_selection(weapon)
            self.update_weapon_status()
            
            # ✅ BÜYÜK VE GÖRÜNÜR LOG
            print(f"\n{'*'*50}")
            print(f"🎮 GUI WEAPON SELECTION: {weapon}")
            print(f"🎮 Control Mode: {self.control_mode}")
            print(f"{'*'*50}")
            
            if self.app_controller:
                self.app_controller.send_command("select_weapon", weapon)
            
            print(f"[WEAPON] Manuel silah seçildi: {weapon}")

    def debug_current_selection(self):
        """Debug için mevcut silah seçimini yazdır"""
        print(f"\n[WEAPON DEBUG] 🔫 Mevcut Durum:")
        print(f"   Kontrol Modu: {self.control_mode}")
        print(f"   Seçili Silah: {self.selected_weapon}")
        print(f"   App Controller: {'Var' if self.app_controller else 'Yok'}")

    def update_weapon_selection(self, weapon_type):
        self.weapon_label.configure(text=f"Seçili: {weapon_type}")

    def update_weapon_status(self):
        laser_active = self.selected_weapon == "Lazer"
        pellet_active = self.selected_weapon == "Boncuk"

        self.laser_status_btn.configure(text_color="#00ff88" if laser_active else "#888888")
        self.pellet_status_btn.configure(text_color="#00ff88" if pellet_active else "#888888")

    def lock_manual_selection(self):
        """Manuel seçimi kilitle - Raspberry Pi güncellemelerini engelle"""
        self.manual_locked = True
        print(f"[WEAPON] Manuel seçim kilitlendi: {self.selected_weapon}")

    def unlock_manual_selection(self):
        """Manuel seçim kilidini aç"""
        self.manual_locked = False
        print("[WEAPON] Manuel seçim kilidi açıldı")

    def is_manual_locked(self):
        """Manuel seçim kilitli mi kontrol et"""
        return getattr(self, 'manual_locked', False)




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
        
        # Hedef pozisyonu
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
        self._frame_counter = 0
        
        # Boyutlar belirlendi mi?
        self.dimensions_set = False
        self.display_width = None
        self.display_height = None
        
        self.setup_ui()
        self._register_app_callbacks()
        
        print(f"[CAMERA MODULE] Oluşturuldu - Aşama {phase}")
    
    def setup_ui(self):
        """Kamera modülü UI'ını oluştur"""
        # Ana kamera container - padding yok
        self.camera_container = ctk.CTkFrame(
            self.parent, 
            fg_color="#000000",
            corner_radius=0,
            border_width=2,
            border_color="#ffff00"
        )
        self.camera_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Kamera görüntü alanı - direkt container'a yapış
        self.camera_label = ctk.CTkLabel(
            self.camera_container,
            text="",
            fg_color="#000000",
            corner_radius=0
        )
        # İlk boyut ayarı - sonra pack
        self.camera_label.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Alt durum çubuğu
        self._create_status_bar()
        
        # Kamera kontrolleri
        self._create_camera_controls()
        
        # Boyutları hesapla (GUI tamamen yüklendikten sonra)
        self.parent.after(100, self._calculate_display_dimensions)
        
        print("[CAMERA MODULE] UI oluşturuldu")
    

    def _calculate_display_dimensions(self):
        """Görüntü boyutlarını hesapla"""
        if self.dimensions_set:
            return
            
        # Container'ın gerçek boyutlarını al
        self.parent.update_idletasks()
        
        total_width = self.camera_container.winfo_width()
        total_height = self.camera_container.winfo_height()
        
        # Kontroller ve durum çubuğu için alan çıkar
        # Border (2*2) + minimal padding (2*2) = 8 pixel
        self.display_width = total_width - 8
        
        # Status bar (~40) + controls (~40) + border (4) + padding (4) = ~88
        self.display_height = total_height - 88
        
        # Minimum kontrol
        if self.display_width < 100 or self.display_height < 100:
            # Varsayılan boyutlar
            self.display_width = 735
            self.display_height = 490
        
        self.dimensions_set = True
        print(f"[CAMERA MODULE] Display boyutları: {self.display_width}x{self.display_height}")
        
        # Default frame'i bu boyutlarda oluştur
        self._create_default_frame()

    def _set_fixed_dimensions(self):
        """Sabit boyutları bir kere belirle"""
        # Container'ın ilk boyutlarını al
        container_width = self.camera_container.winfo_width()
        container_height = self.camera_container.winfo_height()
        
        # Kontroller için alan çıkar
        self.fixed_width = container_width - 10
        self.fixed_height = container_height - 130  # Durum çubuğu + kontroller
        
        # Minimum boyutlar
        if self.fixed_width < 500:
            self.fixed_width = 700
        if self.fixed_height < 350:
            self.fixed_height = 450
        
        print(f"[CAMERA MODULE] Sabit boyutlar belirlendi: {self.fixed_width}x{self.fixed_height}")
    
    
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
            if not self.dimensions_set:
                return
                
            # Display boyutlarında siyah frame
            img = Image.new('RGB', (self.display_width, self.display_height), color='black')
            
            # Metin ekle
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            text = "GÖRÜNTÜ YOK"
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Metni ortala
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.display_width - text_width) // 2
            y = (self.display_height - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            
            # PhotoImage oluştur ve göster
            self.current_frame = ImageTk.PhotoImage(img)
            self.camera_label.configure(image=self.current_frame)
            self.camera_label.image = self.current_frame
            
            self.default_frame_created = True
            
        except Exception as e:
            print(f"[CAMERA MODULE] Default frame hatası: {e}")
    


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
    
    # UpdatedCameraModule için basit tam ekran çözümü

    def _on_frame_received(self, frame_data):
        """Raspberry Pi'den frame alındığında"""
        try:
            # Boyutlar henüz belirlenmemişse bekle
            if not self.dimensions_set or not self.display_width or not self.display_height:
                return
                
            if not hasattr(self, 'camera_label') or not self.camera_label:
                return
                
            if isinstance(frame_data, np.ndarray):
                # NumPy array'i PIL Image'a çevir
                pil_image = Image.fromarray(frame_data)
                
                # Tam olarak display boyutlarına sığdır
                pil_image = pil_image.resize(
                    (self.display_width, self.display_height), 
                    Image.Resampling.LANCZOS
                )
                
                # Tkinter PhotoImage'a çevir
                photo_image = ImageTk.PhotoImage(pil_image)
                
                # Label'ı güncelle (thread-safe)
                def update_label():
                    try:
                        if self.camera_label and self.camera_label.winfo_exists():
                            self.camera_label.configure(image=photo_image)
                            self.camera_label.image = photo_image
                            self.current_frame = photo_image
                    except:
                        pass
                
                # Main thread'de güncelle
                if self.parent.winfo_exists():
                    self.parent.after(0, update_label)
                
                # Frame sayacı
                self._frame_counter += 1
                
        except Exception as e:
            if self._frame_counter % 100 == 0:  # Her 100 frame'de bir hata logla
                print(f"[CAMERA MODULE] Frame işleme hatası: {e}")

    def _update_frame_safe(self, photo_image):
        """Thread-safe frame güncelleme"""
        try:
            if hasattr(self, 'camera_label') and self.camera_label:
                self.camera_label.configure(image=photo_image)
                self.camera_label.image = photo_image
        except:
            pass
    
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
        status_frame.pack(fill="x", side="bottom", padx=2, pady=2)
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
        
        # Zaman güncelleme
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
        controls_frame = ctk.CTkFrame(self.camera_container, fg_color="transparent", height=35)
        controls_frame.pack(fill="x", padx=5, pady=2)
        controls_frame.pack_propagate(False)
        
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
        self.app_controller = None  # BU SATIRI EKLE
        

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
        """Aşama 1 kontrolleri - Sadece temel kontroller"""
        # Aşama 1'de özel buton yok, sadece ortak kontrollere (ateş + kalibrasyon) sahip
        pass
            
    def create_phase2_controls(self):
        """Aşama 2 kontrolleri - Sadece kalibrasyon"""
        # Aşama 2'de özel buton yok, sadece ortak kontrollerden kalibrasyon
        pass
            
            
    def create_phase3_controls(self):
            """Aşama 3 kontrolleri - QR CODE & ENGAGEMENT"""
            
            # Angajman başlat
            self.engagement_button = ctk.CTkButton(
                self.frame,
                text="⚡ ANGAJMAN BAŞLAT",
                fg_color="#F44336",
                hover_color="#D32F2F",
                height=40,
                command=self.start_engagement
            )
            self.engagement_button.pack(fill="x", padx=10, pady=5)
            
    def create_common_controls(self):
        """Ortak kontroller"""
        # Ateş butonu - Sadece Aşama 0 ve 1'de
        if self.phase in [0, 1]:  # Sadece Aşama 0 ve 1'de ateş butonu
            self.fire_button = ctk.CTkButton(
                self.frame,
                text="🔥 ATEŞ!",
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#ff4444",
                hover_color="#cc3333",
                height=50,
                command=self.fire_weapon
            )
            self.fire_button.pack(fill="x", padx=10, pady=10)
        
        # Kalibrasyon - Tüm aşamalarda
        calibrate_button = ctk.CTkButton(
            self.frame,
            text="🔧 KALİBRASYON",
            fg_color="#4499ff",
            hover_color="#3377cc",
            height=35,
            command=self.calibrate
        )
        calibrate_button.pack(fill="x", padx=10, pady=2)
        
        # ========== AŞAMA 1 KOMUTLARI ==========
    def start_balloon_hunt(self):
            """Balon avı başlat"""
            if self.app_controller:
                self.app_controller.send_command("start_system")
                self.app_controller.send_command("change_mode", 1)
                print("[CONTROL] Balon avı başlatıldı")
        
    def toggle_auto_hunt(self):
            """Otomatik av modunu aç/kapat"""
            if self.app_controller:
                self.app_controller.send_command("auto_hunt_toggle")
                print("[CONTROL] Otomatik av modu değiştirildi")
        
        # ========== AŞAMA 2 KOMUTLARI ==========
    def start_foe_detection(self):
            """Düşman tespit sistemini başlat"""
            if self.app_controller:
                self.app_controller.send_command("start_system")
                self.app_controller.send_command("change_mode", 2)
                print("[CONTROL] Düşman tespit sistemi başlatıldı")
        
    def open_classification_settings(self):
            """Sınıflandırma ayarları penceresini aç"""
            # Basit popup pencere
            settings_window = ctk.CTkToplevel()
            settings_window.title("Sınıflandırma Ayarları")
            settings_window.geometry("300x200")
            
            ctk.CTkLabel(settings_window, text="Dost-Düşman Tanıma Ayarları", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
            
            ctk.CTkLabel(settings_window, text="Doğruluk Eşiği: %90").pack(pady=5)
            ctk.CTkSlider(settings_window, from_=70, to=99).pack(pady=10)
            
            ctk.CTkButton(settings_window, text="Kaydet", 
                        command=settings_window.destroy).pack(pady=20)
        
        # ========== AŞAMA 3 KOMUTLARI ==========
    def read_qr_code(self):
            """QR kod okuma başlat"""
            if self.app_controller:
                self.app_controller.send_command("read_qr")
                print("[CONTROL] QR kod okuma başlatıldı")
        
    def switch_platform(self):
            """Platform değiştir"""
            if self.app_controller:
                self.app_controller.send_command("switch_platform")
                print("[CONTROL] Platform değiştirme komutu gönderildi")
        
    def start_engagement(self):
            """Angajman başlat"""
            if self.app_controller:
                self.app_controller.send_command("start_system") 
                self.app_controller.send_command("change_mode", 3)
                self.app_controller.send_command("start_engagement")
                print("[CONTROL] Angajman başlatıldı")
        
        # ========== ORTAK KOMUTLAR ==========
    def fire_weapon(self):
            """Ateş et"""
            if self.app_controller:
                self.app_controller.send_command("fire_weapon")
                print(f"[CONTROL] ATEŞ komutu gönderildi (Aşama {self.phase})")

    def calibrate(self):
            """Kalibrasyon"""
            if self.app_controller:
                self.app_controller.send_command("calibrate_joystick")
                print("[CONTROL] Kalibrasyon başlatıldı")
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
        self.weapon_module.app_controller = self.app_controller  # EKLE

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
        self.control_module.app_controller = self.app_controller  # EKLE
        self.control_module.pack(fill="x", padx=10, pady=5)
         # Log
        self.log_module = LogModule(right_frame)
        self.log_module.pack(fill="both", expand=True, padx=10, pady=5)

    def start_system(self):
        """Sistem başlat - Acil durdur sonrası özel davranış"""
        if self.emergency_active:
            # ✅ YENİ: AppController'da emergency mode deaktif et
            self.app_controller.set_emergency_mode(False)
            
            # Acil durdurdan çıkış
            self.emergency_active = False
            
            # Tüm butonları tekrar aktif et
            self._enable_all_buttons()
            
            # Durum güncelle
            self.status_module.update_status("Sistem Yeniden Başlatıldı", "#00ff88")
            self.log_module.add_log("✅ Acil durdurdan çıkıldı - Sistem normale döndü")
        
        # Normal sistem başlatma
        self.app_controller.send_command("start_system")
        self.app_controller.send_command("change_mode", self.phase)
        
        if hasattr(self, 'log_module'):
            self.log_module.add_log(f"Sistem başlatıldı - Aşama {self.phase}")

    def stop_system(self):
        """Sistem durdur - AppController ile"""
        # AppController'a komut gönder
        self.app_controller.send_command("stop_system")
        
        # UI güncellemeleri callback'ler ile gelecek
        if hasattr(self, 'log_module'):
            self.log_module.add_log("Sistem durduruldu")

    def _stop_all_systems(self):
        """Acil durdurma - Tüm sistemleri durdur ve veri akışını kes"""
        try:
            self.emergency_active = True  # Acil durum flag'i
            
            # Kamera modülünü durdur
            if hasattr(self, 'camera_module'):
                self.camera_module.stop_camera()
            
            # AppController'a acil durdur gönder
            self.app_controller.send_command("emergency_stop")
            
            # ✅ YENİ: Raspberry Pi iletişimini tamamen durdur
            if hasattr(self.app_controller, 'comm_manager'):
                print("[EMERGENCY] Raspberry Pi iletişimi durduruluyor...")
                self.app_controller.comm_manager.stop_communication()
            
            # ✅ YENİ: AppController'ı da durdur
            if hasattr(self, 'app_controller'):
                print("[EMERGENCY] AppController durduruluyor...")
                self.app_controller.stop()
            
            # Log ekle
            if hasattr(self, 'log_module'):
                self.log_module.add_log("🛑 ACİL DURDUR - Tüm sistemler ve veri akışı durduruldu")
            
        except Exception as e:
            print(f"[EMERGENCY] Sistem durdurma hatası: {e}")

    def emergency_stop(self):
        """Acil durdur - AppController ile"""
        # Acil durdur butonu titreme efekti
        self.emergency_button.configure(fg_color="#ff0000", text="🚨 ACTİVE! 🚨")
        
        # AppController'a acil durdur komutu gönder
        self.app_controller.send_command("emergency_stop")
        
        # TÜM SİSTEMLERİ DURDUR
        self._stop_all_systems()
        
        
        
        

    def _stop_all_systems(self):
        """Acil durdurma - Tüm sistemleri durdur ve veri akışını kes"""
        try:
            self.emergency_active = True  # Acil durum flag'i
            
            # Kamera modülünü durdur
            if hasattr(self, 'camera_module'):
                self.camera_module.stop_camera()
            
            # AppController'a acil durdur gönder
            self.app_controller.send_command("emergency_stop")
            
            # Log ekle
            if hasattr(self, 'log_module'):
                self.log_module.add_log("🛑 ACİL DURDUR - Tüm sistemler ve veri akışı durduruldu")
            
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
        
    def emergency_stop(self):
        """Acil durdur - YENİ VERSİYON"""
        # ✅ YENİ: AppController'da emergency mode aktif et
        self.app_controller.set_emergency_mode(True)
        
        # Acil durdur butonu titreme efekti
        self.emergency_button.configure(fg_color="#ff0000", text="🚨 ACTİVE! 🚨")
        
        # AppController'a acil durdur komutu gönder
        self.app_controller.send_command("emergency_stop")
        
        # TÜM SİSTEMLERİ DURDUR
        self._stop_all_systems()
        
        # Basit uyarı popup'ı oluştur (geri sayım yok)
        self.create_simple_emergency_popup()
        
        # TÜM BUTONLARI DEVRE DIŞI BIRAK (Sistem Başlat hariç)
        self._disable_all_buttons_except_start()

    def create_simple_emergency_popup(self):
        """Basit acil durdur uyarı popup'ı (geri sayım yok)"""
        # Popup penceresi
        self.emergency_popup = ctk.CTkToplevel(self.root)
        self.emergency_popup.title("⚠️ ACİL DURDUR")
        self.emergency_popup.geometry("400x200")
        self.emergency_popup.resizable(False, False)
        
        # Pencereyi üstte tut
        self.emergency_popup.attributes('-topmost', True)
        self.emergency_popup.grab_set()
        
        # Ortalama
        self.emergency_popup.update_idletasks()
        x = (self.emergency_popup.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.emergency_popup.winfo_screenheight() // 2) - (200 // 2)
        self.emergency_popup.geometry(f"400x200+{x}+{y}")
        
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
        warning_label.pack(pady=30)
        
        # Açıklama
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Tüm operasyonlar durduruldu!\nSistemi yeniden başlatmak için \n 'SİSTEM BAŞLAT' butonunu kullanın.",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff"
        )
        desc_label.pack(pady=20)
        
        # Tamam butonu
        ok_button = ctk.CTkButton(
            main_frame,
            text="TAMAM",
            command=self.close_emergency_popup,
            fg_color="#ffffff",
            text_color="#cc0000",
            hover_color="#f0f0f0",
            width=100,
            height=35
        )
        ok_button.pack(pady=10)

    def close_emergency_popup(self):
        """Emergency popup'ını kapat"""
        if hasattr(self, 'emergency_popup'):
            self.emergency_popup.destroy()

    def _disable_all_buttons_except_start(self):
        """Sistem başlat hariç tüm butonları devre dışı bırak"""
        try:
            # Sağ panel kontrol butonları
            if hasattr(self, 'control_module'):
                # Ateş butonu
                if hasattr(self.control_module, 'fire_button'):
                    self.control_module.fire_button.configure(state="disabled")
                
                # Otomatik butonlar
                if hasattr(self.control_module, 'auto_button'):
                    self.control_module.auto_button.configure(state="disabled")
            
            # Mühimmat sistemi butonları
            if hasattr(self, 'weapon_module'):
                if hasattr(self.weapon_module, 'control_mode_selector'):
                    self.weapon_module.control_mode_selector.configure(state="disabled")
                if hasattr(self.weapon_module, 'laser_status_btn'):
                    self.weapon_module.laser_status_btn.configure(state="disabled")
                if hasattr(self.weapon_module, 'pellet_status_btn'):
                    self.weapon_module.pellet_status_btn.configure(state="disabled")
            
            # Kamera kontrolleri
            if hasattr(self, 'camera_module'):
                if hasattr(self.camera_module, 'record_button'):
                    self.camera_module.record_button.configure(state="disabled")
                if hasattr(self.camera_module, 'snapshot_button'):
                    self.camera_module.snapshot_button.configure(state="disabled")
                if hasattr(self.camera_module, 'lock_button'):
                    self.camera_module.lock_button.configure(state="disabled")
            
            # Sistem durdur butonunu devre dışı bırak
            if hasattr(self, 'stop_button'):
                self.stop_button.configure(state="disabled")
            
            # Acil durdur butonunu devre dışı bırak (tekrar basılmasın)
            self.emergency_button.configure(state="disabled")
            
            # Durum güncelle
            self.status_module.update_status("SİSTEM DURDURULDU", "#ff0000")
            self.log_module.add_log("🔒 Tüm kontroller devre dışı bırakıldı")
            
        except Exception as e:
            print(f"[EMERGENCY] Buton devre dışı bırakma hatası: {e}")

    def _enable_all_buttons(self):
        """Tüm butonları tekrar aktif et"""
        try:
            # Sağ panel kontrol butonları
            if hasattr(self, 'control_module'):
                if hasattr(self.control_module, 'fire_button'):
                    self.control_module.fire_button.configure(state="normal")
                if hasattr(self.control_module, 'auto_button'):
                    self.control_module.auto_button.configure(state="normal")
            
            # Mühimmat sistemi butonları
            if hasattr(self, 'weapon_module'):
                if hasattr(self.weapon_module, 'control_mode_selector'):
                    self.weapon_module.control_mode_selector.configure(state="normal")
                if hasattr(self.weapon_module, 'laser_status_btn'):
                    self.weapon_module.laser_status_btn.configure(state="normal")
                if hasattr(self.weapon_module, 'pellet_status_btn'):
                    self.weapon_module.pellet_status_btn.configure(state="normal")
            
            # Kamera kontrolleri
            if hasattr(self, 'camera_module'):
                if hasattr(self.camera_module, 'record_button'):
                    self.camera_module.record_button.configure(state="normal")
                if hasattr(self.camera_module, 'snapshot_button'):
                    self.camera_module.snapshot_button.configure(state="normal")
                if hasattr(self.camera_module, 'lock_button'):
                    self.camera_module.lock_button.configure(state="normal")
            
            # Sistem durdur butonunu aktif et
            if hasattr(self, 'stop_button'):
                self.stop_button.configure(state="normal")
            
            # Acil durdur butonunu normale döndür
            self.emergency_button.configure(
                state="normal",
                fg_color="#cc0000",
                text="ACİL DURDUR"
            )
            
            self.log_module.add_log("🔓 Tüm kontroller yeniden aktif edildi")
            
        except Exception as e:
            print(f"[RESTART] Buton aktifleştirme hatası: {e}")
        
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



    def _register_app_callbacks(self):
         
        
        def safe_data_callback(data):
            try:
                if (hasattr(self, 'root') and self.root and 
                    hasattr(self.root, 'winfo_exists') and self.root.winfo_exists()):
                    self.root.after_idle(lambda: self._safe_update_gui(data))
            except:
                pass
        
        def safe_log_callback(log_entry):
            try:
                if (hasattr(self, 'root') and self.root and 
                    hasattr(self.root, 'winfo_exists') and self.root.winfo_exists()):
                    self.root.after_idle(lambda: self._safe_add_log(log_entry))
            except:
                pass
        
        def safe_connection_callback(connection_data):
            try:
                if (hasattr(self, 'root') and self.root and 
                    hasattr(self.root, 'winfo_exists') and self.root.winfo_exists()):
                    self.root.after_idle(lambda: self._safe_connection_update(connection_data))
            except:
                pass
        
        def safe_error_callback(error_message):
            try:
                if (hasattr(self, 'root') and self.root and 
                    hasattr(self.root, 'winfo_exists') and self.root.winfo_exists()):
                    self.root.after_idle(lambda: self._safe_error_update(error_message))
            except:
                pass
        
        # Tamamen sessiz kayıt
        self.app_controller.register_callback("data_updated", safe_data_callback)
        self.app_controller.register_callback("log_added", safe_log_callback)
        self.app_controller.register_callback("raspberry_connection_changed", safe_connection_callback)
        self.app_controller.register_callback("raspberry_error", safe_error_callback)
  
  
    def _safe_update_gui(self, data):
        """CLEAN: Thread-safe GUI güncellemesi - Sessiz versiyon"""
        try:
            # Sessiz çalışma - sadece GUI güncellemeleri
            
            # ========== ORTAK VERİLER ==========
            if hasattr(self, 'coords_module') and data:
                if 'pan_angle' in data and 'tilt_angle' in data:
                    self.coords_module.update_coordinates(
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
            
            # ========== CONTROLLER DURUMU (Aşama 0) ==========
            if (self.phase == 0 and 
                hasattr(self.target_module, 'update_controller_status')):
                self.target_module.update_controller_status(data)
            
            # ========== AŞAMA-SPESİFİK VERİLER ==========
            if hasattr(self.target_module, 'update_phase_data'):
                self.target_module.update_phase_data(data)
            
            # ========== MÜHİMMAT SİSTEMİ ==========
            if hasattr(self, 'weapon_module') and 'weapon' in data:
                # Sadece otomatik modda Raspberry Pi'den gelen veriyi kullan
                if (hasattr(self.weapon_module, 'control_mode') and 
                    self.weapon_module.control_mode == "Otomatik"):
                    weapon_type = data['weapon']
                    weapon_map = {
                        'Laser': 'Lazer',
                        'Airgun': 'Boncuk', 
                        'Auto': 'Otomatik',
                        'None': 'Seçilmedi'
                    }
                    gui_weapon = weapon_map.get(weapon_type, weapon_type)
                    self.weapon_module.update_weapon_selection(gui_weapon)
                # Manuel modda kullanıcı seçimini koru, Raspberry Pi verisini ignore et
        except Exception as e:
            print(f"[MAIN GUI] ❌ GUI güncelleme hatası: {e}")
    
    
    def _safe_add_log(self, log_entry):
        """CLEAN: Sessiz log ekleme"""
        try:
            if hasattr(self, 'log_module'):
                parts = log_entry.split('] ', 2)
                if len(parts) >= 3:
                    message = parts[2]
                    phase_prefix = f"[AŞAMA {self.phase}] " if self.phase > 0 else "[MANUEL] "
                    self.log_module.add_log(f"{phase_prefix}{message}")
                else:
                    self.log_module.add_log(log_entry)
        except:
         pass    


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