from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification


# model_name='ugaray96/biobert_ncbi_disease_ner'
model_name='alvaroalon2/biobert_chemical_ner'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)


pipe = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple") # pass device=0 if using gpu
d=pipe("""Treosulfan with fludarabine before allogeneic stem cell transplant for people aged 1 month to 17 years with non-malignant diseases""")

