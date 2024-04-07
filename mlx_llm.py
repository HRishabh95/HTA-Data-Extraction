from mlx_lm import load, generate

model, tokenizer = load("mlx-community/quantized-gemma-2b")
MEDICAL_DOCUMENT = 'Fluocinolone acetonide intravitreal implant is recommended, within its marketing authorisation, as an option for treating visual impairment caused by chronic diabetic macular oedema that has not responded well enough to available treatments in adults. It is recommended only if the company provides it according to thecommercial arrangement.'

response = generate(model, tokenizer, prompt=f"what is recommended:{MEDICAL_DOCUMENT} \n Generate response from above context only", verbose=True)



from transformers import AutoModelForCausalLM, AutoTokenizer

checkpoint = "bigscience/bloomz-560m"

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map="auto")
prompt=f"what is recommended:{MEDICAL_DOCUMENT} \n Generate response from above context only"

inputs = tokenizer.encode(prompt, return_tensors="pt")
outputs = model.generate(inputs)
print(tokenizer.decode(outputs[0]))


from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

checkpoint = "CohereForAI/aya-101"

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
aya_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)

# Turkish to English translation
prompt=f"what is recommended:{MEDICAL_DOCUMENT} \n Generate response from above context only"

tur_inputs = tokenizer.encode(prompt, return_tensors="pt")
tur_outputs = aya_model.generate(tur_inputs, max_new_tokens=128)
print(tokenizer.decode(tur_outputs[0]))