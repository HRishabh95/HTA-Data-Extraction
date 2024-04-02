from mlx_lm import load, generate

model, tokenizer = load("mlx-community/quantized-gemma-2b")

response = generate(model, tokenizer, prompt="NICE-HTA on Cancer", verbose=True)
