# def formatBST(example):
# import datasets
# import whisper
# import speech_recognition
import torch
# from transformers import GPT2LMHeadModel, GPT2Tokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer, BitsAndBytesConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import datetime

# from datasets import load_dataset
#     persona = " ".join(example["personas"])
#     context = example["context"] if example["context"] else ""
#     # freeMessges = " ".join(example["free_messages"])
#     guidedMessges = " ".join(example["guided_messages"])

#     formattedText = f"Persona: {persona} Context: {context} Dialogue: {guidedMessges}"
#     return {"text" : formattedText}

# def preprocess_function(examples):
#     return tokenizer(examples['text'], truncation = True, padding = 'max_length', max_length = 512)

# def trainGPT(dataset, model, tokenizer):
#     dataCollator = DataCollatorForLanguageModeling(tokenizer = tokenizer, mlm = False)

#     formattedDataset = dataset.map(formatBST)

#     tokenizedDataset = formattedDataset.map(preprocess_function, batched = True)

#     trainingArgs = TrainingArguments(
#         output_dir= "./gpt2-finetuned-large",
#         evaluation_strategy= "epoch",
#         save_strategy= "epoch",
#         learning_rate= 5e-5,
#         per_device_train_batch_size = 2,
#         per_device_eval_batch_size = 2,
#         num_train_epochs = 3,
#         weight_decay = 0.01,
#         logging_dir = "./logs",
#         logging_steps = 200,
#         save_total_limit = 2,
#         push_to_hub = False,
#         fp16 = True,
#         gradient_accumulation_steps = 4
#     )

#     trainer = Trainer(
#         model = model,
#         args = trainingArgs,
#         train_dataset = tokenizedDataset["train"],
#         eval_dataset = tokenizedDataset["validation"],
#         tokenizer = tokenizer,
#         data_collator = dataCollator
#     )

#     trainer.train()

#     trainer.save_model("./gpt2-finetuned-large")
#     tokenizer.save_pretrained("./gpt2-finetuned-large")
#     pass