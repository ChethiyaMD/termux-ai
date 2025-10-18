import os, tempfile, platform
try:
    import sounddevice as sd
    import wavio
except ImportError:
    sd = None
    wavio = None

console_msg = lambda x: print(f"[Voice] {x}")

def tts_play(text):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return
    except Exception:
        console_msg("pyttsx3 failed, using gTTS fallback")
    try:
        from gtts import gTTS
        tmpfile = os.path.join(tempfile.gettempdir(), "chethiya_md.mp3")
        tts = gTTS(text)
        tts.save(tmpfile)
        if platform.system().lower() in ("linux","android"):
            os.system(f"termux-media-player play {tmpfile} >/dev/null 2>&1 || ffplay -nodisp -autoexit {tmpfile} >/dev/null 2>&1")
        else:
            os.system(f"start {tmpfile}")
    except Exception as e:
        console_msg(f"gTTS failed: {e}")

def record_seconds(seconds=5, fs=16000):
    if sd is None or wavio is None:
        console_msg("sounddevice/wavio not installed; cannot record")
        return None
    console_msg(f"Recording {seconds} seconds...")
    data = sd.rec(int(seconds*fs), samplerate=fs, channels=1)
    sd.wait()
    tmpfile = os.path.join(tempfile.gettempdir(), "chethiya_md_record.wav")
    wavio.write(tmpfile, data, fs, sampwidth=2)
    console_msg(f"Saved: {tmpfile}")
    return tmpfile