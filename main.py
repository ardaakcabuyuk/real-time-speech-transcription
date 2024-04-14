import asyncio
import getpass
import logging
from pick import pick
from supabase_py_async import StorageException

from src.auth import AuthManager
from src.storage import StorageManager
from src.recording import Recorder
from src.recording import Player
from src.recording import Summarizer

logging.getLogger('httpx').setLevel(logging.WARNING)

class SpeechTranscriptionApp:
    '''
    A command-line application for real-time speech transcription.

    This application allows users to register, login, record and transcribe speech, 
    upload recordings, list and play recordings, and logout.

    Attributes:
        auth_manager (AuthManager): An instance of the AuthManager class for user authentication.
        storage (StorageManager): An instance of the StorageManager class for managing recordings.

    Methods:
        run: Runs the application.
        _welcome_screen: Displays the welcome screen and handles user actions.
        _register: Registers a new user.
        _login: Logs in an existing user.
        _main_menu: Displays the main menu and handles user actions.
        _new_recording: Records and transcribes speech, and lets the user upload the recording.
        _list_recordings: Lists the user's recordings and lets the user play a selected recording.
        _logout: Logs out the user and returns to the welcome screen.
    '''

    def __init__(self) -> None:
        self.auth_manager = AuthManager()
        self.storage = StorageManager()

    async def run(self) -> None:
        '''
        Runs the application.
        '''
        print('Welcome to Speech Transcription App!')
        await self._welcome_screen()

    async def _welcome_screen(self) -> None:
        '''
        Displays the welcome screen and handles user actions.
        '''
        actions = {
            '0': self._register,
            '1': self._login,
            '2': exit
        }

        while True:
            # without pick, simple input() can be used
            print('\n0: Register\n1: Login\n2: Exit\n')
            choice = input('Select an option: ')

            action = actions.get(choice)
            if action:
                await action()
            else:
                print('Invalid choice. Please try again.\n')

    async def _register(self) -> None:
        email = input('Enter email: ')
        password = getpass.getpass('Enter password: ')

        try:
            await self.auth_manager.register(email, password)
        except Exception as e:
            print(f'Registration failed: {e}\n')

    async def _login(self) -> None:
        email = input('Enter email: ')
        password = getpass.getpass('Enter password: ')
        success = False

        try:
            success = await self.auth_manager.login(email, password)
        except Exception as e:
            print(f'Login failed: {e}\n')

        if success:
            await self._main_menu()

    async def _main_menu(self) -> None:
        choices = {
            '0': self._new_recording,
            '1': self._list_recordings,
            '2': self._logout
        }

        while True:
            print('\n0: Record\n1: List Recordings\n2: Logout\n')
            choice = input('Select an option: ')
            action = choices.get(choice)
            if action:
                await action()

    async def _new_recording(self) -> None:
        recorder = Recorder()
        transcription = await recorder.record_and_transcribe_live()

        print('\nDo you want to summarize the recording?\n')
        print('0: Yes\n1: No\n')
        choice = input('Select an option: ')
        if choice == '0':
            summarizer = Summarizer()
            try:
                summary = await summarizer.summarize(transcription)
                print(f'\nSummary: {summary}')
            except Exception as e:
                print(f'Failed to summarize speech: {e}')


        print('\nDo you want to upload the recording?\n')
        print('0: Upload\n1: Discard\n')
        choice = input('Select an option: ')

        if choice == '0':
            name = input('Give your recording a name: ')
            try:
                await self.storage.upload_recording(name)
                print('Recording uploaded successfully!\n')
            except StorageException as e:
                print(f'Failed to upload recording: {e}\n')
            except Exception as e:
                # print(f'An unexpected error occurred while uploading: {e}')
                raise e
        
        try:
            await recorder.delete_recording()
        except FileNotFoundError as e:
            print(f'Failed to delete recording: {e.strerror}\n')
        except Exception as e:
            print(f'An unexpected error occurred while discarding: {e}\n')

    async def _list_recordings(self) -> None:
        try:
            recordings = await self.storage.list_recordings()
            if not recordings:
                print('No recordings found.\n')
                return            
            _, index = pick([r[1] for r in recordings], 'Select a recording to listen:')
            recording_id = recordings[index][0]
            url = await self.storage.get_stream_url(recording_id)
            player = Player(url)
            await player.stream_and_transcribe_live()
        except StorageException as e:
            print(f'Failed to list or play recordings: {e}\n')
        except Exception as e:
            print(f'An unexpected error occurred while listing recordings: {e}\n')

    async def _logout(self) -> None:
        try:
            await self.auth_manager.logout()
            print('Logged out successfully.\n')
        except Exception as e:
            print(f'Failed to logout: {e}\n')
        finally:
            await self._welcome_screen()

if __name__ == '__main__':
    app = SpeechTranscriptionApp()
    asyncio.run(app.run())
