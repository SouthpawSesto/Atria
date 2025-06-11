import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
import datetime
import json
import os

class atriaDataset:
    def __init__(self, modelName, tokenizer, transcriptFile, inputToken, outputToken, metric):
        self.tokenizer = tokenizer
        self.sampleDict = []
        file = open(transcriptFile, "r")
        try:
            file = json.load(file)
        except:
            print(f"Could not open file {transcriptFile}")
        for model in file:
            if model != modelName:
                # print(f"Skipping model {model} logs")
                continue
            # print(f"Model: {model}")
            for interaction in file[f"{model}"]:
                # print(f"Interaction: {interaction}")
                if f"{interaction}" != "directory":
                    userQuery = file[f"{model}"][f"{interaction}"]["userQuery"]
                    modelResponse = file[f"{model}"][f"{interaction}"]["response"]
                    weight = file[f"{model}"][f"{interaction}"]["metrics"][f"{metric}"]
                    # weight = interaction[metric]

                    if weight <= 25:
                        weight = (weight - 25) / 25
                    else:
                        weight = (weight - 25) / 75

                    sampleText = f"{inputToken}: {userQuery}\n{outputToken}: {modelResponse}"
                    tokenizedData = self.tokenizer(sampleText, truncation = True, max_length = 512, padding = "max_length", return_tensors = "pt")
                    #ID's, Mask and Labels are all neccessary for huggingface's trainer module, weights are used in this
                    #implimentation for taking user input into consideration
                    sample = {
                        "input_ids" : tokenizedData["input_ids"],
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
    def train(self, transcriptFile, outputDir):
        returnArgs = None

        torch.cuda.empty_cache()
        trainingArgs = TrainingArguments(
            output_dir= outputDir,
            # evaluation_strategy= "epoch",
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

        file = open(transcriptFile, "r")
        try:
            file = json.load(file)
        except:
            print(f"Could not open file {transcriptFile}")
            self.parent.write(f"Could not open file {transcriptFile}", sys = True)
            self.parent.root.update()
            return
        index = 1
        for metric in file[f"{self.name}"][f"{self.name}_interaction_0"]["metrics"]:
            print(f"Training metric: {metric}")
            self.parent.write(f"Training metric ({index}/{len(file[f"{self.name}"][f"{self.name}_interaction_0"]["metrics"])}): {metric}", sys = True)
            self.parent.root.update()
            trainer = Trainer(
                model = self.model,
                args = trainingArgs,
                train_dataset = atriaDataset(self.name, self.tokenizer, transcriptFile, self.inputToken, self.outputToken, metric),
                tokenizer = self.tokenizer,
            )

            trainer.train()

            timeStamp = datetime.datetime.now()
            timeStampString = f"{timeStamp.date()}_{timeStamp.hour}_{timeStamp.minute}"
            timeStampString.replace("-", "_")
            outputDirString = f"{outputDir}/{self.name}_{timeStampString}"
            returnArgs = outputDirString
            # print(f"Output Directory: {outputDirString}")

            try:
                trainer.save_model(f"{outputDirString}")
                self.tokenizer.save_pretrained(f"{outputDirString}")
            except:
                trainer.save_model(f"{self.name}_{timeStampString}")
                self.tokenizer.save_pretrained(f"{self.name}_{timeStampString}")

            tempTokenizer = self.tokenizer
            del tempTokenizer

            tempModel = self.model
            del tempModel

            torch.cuda.empty_cache()

            try:
                self.tokenizer = AutoTokenizer.from_pretrained(f"{outputDirString}")
                self.tokenizer.pad_token = self.tokenizer.eos_token

                self.model = AutoModelForCausalLM.from_pretrained(f"{outputDirString}")
                self.model.config.pad_token_id = self.tokenizer.eos_token_id
            except:
                self.tokenizer = AutoTokenizer.from_pretrained(f"{self.name}_{timeStampString}")
                self.tokenizer.pad_token = self.tokenizer.eos_token

                self.model = AutoModelForCausalLM.from_pretrained(f"{self.name}_{timeStampString}")
                self.model.config.pad_token_id = self.tokenizer.eos_token_id

            index += 1
        return returnArgs

    def __init__(self, modelDir):
        self.modelDir = modelDir

        self.tokenizer = AutoTokenizer.from_pretrained(self.modelDir)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(self.modelDir)
        self.model.config.pad_token_id = self.tokenizer.eos_token_id

        self.name = ""
        self.context =  ""
        self.inputToken = ""
        self.outputToken = ""
        self.parent = None