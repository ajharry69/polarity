from enum import Enum, auto


class SignInMethod(Enum):
    EMAIL = auto()
    GOOGLE = auto()
    FACEBOOK = auto()
    TWITTER = auto()
    GITHUB = auto()
    APPLE = auto()

    @staticmethod
    def value_of(value, default=EMAIL) -> Enum:
        if value is not None:
            for k, v in SignInMethod.__members__.items():
                if k == value.upper():
                    return v
        return default
