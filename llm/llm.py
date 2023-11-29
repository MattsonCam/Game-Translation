from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

task_prefix = "translate English to German: "
# use different length sentences to test batching
sentences = ["Germans like beer during halloween", "Two in the bush is one in the hand"]

inputs = tokenizer([task_prefix + sentence for sentence in sentences], return_tensors="pt", padding=True)

output_sequences = model.generate(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    no_repeat_ngram_size=5,
    max_length=512,
    do_sample=False,  # disable sampling to test if batching affects output
)


#help(model.generate)

print(tokenizer.batch_decode(output_sequences, skip_special_tokens=True))
