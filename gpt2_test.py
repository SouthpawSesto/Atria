import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer, BitsAndBytesConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from datasets import load_dataset

torch.cuda.empty_cache()

def formatBST(example):
    persona = " ".join(example["personas"])
    context = example["context"] if example["context"] else ""
    # freeMessges = " ".join(example["free_messages"])
    guidedMessges = " ".join(example["guided_messages"])

    formattedText = f"Persona: {persona} Context: {context} Dialogue: {guidedMessges}"
    return {"text" : formattedText}

def preprocess_function(examples):
    return tokenizer(examples['text'], truncation = True, padding = 'max_length', max_length = 512)

def chat_with_gpt():

    promptHistory = ""

    while True:
        user_input = input("Type anything to GPT-J: ")

        if user_input.lower() == "exit":
            break

        # if promptHistory == "":
        promptHistory = f"""An AI, talking to a user, is in charge of naming the most relevant function Plot, Sum or Average. The AI may only resond with the name of the function without any other output.
Example interactions:
User: Plot x vs y
Response: Plot(x,y)
User: Plot x y
Response: Plot(x,y)
User: Plot a, b
Response: Plot(a,b)
User: Sum over x
Response: Sum(x)
User: Sum over y
Response: Sum(y)
User: Sum a
Response: Sum(a)
User: Average over x
Response: Average(x)
User: Average over a
Response: Average(a)
User: average g
Response: Average(g)

The current conversation:
User:{user_input}
Response:"""
        # else:
        #     promptHistory += f"\nUser: {user_input}\nResponse:"

        inputs = tokenizer(promptHistory, return_tensors = "pt", padding = True, truncation = True).to(device)

        inputIDs = inputs["input_ids"]
        attentionMask = inputs["attention_mask"]
        
        output = model.generate(
            inputIDs,
            max_length= len(inputIDs[0]) + 10,
            num_return_sequences=1,
            attention_mask = attentionMask,
            # temperature=0.7,
            # top_k=50,
            # top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id = tokenizer.eos_token_id,
            eos_token_id = tokenizer.eos_token_id,
        )
        
        result = tokenizer.decode(output[0], skip_special_tokens=True).strip()
        ai_response = result.split(f"Response:")[-1].strip()
        ai_response = ai_response.split("\n")[0].strip()
        ai_response = ai_response.split(".")[0].strip()
        # promptHistory += f"{ai_response}" 
        print(f"{ai_response}")

def trainGPT(dataset, model, tokenizer):
    dataCollator = DataCollatorForLanguageModeling(tokenizer = tokenizer, mlm = False)

    formattedDataset = dataset.map(formatBST)

    tokenizedDataset = formattedDataset.map(preprocess_function, batched = True)

    trainingArgs = TrainingArguments(
        output_dir= "./gpt2-finetuned-large",
        evaluation_strategy= "epoch",
        save_strategy= "epoch",
        learning_rate= 5e-5,
        per_device_train_batch_size = 2,
        per_device_eval_batch_size = 2,
        num_train_epochs = 3,
        weight_decay = 0.01,
        logging_dir = "./logs",
        logging_steps = 200,
        save_total_limit = 2,
        push_to_hub = False,
        fp16 = True,
        gradient_accumulation_steps = 4
    )

    trainer = Trainer(
        model = model,
        args = trainingArgs,
        train_dataset = tokenizedDataset["train"],
        eval_dataset = tokenizedDataset["validation"],
        tokenizer = tokenizer,
        data_collator = dataCollator
    )

    trainer.train()

    trainer.save_model("./gpt2-finetuned-large")
    tokenizer.save_pretrained("./gpt2-finetuned-large")
    pass

if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # model_name = "EleutherAI/gpt-j-6B" 
    model_name = "./gpt2FinetunedLarge" 

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype = torch.float16)
    model.config.pad_token_id = tokenizer.eos_token_id
    model.to(device)

    promptHistory = ""

    chat_with_gpt()