import customtkinter
import os
import json
import GenericModel
import shutil


class modelEditWindow:
    def addModelButtonPress(self, * args):
        self.returnArgs = []
        self.returnArgs.append(self.name.get())
        self.returnArgs.append(self.dir.get())
        self.returnArgs.append(self.contextTextBox.get("0.0", "end"))
        self.returnArgs.append(self.inputTokenCombobox.get())
        self.returnArgs.append(self.outputTokenCombobox.get())

        self.onClose()
    
    def browseModelDir(self):
        self.modelDir = customtkinter.filedialog.askdirectory(initialdir= f"{os.getcwd()}")
        self.dirTextVar.set(self.modelDir)
        self.model = GenericModel.Model(self.modelDir)

        self.refreshTokens()

    def refreshTokens(self):
        specialTokens = []

        try:
            for item in self.model.tokenizer.get_added_vocab():
                specialTokens.append(item)
            #Model turn tokens
            self.inputTokenCombobox = customtkinter.CTkComboBox(self.turnTokenFrame, width = 100, values= specialTokens)
            self.inputTokenCombobox.configure(state = "readonly")
            self.inputTokenCombobox.grid(row = 1, column = 1, sticky = "nsew", padx = 5, pady = 5)
            self.inputTokenCombobox.set(self.model.inputToken)

            self.outputTokenCombobox = customtkinter.CTkComboBox(self.turnTokenFrame, width = 100, values= specialTokens)
            self.outputTokenCombobox.configure(state = "readonly")
            self.outputTokenCombobox.grid(row = 2, column = 1, sticky = "nsew", padx = 5, pady = 5)
            self.outputTokenCombobox.set(self.model.outputToken)

            self.TokenLabel = customtkinter.CTkLabel(self.turnTokenFrame, text = "New Token", font = self.font)
            self.TokenLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)
            self.TokenTextVar = customtkinter.StringVar(value = f"New Model Token")
            self.TokenEntry = customtkinter.CTkEntry(self.turnTokenFrame, textvariable= self.TokenTextVar, font = self.font)
            self.TokenEntry.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
            self.addTokenButton = customtkinter.CTkButton(self.turnTokenFrame, text="Add Token", command=self.addTokenButtonPress, font = self.font)
            self.addTokenButton.grid(column = 2, row = 0, sticky = "nsew", padx = 5, pady = 5)
            self.TokenLabelWarning = customtkinter.CTkLabel(self.turnTokenFrame, text = "Cannot Be Undone!", font = self.font)
            self.TokenLabelWarning.grid(row = 0, column = 3, sticky = "nw", padx = 5, pady = 5)

            self.inputTokenLabel = customtkinter.CTkLabel(self.turnTokenFrame, text= "Input Token", font= self.font)
            self.inputTokenLabel.grid(row = 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
            self.outputTokenLabel = customtkinter.CTkLabel(self.turnTokenFrame, text= "Output Token", font= self.font)
            self.outputTokenLabel.grid(row = 2, column = 0, sticky = "nsew", padx = 5, pady = 5)
        except:
            pass

    def onClose(self):
        self.root.destroy()
        return self.returnArgs

    def addTokenButtonPress(self):
        temp = f"{self.TokenTextVar.get()}"
        self.model.tokenizer.add_special_tokens({"additional_special_tokens": [f"{temp}"]})
        self.model.model.resize_token_embeddings(len(self.model.tokenizer))
        # self.model.tokenizer.save_pretrained(f"{self.modelDir}")
        self.model.model.save_pretrained(f"{self.modelDir}_tokenized")
        self.model.tokenizer.save_pretrained(f"{self.modelDir}_tokenized")
        self.model = GenericModel.Model(f"{self.modelDir}_tokenized")
        self.model.model.save_pretrained(f"{self.modelDir}")
        self.model.tokenizer.save_pretrained(f"{self.modelDir}")
        self.model = GenericModel.Model(f"{self.modelDir}")
        shutil.rmtree(f"{self.modelDir}_tokenized")

        self.TokenTextVar.set(value = "Token Added!")

        self.refreshTokens()
        pass

    def __init__(self, model = None):
        self.font = customtkinter.CTkFont(family= "Segoe UI", size= 18)
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)

        self.returnArgs = []
        self.model = model

        self.root = customtkinter.CTkToplevel()
        self.root.geometry("1000x500")
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.title("Add or Edit Model")
        self.root.focus()
        self.root.columnconfigure(1, weight= 1)
        self.root.rowconfigure(2, weight= 1)

        #Model Name
        self.nameLabel = customtkinter.CTkLabel(self.root, text = "Name", font = self.font)
        self.nameLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)
        if model == None:
            self.nameTextVar = customtkinter.StringVar(value = f"New Model Name")
        else:
            self.nameTextVar = customtkinter.StringVar(value = f"{self.model.name}")
        self.name = customtkinter.CTkEntry(self.root, textvariable= self.nameTextVar, font = self.font)
        self.name.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)

        #Model Directory
        self.modelDir = ""
        self.dirLabel = customtkinter.CTkLabel(self.root, text = "Model Location", font = self.font)
        self.dirLabel.grid(row = 1, column = 0, sticky = "n", padx = 5, pady = 5)
        if model == None:
            self.dirTextVar = customtkinter.StringVar(value = f"New Model Directory")
        else:
            self.dirTextVar = customtkinter.StringVar(value = f"{self.model.modelDir}")
        self.dir = customtkinter.CTkEntry(self.root, textvariable= self.dirTextVar, font = self.font)
        self.dir.grid(row = 1, column = 1, sticky = "nsew", padx = 5, pady = 5)
        self.browseModelButton = customtkinter.CTkButton(self.root, text="Browse", command=self.browseModelDir, font = self.font)
        self.browseModelButton.grid(row = 1, column = 2, sticky = "nsew", padx = 5, pady = 5)

        #Model Starting Context
        self.contextLabel = customtkinter.CTkLabel(self.root, text = "Starting Context", font = self.font)
        self.contextLabel.grid(row = 2, column = 0, sticky = "n", padx = 5, pady = 5)
        if model == None:
            self.modelStartContext = ""
        else:
            self.modelStartContext = self.model.startingContext
        self.contextTextBox = customtkinter.CTkTextbox(self.root, width = 200, height = 100, font = self.smallFont, wrap = "word")
        self.contextTextBox.grid(row = 2, column = 1, columnspan = 2, sticky = "nsew", padx = 5, pady = 5)
        self.contextTextBox.insert("0.0", self.modelStartContext)

        #Model turn tokens
        self.turnTokenFrame = customtkinter.CTkFrame(self.root)
        self.turnTokenFrame.grid(row = 4, column = 0, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)
        self.turnTokenFrame.columnconfigure(1, weight = 1)

        try:
            self.inputTokenCombobox = customtkinter.CTkComboBox(self.turnTokenFrame, width = 100, values= self.model.specialTokens)
            self.inputTokenCombobox.configure(state = "readonly")
            self.inputTokenCombobox.grid(row = 1, column = 1, sticky = "nsew", padx = 5, pady = 5)
            self.inputTokenCombobox.set(self.model.inputToken)

            self.outputTokenCombobox = customtkinter.CTkComboBox(self.turnTokenFrame, width = 100, values= self.model.specialTokens)
            self.outputTokenCombobox.configure(state = "readonly")
            self.outputTokenCombobox.grid(row = 2, column = 1, sticky = "nsew", padx = 5, pady = 5)
            self.outputTokenCombobox.set(self.model.outputToken)

            self.TokenLabel = customtkinter.CTkLabel(self.turnTokenFrame, text = "New Token", font = self.font)
            self.TokenLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)
            self.TokenTextVar = customtkinter.StringVar(value = f"New Model Token")
            self.TokenEntry = customtkinter.CTkEntry(self.turnTokenFrame, textvariable= self.TokenTextVar, font = self.font)
            self.TokenEntry.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
            self.addTokenButton = customtkinter.CTkButton(self.turnTokenFrame, text="Add Token", command=self.addTokenButtonPress, font = self.font)
            self.addTokenButton.grid(column = 2, row = 0, sticky = "nsew", padx = 5, pady = 5)
            self.TokenLabelWarning = customtkinter.CTkLabel(self.turnTokenFrame, text = "Cannot Be Undone!", font = self.font)
            self.TokenLabelWarning.grid(row = 0, column = 3, sticky = "nw", padx = 5, pady = 5)

            self.inputTokenLabel = customtkinter.CTkLabel(self.turnTokenFrame, text= "Input Token", font= self.font)
            self.inputTokenLabel.grid(row = 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
            self.outputTokenLabel = customtkinter.CTkLabel(self.turnTokenFrame, text= "Output Token", font= self.font)
            self.outputTokenLabel.grid(row = 2, column = 0, sticky = "nsew", padx = 5, pady = 5)
        except:
            pass

        self.addModelButton = customtkinter.CTkButton(self.root, text="Confirm", command=self.addModelButtonPress, font = self.font)
        self.addModelButton.grid(column = 0, row = 5, sticky = "nsew", padx = 5, pady = 5)
        self.root.focus()
        self.root.wait_window()

class metricEditWindow:
    def addMetricButtonPress(self, * args):
        self.returnArgs = []
        self.returnArgs.append(self.name.get())

        self.onClose()
    
    def onClose(self):
        self.root.destroy()
        return self.returnArgs

    def __init__(self, *args):
        self.font = customtkinter.CTkFont(family= "Segoe UI", size= 18)
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)

        self.returnArgs = []

        self.root = customtkinter.CTkToplevel()
        self.root.geometry("400x100")
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.title("Add or Edit Metric")
        self.root.focus()
        self.root.columnconfigure(1, weight= 1)
        self.root.bind("<Return>", self.addMetricButtonPress)

        self.nameLabel = customtkinter.CTkLabel(self.root, text = "Name", font = self.font)
        self.nameLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)
        self.name = customtkinter.CTkEntry(self.root, placeholder_text= "Enter the name of your model", font = self.font)
        self.name.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
        self.name.bind("<Return>", self.addMetricButtonPress)
        self.name.focus()

        self.addMetricButton = customtkinter.CTkButton(self.root, text="Add Metric", command=self.addMetricButtonPress, font = self.font)
        self.addMetricButton.grid(column = 0, row = 2, sticky = "nsew", padx = 5, pady = 5)

        self.root.wait_window()

class yesNoWindow:
    def yesButtonPress(self, * args):
        self.returnArgs = "Yes"
        self.onClose()

    def noButtonPress(self, * args):
        self.returnArgs = "No"
        self.onClose()
    
    def onClose(self):
        self.root.destroy()
        return self.returnArgs

    def __init__(self, *args):
        self.font = customtkinter.CTkFont(family= "Segoe UI", size= 18)
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)

        self.returnArgs = None

        self.root = customtkinter.CTkToplevel()
        self.root.geometry("400x100")
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.title("Current Model Update")
        self.root.focus()
        self.root.columnconfigure(1, weight= 1)

        self.nameLabel = customtkinter.CTkLabel(self.root, text = "Update Current Model?", font = self.font)
        self.nameLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)

        self.addMetricButton = customtkinter.CTkButton(self.root, text="Yes", command=self.yesButtonPress, font = self.font)
        self.addMetricButton.grid(column = 0, row = 2, sticky = "nsew", padx = 5, pady = 5)
        self.addMetricButton = customtkinter.CTkButton(self.root, text="Keep Current Model", command=self.noButtonPress, font = self.font)
        self.addMetricButton.grid(column = 1, row = 2, sticky = "nsew", padx = 5, pady = 5)

        self.root.wait_window()

class preferencesEditWindow:
    def saveButtonPress(self, caller):
        self.returnArgs = []
        self.returnArgs.append(self.name.get())

        file = open("userConfig.config", "w+")
        file.write("{")
        file.write(f"\n\"username\" : \"{self.name.get()}\"")
        file.write("\n}")
        file.close()
        self.onClose()
    
    def onClose(self):
        self.root.destroy()
        return self.returnArgs

    def __init__(self, *args):
        self.font = customtkinter.CTkFont(family= "Segoe UI", size= 18)
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)

        self.returnArgs = []

        self.root = customtkinter.CTkToplevel()
        self.root.geometry("400x100")
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.title("User Config")
        self.root.focus()
        self.root.columnconfigure(1, weight= 1)
        self.root.bind("<Return>", self.saveButtonPress)

        self.userName = ""

        try:
            file = open("userConfig.config", "r")
            file = json.load(file)
            self.userName = file["username"]
        except:
            print("Could not open user config!")

        self.nameLabel = customtkinter.CTkLabel(self.root, text = "User Name", font = self.font)
        self.nameLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)

        self.nameTextVar = customtkinter.StringVar(value = f"{self.userName}")
        self.name = customtkinter.CTkEntry(self.root, placeholder_text= "Enter your name!", textvariable = self.nameTextVar, font = self.font)
        self.name.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
        self.name.bind("<Return>", self.saveButtonPress)
        self.name.focus()

        self.saveButton = customtkinter.CTkButton(self.root, text="Save Metric", command=self.saveButtonPress, font = self.font)
        self.saveButton.grid(column = 0, row = 2, sticky = "nsew", padx = 5, pady = 5)

        self.root.wait_window()
