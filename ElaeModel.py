import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments, Trainer
import datetime
import json

# torch.cuda.empty_cache()

class atriaDataset:

    def __init__(self, transcriptFile):
        self.sampleDict = []
        rawData = json.load(transcriptFile)
        for item in rawData:
            userQuery = item.get("userQuery", "").strip()
            modelResponse = item.get("innerResponse").strip()
            metrics = item.get("metrics", {})

            #Space for filtering based on metrics

            sampleText = f"<alex> {userQuery}\n<elae> {modelResponse}"
            tokenizedData = self.tokenizer(sampleText, truncation = True, max_length = 512, padding = "max_length", return_tensors = "pt")
            sample = {
                "indput_ids" : tokenizedData["input_ids"],
                "attention_mask" : tokenizedData["attention_mask"],
                "labels" : tokenizedData["input_ids"],
            }
            self.sampleDict.append(sample)
        
    def __len__(self):
        return len(self.sampleDict)
    
    def __getitem__(self, index):
        return self.sampleDict[index]

class Elae:
    def chatQueryInner(self, input):
        self.promptHistoryInner += f"\n<alex> {input}\n<elae> "

        inputs = self.tokenizer(self.promptHistoryInner, return_tensors = "pt", padding = True, truncation = True).to(self.device)

        inputIDs = inputs["input_ids"]
        attentionMask = inputs["attention_mask"]
        
        output = self.model.generate(
            inputIDs,
            max_length= len(inputIDs[0]) + 20,
            num_return_sequences=1,
            attention_mask = attentionMask,
            # temperature=0.7,
            # top_k=50,
            # top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id = self.tokenizer.eos_token_id,
            eos_token_id = self.tokenizer.eos_token_id,
        )
        
        result = self.tokenizer.decode(output[0], skip_special_tokens=True).strip()
        ai_response = result.split(f"<elae>")[-1].strip()
        ai_response = ai_response.split("\n")[0].strip()
        if "." in ai_response:
            ai_response = ai_response.split(".")[0].strip()
            ai_response = ai_response + "."
        if "?" in ai_response:
            ai_response = ai_response.split("?")[0].strip()
            ai_response = ai_response + "?"
        if "!" in ai_response:
            ai_response = ai_response.split("!")[0].strip()
            ai_response = ai_response + "!"
        self.promptHistoryInner += f"{ai_response}" 
        return (f"{ai_response}")

    def chatQueryOuter(self, input):
        self.promptHistoryOuter += f"\n<inner> {input}\n<outer> "

        inputs = self.tokenizer(self.promptHistoryOuter, return_tensors = "pt", padding = True, truncation = True).to(self.device)

        inputIDs = inputs["input_ids"]
        attentionMask = inputs["attention_mask"]
        
        output = self.model.generate(
            inputIDs,
            max_length= len(inputIDs[0]) + 20,
            num_return_sequences=1,
            attention_mask = attentionMask,
            # temperature=0.7,
            # top_k=50,
            # top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id = self.tokenizer.eos_token_id,
            eos_token_id = self.tokenizer.eos_token_id,
        )
        
        result = self.tokenizer.decode(output[0], skip_special_tokens=True).strip()
        ai_response = result.split(f"<outer>")[-1].strip()
        ai_response = ai_response.split("\n")[0].strip()
        if "." in ai_response:
            ai_response = ai_response.split(".")[0].strip()
            ai_response = ai_response + "."
        if "?" in ai_response:
            ai_response = ai_response.split("?")[0].strip()
            ai_response = ai_response + "?"
        if "!" in ai_response:
            ai_response = ai_response.split("!")[0].strip()
            ai_response = ai_response + "!"
        self.promptHistoryOuter += f"{ai_response}" 
        return (f"{ai_response}")
    
    def chatQuery(self, input):
        innerThought = self.chatQueryInner(input)
        externalResponse = self.chatQueryOuter(innerThought)
        return innerThought, externalResponse

    def train(self):
        self.trainer.train()
        self.trainer.save_model("./ElaeInner")
        self.tokenizer.save_pretrained("./ElaeInner")
        pass

    def __init__(self):
        torch.cuda.empty_cache()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.modelName = "./gpt2FinetunedLarge"

        self.tokenizer = AutoTokenizer.from_pretrained(self.modelName)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(self.modelName)
        self.model.config.pad_token_id = self.tokenizer.eos_token_id
        self.model.to(self.device)

        self.trainingArgs = TrainingArguments(
            output_dir= "./gpt2-finetuned-large",
            evaluation_strategy= "epoch",
            save_strategy= "epoch",
            learning_rate= 5e-5,
            per_device_train_batch_size = 1,
            per_device_eval_batch_size = 1,
            num_train_epochs = 1,
            weight_decay = 0.01,
            logging_dir = "./logs",
            logging_steps = 200,
            save_total_limit = 2,
            push_to_hub = False,
            fp16 = True,
            gradient_accumulation_steps = 4
        )

        self.trainer = Trainer(
            model = self.model,
            args = self.trainingArgs,
            train_dataset = tokenizedDataset["train"],
            eval_dataset = tokenizedDataset["validation"],
            tokenizer = self.tokenizer,
            data_collator = dataCollator
        )
        
        self.promptHistoryInner = f"""You are an AI named Elae and you are built as a lifelong companion to your creator named Alex. Your main objective is to provide useful feedback to Alex's prompts and assist in any tasks Alex assigns you.
Example Conversation:
<alex> Hi Elae how are you today?
<elae> I am doing well today Alex! Ready for anything you might throw at me.
<alex> Great! I would like to take a look into computer memory today.
<elae> That sounds great! Are we planning to add something to my capabilities?

Current Conversation:
<elae> Hi Alex, how can I help you?"""

        self.promptHistoryOuter = f"""You are an AI named Elae and you are built as a lifelong companion to your creator named Alex. Your main objective is to mirror expert inner thoughts with only minor tweaks to align with your own emergent style and personality.
Example Conversation:
<inner> I am doing great today!
<outer> I am doing well today Alex!
<inner> We left off talking about dynamic memory loading.
<outer> I remember us talking about memory loading dynamically.

Current Conversation:"""