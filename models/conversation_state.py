"""
Conversation State Management
Kullanıcı oturumlarını ve conversation akışını yöneten state modeli
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import uuid
import pickle
import os
from pathlib import Path

class ConversationStage(str, Enum):
    """Konuşma aşamaları"""
    INITIAL = "initial"                    # İlk mesaj
    GATHERING_INFO = "gathering_info"      # Bilgi toplama (eksik detaylar)
    ANALYZING = "analyzing"                # Ürün analizi
    PRICING = "pricing"                    # Fiyat belirleme
    PREVIEW = "preview"                    # Önizleme gösterimi
    NEGOTIATION = "negotiation"            # Fiyat müzakeresi
    EDITING = "editing"                    # Düzenleme
    CONFIRMING = "confirming"              # Onaylama
    COMPLETED = "completed"                # Tamamlandı
    CANCELLED = "cancelled"                # İptal edildi

class UserIntent(str, Enum):
    """Kullanıcı niyeti"""
    LISTING = "listing"           # Ürün satmak istiyor
    SEARCHING = "searching"       # Ürün arıyor
    NEGOTIATING = "negotiating"   # Fiyat pazarlık yapıyor
    EDITING = "editing"          # İlan düzenliyor
    CONFIRMING = "confirming"    # Onaylıyor
    CANCELLING = "cancelling"    # İptal ediyor
    QUESTION = "question"        # Soru soruyor
    UNKNOWN = "unknown"          # Belirsiz

class SessionState(BaseModel):
    """
    Kullanıcı oturum state'i
    Her kullanıcı için ayrı session tutulacak
    """
    session_id: str = ""
    user_id: str
    platform: str = "web"  # web, whatsapp
    
    # Conversation tracking
    stage: ConversationStage = ConversationStage.INITIAL
    intent: UserIntent = UserIntent.UNKNOWN
    conversation_history: List[Dict[str, Any]] = []
    
    # Product information
    product_info: Optional[Dict[str, Any]] = None
    missing_fields: List[str] = []  # Eksik bilgiler
    
    # Pricing & stats
    internal_stats: Dict[str, Any] = {}  # Benzer ürünler
    external_stats: Dict[str, Any] = {}  # Web araması
    pricing: Optional[Dict[str, Any]] = None
    user_price_preference: Optional[float] = None  # Kullanıcının istediği fiyat
    
    # Listing draft
    listing_draft: Optional[Dict[str, Any]] = None
    draft_version: int = 1  # Kaçıncı versiyon
    
    # Images
    image_url: Optional[str] = None
    uploaded_images: List[str] = []
    
    # User preferences
    user_location: Optional[str] = None
    preferred_category: Optional[str] = None
    
    # Metadata
    created_at: datetime = None
    updated_at: datetime = None
    last_message_at: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_message_at = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Conversation history'ye mesaj ekle"""
        self.conversation_history.append({
            "role": role,  # user, assistant, system
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        self.last_message_at = datetime.now()
        self.updated_at = datetime.now()
    
    def set_stage(self, stage: ConversationStage):
        """Aşamayı değiştir"""
        self.stage = stage
        self.updated_at = datetime.now()
    
    def set_missing_fields(self, fields: List[str]):
        """Eksik alanları işaretle"""
        self.missing_fields = fields
        if fields:
            self.set_stage(ConversationStage.GATHERING_INFO)
    
    def update_product_info(self, info: Dict[str, Any]):
        """Ürün bilgisini güncelle (merge)"""
        if not self.product_info:
            self.product_info = {}
        self.product_info.update(info)
        self.updated_at = datetime.now()
    
    def update_listing_draft(self, draft: Dict[str, Any]):
        """Listing draft'ı güncelle"""
        self.listing_draft = draft
        self.draft_version += 1
        self.updated_at = datetime.now()
    
    def set_user_price(self, price: float):
        """Kullanıcının belirlediği fiyatı kaydet"""
        self.user_price_preference = price
        self.set_stage(ConversationStage.NEGOTIATION)
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Oturum süresi dolmuş mu?"""
        if not self.last_message_at:
            return True
        elapsed = (datetime.now() - self.last_message_at).total_seconds() / 60
        return elapsed > timeout_minutes
    
    def reset(self):
        """State'i sıfırla (yeni ilan için)"""
        self.stage = ConversationStage.INITIAL
        self.intent = UserIntent.UNKNOWN
        self.product_info = None
        self.missing_fields = []
        self.internal_stats = {}
        self.external_stats = {}
        self.pricing = None
        self.user_price_preference = None
        self.listing_draft = None
        self.draft_version = 1
        self.image_url = None
        # conversation_history saklanır (geçmişi görmek için)
        self.updated_at = datetime.now()

class SessionManager:
    """
    Session yönetimi
    Memory + File-based persistence (pickle)
    """
    def __init__(self, persist_dir: str = "sessions"):
        self.sessions: Dict[str, SessionState] = {}
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
    
    def _get_session_file(self, user_id: str) -> Path:
        """Session dosya yolunu döndür"""
        # Güvenli dosya adı (user_id'deki özel karakterleri temizle)
        safe_id = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in user_id)
        return self.persist_dir / f"session_{safe_id}.pkl"
    
    def _load_from_disk(self, user_id: str) -> Optional[SessionState]:
        """Disk'ten session yükle"""
        session_file = self._get_session_file(user_id)
        if session_file.exists():
            try:
                with open(session_file, 'rb') as f:
                    session = pickle.load(f)
                
                # Expired kontrolü
                if session.is_expired():
                    # Dosyayı sil
                    session_file.unlink(missing_ok=True)
                    return None
                
                return session
            except Exception as e:
                # Corrupt file, sil
                session_file.unlink(missing_ok=True)
                return None
        return None
    
    def _save_to_disk(self, session: SessionState):
        """Session'ı disk'e kaydet"""
        session_file = self._get_session_file(session.user_id)
        try:
            with open(session_file, 'wb') as f:
                pickle.dump(session, f)
        except Exception as e:
            # Logging yapılabilir
            pass
    
    def get_or_create_session(self, user_id: str, platform: str = "web") -> SessionState:
        """Session getir veya yeni oluştur (disk'ten otomatik yükleme)"""
        # Önce memory'de var mı?
        if user_id in self.sessions:
            session = self.sessions[user_id]
            # Expired mı kontrol et
            if session.is_expired():
                # Memory'den sil
                del self.sessions[user_id]
                # Disk'ten de sil
                self._get_session_file(user_id).unlink(missing_ok=True)
                # Yeni session oluştur
                session = SessionState(user_id=user_id, platform=platform)
                self.sessions[user_id] = session
                self._save_to_disk(session)
            return session
        
        # Memory'de yok, disk'ten yükle
        session = self._load_from_disk(user_id)
        if session:
            self.sessions[user_id] = session
            return session
        
        # Hiç yok, yeni oluştur
        session = SessionState(user_id=user_id, platform=platform)
        self.sessions[user_id] = session
        self._save_to_disk(session)
        return session
    
    def get_session(self, user_id: str) -> Optional[SessionState]:
        """Session getir (disk'ten otomatik yükleme)"""
        # Memory'de var mı?
        if user_id in self.sessions:
            return self.sessions[user_id]
        
        # Disk'ten yükle
        session = self._load_from_disk(user_id)
        if session:
            self.sessions[user_id] = session
        return session
    
    def update_session(self, session: SessionState):
        """Session'ı güncelle ve disk'e kaydet"""
        self.sessions[session.user_id] = session
        self._save_to_disk(session)
    
    def delete_session(self, user_id: str):
        """Session'ı sil (memory + disk)"""
        if user_id in self.sessions:
            del self.sessions[user_id]
        # Disk'ten de sil
        self._get_session_file(user_id).unlink(missing_ok=True)
    
    def cleanup_expired(self):
        """Süresi dolmuş session'ları temizle (memory + disk)"""
        # Memory'den temizle
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if session.is_expired()
        ]
        for user_id in expired_users:
            del self.sessions[user_id]
            self._get_session_file(user_id).unlink(missing_ok=True)
        
        # Disk'teki tüm session dosyalarını kontrol et
        for session_file in self.persist_dir.glob("session_*.pkl"):
            try:
                with open(session_file, 'rb') as f:
                    session = pickle.load(f)
                if session.is_expired():
                    session_file.unlink(missing_ok=True)
            except:
                # Corrupt file, sil
                session_file.unlink(missing_ok=True)

# Global session manager
session_manager = SessionManager()
