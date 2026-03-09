from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GoogleUserInfo:
    googleSub: str
    name: str
    email: str
