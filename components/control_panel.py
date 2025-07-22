# gui/components/control_panel.py
import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, Optional
from .base_component import BaseGUIComponent

class ControlPanel(BaseGUIComponent):
   """
   Sol taraftaki sistem kontrol paneli
   Sistem modu, başlat/durdur, acil durdurma gibi kontrolleri içerir
   """
   
   def __init__(self, parent, app_controller):
       super().__init__(parent, app_controller)
       
       # Kontrol değişkenleri
       self.mode_var = tk.StringVar(value="Manuel")
       self.weapon_mode_var = tk.StringVar(value="Otomatik")
       
       # UI elementleri referansları
       self.emergency_btn: Optional[ctk.CTkButton] = None
       self.start_btn: Optional[ctk.CTkButton] = None
       self.scan_btn: Optional[ctk.CTkButton] = None
       self.fire_btn: Optional[ctk.CTkButton] = None
       self.mode_menu: Optional[ctk.CTkOptionMenu] = None
       
       # Durum takibi
       self.system_active = False
       self.emergency_active = False
       
       self.setup_ui()
   
   def setup_ui(self) -> None:
       """Kontrol paneli UI'ını oluştur"""
       # Ana frame
       self.frame = ctk.CTkFrame(self.parent, width=320, corner_radius=10)
       self.frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)
       self.frame.grid_propagate(False)
       
       # Bileşenleri oluştur
       self._create_header()
       self._create_mode_selector()
       self._create_emergency_controls()
       self._create_system_controls()
       self._create_weapon_controls()
       self._create_manual_controls()
       self._create_info_section()
   
   def _create_header(self) -> None:
       """Panel başlığını oluştur"""
       header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
       header_frame.pack(fill="x", padx=20, pady=(20,10))
       
       title = ctk.CTkLabel(
           header_frame,
           text="🛡️ KONTROL PANELİ",
           font=ctk.CTkFont(size=20, weight="bold"),
           text_color=("#ffffff", "#ffffff")
       )
       title.pack()
       
       # Alt başlık
       subtitle = ctk.CTkLabel(
           header_frame,
           text="SKY SHIELD v2.0",
           font=ctk.CTkFont(size=12),
           text_color=("#a0a0a0", "#a0a0a0")
       )
       subtitle.pack(pady=(5,0))
   
   def _create_mode_selector(self) -> None:
       """Sistem modu seçicisini oluştur"""
       mode_frame = ctk.CTkFrame(self.frame)
       mode_frame.pack(fill="x", padx=20, pady=10)
       
       # Başlık
       mode_title = ctk.CTkLabel(
           mode_frame, 
           text="📡 Sistem Modu",
           font=ctk.CTkFont(size=14, weight="bold")
       )
       mode_title.pack(pady=(15,5))
       
       # Mod seçici
       self.mode_menu = ctk.CTkOptionMenu(
           mode_frame,
           values=["Manuel", "Aşama 1", "Aşama 2", "Aşama 3"],
           variable=self.mode_var,
           command=self._on_mode_change,
           button_color=("#1f538d", "#14375e"),
           button_hover_color=("#1f538d", "#14375e")
       )
       self.mode_menu.pack(pady=(0,10), padx=15, fill="x")
       
       # Mod açıklaması
       self.mode_description = ctk.CTkLabel(
           mode_frame,
           text="Manuel kontrol modu aktif",
           font=ctk.CTkFont(size=11),
           text_color=("#808080", "#808080"),
           wraplength=250
       )
       self.mode_description.pack(pady=(0,15), padx=15)
   
   def _create_emergency_controls(self) -> None:
       """Acil durdurma kontrollerini oluştur"""
       emergency_frame = ctk.CTkFrame(self.frame, fg_color="#2d1b1b")
       emergency_frame.pack(fill="x", padx=20, pady=10)
       
       # Acil durdurma butonu
       self.emergency_btn = ctk.CTkButton(
           emergency_frame,
           text="🚨 ACİL DURDUR",
           command=self._emergency_stop,
           fg_color="#dc2626",
           hover_color="#991b1b",
           height=50,
           font=ctk.CTkFont(size=16, weight="bold")
       )
       self.emergency_btn.pack(pady=15, padx=15, fill="x")
       
       # Sistem sıfırlama butonu
       self.reset_btn = ctk.CTkButton(
           emergency_frame,
           text="🔄 SİSTEMİ SIFIRLA",
           command=self._reset_system,
           fg_color="#d97706",
           hover_color="#92400e",
           height=35,
           font=ctk.CTkFont(size=12)
       )
       self.reset_btn.pack(pady=(0,15), padx=15, fill="x")
   
   def _create_system_controls(self) -> None:
       """Sistem kontrollerini oluştur"""
       controls_frame = ctk.CTkFrame(self.frame)
       controls_frame.pack(fill="x", padx=20, pady=10)
       
       # Başlık
       controls_title = ctk.CTkLabel(
           controls_frame,
           text="⚙️ Sistem Kontrolleri",
           font=ctk.CTkFont(size=14, weight="bold")
       )
       controls_title.pack(pady=(15,10))
       
       # Başlat/Durdur butonu
       self.start_btn = ctk.CTkButton(
           controls_frame,
           text="▶ SİSTEMİ BAŞLAT",
           command=self._toggle_system,
           fg_color="#16a34a",
           hover_color="#15803d",
           height=40
       )
       self.start_btn.pack(pady=(0,10), padx=15, fill="x")
       
       # Hedef arama butonu
       self.scan_btn = ctk.CTkButton(
           controls_frame,
           text="🔍 HEDEF ARA",
           command=self._start_scan,
           height=35
       )
       self.scan_btn.pack(pady=(0,15), padx=15, fill="x")
   
   def _create_weapon_controls(self) -> None:
       """Mühimmat kontrollerini oluştur"""
       weapon_frame = ctk.CTkFrame(self.frame)
       weapon_frame.pack(fill="x", padx=20, pady=10)
       
       # Başlık
       weapon_title = ctk.CTkLabel(
           weapon_frame,
           text="🎯 Mühimmat Kontrolleri",
           font=ctk.CTkFont(size=14, weight="bold")
       )
       weapon_title.pack(pady=(15,10))
       
       # Mühimmat seçim modu
       mode_frame = ctk.CTkFrame(weapon_frame, fg_color="transparent")
       mode_frame.pack(fill="x", padx=15, pady=(0,10))
       
       self.weapon_auto_radio = ctk.CTkRadioButton(
           mode_frame,
           text="🤖 Otomatik Seçim",
           variable=self.weapon_mode_var,
           value="Otomatik",
           command=self._on_weapon_mode_change
       )
       self.weapon_auto_radio.pack(anchor="w", pady=2)
       
       self.weapon_manual_radio = ctk.CTkRadioButton(
           mode_frame,
           text="👤 Manuel Seçim",
           variable=self.weapon_mode_var,
           value="Manuel",
           command=self._on_weapon_mode_change
       )
       self.weapon_manual_radio.pack(anchor="w", pady=2)
       
       # Manuel seçim menüsü
       self.manual_weapon_var = tk.StringVar(value="Lazer")
       self.weapon_menu = ctk.CTkOptionMenu(
           weapon_frame,
           values=["Lazer", "Gazlı İtki"],
           variable=self.manual_weapon_var,
           command=self._on_manual_weapon_select,
           state="disabled"
       )
       self.weapon_menu.pack(pady=(0,10), padx=15, fill="x")
       
       # Ateş et butonu
       self.fire_btn = ctk.CTkButton(
           weapon_frame,
           text="🎯 ATEŞ ET",
           command=self._fire_weapon,
           fg_color="#dc2626",
           hover_color="#991b1b",
           height=45,
           font=ctk.CTkFont(size=14, weight="bold"),
           state="disabled"
       )
       self.fire_btn.pack(pady=(0,15), padx=15, fill="x")
   
   def _create_manual_controls(self) -> None:
       """Manuel kontrol joystick bilgilerini oluştur"""
       manual_frame = ctk.CTkFrame(self.frame)
       manual_frame.pack(fill="x", padx=20, pady=10)
       
       # Başlık
       manual_title = ctk.CTkLabel(
           manual_frame,
           text="🕹️ Manuel Kontrol",
           font=ctk.CTkFont(size=14, weight="bold")
       )
       manual_title.pack(pady=(15,10))
       
       # Joystick durumu
       self.joystick_status = ctk.CTkLabel(
           manual_frame,
           text="🔴 Joystick: Bağlı Değil",
           font=ctk.CTkFont(size=12)
       )
       self.joystick_status.pack(pady=(0,10), padx=15)
       
       # Joystick kalibrasyonu
       self.calibrate_btn = ctk.CTkButton(
           manual_frame,
           text="⚙️ Kalibrasyon",
           command=self._calibrate_joystick,
           height=30,
           font=ctk.CTkFont(size=11)
       )
       self.calibrate_btn.pack(pady=(0,15), padx=15, fill="x")
   
   def _create_info_section(self) -> None:
       """Bilgi bölümünü oluştur"""
       info_frame = ctk.CTkFrame(self.frame)
       info_frame.pack(fill="both", expand=True, padx=20, pady=(10,20))
       
       # Başlık
       info_title = ctk.CTkLabel(
           info_frame,
           text="ℹ️ Sistem Bilgileri",
           font=ctk.CTkFont(size=14, weight="bold")
       )
       info_title.pack(pady=(15,10))
       
       # Bilgi grid'i
       info_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
       info_grid.pack(fill="x", padx=15, pady=(0,15))
       
       # CPU kullanımı
       cpu_frame = ctk.CTkFrame(info_grid)
       cpu_frame.pack(fill="x", pady=2)
       
       ctk.CTkLabel(cpu_frame, text="CPU:", anchor="w").pack(side="left", padx=(10,5))
       self.cpu_label = ctk.CTkLabel(cpu_frame, text="0%", anchor="e")
       self.cpu_label.pack(side="right", padx=(5,10))
       
       # Bellek kullanımı
       ram_frame = ctk.CTkFrame(info_grid)
       ram_frame.pack(fill="x", pady=2)
       
       ctk.CTkLabel(ram_frame, text="RAM:", anchor="w").pack(side="left", padx=(10,5))
       self.ram_label = ctk.CTkLabel(ram_frame, text="0 MB", anchor="e")
       self.ram_label.pack(side="right", padx=(5,10))
       
       # Sıcaklık
       temp_frame = ctk.CTkFrame(info_grid)
       temp_frame.pack(fill="x", pady=2)
       
       ctk.CTkLabel(temp_frame, text="Sıcaklık:", anchor="w").pack(side="left", padx=(10,5))
       self.temp_label = ctk.CTkLabel(temp_frame, text="--°C", anchor="e")
       self.temp_label.pack(side="right", padx=(5,10))
   
   # Event handler'lar
   def _on_mode_change(self, value: str) -> None:
       """Mod değiştiğinde çağrılır"""
       mode_map = {"Manuel": 0, "Aşama 1": 1, "Aşama 2": 2, "Aşama 3": 3}
       mode_descriptions = {
           "Manuel": "Operatör joystick ile kontrol eder",
           "Aşama 1": "Tüm hareketli hedefler otomatik imha edilir",
           "Aşama 2": "Dost-düşman ayrımı yapılarak imha edilir",
           "Aşama 3": "Angajman emri ile belirli hedefler imha edilir"
       }
       
       # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
       if self.app:
           self.app.send_command("change_mode", mode_map[value])
       
       self.mode_description.configure(text=mode_descriptions[value])
       
       # Manuel mod kontrollerini güncelle
       if value == "Manuel":
           self._enable_manual_controls()
       else:
           self._disable_manual_controls()
   
   def _emergency_stop(self) -> None:
       """Acil durdurma işlemi"""
       # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
       if self.app:
           self.app.send_command("emergency_stop")
       
       self.emergency_active = True
       
       # UI güncellemeleri
       self.emergency_btn.configure(
           text="⏹ DURDURULDU",
           state="disabled",
           fg_color="#991b1b"
       )
       self.start_btn.configure(
           text="▶ SİSTEMİ BAŞLAT",
           fg_color="#16a34a",
           state="disabled"
       )
       self._disable_all_controls()
   
   def _reset_system(self) -> None:
       """Sistemi sıfırla"""
       # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
       if self.app:
           self.app.send_command("reset_system")
       
       self.emergency_active = False
       self.system_active = False
       
       # UI'yi sıfırla
       self.emergency_btn.configure(
           text="🚨 ACİL DURDUR",
           state="normal",
           fg_color="#dc2626"
       )
       self.start_btn.configure(
           text="▶ SİSTEMİ BAŞLAT",
           fg_color="#16a34a",
           state="normal"
       )
       self._enable_all_controls()
   
   def _toggle_system(self) -> None:
       """Sistemi başlat/durdur"""
       if self.system_active:
           # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
           if self.app:
               self.app.send_command("stop_system")
           
           self.system_active = False
           self.start_btn.configure(
               text="▶ SİSTEMİ BAŞLAT",
               fg_color="#16a34a"
           )
           self.scan_btn.configure(state="disabled")
       else:
           # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
           if self.app:
               self.app.send_command("start_system")
           
           self.system_active = True
           self.start_btn.configure(
               text="⏸ SİSTEMİ DURDUR",
               fg_color="#dc2626"
           )
           self.scan_btn.configure(state="normal")
   
   def _start_scan(self) -> None:
       """Hedef arama başlat"""
       if self.system_active:
           # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
           if self.app:
               self.app.send_command("start_scan")
           
           self.scan_btn.configure(
               text="🔄 ARANIYOR...",
               state="disabled"
           )
   
   def _on_weapon_mode_change(self) -> None:
       """Mühimmat modu değiştiğinde"""
       if self.weapon_mode_var.get() == "Manuel":
           self.weapon_menu.configure(state="normal")
       else:
           self.weapon_menu.configure(state="disabled")
       
       # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
       if self.app:
           self.app.send_command("weapon_mode_change", self.weapon_mode_var.get())
   
   def _on_manual_weapon_select(self, value: str) -> None:
       """Manuel mühimmat seçimi"""
       # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
       if self.app:
           self.app.send_command("select_weapon", value)
   
   def _fire_weapon(self) -> None:
       """Ateş et"""
       # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
       if self.app:
           self.app.send_command("fire_weapon")
       
       self.fire_btn.configure(
           text="🔥 ATEŞLENIYOR...",
           state="disabled"
       )
   
   def _calibrate_joystick(self) -> None:
       """Joystick kalibrasyonu"""
       # APP CONTROLLER İLE KOMUT GÖNDER - DÜZELTME
       if self.app:
           self.app.send_command("calibrate_joystick")
       
       self.calibrate_btn.configure(text="⏳ Kalibrasyon...")
   
   def _enable_manual_controls(self) -> None:
       """Manuel kontrolleri etkinleştir"""
       self.calibrate_btn.configure(state="normal")
       self.joystick_status.configure(text="🟡 Joystick: Manuel Mod")
   
   def _disable_manual_controls(self) -> None:
       """Manuel kontrolleri devre dışı bırak"""
       self.calibrate_btn.configure(state="disabled")
       self.joystick_status.configure(text="🟢 Joystick: Otomatik Mod")
   
   def _enable_all_controls(self) -> None:
       """Tüm kontrolleri etkinleştir"""
       widgets = [self.mode_menu, self.start_btn, self.scan_btn]
       for widget in widgets:
           if widget:
               widget.configure(state="normal")
   
   def _disable_all_controls(self) -> None:
       """Tüm kontrolleri devre dışı bırak"""
       widgets = [self.mode_menu, self.scan_btn, self.fire_btn]
       for widget in widgets:
           if widget:
               widget.configure(state="disabled")
   
   def update_data(self, data: Dict[str, Any]) -> None:
       """Kontrol paneli verilerini güncelle"""
       # Hedef kilidi durumu
       if data.get('target_locked'):
           self.fire_btn.configure(state="normal")
           self.scan_btn.configure(
               text="🔒 HEDEF KİLİTLİ",
               state="disabled"
           )
       else:
           if not self.emergency_active:
               self.fire_btn.configure(state="disabled")
               if self.system_active:
                   self.scan_btn.configure(
                       text="🔍 HEDEF ARA",
                       state="normal"
                   )
       
       # Sistem durumu
       if not data.get('active') and self.system_active:
           self.system_active = False
           self.start_btn.configure(
               text="▶ SİSTEMİ BAŞLAT",
               fg_color="#16a34a"
           )
       
       # Ateş durumu sıfırlama
       if self.fire_btn.cget("text") == "🔥 ATEŞLENIYOR...":
           self.fire_btn.configure(text="🎯 ATEŞ ET")
       
       # Sistem bilgileri güncelle
       if 'cpu_usage' in data:
           self.cpu_label.configure(text=f"{data['cpu_usage']:.1f}%")
       if 'ram_usage' in data:
           self.ram_label.configure(text=f"{data['ram_usage']:.0f} MB")
       if 'temperature' in data:
           self.temp_label.configure(text=f"{data['temperature']:.1f}°C")
   
   def get_data(self) -> Dict[str, Any]:
       """Kontrol paneli verilerini döndür"""
       return {
           'mode': self.mode_var.get(),
           'weapon_mode': self.weapon_mode_var.get(),
           'manual_weapon': self.manual_weapon_var.get(),
           'system_active': self.system_active,
           'emergency_active': self.emergency_active
       }
   
   def reset(self) -> None:
       """Kontrol panelini sıfırla"""
       self.mode_var.set("Manuel")
       self.weapon_mode_var.set("Otomatik")
       self.manual_weapon_var.set("Lazer")
       self.system_active = False
       self.emergency_active = False
       
       # Butonları sıfırla
       if self.emergency_btn:
           self.emergency_btn.configure(
               text="🚨 ACİL DURDUR",
               state="normal",
               fg_color="#dc2626"
           )
       if self.start_btn:
           self.start_btn.configure(
               text="▶ SİSTEMİ BAŞLAT",
               fg_color="#16a34a"
           )
       if self.scan_btn:
           self.scan_btn.configure(
               text="🔍 HEDEF ARA",
               state="disabled"
           )
       if self.fire_btn:
           self.fire_btn.configure(
               text="🎯 ATEŞ ET",
               state="disabled"
           )