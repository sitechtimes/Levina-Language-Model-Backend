import whisper

model = whisper.load_model("turbo")
result = model.transcribe("audio3.wav", language="ru")
print(result["text"])




from phonemizer import phonemize
from Levenshtein import distance

# little note: Levenshtein distance algorithm computes the diffrenece between two strings by how many changes are needed to convert a string to another
# So like car -> bits would be 4 changes (c->b, a->i, r->t, add s)

text = result["text"]

correct_phones = phonemize(text, language="ru", backend="espeak", strip=True, preserve_punctuation=True, with_stress=True)

student_phones = ""
#Fill this in later with a way to get student phones

d = distance(correct_phones, student_phones)