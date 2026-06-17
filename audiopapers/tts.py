"""Text-to-speech via any OpenAI-compatible /v1/audio/speech endpoint."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "tts-1"
DEFAULT_VOICE = "alloy"

_KEY_ENV_VARS = ("AUDIOPAPERS_API_KEY", "OPENAI_API_KEY")


@dataclass
class SynthArgs:
    model: str = DEFAULT_MODEL
    voice: str = DEFAULT_VOICE
    format: str = "mp3"
    speed: float = 1.0
    timeout: int = 180
    base_url: str = DEFAULT_BASE_URL


def candidate_api_keys() -> list[str]:
    """API keys from env (AUDIOPAPERS_API_KEY, then OPENAI_API_KEY), de-duplicated.

    Raises RuntimeError naming the env vars if none are set.
    """
    keys: list[str] = []
    for var in _KEY_ENV_VARS:
        val = os.environ.get(var)
        if val:
            keys.append(val.strip())
    seen: set[str] = set()
    keys = [k for k in keys if not (k in seen or seen.add(k))]
    if not keys:
        raise RuntimeError(
            "No API key found. Set AUDIOPAPERS_API_KEY (or OPENAI_API_KEY) "
            "to your TTS provider's key."
        )
    return keys


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Split text into chunks <= max_chars on paragraph then sentence breaks."""
    if len(text) <= max_chars:
        return [text]
    paragraphs = re.split(r"\n\s*\n", text)
    units: list[str] = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_chars:
            units.append(para)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", para)
        buf = ""
        for sent in sentences:
            if len(sent) > max_chars:
                if buf:
                    units.append(buf)
                    buf = ""
                for i in range(0, len(sent), max_chars):
                    units.append(sent[i : i + max_chars])
            elif len(buf) + len(sent) + 1 <= max_chars:
                buf = f"{buf} {sent}".strip()
            else:
                units.append(buf)
                buf = sent
        if buf:
            units.append(buf)
    chunks: list[str] = []
    buf = ""
    for unit in units:
        if not buf:
            buf = unit
        elif len(buf) + len(unit) + 2 <= max_chars:
            buf = f"{buf}\n\n{unit}"
        else:
            chunks.append(buf)
            buf = unit
    if buf:
        chunks.append(buf)
    return chunks


def synthesize(text: str, args: SynthArgs, api_keys: list[str]) -> bytes:
    """Call the speech endpoint, trying each key until one authenticates."""
    payload = json.dumps({
        "model": args.model,
        "input": text,
        "voice": args.voice,
        "response_format": args.format,
        "speed": args.speed,
    }).encode("utf-8")

    url = args.base_url.rstrip("/") + "/audio/speech"
    last_error = ""
    for key in api_keys:
        header_key = key if key.startswith("Bearer ") else f"Bearer {key}"
        request = urllib.request.Request(
            url, data=payload, method="POST",
            headers={"Authorization": header_key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace") if hasattr(exc, "read") else str(exc)
            if exc.code in (400, 401):
                last_error = f"HTTP {exc.code}: {detail}"
                continue
            raise RuntimeError(f"API returned HTTP {exc.code}\n{detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"could not reach {url}: {exc.reason}") from exc
    raise RuntimeError(f"no working API key (tried {len(api_keys)}). last: {last_error}")
