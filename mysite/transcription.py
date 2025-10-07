from speech_interpretation import SpeechInterpreter
from speech_detection import SpeechDetection

interpreter = SpeechInterpreter()
dectector = SpeechDetection()
speech_detection_result = dectector.transcribe("audio.wav")
print(speech_detection_result)
#speech detectoin result is returning None
result = interpreter.interpret(speech_detection_result[0])
print(result)