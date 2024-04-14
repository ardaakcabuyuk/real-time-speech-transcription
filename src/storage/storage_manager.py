import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiofiles
from config import AUDIO_FILE_PATH, AUDIO_FILE_NAME
from .client import supabase_client

class StorageManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor()
    '''
    A class that manages the storage operations for recordings.
    '''

    async def upload_recording(self, name: str) -> None:
        '''
        Uploads a recording to the storage.

        Args:
            name (str): The name of the recording.

        Raises:
            Exception: If the user is not authenticated 
            or if there is an error creating the recording record in the database.
        '''

        from src.auth import session
        if session.is_authenticated():
            supabase = await supabase_client(session.get_token())

            # first, create a database record for the recording
            response = await supabase.table('recordings').insert({'name': name}).execute()

            if response:
                # get the ID of the newly created record
                recording_id = response.data[0]['id']
                user_id = session.get_user().id
                # upload the file to {user_id}/{recording_id}
                async with aiofiles.open(f'{AUDIO_FILE_PATH}/{AUDIO_FILE_NAME}', 'rb') as f:
                    file = await f.read()

                await supabase.storage.from_('recordings').upload(
                    file=file,
                    path=f'{user_id}/{recording_id}',
                    file_options={'content-type': 'audio/wav'}
                )
            else:
                raise Exception('Failed to create a new recording record in the database.')
        else:
            raise Exception('User is not authenticated. Please log in first.')
        
    async def list_recordings(self) -> list:
        '''
        Lists all the recordings for the authenticated user.

        Returns:
            list: A list of tuples containing the recording ID and name.

        Raises:
            Exception: If the user is not authenticated 
            or if there is an error fetching the recordings from the database.
        '''
        from src.auth import session
        if session.is_authenticated():   
            supabase = await supabase_client(session.get_token())

            # get all recordings for the user
            user_id = session.get_user().id
            response = await supabase.table('recordings').select('*').eq('user_id', user_id).execute()

            if response:
                return [(recording['id'], recording['name']) for recording in response.data]
            
            raise Exception('Failed to fetch recordings from the database.')
        
        raise Exception('User is not authenticated. Please log in first.')
        
    async def get_stream_url(self, recording_id: str) -> str:
        '''
        Retrieves the public stream URL for a recording.

        Args:
            recording_id (str): The ID of the recording.

        Returns:
            str: The public stream URL of the recording.

        Raises:
            Exception: If the user is not authenticated 
            or if there is an error retrieving the stream URL.
        '''
        from src.auth import session
        if session.is_authenticated():
            supabase = await supabase_client(session.get_token())
            user_id = session.get_user().id
            res = await supabase.storage.from_('recordings').create_signed_url(f'{user_id}/{recording_id}', 600)
            return res['signedURL']
        
        raise Exception('User is not authenticated. Please log in first.')
