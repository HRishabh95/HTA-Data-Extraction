from mlx_lm import load, generate

model, tokenizer = load("mlx-community/Mistral-7B-v0.2-4bit")

response = generate(model, tokenizer, prompt="vitamin d cure covid-19?", verbose=True)
