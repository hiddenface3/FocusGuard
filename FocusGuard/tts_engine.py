"""
TTS Engine — uses Microsoft Edge TTS (edge-tts) or Google Gemini Flash TTS with local MP3 caching.
Only re-generates audio when the phrase, voice, or TTS system changes (hash-based cache).
"""

import asyncio
import hashlib
import os
import threading

import pygame

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

KOKORO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kokoro_onnx_data")
KOKORO_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
KOKORO_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"


def _get_cache_path(phrase: str, voice: str, is_htts: bool = True, is_gemini: bool = False, is_kokoro: bool = False) -> str:
    key = hashlib.md5(f"{phrase}|||{voice}|||{is_htts}|||{is_gemini}|||{is_kokoro}".encode("utf-8")).hexdigest()
    ext = ".wav" if (is_gemini or is_kokoro or not is_htts) else ".mp3"
    return os.path.join(CACHE_DIR, f"{key}{ext}")


def _generate_tts_local_sync(phrase: str, output_path: str):
    """Blocking TTS generation — runs pyttsx3 locally without internet."""
    import pyttsx3
    engine = pyttsx3.init()
    engine.save_to_file(phrase, output_path)
    engine.runAndWait()


def _generate_tts_sync(phrase: str, voice: str, output_path: str):
    """Blocking TTS generation — runs edge-tts in a fresh event loop."""
    import edge_tts

    async def _gen():
        communicate = edge_tts.Communicate(phrase, voice)
        await communicate.save(output_path)

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_gen())
    finally:
        loop.close()


def _generate_tts_gemini_sync(phrase: str, voice: str, api_key: str, output_path: str):
    """Blocking TTS generation — runs google-genai using Gemini 2.5 Flash."""
    import os
    import struct
    from google import genai
    from google.genai import types

    voice_name = voice
    if voice_name.startswith("gemini-"):
        voice_name = voice_name.split("gemini-")[1]

    # Configure API key in environment
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    elif "GEMINI_API_KEY" not in os.environ:
        # Check standard config or settings, but raise if completely missing
        raise ValueError("GEMINI_API_KEY environment variable or config key is not set.")

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=phrase,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            )
        )
    )

    audio_bytes = None
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                audio_bytes = part.inline_data.data
                break

    if not audio_bytes:
        raise ValueError("No audio content returned in Gemini response.")

    # Write WAV header for 24kHz Mono 16-bit PCM
    subchunk2_size = len(audio_bytes)
    chunk_size = 36 + subchunk2_size
    sample_rate = 24000
    num_channels = 1
    bits_per_sample = 16
    byte_rate = int(sample_rate * num_channels * bits_per_sample / 8)
    block_align = int(num_channels * bits_per_sample / 8)
    
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        chunk_size,
        b'WAVE',
        b'fmt ',
        16,
        1,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        subchunk2_size
    )

    with open(output_path, "wb") as f:
        f.write(header + audio_bytes)


_kokoro_download_lock = threading.Lock()
_kokoro_instance = None
_kokoro_instance_lock = threading.Lock()

def _check_and_download_kokoro_files():
    """Ensure local Kokoro model assets (~108MB) exist, downloading them in background if missing."""
    with _kokoro_download_lock:
        os.makedirs(KOKORO_DIR, exist_ok=True)
        model_path = os.path.join(KOKORO_DIR, "kokoro-v1.0.int8.onnx")
        voices_path = os.path.join(KOKORO_DIR, "voices-v1.0.bin")
        
        # Double check existence under lock
        if os.path.exists(model_path) and os.path.exists(voices_path):
            return
            
        import urllib.request
        
        if not os.path.exists(model_path):
            print(f"[TTS] Downloading Kokoro model (88MB)...")
            temp_path = model_path + ".tmp"
            try:
                urllib.request.urlretrieve(KOKORO_MODEL_URL, temp_path)
                if os.path.exists(model_path):
                    os.remove(model_path)
                os.rename(temp_path, model_path)
                print(f"[TTS] Kokoro model downloaded successfully.")
            except Exception as e:
                if os.path.exists(temp_path):
                    try: os.remove(temp_path)
                    except: pass
                raise e
            
        if not os.path.exists(voices_path):
            print(f"[TTS] Downloading Kokoro voices (20MB)...")
            temp_path = voices_path + ".tmp"
            try:
                urllib.request.urlretrieve(KOKORO_VOICES_URL, temp_path)
                if os.path.exists(voices_path):
                    os.remove(voices_path)
                os.rename(temp_path, voices_path)
                print(f"[TTS] Kokoro voices downloaded successfully.")
            except Exception as e:
                if os.path.exists(temp_path):
                    try: os.remove(temp_path)
                    except: pass
                raise e


def _generate_tts_kokoro_sync(phrase: str, voice: str, output_path: str):
    """Blocking TTS generation — runs Kokoro-ONNX locally."""
    global _kokoro_instance
    _check_and_download_kokoro_files()
    
    from kokoro_onnx import Kokoro
    import soundfile as sf
    import onnxruntime as ort
    
    model_path = os.path.join(KOKORO_DIR, "kokoro-v1.0.int8.onnx")
    voices_path = os.path.join(KOKORO_DIR, "voices-v1.0.bin")
    
    # Clean voice prefix if it starts with "kokoro-"
    clean_voice = voice
    if clean_voice.startswith("kokoro-"):
        clean_voice = clean_voice.split("kokoro-")[1]
        
    with _kokoro_instance_lock:
        if _kokoro_instance is None:
            # We configure session options to limit threads to 2 (to prevent CPU spikes)
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.inter_op_num_threads = 1
            
            # Use CPUExecutionProvider
            providers = ["CPUExecutionProvider"]
            import importlib.util
            gpu_enabled = importlib.util.find_spec("onnxruntime-gpu")
            if gpu_enabled:
                providers = ort.get_available_providers()
                
            env_provider = os.getenv("ONNX_PROVIDER")
            if env_provider:
                providers = [env_provider]
                
            sess = ort.InferenceSession(model_path, sess_options=opts, providers=providers)
            _kokoro_instance = Kokoro.from_session(sess, voices_path)
            
        kokoro = _kokoro_instance
    
    # Determine language (if British voice, use en-gb, else en-us)
    lang = "en-gb" if clean_voice.startswith("b") else "en-us"
    
    samples, sample_rate = kokoro.create(
        phrase,
        voice=clean_voice,
        speed=1.0,
        lang=lang
    )
    
    sf.write(output_path, samples, sample_rate)


def _generate_with_fallback(phrase: str, voice: str, use_htts: bool, use_gemini: bool, use_kokoro: bool, gemini_api_key: str, path: str):
    """Attempts generation based on use_kokoro, use_gemini, and use_htts, falling back if necessary."""
    if use_kokoro or (voice and voice.startswith("kokoro-")):
        try:
            _generate_tts_kokoro_sync(phrase, voice, path)
            return
        except Exception as e:
            print(f"[TTS] Kokoro TTS failed, falling back: {e}")
            # Fall through to other options

    if use_gemini or (voice and voice.startswith("gemini-")):
        try:
            _generate_tts_gemini_sync(phrase, voice, gemini_api_key, path)
            return
        except Exception as e:
            print(f"[TTS] Gemini TTS failed, falling back: {e}")
            # Fall through to edge-tts/local
    
    if use_htts:
        try:
            edge_voice = voice
            if edge_voice.startswith("gemini-") or edge_voice.startswith("kokoro-"):
                edge_voice = "en-US-AriaNeural"
            _generate_tts_sync(phrase, edge_voice, path)
            return
        except Exception as e:
            print(f"[TTS] HTTS failed, falling back to local: {e}")
            # Fall through to local
    
    # Local fallback or default
    try:
        _generate_tts_local_sync(phrase, path)
    except Exception as e:
        print(f"[TTS] Local TTS generation error: {e}")
        # If local fails and we haven't tried HTTS yet, try HTTS as a last resort
        if not use_htts and not use_gemini and not use_kokoro:
            print(f"[TTS] Attempting HTTS as fallback...")
            edge_voice = voice
            if edge_voice.startswith("gemini-") or edge_voice.startswith("kokoro-"):
                edge_voice = "en-US-AriaNeural"
            _generate_tts_sync(phrase, edge_voice, path)
        else:
            raise


def _is_valid_cache(path: str) -> bool:
    """Check if the cache file exists and is not empty or corrupted (at least larger than 44 bytes)."""
    try:
        return os.path.exists(path) and os.path.getsize(path) > 44
    except Exception:
        return False


class TTSEngine:
    """Thread-safe TTS engine with caching and pygame audio playback."""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def prepare(self, phrase: str, voice: str = "en-US-AriaNeural",
                use_htts: bool = False, use_gemini: bool = False, use_kokoro: bool = False,
                gemini_api_key: str = "", on_done=None):
        """
        Pre-generate (and cache) TTS for a phrase.
        Non-blocking when on_done callback is provided.
        """
        def _work():
            path = _get_cache_path(phrase, voice, use_htts, use_gemini, use_kokoro)
            if not _is_valid_cache(path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
                try:
                    _generate_with_fallback(phrase, voice, use_htts, use_gemini, use_kokoro, gemini_api_key, path)
                except Exception as e:
                    print(f"[TTS] Generation error: {e}")
                    if on_done:
                        on_done(False)
                    return
            if on_done:
                on_done(True)

        t = threading.Thread(target=_work, daemon=True)
        t.start()
        if on_done is None:
            t.join()

    def prepare_many(self, phrases: list[str], voice: str = "en-US-AriaNeural", use_htts: bool = False,
                     use_gemini: bool = False, use_kokoro: bool = False, gemini_api_key: str = ""):
        """Pre-generates multiple phrases asynchronously."""
        def _work():
            for p in phrases:
                if not p.strip(): continue
                path = _get_cache_path(p, voice, use_htts, use_gemini, use_kokoro)
                if not _is_valid_cache(path):
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                        except:
                            pass
                    try:
                        _generate_with_fallback(p, voice, use_htts, use_gemini, use_kokoro, gemini_api_key, path)
                    except:
                        pass
        threading.Thread(target=_work, daemon=True).start()

    def speak(self, phrase: str, voice: str = "en-US-AriaNeural", use_htts: bool = False,
              use_gemini: bool = False, use_kokoro: bool = False, gemini_api_key: str = ""):
        """Speak phrase. Generates if not cached. Always non-blocking."""
        def _work():
            path = _get_cache_path(phrase, voice, use_htts, use_gemini, use_kokoro)
            if not _is_valid_cache(path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
                try:
                    _generate_with_fallback(phrase, voice, use_htts, use_gemini, use_kokoro, gemini_api_key, path)
                except Exception as e:
                    print(f"[TTS] Final Generation error: {e}")
                    return
            with self._lock:
                try:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"[TTS] Playback error: {e}")

        threading.Thread(target=_work, daemon=True).start()

    def is_speaking(self) -> bool:
        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return False

    def stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def unload_kokoro(self):
        """Unload Kokoro ONNX model from memory if loaded."""
        global _kokoro_instance
        with _kokoro_instance_lock:
            if _kokoro_instance is not None:
                _kokoro_instance = None
                print("[TTS] Unloaded Kokoro ONNX model from memory.")

    def cleanup(self):
        global _kokoro_instance
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        with _kokoro_instance_lock:
            _kokoro_instance = None
