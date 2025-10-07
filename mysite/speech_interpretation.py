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
        You are an AI assistant that corrects sentences spoken in broken or transliterated Russian. Be as accurate and consistent as possible. Use only the information provided. You must be deterministic: for the same input, always give the same correction. Do not use any outside knowledge or assumptions.

        TASK:
        - For each input, output only the corrected Russian sentence.
        - Output only the corrected sentence, with no explanations, labels, or extra text.

        INPUT:
        1. Broken or transliterated Russian sentence(s):

        EXAMPLES:
        Input: Гдe находица автобус
        Output: Где находится автобус

        Input: Я хачу пит воды
        Output: Я хочу пить воды

        NOW ANSWER:
        Input: {user_input}
        Output:
        """

        input_ids = self.tokenizer(dynamic_prompt, return_tensors="pt").input_ids.to(self.device)
        output_ids = self.model.generate(
            input_ids,
            max_new_tokens=len(user_input.split())*1.05 + 10,
            pad_token_id=self.tokenizer.pad_token_id,
            )
        output = self.tokenizer.decode(output_ids[0])
        return self.format_output(output)
    def format_output(self, output):
        if "Output:" in output:
            answer = output.split("Output:")[-1].strip()
            answer = answer.split("\n")[0].strip()
            return(answer)
        else:
            print("ERROR: 'Output:' not found in model response.")