from enum import Enum, auto


class AuthProvider(Enum):
    EMAIL = auto()
    GOOGLE = auto()
    FACEBOOK = auto()
    TWITTER = auto()
    GITHUB = auto()
    APPLE = auto()

    @staticmethod
    def value_of(value, default=EMAIL) -> Enum:
        if value is not None:
            for k, v in AuthProvider.__members__.items():
                if k == value.upper():
                    return v
        return default


class PasswordResetType(Enum):
    CHANGE = auto()
    RESET = auto()

    @staticmethod
    def value_of(value, default=RESET) -> Enum:
        if value is not None:
            for k, v in PasswordResetType.__members__.items():
                if k == value.upper():
                    return v
        return default
