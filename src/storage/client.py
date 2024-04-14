from supabase_py_async import AsyncClient, create_client
from config import SUPABASE_URL, SUPABASE_KEY

async def supabase_client(access_token: str = None) -> AsyncClient:
    '''
    Creates a Supabase client with the given access token.

    Args:
        access_token (str, optional): The access token to authenticate the client. Defaults to None.

    Returns:
        AsyncClient: The Supabase client instance.

    '''
    if access_token:
        return await create_client(SUPABASE_URL, SUPABASE_KEY, access_token=access_token)

    return await create_client(SUPABASE_URL, SUPABASE_KEY)
