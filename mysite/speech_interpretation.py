from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype="bfloat16",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)

device = model.device
user_input = "мен зо вут Саймон"
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
eos_token_id = tokenizer.eos_token_id

input_ids = tokenizer(dynamic_prompt, return_tensors="pt").input_ids.to(device)
output_ids = model.generate(
    input_ids,
    max_new_tokens=len(user_input.split()) + 20,
    eos_token_id=eos_token_id,
    pad_token_id=tokenizer.pad_token_id,
    )
output = tokenizer.decode(output_ids[0])
print(output)