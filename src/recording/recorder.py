import asyncio
import os
from typing import Any, Tuple
from scipy.io.wavfile import write
import numpy as np
from deepgram import (
    DeepgramClient,
    LiveOptions,
    LiveTranscriptionEvents,
    Microphone
)

from config import DEEPGRAM_API_KEY, AUDIO_FILE_PATH, AUDIO_FILE_NAME
from src.utils.audio_processing import u_law_e

class Recorder():
    '''
    The Recorder class is responsible for recording audio and performing real-time speech transcription.

    Attributes:
        recording (bytearray): The recorded audio data.

    Methods:
        record_and_transcribe_live: Starts recording audio and performs real-time speech transcription.
        delete_recording: Deletes the recorded audio file.
    '''

    def __init__(self) -> None:
        self.recording = None
        self.transcription = ''

    async def record_and_transcribe_live(self) -> str:
        '''
        Starts recording audio and performs real-time speech transcription.

        Returns:
            str: The transcription of the recorded speech.

        Raises:
            RuntimeError: If the recorder is already running.
        '''
        if self.recording is not None:
            raise RuntimeError('Recorder is already running')
        self.recording = bytearray()

        try:
            dg_connection, options = await self.__configure_deepgram()

            if dg_connection.start(options) is False:
                print('Failed to connect to Deepgram')
                return

            def microphone_callback(data):
                self.recording.extend(data)
                dg_connection.send(data)

            microphone = Microphone(microphone_callback)

            print('Recording... Press Enter to stop recording.')

            # start microphone
            microphone.start()
            input('')
            microphone.finish()
            dg_connection.finish()

            print('Recording complete.\n')

            print('Processing recording...')
            await self.__process_and_save_recording(self.recording)
            print('Recording processed.\n')

            return self.transcription

        except Exception as e:
            print(f'Recording error: {e}')
            return
        finally:
            self.__cleanup()
    
    def __cleanup(self) -> None:
        '''
        Cleans up the recorder by resetting the recording and transcription attributes.
        '''
        self.recording = None
        self.transcription = ''

    async def __configure_deepgram(self) -> Tuple[Any, LiveOptions]:
        '''
        Configures the Deepgram client and sets up the connection for real-time transcription.

        Returns:
            Tuple: A tuple containing the Deepgram connection and the transcription options.
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
                extend_transcription(sentence)

            def extend_transcription(sentence):
                self.transcription += f'{sentence} '

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
                # interim_results=True,
                # utterance_end_ms='1000',
                endpointing=10,
                vad_events=True,
            )

            return dg_connection, options
        except Exception as e:
            print(f'Error configuring Deepgram: {e}')
            return

    async def __process_and_save_recording(self, recording: bytes) -> None:
        '''
        Processes and saves the recorded audio.

        Args:
            recording (bytes): The recorded audio data.
        '''

        # Convert the bytearray to a numpy array of int16
        int16_array = np.frombuffer(recording, dtype=np.int16)
        # convert np.int16 array to int array
        int_array = [int(sample) for sample in int16_array]
        # Encode each sample using the u_law_e function
        encoded_recording = np.array([u_law_e(sample) for sample in int_array], dtype=np.uint8)
        # Save the encoded recording to a WAV file
        await asyncio.to_thread(write, f'{AUDIO_FILE_PATH}/{AUDIO_FILE_NAME}', 16000, encoded_recording)

    async def delete_recording(self) -> None:
        '''
        Deletes the recorded audio file.
        '''
        try:
            await asyncio.to_thread(os.remove, f'{AUDIO_FILE_PATH}/{AUDIO_FILE_NAME}')
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise e
