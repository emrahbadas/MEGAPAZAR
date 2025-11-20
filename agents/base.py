from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.logger import setup_logger

class BaseAgent(ABC):
    """Tüm agent'ların base class'ı"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = setup_logger(name)
    
    @abstractmethod
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Agent'ın ana işlev metodu - her agent implement etmeli"""
        pass
    
    def log(self, message: str, level: str = "info"):
        """Log mesajı gönder"""
        if level == "info":
            self.logger.info(f"[{self.name}] {message}")
        elif level == "error":
            self.logger.error(f"[{self.name}] {message}")
        elif level == "warning":
            self.logger.warning(f"[{self.name}] {message}")
        elif level == "debug":
            self.logger.debug(f"[{self.name}] {message}")
