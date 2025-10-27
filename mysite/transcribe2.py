import whisperx
from phonemizer import phonemize


audio_file = "audio.wav"

#STep 1: transcribe the audio
model = whisperx.load_model("small", device="cuda")
result = model.transcribe(audio_file, language="ru")
print("Transcription:", result)

#Then align the transcription (this means get the word-level timestamps)
align_model, metadata = whisperx.load_align_model(language_code="ru", device="cuda")
aligned = whisperx.align(result["segments"], align_model, metadata, audio_file, device="cuda")
print("Aligned", aligned)

# Cycle through the result and grab those phonemes
for segment in aligned["segments"]:
    phonemes = phonemize(segment["text"], language="ru", backend="espeak", strip=True, preserve_punctuation=True, with_stress=False)
    print(f'Segment {segment["id"]}: {phonemes}')
