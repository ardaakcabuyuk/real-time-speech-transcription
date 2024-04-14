import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.environ.get('SUPABASE_URL')
SUPABASE_KEY: str = os.environ.get('SUPABASE_KEY')
DEEPGRAM_API_KEY: str = os.environ.get('DEEPGRAM_KEY')
OPENAI_API_KEY: str = os.environ.get('OPENAI_KEY')

AUDIO_FILE_PATH: str = os.path.join(os.getcwd(), 'audio_files')
AUDIO_FILE_NAME: str = 'recording.wav'

if not os.path.exists(AUDIO_FILE_PATH):
  os.makedirs(AUDIO_FILE_PATH)

SUMMARIZE_PROMPT: str = 'You will be given a transcript of an audio recording. Summarize the text in 100 words or less.'

