import threading
from typing import Optional, Tuple, List

import numpy as np
import sounddevice as sd


def list_input_devices():
    print(sd.query_devices())


def record_until_enter(
    samplerate: int = 16000,
    device: Optional[int] = None,
    channels: int = 1,
    dtype: str = "float32",
) -> np.ndarray:
    """
    Records audio from the mic until the user presses ENTER.

    Usage pattern in main:
      input("Press ENTER to start...")
      audio = record_until_enter(...)
    """
    frames: List[np.ndarray] = []
    stop_flag = threading.Event()

    def callback(indata, frames_count, time_info, status):
        if status:
            # you can print(status) if debugging
            pass
        frames.append(indata.copy())
        if stop_flag.is_set():
            raise sd.CallbackStop()

    # Start stream
    with sd.InputStream(
        samplerate=samplerate,
        device=device,
        channels=channels,
        dtype=dtype,
        callback=callback,
    ):
        input("Recording... press ENTER to stop > ")
        stop_flag.set()

    audio = np.concatenate(frames, axis=0) if frames else np.zeros((0, channels), dtype=np.float32)

    # Downmix to mono if needed
    if channels > 1 and audio.size:
        audio = np.mean(audio, axis=1, keepdims=False)
    elif channels == 1 and audio.size:
        audio = audio.reshape(-1)

    return audio.astype(np.float32)