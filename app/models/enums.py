import enum


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"

class SubscriptionStatus(enum.Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    POST_DUE = "POST_DUE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class BillingCycle(enum.Enum):
    MONTHLY = "MONTHLY"
    ANNUAL = "ANNUAL"

class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

