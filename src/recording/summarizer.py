from openai import AsyncOpenAI
from config import OPENAI_API_KEY, SUMMARIZE_PROMPT

class Summarizer:
    '''
    A class that summarizes the transcribed speech using OpenAI's GPT-4.
    '''

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def summarize(self, transcription: str) -> str:
        '''
        Summarizes the transcribed speech using OpenAI's GPT-4.

        Args:
            text (str): The transcribed speech.

        Returns:
            str: The summarized text.
        '''

        response = await self.client.chat.completions.create(
            messages = [
                {
                    'role': 'system',
                    'content': SUMMARIZE_PROMPT
                },
                {
                    'role': 'user',
                    'content': transcription
                }
            ],
            model='gpt-4',
            max_tokens=256
        )

        return response.choices[0].message.content
        
