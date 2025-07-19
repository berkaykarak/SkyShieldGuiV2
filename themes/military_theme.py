# gui/themes/military_theme.py
import customtkinter as ctk
from typing import Dict, Any

class MilitaryTheme:
    """
    Askeri/Savunma sanayi teması
    Koyu renkler, yüksek kontrast, profesyonel görünüm
    """
    
    # Ana renkler
    PRIMARY_DARK = "#0d1117"      # Ana koyu arka plan
    SECONDARY_DARK = "#161b22"    # İkincil arka plan
    ACCENT_BLUE = "#1f538d"       # Mavi vurgu
    ACCENT_GREEN = "#238636"      # Yeşil (başarı)
    ACCENT_RED = "#da3633"        # Kırmızı (tehlike)
    ACCENT_ORANGE = "#f85149"     # Turuncu (uyarı)
    ACCENT_YELLOW = "#d29922"     # Sarı (bilgi)
    
    # Metin renkleri
    TEXT_PRIMARY = "#f0f6fc"      # Ana metin
    TEXT_SECONDARY = "#8b949e"    # İkincil metin
    TEXT_MUTED = "#6e7681"        # Soluk metin
    
    # Sınır renkleri
    BORDER_DEFAULT = "#30363d"    # Varsayılan sınır
    BORDER_MUTED = "#21262d"      # Soluk sınır
    
    # Durum renkleri
    STATUS_READY = "#7c3aed"      # Hazır (mor)
    STATUS_ACTIVE = "#f59e0b"     # Aktif (sarı)
    STATUS_LOCKED = "#10b981"     # Kilitli (yeşil)
    STATUS_ERROR = "#ef4444"      # Hata (kırmızı)
    STATUS_OFFLINE = "#6b7280"    # Çevrimdışı (gri)
    
    # Gradyan renkleri
    GRADIENT_START = "#1a1a2e"
    GRADIENT_END = "#16213e"
    
    @classmethod
    def get_color_scheme(cls) -> Dict[str, str]:
        """Tam renk şemasını döndür"""
        return {
            # Ana renkler
            "bg_primary": cls.PRIMARY_DARK,
            "bg_secondary": cls.SECONDARY_DARK,
            "accent_blue": cls.ACCENT_BLUE,
            "accent_green": cls.ACCENT_GREEN,
            "accent_red": cls.ACCENT_RED,
            "accent_orange": cls.ACCENT_ORANGE,
            "accent_yellow": cls.ACCENT_YELLOW,
            
            # Metin
            "text_primary": cls.TEXT_PRIMARY,
            "text_secondary": cls.TEXT_SECONDARY,
            "text_muted": cls.TEXT_MUTED,
            
            # Sınırlar
            "border_default": cls.BORDER_DEFAULT,
            "border_muted": cls.BORDER_MUTED,
            
            # Durumlar
            "status_ready": cls.STATUS_READY,
            "status_active": cls.STATUS_ACTIVE,
            "status_locked": cls.STATUS_LOCKED,
            "status_error": cls.STATUS_ERROR,
            "status_offline": cls.STATUS_OFFLINE,
        }
    
    @classmethod
    def get_button_styles(cls) -> Dict[str, Dict[str, str]]:
        """Buton stilleri"""
        return {
            "primary": {
                "fg_color": cls.ACCENT_BLUE,
                "hover_color": "#14375e",
                "text_color": cls.TEXT_PRIMARY,
                "corner_radius": 6
            },
            "success": {
                "fg_color": cls.ACCENT_GREEN,
                "hover_color": "#1a5928",
                "text_color": cls.TEXT_PRIMARY,
                "corner_radius": 6
            },
            "danger": {
                "fg_color": cls.ACCENT_RED,
                "hover_color": "#991b1b",
                "text_color": cls.TEXT_PRIMARY,
                "corner_radius": 6
            },
            "warning": {
                "fg_color": cls.ACCENT_ORANGE,
                "hover_color": "#dc2626",
                "text_color": cls.TEXT_PRIMARY,
                "corner_radius": 6
            },
            "secondary": {
                "fg_color": cls.SECONDARY_DARK,
                "hover_color": cls.BORDER_DEFAULT,
                "text_color": cls.TEXT_SECONDARY,
                "corner_radius": 6,
                "border_width": 1,
                "border_color": cls.BORDER_DEFAULT
            }
        }
    
    @classmethod
    def get_frame_styles(cls) -> Dict[str, Dict[str, str]]:
        """Frame stilleri"""
        return {
            "primary": {
                "fg_color": cls.SECONDARY_DARK,
                "corner_radius": 8,
                "border_width": 1,
                "border_color": cls.BORDER_DEFAULT
            },
            "secondary": {
                "fg_color": cls.PRIMARY_DARK,
                "corner_radius": 6,
                "border_width": 1,
                "border_color": cls.BORDER_MUTED
            },
            "transparent": {
                "fg_color": "transparent",
                "corner_radius": 0
            },
            "status_ready": {
                "fg_color": cls.STATUS_READY,
                "corner_radius": 4
            },
            "status_active": {
                "fg_color": cls.STATUS_ACTIVE,
                "corner_radius": 4
            },
            "status_locked": {
                "fg_color": cls.STATUS_LOCKED,
                "corner_radius": 4
            },
            "status_error": {
                "fg_color": cls.STATUS_ERROR,
                "corner_radius": 4
            }
        }
    
    @classmethod
    def get_text_styles(cls) -> Dict[str, Dict[str, Any]]:
        """Metin stilleri"""
        return {
            "heading_large": {
                "font": ctk.CTkFont(size=24, weight="bold"),
                "text_color": cls.TEXT_PRIMARY
            },
            "heading_medium": {
                "font": ctk.CTkFont(size=18, weight="bold"),
                "text_color": cls.TEXT_PRIMARY
            },
            "heading_small": {
                "font": ctk.CTkFont(size=14, weight="bold"),
                "text_color": cls.TEXT_PRIMARY
            },
            "body_large": {
                "font": ctk.CTkFont(size=14),
                "text_color": cls.TEXT_PRIMARY
            },
            "body_medium": {
                "font": ctk.CTkFont(size=12),
                "text_color": cls.TEXT_PRIMARY
            },
            "body_small": {
                "font": ctk.CTkFont(size=10),
                "text_color": cls.TEXT_SECONDARY
            },
            "caption": {
                "font": ctk.CTkFont(size=9),
                "text_color": cls.TEXT_MUTED
            },
            "code": {
                "font": ctk.CTkFont(family="Consolas", size=10),
                "text_color": cls.TEXT_PRIMARY
            },
            "status_success": {
                "font": ctk.CTkFont(size=12, weight="bold"),
                "text_color": cls.ACCENT_GREEN
            },
            "status_error": {
                "font": ctk.CTkFont(size=12, weight="bold"),
                "text_color": cls.ACCENT_RED
            },
            "status_warning": {
                "font": ctk.CTkFont(size=12, weight="bold"),
                "text_color": cls.ACCENT_ORANGE
            }
        }
    
    @classmethod
    def get_progress_styles(cls) -> Dict[str, Dict[str, str]]:
        """Progress bar stilleri"""
        return {
            "default": {
                "progress_color": cls.ACCENT_BLUE,
                "fg_color": cls.BORDER_DEFAULT,
                "corner_radius": 4
            },
            "success": {
                "progress_color": cls.ACCENT_GREEN,
                "fg_color": cls.BORDER_DEFAULT,
                "corner_radius": 4
            },
            "warning": {
                "progress_color": cls.ACCENT_ORANGE,
                "fg_color": cls.BORDER_DEFAULT,
                "corner_radius": 4
            },
            "danger": {
                "progress_color": cls.ACCENT_RED,
                "fg_color": cls.BORDER_DEFAULT,
                "corner_radius": 4
            }
        }
    
    @classmethod
    def get_input_styles(cls) -> Dict[str, Dict[str, str]]:
        """Input (Entry, Textbox) stilleri"""
        return {
            "default": {
                "fg_color": cls.PRIMARY_DARK,
                "border_color": cls.BORDER_DEFAULT,
                "text_color": cls.TEXT_PRIMARY,
                "placeholder_text_color": cls.TEXT_MUTED,
                "corner_radius": 4
            },
            "focused": {
                "border_color": cls.ACCENT_BLUE
            },
            "error": {
                "border_color": cls.ACCENT_RED
            }
        }

class MilitaryThemeApplier:
    """Askeri temayı uygulayan yardımcı sınıf"""
    
    def __init__(self):
        self.theme = MilitaryTheme()
    
    def apply_to_button(self, button: ctk.CTkButton, style: str = "primary") -> None:
        """Butona stil uygula"""
        styles = self.theme.get_button_styles()
        if style in styles:
            button.configure(**styles[style])
    
    def apply_to_frame(self, frame: ctk.CTkFrame, style: str = "primary") -> None:
        """Frame'e stil uygula"""
        styles = self.theme.get_frame_styles()
        if style in styles:
            frame.configure(**styles[style])
    
    def apply_to_label(self, label: ctk.CTkLabel, style: str = "body_medium") -> None:
        """Label'a stil uygula"""
        styles = self.theme.get_text_styles()
        if style in styles:
            label.configure(**styles[style])
    
    def apply_to_progressbar(self, progressbar: ctk.CTkProgressBar, style: str = "default") -> None:
        """Progress bar'a stil uygula"""
        styles = self.theme.get_progress_styles()
        if style in styles:
            progressbar.configure(**styles[style])
    
    def apply_to_entry(self, entry: ctk.CTkEntry, style: str = "default") -> None:
        """Entry'e stil uygula"""
        styles = self.theme.get_input_styles()
        if style in styles:
            entry.configure(**styles[style])
    
    def apply_to_textbox(self, textbox: ctk.CTkTextbox, style: str = "default") -> None:
        """Textbox'a stil uygula"""
        styles = self.theme.get_input_styles()
        if style in styles:
            textbox.configure(**styles[style])

def apply_military_theme() -> None:
    """
    Global olarak askeri temayı uygula
    CustomTkinter'ın varsayılan ayarlarını değiştir
    """
    # Tema modunu ayarla
    ctk.set_appearance_mode("dark")
    
    # Özel renk teması oluştur
    theme_colors = {
        "CTk": {
            "fg_color": [MilitaryTheme.PRIMARY_DARK, MilitaryTheme.PRIMARY_DARK]
        },
        "CTkToplevel": {
            "fg_color": [MilitaryTheme.PRIMARY_DARK, MilitaryTheme.PRIMARY_DARK]
        },
        "CTkFrame": {
            "corner_radius": 8,
            "border_width": 1,
            "fg_color": [MilitaryTheme.SECONDARY_DARK, MilitaryTheme.SECONDARY_DARK],
            "border_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT]
        },
        "CTkButton": {
            "corner_radius": 6,
            "border_width": 0,
            "fg_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "hover_color": ["#14375e", "#14375e"],
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY],
            "text_color_disabled": [MilitaryTheme.TEXT_MUTED, MilitaryTheme.TEXT_MUTED]
        },
        "CTkLabel": {
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY]
        },
        "CTkEntry": {
            "corner_radius": 4,
            "border_width": 1,
            "fg_color": [MilitaryTheme.PRIMARY_DARK, MilitaryTheme.PRIMARY_DARK],
            "border_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY],
            "placeholder_text_color": [MilitaryTheme.TEXT_MUTED, MilitaryTheme.TEXT_MUTED]
        },
        "CTkTextbox": {
            "corner_radius": 4,
            "border_width": 1,
            "fg_color": [MilitaryTheme.PRIMARY_DARK, MilitaryTheme.PRIMARY_DARK],
            "border_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY]
        },
        "CTkScrollbar": {
            "corner_radius": 4,
            "fg_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "button_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "button_hover_color": ["#14375e", "#14375e"]
        },
        "CTkProgressBar": {
            "corner_radius": 4,
            "border_width": 0,
            "fg_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "progress_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE]
        },
        "CTkOptionMenu": {
            "corner_radius": 4,
            "fg_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "button_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "button_hover_color": ["#14375e", "#14375e"],
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY]
        },
        "CTkComboBox": {
            "corner_radius": 4,
            "border_width": 1,
            "fg_color": [MilitaryTheme.PRIMARY_DARK, MilitaryTheme.PRIMARY_DARK],
            "border_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "button_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "button_hover_color": ["#14375e", "#14375e"],
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY]
        },
        "CTkCheckBox": {
            "corner_radius": 4,
            "border_width": 2,
            "fg_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "border_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "hover_color": ["#14375e", "#14375e"],
            "checkmark_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY],
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY]
        },
        "CTkRadioButton": {
            "corner_radius": 10,
            "border_width_checked": 5,
            "border_width_unchecked": 2,
            "fg_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "border_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "hover_color": ["#14375e", "#14375e"],
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY]
        },
        "CTkSwitch": {
            "corner_radius": 12,
            "border_width": 2,
            "button_length": 0,
            "fg_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "progress_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "button_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY],
            "button_hover_color": [MilitaryTheme.TEXT_SECONDARY, MilitaryTheme.TEXT_SECONDARY],
            "text_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY]
        },
        "CTkSlider": {
            "corner_radius": 6,
            "button_corner_radius": 8,
            "border_width": 0,
            "button_length": 16,
            "fg_color": [MilitaryTheme.BORDER_DEFAULT, MilitaryTheme.BORDER_DEFAULT],
            "progress_color": [MilitaryTheme.ACCENT_BLUE, MilitaryTheme.ACCENT_BLUE],
            "button_color": [MilitaryTheme.TEXT_PRIMARY, MilitaryTheme.TEXT_PRIMARY],
            "button_hover_color": [MilitaryTheme.TEXT_SECONDARY, MilitaryTheme.TEXT_SECONDARY]
        }
    }
    
    try:
        # Özel tema dosyası oluştur ve uygula
        import json
        import tempfile
        import os
        
        # Geçici tema dosyası oluştur
        theme_file = os.path.join(tempfile.gettempdir(), "military_theme.json")
        with open(theme_file, 'w') as f:
            json.dump(theme_colors, f, indent=2)
        
        # Temayı uygula
        ctk.set_default_color_theme(theme_file)
        
        print("[THEME] Askeri tema başarıyla uygulandı")
        
    except Exception as e:
        print(f"[THEME] Tema uygulama hatası: {e}")
        # Varsayılan koyu tema kullan
        ctk.set_default_color_theme("dark-blue")

def get_status_color(status: str) -> str:
    """Durum için uygun renk döndür"""
    status_colors = {
        "ready": MilitaryTheme.STATUS_READY,
        "active": MilitaryTheme.STATUS_ACTIVE,
        "locked": MilitaryTheme.STATUS_LOCKED,
        "error": MilitaryTheme.STATUS_ERROR,
        "offline": MilitaryTheme.STATUS_OFFLINE,
        "success": MilitaryTheme.ACCENT_GREEN,
        "warning": MilitaryTheme.ACCENT_ORANGE,
        "danger": MilitaryTheme.ACCENT_RED,
        "info": MilitaryTheme.ACCENT_BLUE
    }
    return status_colors.get(status.lower(), MilitaryTheme.TEXT_SECONDARY)

def get_weapon_color(weapon: str) -> str:
    """Mühimmat türü için renk döndür"""
    weapon_colors = {
        "laser": "#ef4444",      # Kırmızı - lazer
        "airgun": "#3b82f6",     # Mavi - gazlı itki
        "auto": "#8b5cf6",       # Mor - otomatik
        "none": "#6b7280"        # Gri - seçilmemiş
    }
    return weapon_colors.get(weapon.lower(), MilitaryTheme.TEXT_MUTED)

def get_mode_color(mode: int) -> str:
    """Sistem modu için renk döndür"""
    mode_colors = {
        0: "#6b7280",  # Gri - Manuel
        1: "#f59e0b",  # Sarı - Aşama 1
        2: "#3b82f6",  # Mavi - Aşama 2
        3: "#ef4444"   # Kırmızı - Aşama 3
    }
    return mode_colors.get(mode, MilitaryTheme.TEXT_MUTED)

# Hazır widget fabrika fonksiyonları
def create_status_button(parent, text: str, command=None, status: str = "ready") -> ctk.CTkButton:
    """Durum buton oluştur"""
    color = get_status_color(status)
    button = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=color,
        hover_color=color,
        font=ctk.CTkFont(size=12, weight="bold"),
        corner_radius=6
    )
    return button

def create_info_frame(parent, title: str = "") -> ctk.CTkFrame:
    """Bilgi frame'i oluştur"""
    frame = ctk.CTkFrame(
        parent,
        fg_color=MilitaryTheme.SECONDARY_DARK,
        border_color=MilitaryTheme.BORDER_DEFAULT,
        border_width=1,
        corner_radius=8
    )
    
    if title:
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=MilitaryTheme.TEXT_PRIMARY
        )
        title_label.pack(pady=(15,10))
    
    return frame

def create_status_indicator(parent, size: int = 12) -> ctk.CTkFrame:
    """Durum göstergesi oluştur"""
    indicator = ctk.CTkFrame(
        parent,
        width=size,
        height=size,
        corner_radius=size//2,
        fg_color=MilitaryTheme.STATUS_OFFLINE
    )
    indicator.pack_propagate(False)
    return indicator

def update_status_indicator(indicator: ctk.CTkFrame, status: str) -> None:
    """Durum göstergesini güncelle"""
    color = get_status_color(status)
    indicator.configure(fg_color=color)

# CSS benzeri stil uygulama sistemi
class StyleManager:
    """Stil yöneticisi - CSS benzeri stil uygulama"""
    
    def __init__(self):
        self.theme = MilitaryTheme()
        self.styles = {}
        self._load_default_styles()
    
    def _load_default_styles(self):
        """Varsayılan stilleri yükle"""
        self.styles.update({
            "btn-primary": self.theme.get_button_styles()["primary"],
            "btn-success": self.theme.get_button_styles()["success"],
            "btn-danger": self.theme.get_button_styles()["danger"],
            "btn-warning": self.theme.get_button_styles()["warning"],
            "btn-secondary": self.theme.get_button_styles()["secondary"],
            
            "frame-primary": self.theme.get_frame_styles()["primary"],
            "frame-secondary": self.theme.get_frame_styles()["secondary"],
            "frame-transparent": self.theme.get_frame_styles()["transparent"],
            
            "text-heading": self.theme.get_text_styles()["heading_medium"],
            "text-body": self.theme.get_text_styles()["body_medium"],
            "text-caption": self.theme.get_text_styles()["caption"],
            "text-code": self.theme.get_text_styles()["code"],
            
            "input-default": self.theme.get_input_styles()["default"],
            "progress-default": self.theme.get_progress_styles()["default"]
        })
    
    def apply_style(self, widget, style_name: str):
        """Widget'a stil uygula"""
        if style_name in self.styles:
            widget.configure(**self.styles[style_name])
        else:
            print(f"[THEME] Stil bulunamadı: {style_name}")
    
    def register_style(self, name: str, style_dict: Dict[str, Any]):
        """Yeni stil kaydet"""
        self.styles[name] = style_dict
    
    def get_style(self, name: str) -> Dict[str, Any]:
        """Stil bilgisini al"""
        return self.styles.get(name, {})

# Global stil yöneticisi
style_manager = StyleManager()

def apply_style(widget, style: str):
    """Widget'a stil uygula (kısayol)"""
    style_manager.apply_style(widget, style)

# Modern animasyon desteği
class AnimationManager:
    """Basit animasyon yöneticisi"""
    
    @staticmethod
    def fade_in(widget, duration: int = 500):
        """Fade in animasyonu"""
        # CustomTkinter'da basit animasyon
        try:
            widget.pack()
            widget.update()
        except:
            pass
    
    @staticmethod
    def fade_out(widget, duration: int = 500):
        """Fade out animasyonu"""
        try:
            widget.pack_forget()
        except:
            pass
    
    @staticmethod
    def pulse_color(widget, color: str, duration: int = 1000):
        """Renk pulse animasyonu"""
        original_color = widget.cget("fg_color")
        widget.configure(fg_color=color)
        widget.after(duration, lambda: widget.configure(fg_color=original_color))

# Tema test fonksiyonu
def test_theme():
    """Tema test penceresi"""
    test_window = ctk.CTk()
    test_window.title("Military Theme Test")
    test_window.geometry("800x600")
    
    # Temayı uygula
    apply_military_theme()
    
    # Test bileşenleri
    main_frame = ctk.CTkFrame(test_window)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Başlık
    title = ctk.CTkLabel(main_frame, text="🛡️ MILITARY THEME TEST", 
                        font=ctk.CTkFont(size=24, weight="bold"))
    title.pack(pady=20)
    
    # Butonlar
    button_frame = ctk.CTkFrame(main_frame)
    button_frame.pack(fill="x", padx=20, pady=10)
    
    buttons = [
        ("Primary", "btn-primary"),
        ("Success", "btn-success"), 
        ("Danger", "btn-danger"),
        ("Warning", "btn-warning"),
        ("Secondary", "btn-secondary")
    ]
    
    for text, style in buttons:
        btn = ctk.CTkButton(button_frame, text=text)
        apply_style(btn, style)
        btn.pack(side="left", padx=5, pady=10)
    
    # Durum göstergeleri
    status_frame = ctk.CTkFrame(main_frame)
    status_frame.pack(fill="x", padx=20, pady=10)
    
    statuses = ["ready", "active", "locked", "error", "offline"]
    for status in statuses:
        indicator = create_status_indicator(status_frame)
        update_status_indicator(indicator, status)
        ctk.CTkLabel(status_frame, text=status.upper()).pack(side="left", padx=10)
    
    test_window.mainloop()

if __name__ == "__main__":
    test_theme()