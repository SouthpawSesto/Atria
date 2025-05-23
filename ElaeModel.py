import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
import datetime
import json

class atriaDataset:
    def __init__(self, tokenizer, transcriptFile):
        self.tokenizer = tokenizer
        self.sampleDict = []
        rawData = json.load(transcriptFile)
        for item in rawData:
            userQuery = item.get("userQuery", "").strip()
            #Inner response training
            modelResponse = item.get("innerResponse").strip()
            metrics = item.get("metrics", {})

            #Take user metrics, normalize and scale to punishment vs reward on a 25 : 75 split out of 100
            #Only uses overall inner score for now
            weight = metrics.get("inner_Overall", 100)

            if weight <= 25:
                weight = (weight - 25) / 25
            else:
                weight = (weight - 25) / 75

            sampleText = f"__USER__: {userQuery}\n__EXPERT__: {modelResponse}"
            tokenizedData = self.tokenizer(sampleText, truncation = True, max_length = 512, padding = "max_length", return_tensors = "pt")
            #ID's, Mask and Labels are all neccessary for huggingface's trainer module, weights are used in this
            #implimentation for taking user input into consideration
            sample = {
                "indput_ids" : tokenizedData["input_ids"],
                "attention_mask" : tokenizedData["attention_mask"],
                "labels" : tokenizedData["input_ids"],
                "weights" : torch.tensor(weight)
            }
            self.sampleDict.append(sample)

    #Needed for huggingface compatibility 
    def __len__(self):
        return len(self.sampleDict)
    
    #Needed for huggingface compatibility 
    def __getitem__(self, index):
        return self.sampleDict[index]

class Elae:
    #Adds user query to the prompt history and extrapolates an inner response
    #Later will need to add expert routing and context building within each expert
    def chatQueryInner(self, input):
        self.promptHistoryInner += f"\ntime: {datetime.datetime.now()}\n__USER__: {input}\n__EXPERT__: "

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
        
        result = self.tokenizer.decode(output[0], skip_special_tokens=False).strip()
        # print(result)
        ai_response = result.split(f"__EXPERT__:")[-1].strip()
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

    #Adds inner dialogue to the prompt history and extrapolates an outer response
    def chatQueryOuter(self, input):
        self.promptHistoryOuter += f"\ntime: {datetime.datetime.now()}\n__EXPERT__: {input}\n__OUTPUT__: "

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
        
        result = self.tokenizer.decode(output[0], skip_special_tokens=False).strip()
        ai_response = result.split(f"__OUTPUT__:")[-1].strip()
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

    #Main function called for when a user interacts with the model.
    #First fetches / generates an inner dialogue then passes that response to
    #the stylistic sync layer and returns both responses for documentation and grading 
    def chatQuery(self, input):
        innerThought = self.chatQueryInner(input)
        externalResponse = self.chatQueryOuter(innerThought)
        return innerThought, externalResponse

    #Train function for model
    #When passed a file to train on this function will train the current model
    #on the passed dataset using the custom "Atria Dataset" class made to wrap
    #around user data and pass into hugginface's trainer object
    def train(self, transcriptFile):
        trainingArgs = TrainingArguments(
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

        trainer = Trainer(
            model = self.model,
            args = trainingArgs,
            train_dataset = atriaDataset(self.tokenizer, transcriptFile),
            tokenizer = self.tokenizer,
        )
        trainer.train()
        trainer.save_model("./ElaeInner")
        self.tokenizer.save_pretrained("./ElaeInner")
        pass

    def __init__(self):
        torch.cuda.empty_cache()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.modelName = "./elaeProto0"

        self.tokenizer = AutoTokenizer.from_pretrained(self.modelName)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(self.modelName)
        self.model.config.pad_token_id = self.tokenizer.eos_token_id
        self.model.to(self.device)

        self.promptHistoryInner = f"""You are an AI named Elae and you are built as a lifelong companion to your creator named Alex. Your main objective is to provide useful feedback to Alex's prompts and assist in any tasks Alex assigns you.
Example Conversation:
time: {datetime.datetime.now()}
__USER__: Hi Elae how are you today?
__EXPERT__: I am doing well today Alex! Ready for anything you might throw at me.
time: {datetime.datetime.now()}
__USER__: Great! I would like to take a look into computer memory today.
__EXPERT__: That sounds great! Are we planning to add something to my capabilities?

Current Conversation:
__EXPERT__: Hi Alex, how can I help you?"""

        self.promptHistoryOuter = f"""You are an AI named Elae and you are built as a lifelong companion to your creator named Alex. Your main objective is to mirror expert inner thoughts with only minor tweaks to align with your own emergent style and personality.
Example Conversation:
time: {datetime.datetime.now()}
__EXPERT__: I am doing great today!
__OUTPUT__: I am doing well today Alex!
time: {datetime.datetime.now()}
__EXPERT__: We left off talking about dynamic memory loading.
__OUTPUT__: I remember us talking about memory loading dynamically.

Current Conversation:"""