import customtkinter
import torch
import datetime

import GenericModel
import ModelEditWindow

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
        self.model.context = self.context + f"\n{self.inputToken}:" + f"{query}\n" + f"{self.outputToken}:"
        response = self.model.query()
        self.model.model.to("cpu")

        newInteraction.response = response
        self.context = self.context + f"{self.inputToken}:{query}\n" + f"{self.outputToken}:{response}\n"
        self.write(response)

        self.interactionCol.append(newInteraction)
        self.interactionIndex = self.interactionID
        self.interactionID += 1
        return response
    
    def editButtonPress(self, editArgs = None):
        if editArgs == None:
            editArgs = ModelEditWindow.modelEditWindow(self).onClose()
        else:
            self.name = editArgs[0]
            self.modelDir = editArgs[1]
            self.context = editArgs[2]
            self.inputToken = editArgs[3]
            self.outputToken = editArgs[4]
            self.startingContext = self.context
            self.model.outputToken = self.outputToken

        if editArgs != [] or editArgs != None:
            self.name = editArgs[0]
            self.modelDir = editArgs[1]
            self.context = editArgs[2]
            self.inputToken = editArgs[3]
            self.outputToken = editArgs[4]
            self.startingContext = self.context
            self.model.outputToken = self.outputToken

            if editArgs[1] != self.modelDir and editArgs[1] != "":
                try:
                    delModel = self.model
                    self.model = GenericModel.Model(self.modelDir)
                    self.model.model.to("cpu")
                    self.model.name = self.name
                    self.model.inputToken = self.inputToken
                    self.model.outputToken = self.outputToken
                    self.model.parent = self.caller
                    del delModel
                except:
                    self.caller.write(f"Could not load model at {self.modelDir}")

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
        self.inputToken = ""
        self.outputToken = ""

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

        self.specialTokens = []
        try:
            self.model = GenericModel.Model(self.modelDir)
            self.model.model.to("cpu")
            self.model.name = self.name
            self.model.inputToken = self.inputToken
            self.model.outputToken = self.outputToken
            self.model.parent = self.caller

            for item in self.model.tokenizer.get_added_vocab():
                # print(item)
                self.specialTokens.append(item)
        except:
            self.caller.write(f"Could not load model at {self.modelDir}", "left")

        self.context = ""
        self.startingContext = self.context
        caller.modelCol.append(self)
        pass