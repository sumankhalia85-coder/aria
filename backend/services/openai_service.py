import io
from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY, GPT_MODEL, WHISPER_MODEL, TTS_MODEL, TTS_VOICE

# Initialize client with API key if available, otherwise with a placeholder
client = AsyncOpenAI(api_key=OPENAI_API_KEY or "sk-placeholder")

async def chat_completion(messages: list, json_mode: bool = False) -> str:
    kwargs = {"model": GPT_MODEL, "messages": messages, "temperature": 0.7}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
        kwargs["temperature"] = 0.3
    resp = await client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content

async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    # Ensure filename has correct extension for Whisper
    supported_exts = ['.webm', '.mp4', '.mp3', '.wav', '.ogg', '.m4a', '.mpeg', '.mpga']
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext not in supported_exts:
        filename = "audio.webm"
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename
    transcript = await client.audio.transcriptions.create(
        model=WHISPER_MODEL,
        file=audio_file,
        response_format="text"
    )
    return transcript if isinstance(transcript, str) else transcript.text

async def text_to_speech(text: str) -> bytes:
    response = await client.audio.speech.create(
        model=TTS_MODEL, voice=TTS_VOICE, input=text[:4096]
    )
    return response.content
