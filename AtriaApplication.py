import customtkinter
import CTkMenuBar
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import datetime

import GenericModel
import ModelEditWindow
import AtriaSaveLoad

class metricSlider:
    def __init__(self, caller, text):
        self.font = customtkinter.CTkFont(family= "Segoe UI", size= 18)
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)

        self.caller = caller
        self.caller.metricCol.append(self)
        self.root = caller.responseFrame
        self.name = text
        self.editMode = caller.editMode
        self.scoreIndex = len(self.caller.metricCol) - 1
        self.frame = customtkinter.CTkFrame(self.root)
        self.frame.grid(row = len(caller.metricCol) + 1, column = 0, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)
        self.frame.columnconfigure(1, weight= 1)
        self.sliderLabel = customtkinter.CTkLabel(self.frame, text = f"{self.name}", font = self.smallFont, width = 30)
        self.sliderLabel.grid(row = 0, column = 0, sticky = "ne", padx = 5, pady = 5)
        self.slider = customtkinter.CTkSlider(self.frame, from_=0, to=100, command = self.innerSliderEvent)
        # self.slider.grid(row = 0, column = 1, sticky = "new", padx = 5, pady = 5)
        self.slider.set(0)
        self.sliderValLabel = customtkinter.CTkLabel(self.frame, text = f"0", font = self.smallFont)
        # self.sliderValLabel.grid(row = 0, column = 2, sticky = "new", padx = 5, pady = 5)
        self.editButton = customtkinter.CTkButton(self.frame, text="Edit Metric", command=self.editButtonPress, font = self.smallFont)
        self.editButton.grid(row = 0, column = 3, sticky = "nsew", padx = 5, pady = 5)
        self.deleteButton = customtkinter.CTkButton(self.frame, text="Delete Metric", command=self.deleteButtonPress, font = self.smallFont)
        self.deleteButton.grid(column = 4, row = 0, sticky = "nsew", padx = 5, pady = 5)

    def innerSliderEvent(self, * args):
        self.caller.interactionCol[self.caller.interactionIndex].scoreVector[self.scoreIndex] = round(args[0], 0)
        self.sliderValLabel.configure(text = f"{self.caller.interactionCol[self.caller.interactionIndex].scoreVector[self.scoreIndex]}")

    def update(self):
        try:
            self.slider.set(self.caller.interactionCol[self.caller.interactionIndex].scoreVector[self.scoreIndex])
            self.sliderValLabel.configure(text = f"{self.caller.interactionCol[self.caller.interactionIndex].scoreVector[self.scoreIndex]}")
        except:
            pass

    def toggleEdit(self):
        if self.editMode == True:
            self.editButton.grid_forget()
            self.deleteButton.grid_forget()
            self.slider.grid(row = 0, column = 1, sticky = "new", padx = 5, pady = 5)
            self.sliderValLabel.grid(row = 0, column = 2, sticky = "new", padx = 5, pady = 5)
            self.editMode = False
        else:
            self.editButton.grid(row = 0, column = 3, sticky = "nsew", padx = 5, pady = 5)
            self.deleteButton.grid(column = 4, row = 0, sticky = "nsew", padx = 5, pady = 5)
            self.slider.grid_forget()
            self.sliderValLabel.grid_forget()
            self.editMode = True

    def editButtonPress(self):
        name = ModelEditWindow.metricEditWindow().onClose()[0]
        self.name  = name
        self.sliderLabel.configure(text = f"{self.name}")

    def deleteButtonPress(self):
        self.caller.deleteMetric(self)
        
class interactionInstance:
    def __init__(self, caller):
        self.caller = caller
        self.context = ""
        self.userQuery = ""
        self.response = ""
        self.id = None
        self.time = datetime.datetime.now()
        self.scoreVector = [0] * len(caller.metricCol)
        pass

class modelWrapper:

    def addMetric(self, name = None):
        if name == None:
            name = ModelEditWindow.metricEditWindow().onClose()[0]

        metricSlider(self, f"{name}")
        self.addMetricButton.grid(column = 0, row = len(self.metricCol) + 2, sticky = "nsew", padx = 5, pady = 5)

        try:
            for interaction in self.interactionCol:
                interaction.scoreVector.append(0)
                pass
        except:
            pass

    def write(self, text):
        self.responseTextBox.configure(state = "normal")
        self.responseTextBox.delete("0.0", "end")
        self.responseTextBox.insert("end", f"{text}\n")
        self.responseTextBox.configure(state = "disabled")
        pass
    
    def toggleEdit(self):
        if self.editMode == True:
            self.addMetricButton.grid_forget()
            self.editButton.grid_forget()
            self.deleteButton.grid_forget()
            self.editMode = False
        else:
            self.addMetricButton.grid(column = 0, row = len(self.metricCol) + 2, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)
            self.editButton.grid(column = 1, row = 0, sticky = "nsew", padx = 5, pady = 5)
            self.deleteButton.grid(column = 2, row = 0, sticky = "nsew", padx = 5, pady = 5)
            self.editMode = True

        for metric in self.metricCol:
            metric.toggleEdit()

    def update(self):
        try:
            self.write(self.interactionCol[self.interactionIndex].response)
        except:
            pass

        for metric in self.metricCol:
            metric.update()

    def addInteraction(self, query):
        newInteraction = interactionInstance(self)
        newInteraction.id = self.interactionID
        newInteraction.context = self.context
        newInteraction.userQuery = query

        self.model.model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        self.model.context = self.context + f"\n__USER__:" + f"{query}\n" + f"__EXPERT__:"
        response = self.model.query()
        self.model.model.to("cpu")

        newInteraction.response = response
        self.context = self.context + f"__USER__:{query}\n" + f"__EXPERT__:{response}\n"
        self.write(response)

        self.interactionCol.append(newInteraction)
        self.interactionIndex = self.interactionID
        self.interactionID += 1
        return response
    
    def editButtonPress(self):
        editArgs = ModelEditWindow.modelEditWindow().onClose()
        self.name = editArgs[0]
        self.Label.configure(text = f"{self.name}\n{self.modelDir}")

        if editArgs[1] != self.modelDir and editArgs[1] != "":
            self.modelDir = editArgs[1]
            delModel = self.model
            self.model = GenericModel.Model(self.modelDir)
            self.model.model.to("cpu")
            del delModel

        self.Label.configure(text = f"{self.name}\n{self.modelDir}", justify = "left", anchor = "w")
        pass

    def deleteButtonPress(self):
        self.caller.deleteModel(self)

    def deleteMetric(self, metric):
        try:
            for interaction in self.interactionCol:
                del interaction.scoreVector[metric.scoreIndex]
        except:
            pass

        for imetric in self.metricCol:
            if imetric != metric and imetric.scoreIndex > metric.scoreIndex:
                imetric.scoreIndex -= 1
        metric.frame.grid_forget()
        del metric

    def __init__(self, caller, name, modelDir):
        self.font = customtkinter.CTkFont(family= "Segoe UI", size= 18)
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)

        self.modelID = len(caller.modelCol)
        self.caller = caller
        self.modelDir = modelDir
        self.name = name
        self.metricCol = []
        self.interactionCol = []
        self.interactionID = 0
        self.interactionIndex = 0
        self.editMode = caller.editMode

        self.responseFrame = customtkinter.CTkFrame(self.caller.modelFrame)
        self.responseFrame.columnconfigure(0, weight= 1)
        self.responseFrame.grid(row = len(caller.modelCol) + 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.Label = customtkinter.CTkLabel(self.responseFrame, text = f"{self.name}\n{self.modelDir}", font = self.smallFont, justify = "left", anchor = "w")
        self.Label.grid(row = 0, column = 0, sticky = "nw", padx = 5, pady = 5)
        self.responseTextBox = customtkinter.CTkTextbox(self.responseFrame, height = 100, font = self.smallFont, wrap = "word")
        self.responseTextBox.grid(row = 1, column = 0, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)
        self.responseTextBox.configure(state = "disabled")
        self.editButton = customtkinter.CTkButton(self.responseFrame, text="Edit Model", command=self.editButtonPress, font = self.smallFont)
        self.editButton.grid(column = 1, row = 0, sticky = "nsew", padx = 5, pady = 5)
        self.deleteButton = customtkinter.CTkButton(self.responseFrame, text="Delete Model", command=self.deleteButtonPress, font = self.smallFont)
        self.deleteButton.grid(column = 2, row = 0, sticky = "nsew", padx = 5, pady = 5)
        self.addMetricButton = customtkinter.CTkButton(self.responseFrame, text="+", command=self.addMetric, font = self.font)
        self.addMetricButton.grid(column = 0, row = len(self.metricCol) + 2, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)

        self.addMetric("Overall")

        self.model =  GenericModel.Model(self.modelDir)
        self.model.model.to("cpu")
        self.context = f"""You are an AI named Elae and you are built as a lifelong companion to your creator named Alex. Your main objective is to provide useful feedback to Alex's prompts and assist in any tasks Alex assigns you.
Example Conversation:
time: {datetime.datetime.now()}
__USER__: Hi Elae how are you today?
__EXPERT__: I am doing well today Alex! Ready for anything you might throw at me.
time: {datetime.datetime.now()}
__USER__: Great! I would like to take a look into computer memory today.
__EXPERT__: That sounds great! Are we planning to add something to my capabilities?

Current Conversation:
__EXPERT__: Hi Alex, how can I help you?\n"""
        
        caller.modelCol.append(self)
        pass

class ElaeApplication:
    #Generic write to the chat window that keeps the window disabled for the user
    def write(self, text, justify):
        self.chatTextbox.configure(state = "normal")
        self.chatTextbox.insert("end", f"{text}\n", justify)
        self.chatTextbox.configure(state = "disabled")

    def userQuery(self, text):
        self.interactionIndex = self.interactionID
        self.interactionID += 1

        feedForwardText = text

        for model in self.modelCol:
            feedForwardText = model.addInteraction(feedForwardText)
            self.write(feedForwardText, "left")

        if self.interactionIndex > 0:
            self.backInteractionButton.configure(state = "normal")

    #Command for sending a query
    def buttonPress(self, * args):
        text = self.entry.get()
        self.entry.delete(0, "end")
        self.write(text, "right")

        self.userQuery(text)

        for model in self.modelCol:
            model.interactionIndex = self.interactionIndex
            model.update()

        self.interactionLabel.configure(text = f"Interaction {self.interactionIndex}")

    def nextInteractionPress(self):

        if self.modelCol[0].interactionIndex < len(self.modelCol[0].interactionCol) + 2 and self.interactionIndex != len(self.modelCol[0].interactionCol) - 1:
            self.interactionIndex += 1

        for model in self.modelCol:
            model.interactionIndex = self.interactionIndex
            model.update()

        self.interactionLabel.configure(text = f"Interaction {self.interactionIndex}")

        if self.interactionIndex == len(self.modelCol[0].interactionCol) - 1:
            self.nextInteractionButton.configure(state = "disabled")
        
        self.backInteractionButton.configure(state = "normal")

    def backInteractionPress(self):

        if len(self.modelCol[0].interactionCol) >= 1 and self.interactionIndex != 0:
                self.interactionIndex -= 1

        for model in self.modelCol:
            model.interactionIndex = self.interactionIndex
            model.update()

        self.interactionLabel.configure(text = f"Interaction {self.interactionIndex}")

        if self.interactionIndex == 0:
            self.backInteractionButton.configure(state = "disabled")
        
        self.nextInteractionButton.configure(state = "normal")

    def addModelButtonPress(self):
        editArgs = ModelEditWindow.modelEditWindow().onClose()
        modelWrapper(self, f"{editArgs[0]}", editArgs[1])
        self.addModelButton.grid(column = 0, row = len(self.modelCol) + 1, sticky = "nsew", padx = 5, pady = 5)
        pass

    #Closing hook
    def onClosing(self):
        timeStamp = datetime.datetime.now()
        timeStampString = f"{timeStamp.date()}_{timeStamp.hour}_{timeStamp.minute}"
        timeStampString = timeStampString.replace("-", "_")
        file = open(f"./transcripts/{timeStampString}_Transcript.json", "w+")
        file.write("{")
        for model in self.modelCol:
            file.write(f"\n\"{model.name}\" : ")
            file.write("{")
            file.write(f"\n\"directory\" : \"{model.modelDir}\",")
            for interaction in model.interactionCol:
                tempText = model.name.replace(" ", "_")
                file.write(f"\n\"{model.name}_interaction_{interaction.id}\" : ")
                file.write("{")
                file.write(f"\n\"id\" : {interaction.id},")
                file.write(f"\n\"time\" : \"{interaction.time}\",")
                tempString = interaction.context.replace("\n", "\\n")
                file.write(f"\n\"context\" : \"{tempString}\",")
                file.write(f"\n\"userQuery\" : \"{interaction.userQuery}\",")
                file.write(f"\n\"outerResponse\" : \"{interaction.response}\",")
                file.write(f"\n\"metrics\" : ")
                file.write("{")
                index = 0
                for metric in model.metricCol:
                    tempText = metric.name.replace(" ", "_")
                    if metric != model.metricCol[-1]:
                        file.write(f"\n\"{tempText}\" : {interaction.scoreVector[index]},")
                    else:
                        file.write(f"\n\"{tempText}\" : {interaction.scoreVector[index]}")
                    index += 1
                file.write("}")

                if interaction == model.interactionCol[-1]:
                    file.write("\n}")
                else:
                    file.write("\n},")

            if model == self.modelCol[-1]:
                file.write("\n}")
            else:
                file.write("\n},")
        file.write("\n}")
        file.close()

        self.root.destroy()
        pass

    #Save and train the model. User selects data to use in training set.
    def saveAndTrain(self):
        customtkinter.filedialog.askopenfilename()
        pass

    def saveModel(self):
        AtriaSaveLoad.saveModel(self)
    
    def toggleEdit(self):
        if self.editMode == True:
            self.addModelButton.grid_forget()
            self.editMode = False
        else:
            self.addModelButton.grid(column = 0, row = len(self.modelCol) + 1, sticky = "nsew", padx = 5, pady = 5)
            self.editMode = True
            pass
        pass

        for model in self.modelCol:
            model.toggleEdit()

    def deleteModel(self, model):
        for imodel in self.modelCol:
            if imodel != model and imodel.modelID > model.modelID:
                imodel.modelID -= 1
                imodel.responseFrame.grid(row = imodel.modelID + 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
        model.responseFrame.grid_forget()
        del self.modelCol[model.modelID]
        del model

    def __init__(self):
        self.saveDir = ""

        self.metricCol = []
        self.interactionID = 0
        self.interactionIndex = 0
        self.modelCol = []
        self.editMode = True

        #Root window
        self.root = customtkinter.CTk()
        self.root.geometry("1200x1000")
        self.root.title("Atria")
        self.root.grid_columnconfigure(0, weight= 1)
        self.root.grid_rowconfigure(0, weight= 1)

        #Menu
        self.menu = CTkMenuBar.CTkMenuBar(self.root, bg_color = "gray17")

        self.fileMenu = self.menu.add_cascade("File")
        self.fileDropdown = CTkMenuBar.CustomDropdownMenu(widget=self.fileMenu)
        self.fileDropdown.add_option("New Submodel")
        self.fileDropdown.add_option("Clone Submodel")
        self.fileDropdown.add_option("New Model")
        self.fileDropdown.add_option("Save Model", self.saveModel)
        self.fileDropdown.add_option("Save Model As...", self.saveModel)
        self.fileDropdown.add_option("Load Model")
        self.fileDropdown.add_option("Clone Model")
        self.fileDropdown.add_option("Train and Save Model", self.saveAndTrain)

        self.editMenu = self.menu.add_cascade("Edit")
        self.editDropdown = CTkMenuBar.CustomDropdownMenu(widget=self.editMenu)
        self.editDropdown.add_option("Toggle Edit Mode", self.toggleEdit)

        #Mainframe for whole window
        self.mainFrame = customtkinter.CTkFrame(self.root)
        self.mainFrame.columnconfigure(0, weight= 3)
        self.mainFrame.columnconfigure(2, weight= 1)
        self.mainFrame.rowconfigure(0, weight= 1)
        self.mainFrame.pack(fill = customtkinter.BOTH, expand = True)

        #Main chat window
        self.font = customtkinter.CTkFont(family= "Segoe UI", size= 18)
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)
        self.chatTextbox = customtkinter.CTkTextbox(self.mainFrame)
        self.chatTextbox.configure(font = self.font, wrap = "word")
        self.chatTextbox.grid(column = 0, columnspan = 2, row = 0, sticky = "nsew")
        self.chatTextbox.tag_config("right", justify = "right")
        self.chatTextbox.tag_config("left", justify = "left")
        self.write(f"Hi Alex, how can I help you?", "left")

        #Entry box and button
        self.entry = customtkinter.CTkEntry(self.mainFrame, placeholder_text= "Type anything to Elae!", font = self.font)
        self.entry.grid(row = 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.entry.bind("<Return>", self.buttonPress)

        self.entryButton = customtkinter.CTkButton(self.mainFrame, text="Send", command=self.buttonPress, font = self.font)
        self.entryButton.grid(column = 1, row = 1, sticky = "nsew", padx = 5, pady = 5)

        #Grading section
        self.gradingFrame = customtkinter.CTkFrame(self.mainFrame)
        self.gradingFrame.grid(row=0, column = 2, rowspan = 2, sticky = "nsew", padx = 5, pady = 5)
        self.gradingFrame.columnconfigure(0, weight= 1)
        self.gradingFrame.rowconfigure(1, weight= 1)

        self.interactionLabel = customtkinter.CTkLabel(self.gradingFrame, text = "Interact with Elae to see information here!", font = self.font)
        self.interactionLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)

        self.modelFrame = customtkinter.CTkScrollableFrame(self.gradingFrame)
        self.modelFrame.grid(row = 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.modelFrame.columnconfigure(0, weight= 1)

        #Add model button
        self.addModelButton = customtkinter.CTkButton(self.modelFrame, text="Add Model", command=self.addModelButtonPress, font = self.font)
        self.addModelButton.grid(column = 0, row = len(self.modelCol) + 1, sticky = "nsew", padx = 5, pady = 5)

        #Interaction buttons
        self.buttonFrame = customtkinter.CTkFrame(self.gradingFrame)
        self.buttonFrame.columnconfigure(0, weight= 1)
        self.buttonFrame.columnconfigure(1, weight= 1)
        self.buttonFrame.grid(row = 2, column = 0, sticky = "sew", padx = 5, pady = 5)
        self.backInteractionButton = customtkinter.CTkButton(self.buttonFrame, text = "Back", command = self.backInteractionPress, font = self.smallFont)
        self.backInteractionButton.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.backInteractionButton.configure(state = "disabled")
        self.nextInteractionButton = customtkinter.CTkButton(self.buttonFrame, text = "Next", command = self.nextInteractionPress, font = self.smallFont)
        self.nextInteractionButton.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
        self.nextInteractionButton.configure(state = "disabled")

        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.root.focus()
        self.root.mainloop()

if __name__ == "__main__":
    torch.cuda.empty_cache()
    applicationWindow = ElaeApplication()