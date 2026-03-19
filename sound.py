"""Generates and plays a mindfulness bell sound."""
import wave, math, struct, os, subprocess


def _generate_bell(path: str):
    freq        = 440          # fundamental (A4)
    sample_rate = 44100
    duration    = 3.0

    n = int(sample_rate * duration)
    samples = []
    for i in range(n):
        t = i / sample_rate
        # Short attack, long exponential decay
        env = (t / 0.008) if t < 0.008 else math.exp(-1.6 * (t - 0.008))
        # Inharmonic partials characteristic of metal bells
        s = env * (
            0.50 * math.sin(2 * math.pi * freq * 1.000 * t) +
            0.25 * math.sin(2 * math.pi * freq * 2.756 * t) +
            0.12 * math.sin(2 * math.pi * freq * 5.404 * t) +
            0.08 * math.sin(2 * math.pi * freq * 8.933 * t) +
            0.05 * math.sin(2 * math.pi * freq * 13.34 * t)
        )
        samples.append(max(-32767, min(32767, int(s * 32767))))

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{n}h", *samples))


def get_bell_path() -> str:
    data_dir = os.path.expanduser("~/.mindful_path")
    path = os.path.join(data_dir, "bell.wav")
    if not os.path.exists(path):
        _generate_bell(path)
    return path


def play_bell():
    """Play the bell sound non-blocking. Silent on failure."""
    path = get_bell_path()
    for cmd in (["paplay", path], ["aplay", "-q", path]):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except FileNotFoundError:
            continue
