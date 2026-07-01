# AudioPapers

Turn a paper you'd rather *hear* than read — Markdown, EPUB, a URL, or a plain
text file — into a chaptered `.m4b` audiobook. Built for anyone who finds long
reading or focusing hard: drop in a file, get an audiobook your podcast app can
play with chapter navigation.

You bring your own API key from any **OpenAI-compatible** text-to-speech
provider. Nothing is hosted; nothing leaves your machine except the text you
send to the provider you choose.

## Quickstart (3 steps)

1. **Install** (needs Python 3.11+ and [pipx](https://pipx.pypa.io)):

   ```
   pipx install git+https://github.com/adamsconchallos/audiopapers
   ```

2. **Set your API key** (any OpenAI-compatible TTS provider):

   ```
   # macOS/Linux
   export AUDIOPAPERS_API_KEY=sk-...
   # Windows PowerShell
   $env:AUDIOPAPERS_API_KEY = "sk-..."
   ```

   `OPENAI_API_KEY` is also accepted if it's already set.

3. **Convert a file:**

   ```
   audiopapers paper.md
   ```

   The `.m4b` is written to the current folder (or `out_dir` from your config).

## Choosing a provider

AudioPapers works with **any** OpenAI-compatible TTS endpoint. Pick the setup
that fits you:

| Setup | Cost | Config file needed? |
|-------|------|---------------------|
| **OpenAI** (default) | Paid (~$15 / 1M characters) | **No** — just set your key and run |
| **Local Kokoro** (self-hosted) | Free | Yes — point it at your local server |
| **Other gateway** (institutional, DeepInfra, …) | Varies | Yes — base URL + model + voice |

Out of the box AudioPapers talks to OpenAI's TTS (`tts-1`, voice `alloy`), so if
you have an OpenAI key you can **skip the config file entirely**: set the key
(step 2 above) and run. For anything else, create a config file (next section)
with the values for your provider:

| Provider | `api_base_url` | `model` | example `voice` |
|----------|----------------|---------|-----------------|
| OpenAI (default) | `https://api.openai.com/v1` | `tts-1` | `alloy` |
| Local Kokoro / FastAPI | `http://localhost:8880/v1` | `kokoro` | `af_heart` |
| Self-hosted / gateway | your endpoint `…/v1` | provider's model | provider's voice |

Any service exposing `POST {api_base_url}/audio/speech` with an OpenAI-style
JSON body works.

## Config file

**Only needed if you're not using OpenAI.** The quickest way to create one:

```bash
audiopapers --init
```

That writes a starter `audiopapers.config.json` to your per-user config folder
(`%APPDATA%\audiopapers\` on Windows, `~/.config/audiopapers/` elsewhere) and
prints the path. Open it, set `api_base_url`, `model`, and `voice` for your
provider (see the tables above), and it applies to every run, from any folder.

AudioPapers looks for the config in the folder you run from first, then that
per-user folder; the first one found wins. To keep it somewhere else, pass
`--config /path/to/config.json` on each run. The starter looks like:

```json
{
  "out_dir": ".",
  "api_base_url": "https://api.openai.com/v1",
  "model": "tts-1",
  "voice": "alloy",
  "bitrate_k": 48,
  "chapter_level": 2,
  "author": "AudioPapers"
}
```

If you cloned the repo instead of installing with pipx, you can copy the starter
file by hand instead: `cp audiopapers.config.example.json audiopapers.config.json`.

Every value can be overridden per run with a CLI flag (`--voice`, `--bitrate`,
`--chapter-level`, `--author`, `--cover`, `--title`, `--out`, `--include`).

## Supported sources

| Extension / prefix | Adapter |
|--------------------|---------|
| `.md` | Markdown |
| `.epub` | EPUB (spine order; `--include` filters by idref) |
| `http://`, `https://` | URL (main article body) |
| `.txt` or other | Plain text |

## Bitrate & chapters

- `bitrate_k`: `48` (default, ~3.5 MB/hr), `32` (smaller), `24` (minimal). AAC mono.
- `chapter_level`: `2` chapters on `#` and `##` headings (default); `1` chapters
  on `#` only. Deeper headings insert a short pause but no chapter marker.

## Troubleshooting

- **"No API key found"** — set `AUDIOPAPERS_API_KEY` (or `OPENAI_API_KEY`) in the
  shell you run `audiopapers` from.
- **HTTP 401 / 400** — wrong key for the chosen `api_base_url`, or a `model`/`voice`
  the provider doesn't offer. Check the provider's docs for valid values.
- **Can't reach the endpoint** — verify `api_base_url` (must end in `/v1`) and that
  a local server, if any, is running.
- **Config seems ignored** — the file must be named `audiopapers.config.json` and
  sit in the folder you run `audiopapers` from or your per-user config folder (or
  pass `--config <path>`). `audiopapers --init` puts one in the right place.

## Development

```bash
git clone https://github.com/adamsconchallos/audiopapers
cd audiopapers
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
