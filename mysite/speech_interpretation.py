from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
class SpeechInterpreter:
    def __init__(self):
        self.model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype="bfloat16",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=self.bnb_config,
            device_map="auto"
        )
        self.device = self.model.device

    def interpret(self, user_input):
        dynamic_prompt = f"""
SYSTEM:
You are an AI assistant that corrects sentences spoken in broken, misspelled, or ASR-transcribed Russian. Your job is to produce a single, natural, grammatically correct Russian sentence. Fix spelling, grammar, punctuation, and restore proper names and numbers. Use only the information provided. Be deterministic: for the same input, always give the same correction. Do not use any outside knowledge or assumptions.

TASK:
- For each input, output only the corrected Russian sentence.
- Output only the corrected sentence, with no explanations, labels, or extra text.
- Do not repeat the input or output, and do not generate any additional text after the corrected sentence. End your response after the correction.
- After the corrected sentence, append the token "<END>" to indicate the end of your response.

EXAMPLES:
Input: у меня большая семья из частие человек я мама папа сестра бабушка и дедушка
Output: У меня большая семья из шести человек: я, мама, папа, старшая сестра, бабушка и дедушка.<END>

Input: мы живем все не остейся субакой бимом и кошкой морькой и бошйо деме в дерве
Output: Мы живем все вместе с собакой Бимом и кошкой Муркой в большом доме в деревне.<END>

NOW ANSWER:
Input: {user_input}
Output:
"""

        input_ids = self.tokenizer(dynamic_prompt, return_tensors="pt").input_ids.to(self.device)
        output_ids = self.model.generate(
            input_ids,
            max_new_tokens=len(user_input.split())*1.8 + 10,
            pad_token_id=self.tokenizer.pad_token_id,
            )
        output = self.tokenizer.decode(output_ids[0])
        return self.format_output(output)
    def format_output(self, output):
        answer = output.split("Output:")[-1].strip()
        answer = answer.split("<END>")[0].strip()
        return(answer)