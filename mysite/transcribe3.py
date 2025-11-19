# from whisper_phoneme import WhisperPhoneme

# model = WhisperPhoneme("small-v3")
# result = model.transcribe("audio.wav", output_phonemes=True)

# for ph in result["phonemes"]:
#     print(ph["phone"], ph["start"], ph["end"], ph["confidence"])


import torch
model, decoder, utils = torch.hub.load(
    'snakers4/silero-models',
    'silero_stt',
)

sample_rate = getattr(model, "sample_rate", 16000)

(read_batch, split_into_batches, read_audio, prepare_model_input) = utils
wav = read_audio('data/corpus/audio.wav')
input = prepare_model_input(wav, 16000)
output = model(input)
phonemes = decoder(output[0], skip_special_tokens=True)

print(phonemes)
