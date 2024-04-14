from typing import Any, Tuple
import aiohttp
import pyaudio
import numpy as np

from deepgram import (
    DeepgramClient, 
    LiveOptions, 
    LiveTranscriptionEvents
)

from config import DEEPGRAM_API_KEY
from src.utils.audio_processing import u_law_d

class Player():
    '''
    Represents a player for streaming and transcribing live audio.

    Args:
        url (str): The URL of the audio stream.

    Attributes:
        url (str): The URL of the audio stream.
        p (pyaudio.PyAudio): The PyAudio instance.
        stream (pyaudio.Stream): The audio stream.
    '''

    def __init__(self, url: str) -> None:
        self.url = url
        self.p = pyaudio.PyAudio()
        self.stream = None
        
    async def stream_and_transcribe_live(self) -> None:
        '''
        Streams and transcribes live audio from the specified URL.

        Raises:
            RuntimeError: If the player is already running.
        '''
        if self.stream is not None:
            raise RuntimeError('Player is already running')
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    
        try:
            dg_connection, options = await self.__configure_deepgram()

            if not dg_connection.start(options):
                raise Exception('Failed to connect to Deepgram')
   
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    async for data in response.content.iter_chunked(1024):
                        decoded_bytes = await self.__decode_stream(data)

                        # Send data to Deepgram
                        dg_connection.send(decoded_bytes)

                        # Play audio
                        self.stream.write(decoded_bytes)

            # Indicate that we've finished
            dg_connection.finish()

            print('Playback complete.')
        except Exception as e:
            print(f'Error: {e}')
            await self.__cleanup()
        finally:
            await self.__cleanup()

    async def __configure_deepgram(self) -> Tuple[Any, LiveOptions]:
        '''
        Configures the Deepgram client and sets up the event callbacks.

        Returns:
            Tuple: A tuple containing the Deepgram connection and the options.
        '''
        try:
            deepgram = DeepgramClient(DEEPGRAM_API_KEY)
            dg_connection = deepgram.listen.live.v('1')

            # callback functions
            def on_message(self, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) == 0:
                    return
                print(f'speaker: {sentence}')

            def on_error(self, error, **kwargs):
                print(f'\n\n{error}\n\n')

            def on_unhandled(self, unhandled, **kwargs):
                print(f'\n\n{unhandled}\n\n')

            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            dg_connection.on(LiveTranscriptionEvents.Error, on_error)
            dg_connection.on(LiveTranscriptionEvents.Unhandled, on_unhandled)

            options: LiveOptions = LiveOptions(
                model='nova-2',
                punctuate=True,
                language='en-US',
                encoding='linear16',
                channels=1,
                sample_rate=16000,
                #interim_results=True,
                #utterance_end_ms='1000',
                endpointing=10,
                vad_events=True,
            )

            return dg_connection, options
        except Exception as e:
            print(f'Error configuring Deepgram: {e}')
            return
        
    async def __decode_stream(self, stream: bytes) -> bytes:
        '''
        Decodes the audio stream.

        Args:
            stream (bytes): The audio stream data.

        Returns:
            bytes: The decoded audio stream.
        '''
        data_uint8 = np.frombuffer(stream, dtype=np.uint8)
        decoded = np.array([u_law_d(sample) for sample in data_uint8], dtype=np.int16)
        return decoded.tobytes()
    
    async def __cleanup(self) -> None:
        '''
        Cleans up the player resources.
        '''
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        self.p.terminate()
        return
