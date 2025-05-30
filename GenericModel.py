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

class Model:
    #Queries the model
    def query(self):
        inputs = self.tokenizer(self.context, return_tensors = "pt", padding = True, truncation = True).to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

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
        ai_response = result.split(f"{self.outputToken}:")[-1].strip()
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
        return (f"{ai_response}")

    #Train function for model
    #When passed a file to train on this function will train the current model
    #on the passed dataset using the custom "Atria Dataset" class made to wrap
    #around user data and pass into hugginface's trainer object
    def train(self, transcriptFile):
        trainingArgs = TrainingArguments(
            output_dir= "./elaeProto0",
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

        timeStamp = datetime.datetime.now()
        timeStampString = f"{timeStamp.date()}_{timeStamp.hour}_{timeStamp.minute}"
        timeStampString.replace("-", "_")
        trainer.save_model(f"{self.modelName}_{timeStampString}")
        self.tokenizer.save_pretrained(f"{self.modelName}_{timeStampString}")
        pass

    def __init__(self, modelDir):
        self.modelName = modelDir

        self.tokenizer = AutoTokenizer.from_pretrained(self.modelName)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(self.modelName)
        self.model.config.pad_token_id = self.tokenizer.eos_token_id

        self.context =  ""
        self.outputToken = ""