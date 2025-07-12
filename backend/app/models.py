from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .database import Base

class UserRole(str, Enum):
    USER = "user"
    PARTNER = "partner"
    SUPERADMIN = "superadmin"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PackageStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

class PackageType(str, Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    PRO = "pro"
    LIFETIME = "lifetime"

class AddonStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    phone = Column(String)
    is_superadmin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default=UserRole.USER.value)
    login_code = Column(String, nullable=True)
    login_code_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    packages = relationship("Package", back_populates="user", cascade="all, delete")
    payments = relationship("Payment", back_populates="user", cascade="all, delete")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete")
    user_addons = relationship("UserAddon", back_populates="user", cascade="all, delete")
    userbot_sessions = relationship("UserbotSession", back_populates="user", cascade="all, delete")
    
    @property
    def package_id(self):
        """Gibt die ID des aktiven Pakets zurück"""
        try:
            active_package = next((pkg for pkg in self.packages if pkg.status == PackageStatus.ACTIVE.value), None)
            return active_package.id if active_package else None
        except Exception:
            return None

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    session_token = Column(String, unique=True, index=True)
    telegram_id = Column(String, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")

# Neue Paket-System Modelle
class PackageTemplate(Base):
    __tablename__ = "package_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # basic, advanced, pro, lifetime
    display_name = Column(String)  # Basic, Advanced, Pro, Lifetime
    package_type = Column(String, default=PackageType.BASIC.value)
    monthly_price = Column(Float, nullable=True)
    one_time_price = Column(Float, nullable=True)
    features = Column(JSON)  # Feature-Matrix als JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    packages = relationship("Package", back_populates="template", cascade="all, delete")
    package_addons = relationship("PackageAddon", back_populates="package_template", cascade="all, delete")

class Addon(Base):
    __tablename__ = "addons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    display_name = Column(String)
    description = Column(Text, nullable=True)
    monthly_price = Column(Float)
    one_time_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    addon_tiers = relationship("AddonTier", back_populates="addon", cascade="all, delete")
    package_addons = relationship("PackageAddon", back_populates="addon", cascade="all, delete")
    user_addons = relationship("UserAddon", back_populates="addon", cascade="all, delete")

class AddonTier(Base):
    __tablename__ = "addon_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    addon_id = Column(Integer, ForeignKey("addons.id", ondelete="CASCADE"))
    level = Column(String)  # 1, 2, 3, VIP
    price = Column(Float)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    addon = relationship("Addon", back_populates="addon_tiers")

class PackageAddon(Base):
    __tablename__ = "package_addons"
    
    id = Column(Integer, primary_key=True, index=True)
    package_template_id = Column(Integer, ForeignKey("package_templates.id", ondelete="CASCADE"))
    addon_id = Column(Integer, ForeignKey("addons.id", ondelete="CASCADE"))
    is_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    package_template = relationship("PackageTemplate", back_populates="package_addons")
    addon = relationship("Addon", back_populates="package_addons")

class Package(Base):
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    duration_days = Column(Integer)
    features = Column(Text)  # JSON string (Legacy)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    template_id = Column(Integer, ForeignKey("package_templates.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, default=PackageStatus.INACTIVE.value)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="packages")
    template = relationship("PackageTemplate", back_populates="packages")
    payments = relationship("Payment", back_populates="package", cascade="all, delete")

class UserAddon(Base):
    __tablename__ = "user_addons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    addon_id = Column(Integer, ForeignKey("addons.id", ondelete="CASCADE"))
    tier_id = Column(Integer, ForeignKey("addon_tiers.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, default=AddonStatus.ACTIVE.value)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="user_addons")
    addon = relationship("Addon", back_populates="user_addons")
    tier = relationship("AddonTier")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    package_id = Column(Integer, ForeignKey("packages.id", ondelete="CASCADE"))
    addon_id = Column(Integer, ForeignKey("addons.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Float)
    status = Column(String, default=PaymentStatus.PENDING.value)
    tx_hash = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="payments")
    package = relationship("Package", back_populates="payments")

# Legacy Modelle (beibehalten für Kompatibilität)
class Feature(Base):
    __tablename__ = "features"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    code = Column(String, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SignalGroup(Base):
    __tablename__ = "signal_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_group_id = Column(String, nullable=True)  # Telegram-Gruppen-ID der Quellgruppe
    created_group_id = Column(String, nullable=True)  # Telegram-Gruppen-ID der erstellten Gruppe
    created_group_invite_link = Column(String, nullable=True)  # Invite-Link der erstellten Gruppe
    theme = Column(String, nullable=True)  # Thema der Gruppe (z.B. "BTC-Signale", "Altcoin-News")
    is_active = Column(Boolean, default=True)
    price_1_group = Column(Float, default=0.0)  # Preis für 1 Signalgruppe
    price_2_groups = Column(Float, default=0.0)  # Preis für 2 Signalgruppen
    price_3_groups = Column(Float, default=0.0)  # Preis für 3 Signalgruppen
    price_4_groups = Column(Float, default=0.0)  # Preis für 4 Signalgruppen
    price_5_groups = Column(Float, default=0.0)  # Preis für 5 Signalgruppen
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Neue Felder für automatische Gruppenverwaltung
    auto_create_groups = Column(Boolean, default=True)  # Automatisch Gruppen erstellen
    group_prefix = Column(String, nullable=True)  # Prefix für erstellte Gruppen (z.B. "BTC-Signale")
    max_members_per_group = Column(Integer, default=1000)  # Maximale Mitglieder pro Gruppe
    auto_forward_messages = Column(Boolean, default=True)  # Automatisch Nachrichten weiterleiten
    forward_delay_seconds = Column(Integer, default=0)  # Verzögerung beim Weiterleiten
    filter_keywords = Column(Text, nullable=True)  # Keywords für Nachrichtenfilter (JSON)
    exclude_keywords = Column(Text, nullable=True)  # Keywords zum Ausschließen (JSON)
    
    # Userbot-Session-Verknüpfung
    userbot_session_id = Column(Integer, ForeignKey("userbot_sessions.id"), nullable=True)
    target_groups = Column(Text, nullable=True)  # JSON-Array der Zielgruppen-IDs
    super_group_id = Column(String, nullable=True)  # ID der Supergruppe für thematische Aufteilung
    
    # Thematische Aufteilung
    themes_config = Column(Text, nullable=True)  # JSON-Konfiguration für Themen
    theme_prices = Column(Text, nullable=True)  # JSON-Preise pro Thema
    
    # Beziehungen
    partner = relationship("User", foreign_keys=[partner_id])
    subscriptions = relationship("SignalGroupSubscription", back_populates="signal_group")
    userbot_session = relationship("UserbotSession", back_populates="signal_groups")
    themes = relationship("SignalTheme", back_populates="signal_group")

class PartnerPermissions(Base):
    __tablename__ = "partner_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("users.id"), unique=True)
    can_manage_users = Column(Boolean, default=False)
    can_manage_packages = Column(Boolean, default=False)
    can_manage_payments = Column(Boolean, default=False)
    can_manage_signal_groups = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserbotSession(Base):
    __tablename__ = "userbot_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    session_name = Column(String, nullable=False)
    session_type = Column(String, nullable=False)  # message_forwarding, signal_groups, auto_reply, custom
    phone = Column(String, nullable=False)
    telegram_session_string = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    telegram_id = Column(String, index=True)  # NEU: Telegram-ID für Zuordnung
    
    # Spezifische Konfiguration je nach Session-Typ
    config_data = Column(Text, nullable=True)  # JSON-Konfiguration für die Session
    
    # Abonnement- und Zahlungsfelder
    subscription_status = Column(String, default="active")  # active, expired, cancelled, pending_payment
    subscription_start_date = Column(DateTime, default=datetime.utcnow)
    subscription_end_date = Column(DateTime, nullable=True)
    last_payment_date = Column(DateTime, nullable=True)
    next_payment_date = Column(DateTime, nullable=True)
    payment_reminder_sent = Column(Boolean, default=False)
    deletion_warning_sent = Column(Boolean, default=False)
    auto_delete_date = Column(DateTime, nullable=True)  # Datum für automatische Löschung (2 Wochen nach letzter Zahlung)

    # NEU: Weiterleitungs-Flag
    forwarding_enabled = Column(Boolean, default=False)
    
    # Beziehungen
    user = relationship("User", back_populates="userbot_sessions")
    signal_groups = relationship("SignalGroup", back_populates="userbot_session", cascade="all, delete")
    # NEU: ForwardingGroupMapping-Relation
    forwarding_mappings = relationship("ForwardingGroupMapping", back_populates="userbot_session", cascade="all, delete")

class SignalGroupSubscription(Base):
    __tablename__ = "signal_group_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    signal_group_id = Column(Integer, ForeignKey("signal_groups.id"))
    group_count = Column(Integer, default=1)  # Anzahl der Gruppen (1-5)
    status = Column(String, default="active")  # active, expired, cancelled
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    user = relationship("User")
    signal_group = relationship("SignalGroup")

class SignalTheme(Base):
    __tablename__ = "signal_themes"
    
    id = Column(Integer, primary_key=True, index=True)
    signal_group_id = Column(Integer, ForeignKey("signal_groups.id"))
    name = Column(String, nullable=False)  # z.B. "BTC-Signale", "Altcoin-News", "DeFi-Token"
    description = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # JSON-Array der Keywords für automatische Zuordnung
    price_monthly = Column(Float, default=0.0)  # Monatlicher Preis für dieses Thema
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    signal_group = relationship("SignalGroup", back_populates="themes")

class SignalGroupThemeSubscription(Base):
    __tablename__ = "signal_group_theme_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    signal_group_id = Column(Integer, ForeignKey("signal_groups.id"))
    theme_id = Column(Integer, ForeignKey("signal_themes.id"))
    status = Column(String, default="active")  # active, expired, cancelled
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    monthly_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    user = relationship("User")
    signal_group = relationship("SignalGroup")
    theme = relationship("SignalTheme")

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(String, unique=True, index=True)  # Telegram-Gruppen-ID
    name = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)  # Weitere Einstellungen als JSON
    welcome_text = Column(Text, nullable=True)
    night_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Beziehungen zu Userrollen, Verwarnungen, Mutes etc. folgen später

class GroupUserRole(Base):
    __tablename__ = "group_user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    role = Column(String, default="user")  # user, mod, admin
    warnings = Column(Integer, default=0)
    mutes = Column(Integer, default=0)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Beziehungen
    user = relationship("User")
    group = relationship("Group")

class GroupWarning(Base):
    __tablename__ = "group_warnings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    reason = Column(Text, nullable=True)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Wer hat verwarnt?
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Beziehungen
    user = relationship("User", foreign_keys=[user_id])
    group = relationship("Group")
    issuer = relationship("User", foreign_keys=[issued_by])

class GroupMute(Base):
    __tablename__ = "group_mutes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    reason = Column(Text, nullable=True)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    active = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Beziehungen
    user = relationship("User", foreign_keys=[user_id])
    group = relationship("Group")
    issuer = relationship("User", foreign_keys=[issued_by])

class GroupKick(Base):
    __tablename__ = "group_kicks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    reason = Column(Text, nullable=True)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Beziehungen
    user = relationship("User", foreign_keys=[user_id])
    group = relationship("Group")
    issuer = relationship("User", foreign_keys=[issued_by])

class ScheduledMessage(Base):
    __tablename__ = "scheduled_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True)
    message_text = Column(Text, nullable=False)
    schedule_time = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # pending, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    category = Column(String, nullable=True)  # z.B. Krypto, Finanzen
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class CoinAnalysis(Base):
    __tablename__ = "coin_analyses"

    id = Column(Integer, primary_key=True, index=True)
    coin = Column(String, nullable=False)
    analysis_text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tags = Column(String, nullable=True)  # Kommagetrennte Tags
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User")

class SourceGroup(Base):
    __tablename__ = "source_groups"
    id = Column(Integer, primary_key=True, index=True)
    telegram_group_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    topic = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User")

class TopicAssignment(Base):
    __tablename__ = "topic_assignments"
    id = Column(Integer, primary_key=True, index=True)
    source_group_id = Column(Integer, ForeignKey("source_groups.id"))
    topic_name = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    source_group = relationship("SourceGroup")

class CustomerSignalGroup(Base):
    __tablename__ = "customer_signal_groups"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    master_group_id = Column(String, nullable=True)  # ID der Mastergruppe
    package_size = Column(Integer, nullable=False)  # 1-5
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    user = relationship("User")

class CustomerGroupTopic(Base):
    __tablename__ = "customer_group_topics"
    id = Column(Integer, primary_key=True, index=True)
    customer_signal_group_id = Column(Integer, ForeignKey("customer_signal_groups.id"))
    topic_name = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    active = Column(Boolean, default=True)
    customer_signal_group = relationship("CustomerSignalGroup")

class ForwardedMessage(Base):
    __tablename__ = "forwarded_messages"
    id = Column(Integer, primary_key=True, index=True)
    source_group_id = Column(Integer, ForeignKey("source_groups.id"))
    target_group_id = Column(String, nullable=False)
    original_message_id = Column(String, nullable=False)
    forwarded_message_id = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    topic = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="success")
    source_group = relationship("SourceGroup")
    user = relationship("User")

# NEU: Mapping-Tabelle für Quell- und Zielgruppen der Weiterleitung
class ForwardingGroupMapping(Base):
    __tablename__ = "forwarding_group_mappings"
    id = Column(Integer, primary_key=True, index=True)
    userbot_session_id = Column(Integer, ForeignKey("userbot_sessions.id"))
    source_group_id = Column(String, nullable=False)  # Telegram-ID der Quellgruppe
    target_group_id = Column(String, nullable=False)  # Telegram-ID der Zielgruppe
    forwarding_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    userbot_session = relationship("UserbotSession", back_populates="forwarding_mappings")
