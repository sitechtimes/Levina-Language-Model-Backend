from speech_interpretation import SpeechInterpreter
from speech_detection import SpeechDetection

interpreter = SpeechInterpreter()
dectector = SpeechDetection()
speech_detection_result = dectector.transcribe("audio3.wav")
print(speech_detection_result)
result = interpreter.interpret(speech_detection_result)
print(result)