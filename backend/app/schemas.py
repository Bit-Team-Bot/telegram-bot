from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

# Enums
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

# Base Models
class UserBase(BaseModel):
    telegram_id: str
    phone: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True

class PackageBase(BaseModel):
    name: str
    price: float
    duration_days: int
    features: Optional[str] = None

class PaymentBase(BaseModel):
    user_id: int
    package_id: int
    amount: float
    status: PaymentStatus = PaymentStatus.PENDING

class FeatureBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True

class SignalGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    partner_id: Optional[int] = None
    source_group_id: Optional[str] = None
    created_group_id: Optional[str] = None
    created_group_invite_link: Optional[str] = None
    theme: Optional[str] = None
    price_1_group: float = 0.0
    price_2_groups: float = 0.0
    price_3_groups: float = 0.0
    price_4_groups: float = 0.0
    price_5_groups: float = 0.0
    is_active: bool = True
    auto_create_groups: bool = True
    group_prefix: Optional[str] = None
    max_members_per_group: int = 1000
    auto_forward_messages: bool = True
    forward_delay_seconds: int = 0
    filter_keywords: Optional[str] = None
    exclude_keywords: Optional[str] = None

class PartnerPermissionsBase(BaseModel):
    partner_id: int
    can_manage_users: bool = False
    can_manage_packages: bool = False
    can_manage_payments: bool = False
    can_manage_signal_groups: bool = False

# Create Models
class UserCreate(UserBase):
    pass

class PackageCreate(PackageBase):
    pass

class PaymentCreate(BaseModel):
    package_id: int
    tx_hash: str

class FeatureCreate(FeatureBase):
    pass

class SignalGroupCreate(SignalGroupBase):
    pass

class PartnerPermissionsCreate(PartnerPermissionsBase):
    pass

# Update Models
class UserUpdate(BaseModel):
    telegram_id: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class PackageUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None
    features: Optional[str] = None
    status: Optional[PackageStatus] = None

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    tx_hash: Optional[str] = None

class FeatureUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class SignalGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    partner_id: Optional[int] = None
    source_group_id: Optional[str] = None
    created_group_id: Optional[str] = None
    created_group_invite_link: Optional[str] = None
    theme: Optional[str] = None
    price_1_group: Optional[float] = None
    price_2_groups: Optional[float] = None
    price_3_groups: Optional[float] = None
    price_4_groups: Optional[float] = None
    price_5_groups: Optional[float] = None
    is_active: Optional[bool] = None

class PartnerPermissionsUpdate(BaseModel):
    can_manage_users: Optional[bool] = None
    can_manage_packages: Optional[bool] = None
    can_manage_payments: Optional[bool] = None
    can_manage_signal_groups: Optional[bool] = None

# Response Models
class UserResponse(BaseModel):
    id: int
    telegram_id: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_superadmin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PackageResponse(BaseModel):
    id: int
    name: str
    price: float
    duration_days: int
    features: Optional[str] = None
    status: PackageStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    package_id: Optional[int] = None
    amount: float
    status: PaymentStatus
    tx_hash: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FeatureResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SignalGroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    partner_id: Optional[int] = None
    source_group_id: Optional[str] = None
    created_group_id: Optional[str] = None
    created_group_invite_link: Optional[str] = None
    theme: Optional[str] = None
    price_1_group: float
    price_2_groups: float
    price_3_groups: float
    price_4_groups: float
    price_5_groups: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PartnerPermissionsResponse(BaseModel):
    id: int
    partner_id: int
    can_manage_users: bool
    can_manage_packages: bool
    can_manage_payments: bool
    can_manage_signal_groups: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Auth Models
class CodeRequest(BaseModel):
    phone: str
    telegram_id: Optional[str] = None
    use_userbot: Optional[bool] = True

class CodeVerify(BaseModel):
    phone: str
    code: str

class AutoLoginRequest(BaseModel):
    telegram_id: str
    session_token: Optional[str] = None

class SessionCreate(BaseModel):
    user_id: int
    telegram_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class SessionResponse(BaseModel):
    session_token: str
    expires_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse 
    session: Optional[SessionResponse] = None

# UserbotSession Schemas
class UserbotSessionBase(BaseModel):
    session_name: str
    session_type: str  # message_forwarding, signal_groups, auto_reply, custom
    phone: str
    telegram_session_string: Optional[str] = None
    is_active: bool = True
    config_data: Optional[str] = None  # JSON-Konfiguration für die Session
    # Abonnement-Felder
    subscription_status: str = "active"
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    last_payment_date: Optional[datetime] = None
    next_payment_date: Optional[datetime] = None

class UserbotSessionCreate(UserbotSessionBase):
    pass

class UserbotSessionUpdate(BaseModel):
    phone: Optional[str] = None
    session_name: Optional[str] = None
    session_type: Optional[str] = None
    telegram_session_string: Optional[str] = None
    is_active: Optional[bool] = None

class UserbotSessionResponse(BaseModel):
    id: int
    user_id: int
    session_name: str
    session_type: str
    phone: str
    telegram_session_string: Optional[str] = None
    is_active: bool
    config_data: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Abonnement-Felder
    subscription_status: str
    subscription_start_date: datetime
    subscription_end_date: Optional[datetime] = None
    last_payment_date: Optional[datetime] = None
    next_payment_date: Optional[datetime] = None
    payment_reminder_sent: bool
    deletion_warning_sent: bool
    auto_delete_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# SignalGroupSubscription Schemas
class SignalGroupSubscriptionBase(BaseModel):
    signal_group_id: int
    group_count: int = 1
    status: str = "active"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SignalGroupSubscriptionCreate(SignalGroupSubscriptionBase):
    pass

class SignalGroupSubscriptionUpdate(BaseModel):
    group_count: Optional[int] = None
    status: Optional[str] = None
    end_date: Optional[datetime] = None

class SignalGroupSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    signal_group_id: int
    group_count: int
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# SignalTheme Schemas
class SignalThemeBase(BaseModel):
    name: str
    description: Optional[str] = None
    keywords: Optional[str] = None  # JSON-Array der Keywords
    price_monthly: float = 0.0
    is_active: bool = True

class SignalThemeCreate(SignalThemeBase):
    signal_group_id: int

class SignalThemeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    price_monthly: Optional[float] = None
    is_active: Optional[bool] = None

class SignalThemeResponse(BaseModel):
    id: int
    signal_group_id: int
    name: str
    description: Optional[str] = None
    keywords: Optional[str] = None
    price_monthly: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# SignalGroupThemeSubscription Schemas
class SignalGroupThemeSubscriptionBase(BaseModel):
    signal_group_id: int
    theme_id: int
    status: str = "active"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    monthly_price: float = 0.0

class SignalGroupThemeSubscriptionCreate(SignalGroupThemeSubscriptionBase):
    pass

class SignalGroupThemeSubscriptionUpdate(BaseModel):
    status: Optional[str] = None
    end_date: Optional[datetime] = None
    monthly_price: Optional[float] = None

class SignalGroupThemeSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    signal_group_id: int
    theme_id: int
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    monthly_price: float
    created_at: datetime

    class Config:
        from_attributes = True

# GroupWarning Schemas
class GroupWarningCreate(BaseModel):
    user_id: int
    group_id: int
    reason: Optional[str] = None
    issued_by: Optional[int] = None

class GroupWarningOut(BaseModel):
    id: int
    user_id: int
    group_id: int
    reason: Optional[str] = None
    issued_by: Optional[int] = None
    timestamp: datetime

    class Config:
        orm_mode = True

class GroupMuteCreate(BaseModel):
    user_id: int
    group_id: int
    duration_seconds: int
    reason: Optional[str] = None
    issued_by: Optional[int] = None

class GroupMuteOut(BaseModel):
    id: int
    user_id: int
    group_id: int
    start_time: datetime
    end_time: Optional[datetime]
    reason: Optional[str]
    issued_by: Optional[int]
    active: bool
    timestamp: datetime

    class Config:
        orm_mode = True

class GroupKickCreate(BaseModel):
    user_id: int
    group_id: int
    reason: Optional[str] = None
    issued_by: Optional[int] = None

class GroupKickOut(BaseModel):
    id: int
    user_id: int
    group_id: int
    reason: Optional[str]
    issued_by: Optional[int]
    timestamp: datetime

    class Config:
        orm_mode = True 