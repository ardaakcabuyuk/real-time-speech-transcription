from typing import Any

class SessionCache:
    '''
    This class represents a session cache for storing authentication information.
    '''

    def __init__(self) -> None:
        self.token = None
        self.user = None

    def authenticate(self, session) -> None:
        self.token = session.access_token
        self.user = session.user

    def deauthenticate(self) -> None:
        self.token = None
        self.user = None

    def is_authenticated(self) -> bool:
        return self.token is not None and self.user is not None

    def get_user(self) -> Any:
        return self.user

    def get_token(self) -> str:
        return self.token

session = SessionCache()
