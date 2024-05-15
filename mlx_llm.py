from mlx_lm import load, generate

model, tokenizer = load("mlx-community/Hermes-2-Pro-Mistral-7B-8bit")
MEDICAL_DOCUMENT = 'Fluocinolone acetonide intravitreal implant is recommended, within its marketing authorisation, as an option for treating visual impairment caused by chronic diabetic macular oedema that has not responded well enough to available treatments in adults. It is recommended only if the company provides it according to thecommercial arrangement.'

response = generate(model, tokenizer, prompt=f"Context:{MEDICAL_DOCUMENT} \n generate a answer only from the context Question: which medicine is recommended? answer: ", verbose=True,repetition_context_size=0)

