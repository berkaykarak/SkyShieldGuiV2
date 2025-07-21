# gui/components/base_component.py
from abc import ABC, abstractmethod
import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, Optional, Callable

class BaseGUIComponent(ABC):
    """
    Tüm GUI bileşenleri için temel sınıf
    Her GUI bileşeni bu sınıftan türetilmelidir
    """
    
    def __init__(self, parent: ctk.CTkFrame, app_controller):
        self.parent = parent
        self.app = app_controller
        self.frame: Optional[ctk.CTkFrame] = None
        self.is_visible = True
        self.is_enabled = True
        self.callbacks: Dict[str, Callable] = {}
        
        # Bileşen kimliği
        self.component_id = self.__class__.__name__.lower()
        
    @abstractmethod
    def setup_ui(self) -> None:
        """
        UI bileşenlerini oluştur ve yerleştir
        Her alt sınıf bu metodu implement etmelidir
        """
        pass
    
    @abstractmethod
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Veri güncellemelerini işle
        Args:
            data: Güncellenecek veri sözlüğü
        """
        pass
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Olay dinleyicisi kaydet
        Args:
            event: Olay adı
            callback: Çağırılacak fonksiyon
        """
        self.callbacks[event] = callback
    
    def trigger_callback(self, event: str, data: Any = None) -> None:
        """
        Kayıtlı callback'i tetikle
        Args:
            event: Olay adı
            data: Callback'e gönderilecek veri
        """
        if event in self.callbacks:
            self.callbacks[event](data)
    
    def show(self) -> None:
        """Bileşeni göster"""
        if self.frame:
            self.frame.pack()
            self.is_visible = True
    
    def hide(self) -> None:
        """Bileşeni gizle"""
        if self.frame:
            self.frame.pack_forget()
            self.is_visible = False
    
    def enable(self) -> None:
        """Bileşeni etkinleştir"""
        self.is_enabled = True
        self._update_state()
    
    def disable(self) -> None:
        """Bileşeni devre dışı bırak"""
        self.is_enabled = False
        self._update_state()
    
    def _update_state(self) -> None:
        """
        Bileşen durumunu güncelle
        Alt sınıflar bu metodu override edebilir
        """
        pass
    
    def get_data(self) -> Dict[str, Any]:
        """
        Bileşenin mevcut veri durumunu döndür
        Alt sınıflar bu metodu override etmelidir
        """
        return {}
    
    def validate_input(self) -> bool:
        """
        Kullanıcı girişlerini doğrula
        Alt sınıflar bu metodu override edebilir
        """
        return True
    
    def reset(self) -> None:
        """
        Bileşeni başlangıç durumuna döndür
        Alt sınıflar bu metodu override edebilir
        """
        pass

class ComponentManager:
    """GUI bileşenlerini yönetir"""
    
    def __init__(self):
        self.components: Dict[str, BaseGUIComponent] = {}
        self.update_callbacks: Dict[str, Callable] = {}
    
    def register_component(self, name: str, component: BaseGUIComponent) -> None:
        """
        Bileşen kaydet
        Args:
            name: Bileşen adı
            component: Bileşen instance'ı
        """
        self.components[name] = component
    
    def get_component(self, name: str) -> Optional[BaseGUIComponent]:
        """
        Bileşen al
        Args:
            name: Bileşen adı
        Returns:
            Bileşen instance'ı veya None
        """
        return self.components.get(name)
    
    def update_all_components(self, data: Dict[str, Any]) -> None:
        """
        Tüm bileşenleri güncelle
        Args:
            data: Güncellenecek veri
        """
        for component in self.components.values():
            component.update_data(data)
    
    def enable_all(self) -> None:
        """Tüm bileşenleri etkinleştir"""
        for component in self.components.values():
            component.enable()
    
    def disable_all(self) -> None:
        """Tüm bileşenleri devre dışı bırak"""
        for component in self.components.values():
            component.disable()
    
    def reset_all(self) -> None:
        """Tüm bileşenleri sıfırla"""
        for component in self.components.values():
            component.reset()