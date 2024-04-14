from typing import Any
from src.storage import supabase_client

class AuthManager:
    '''
    This class provides methods for registering new users, logging in existing users,
    and logging out the currently authenticated user.
    '''

    async def register(self, email: str, password: str) -> Any:
        '''
        Registers a new user with the provided email and password.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            AuthResponse: The response from the registration request.
        '''
        supabase = await supabase_client()
        response = await supabase.auth.sign_up({
            'email': email,
            'password': password
        })
        return response

    async def login(self, email: str, password: str) -> Any:
        '''
        Logs in a user with the provided email and password.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            AuthResponse: The response from the login request.
        '''
        supabase = await supabase_client()
        response = await supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        if response:
            from .session_cache import session
            session.authenticate(response.session)
        return response

    async def logout(self) -> None:
        '''
        Logs out the currently authenticated user.

        Raises:
            Exception: If the user is not authenticated.
        '''
        from .session_cache import session
        if not session.is_authenticated():
            raise Exception('User is not authenticated. Please log in first.')
        supabase = await supabase_client(access_token=session.get_token())
        await supabase.auth.sign_out()
        session.deauthenticate()
