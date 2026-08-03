# Long-audio ASR and diarization best practices

Research date: 2026-08-03

Scope: free, on-device podcast transcription on Apple Silicon with Argmax
WhisperKit and SpeakerKit. This note uses first-party repositories, source code,
official benchmarks, and original papers.

## Recommended production defaults

1. Use incremental audio loading and VAD for long files. Argmax documents that
   incremental loading bounds peak memory, applies VAD boundary detection, and
   should produce the same transcription as full-file loading with VAD. Keep the
   library defaults of 120-second staging chunks and two buffered chunks unless
   a repeatable benchmark justifies tuning them.
   [Argmax README](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/README.md#L160-L183)
   [AudioInputOptions source](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/WhisperKit/Core/Audio/AudioProcessor.swift#L44-L66)

2. Do not hard-split at arbitrary 30-second boundaries. The official VAD
   chunker splits at silence and includes padding to reduce boundary errors.
   The CLI defaults to four concurrent workers; expose this as an advanced
   control, but do not automatically set unlimited concurrency.
   [VAD chunker source](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/WhisperKit/Core/Audio/AudioChunker.swift#L42-L106)
   [CLI arguments](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/ArgmaxCLI/TranscribeCLIArguments.swift#L106-L119)

3. Set the language when it is known. The CLI uses the explicit language to
   prefill language/task/timestamp tokens and avoid unnecessary language
   detection. Keep automatic detection only for genuinely unknown inputs.
   [TranscribeCLIUtils](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/ArgmaxCLI/TranscribeCLIUtils.swift#L69-L91)

4. Use a short proper-noun prompt. WhisperKit exposes `--prompt`, and OpenAI's
   Whisper implementation describes `initial_prompt` as a way to improve custom
   vocabulary and proper nouns. Episode title, show name, guest name, and a
   user-supplied glossary may guide ASR, but they must never become transcript
   content by themselves.
   [WhisperKit prompt handling](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/ArgmaxCLI/TranscribeCLI.swift#L161-L170)
   [OpenAI Whisper transcription source](https://github.com/openai/whisper/blob/main/whisper/transcribe.py)

5. Use the recommended multilingual model for quality-sensitive podcasts.
   Argmax recommends `large-v3-v20240930_626MB` for maximum multilingual
   accuracy and `tiny` only for fast development loops.
   [Argmax model selection](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/README.md#model-selection)

6. Supply a known speaker count. SpeakerKit supports automatic estimation, but
   Argmax OpenBench shows that speaker-count accuracy varies substantially by
   dataset. A known two-person interview should pass `--speaker-count 2`.
   [SpeakerKit options](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/SpeakerKit/Pyannote/PyannoteConfig.swift#L129-L155)
   [Argmax OpenBench](https://github.com/argmaxinc/OpenBench/blob/main/BENCHMARKS.md)

## Speaker attribution

SpeakerKit's supported composition is: keep WhisperKit word timestamps as the
transcription source, then add speaker information by temporal matching. The
default `.subsegment` strategy splits at word gaps and assigns speakers by time
intersection. RTTM is an interchange/audit artifact, not the preferred text
source.

- [Combining transcription and diarization](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/README.md#combining-with-transcription)
- [`addSpeakerInfo` implementation](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/SpeakerKit/DiarizationResult.swift#L182-L210)
- [Word timestamps forced for diarization](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/ArgmaxCLI/TranscribeCLI.swift#L141-L144)

This repository's 129-minute validation episode confirms why this matters:

- RTTM text produced 613 ASCII-internal spaces such as `E v oken` and `PM F`.
- WhisperKit native words reduced that count to 82. The production quality gate
  retained 32,209 supported words from 32,213 native words, dropped four
  unsupported tail words, and consumed all 592 RTTM turns into 584 text-bearing
  speaker paragraphs.
- `Evoken`, `LibLib`, `PMF`, `Founder`, `Survive`, and `Token` were recovered
  without an LLM cleanup pass.

Therefore canonical transcript text should come from WhisperKit native words;
RTTM should supply only speaker attribution and remain available as a preserved
artifact.

## Long-audio diarization limitation

Incremental loading bounds WhisperKit ASR memory, but the combined CLI decodes
the complete audio again into a `[Float]` array for SpeakerKit. A 7,713-second,
16 kHz, Float32 mono recording needs about 494 MB for the raw array alone.
[TranscribeCLI diarization source](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/ArgmaxCLI/TranscribeCLI.swift#L461-L482)

Do not independently diarize chunks and concatenate Speaker A/B labels. Speaker
IDs are local to each run, and Argmax explicitly exposes centroid distance
without claiming a universal same-speaker threshold.
[DiarizationResult centroid API](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/SpeakerKit/DiarizationResult.swift#L34-L52)

Short-term product behavior:

- Keep ASR incremental.
- Run diarization as a distinct, explicit second phase.
- Fail clearly or allow an explicit no-speaker mode when memory is insufficient.
- Do not silently disable requested diarization.
- Treat chunked diarization plus cross-chunk voice linking as an experimental
  feature requiring a labeled calibration set.

## Reliability gates and audit artifacts

Argmax catches diarization errors and prints them without necessarily returning
a failing process status. Individual VAD chunks can also fail while other chunks
are merged. Exit code alone is therefore insufficient.

- [Diarization error handling](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/ArgmaxCLI/TranscribeCLI.swift#L294-L302)
- [VAD chunk error handling](https://github.com/argmaxinc/argmax-oss-swift/blob/97d09fd9790393579d2834e2bc098deb3e26bc06/Sources/WhisperKit/Core/Audio/AudioChunker.swift#L13-L38)

Required gates:

- Native JSON must exist and parse.
- Requested diarization must produce non-empty RTTM/speaker turns.
- Timestamps must be monotonic and non-negative after normalization; record
  native-order violations separately from canonical-order violations.
- Compare the last native timestamp with `timings.inputAudioSeconds` and record
  drift instead of treating the largest token timestamp as physical duration.
- Reject unsupported trailing words that occur beyond both physical audio and
  diarization coverage.
- Record segment count, word count, speaker count, first/last timestamp,
  fallback-aligned words, drift, pipeline time, and speed factor.
- Preserve source audio, native JSON, SRT, raw RTTM, CLI log, canonical JSON,
  metrics, and final Markdown.
- Bind the audio cache to its source URL and expected byte count; never reuse a
  same-named cache entry for a different URL.

## Evaluation strategy

Use stable, manually corrected regression clips rather than judging changes from
one full episode. Argmax OpenBench reports WER, DER, speaker-count accuracy,
word-level diarization error, and speed factor. Chinese product testing should
add CER and proper-noun recall.

- [Argmax OpenBench definitions and results](https://github.com/argmaxinc/OpenBench/blob/main/BENCHMARKS.md)
- [SDBench original paper](https://www.isca-archive.org/interspeech_2025/durmus25_interspeech.html)

Minimum internal set: 5–10 corrected Chinese interview clips covering Mandarin,
Chinese-English code switching, proper nouns, interruptions, background music,
and weak recording quality. Run the same set whenever model, prompt, VAD,
worker count, or speaker strategy changes.

## Implementation priority for this repository

1. **P0 quality:** native-word transcript plus RTTM-only speaker attribution.
2. **P0 correctness:** authoritative physical duration, tail/drift checks, and a
   machine-readable metrics artifact.
3. **P0 cache safety:** URL-bound manifest plus byte-length validation.
4. **P1 ASR guidance:** explicit/metadata-derived proper-noun prompt.
5. **P1 operability:** expose worker count, validate local model paths, preserve
   raw RTTM, and keep verbose model output in the log rather than flooding stdout.
6. **Later:** labeled CER/DER/WDER regression corpus and optional cross-chunk
   speaker linking research.
