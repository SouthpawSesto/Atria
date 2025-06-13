#External Libraries
import customtkinter
import CTkMenuBar
import torch
import datetime
import os
import sys
import json
from PIL import Image, ImageTk

#Internal Modules
import modelWrapper
import modelEditWindow
import AtriaSaveLoad
import pluginManager

class ElaeApplication:
    #Generic write to the chat window that keeps the window disabled for the user
    def write(self, text, justify = "left", sys = False):
        if sys == True:
            self.chatTextbox._textbox.image_create("end", image = self.sysImage)

        self.chatTextbox.configure(state = "normal")
        self.chatTextbox.insert("end", f"{text}\n", justify)
        self.chatTextbox.configure(state = "disabled")

    def userQuery(self, text):
        self.interactionIndex = self.interactionID
        self.interactionID += 1

        feedForwardText = text

        for model in self.modelCol:
            #Example of running plugin
            self.pluginManager.runHook("__on_model_query__", self)

            feedForwardText = model.addInteraction(feedForwardText)
            self.write(feedForwardText, "left")

            #Example of running plugin
            self.pluginManager.runHook("__on_model_output__", self)

        if self.interactionIndex > 0:
            self.backInteractionButton.configure(state = "normal")

    #Command for sending a query
    def buttonPress(self, * args):
        self.chatSaved = False

        text = self.entry.get()
        self.entry.delete(0, "end")
        self.write(text, "right")

        #Example of running plugin
        self.pluginManager.runHook("__preprocessing__", self)

        self.userQuery(text)

        for model in self.modelCol:
            model.interactionIndex = self.interactionIndex
            model.update()

        #Example of running plugin
        self.pluginManager.runHook("__postprocessing__", self)

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
        editArgs = modelEditWindow.modelEditWindow().onClose()
        if editArgs != []:
            modelWrapper.modelWrapper(self, f"{editArgs[0]}", editArgs[1])
            self.modelCol[-1].context = editArgs[2]
            self.modelCol[-1].startingContext = editArgs[2]
        self.addModelButton.grid(column = 0, row = len(self.modelCol) + 1, sticky = "nsew", padx = 5, pady = 5)
        pass

    #Closing hook
    def onClosing(self):
        self.saveChat()

        self.root.destroy()
        pass

    #Save and train the model. User selects data to use in training set.
    def saveAndTrain(self):
        self.newChat()

        self.chatTextbox.configure(state = "normal")
        self.chatTextbox.delete("0.0", "end")
        self.chatTextbox.configure(state = "disabled")

        self.chatTextbox._textbox.image_create("end", image = self.logoImage)
        self.chatTextbox.tag_add("center", "0.0", "end")
        self.write(f"\n")

        transcriptFile = customtkinter.filedialog.askopenfilename(initialdir = f"{self.baseDir}transcripts",title = f"Trianing File", defaultextension= ".json", filetypes=(("JSON File", "*.json"),))
        outputDir = []
        for model in self.modelCol:
            outputDir.append(customtkinter.filedialog.askdirectory(initialdir= f"{self.baseDir}", title = f"Output directory for model: {model.name}"))

        newModelDirectories = []
        i = 0
        for model in self.modelCol:
            self.write(f"Training Model: {model.name}", sys = True)
            self.root.update()
            newModelDirectories.append(model.model.train(transcriptFile, outputDir[i]))
            # newModelDirectories.append("Test")
            self.write(f"Finished Training Model: {model.name}", sys = True)
            self.root.update()
            i += 1

        self.write(f"Finished Training", sys = True)

        yesNo = modelEditWindow.yesNoWindow().onClose()
        if yesNo == "Yes":
            i = 0
            for model in self.modelCol:
                editArgs = []
                editArgs.append(model.name)
                editArgs.append(newModelDirectories[i])
                editArgs.append(model.context)
                editArgs.append(model.inputToken)
                editArgs.append(model.outputToken)
                model.editButtonPress(editArgs)
                i += 1

        pass
    
    def newModel(self):
        self.saveDir = ""
        self.root.title("Atria")
        while self.modelCol != []:
            self.deleteModel(self.modelCol[0])
        
        self.editMode = False
        self.toggleEdit()
        pass

    def saveModel(self):
        AtriaSaveLoad.saveModel(self)

    def saveModelAs(self):
        self.saveDir = ""
        AtriaSaveLoad.saveModel(self)

    def loadModel(self):
        self.newModel()
        AtriaSaveLoad.loadModel(self)
    
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

    def saveChat(self):
        if self.interactionID != 0 and self.chatSaved == False:
            timeStamp = datetime.datetime.now()
            timeStampString = f"{timeStamp.date()}_{timeStamp.hour}_{timeStamp.minute}"
            timeStampString = timeStampString.replace("-", "_")

            fileName = customtkinter.filedialog.asksaveasfilename(initialdir= f"{self.baseDir}transcripts", initialfile =f"{timeStampString}_Transcript.json", defaultextension= ".json", filetypes= (("JSON File", "*.json"),))
            try:
                file = open(f"{fileName}", "w+")
            except:
                self.chatSaved = True
                return
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
                    file.write(f"\n\"response\" : \"{interaction.response}\",")
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

            self.chatSaved = True

    def newChat(self):
        self.saveChat()

        self.chatTextbox.configure(state = "normal")
        self.chatTextbox.delete("0.0", "end")
        self.chatTextbox.configure(state = "disabled")

        self.chatTextbox._textbox.image_create("end", image = self.logoImage)
        self.chatTextbox.tag_add("center", "0.0", "end")

        self.write(f"\n\nHi {self.userName}, how can I help you?", "left")

        for model in self.modelCol:
            model.context = model.startingContext
            model.interactionCol = []
            model.responseTextBox.configure(state = "normal")
            model.responseTextBox.delete("0.0", "end")
            model.responseTextBox.configure(state = "disabled")

            self.backInteractionButton.configure(state = "disabled")
            self.nextInteractionButton.configure(state = "disabled")
            self.interactionLabel.configure(text = "Interact with your model to see information here!")

            for metric in model.metricCol:
                metric.slider.set(0)

    def loadUserConfig(self):
        try:
            file = open(self.baseDir + "userConfig.config", "r")
            file = json.load(file)
            self.userName = file["username"]
        except:
            file = open(self.baseDir + "userConfig.config", "w+")
            file.write("{")
            file.write(f"\n\"username\" : \"{self.userName}\"")
            file.write("\n}")
            file.close()

    def editPreferences(self):
        args = modelEditWindow.preferencesEditWindow(self).onClose()
        if args != []:
            self.userName = args[0]
            print(f"\nUsername set to {self.userName}!")
            self.newChat()
    
    def getBasePath(self):
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        self.saveDir = ""
        self.chatSaved = True
        self.userName = "User"

        self.metricCol = []
        self.interactionID = 0
        self.interactionIndex = 0
        self.modelCol = []
        self.editMode = True
        self.baseDir = self.getBasePath()
        self.baseDir = self.baseDir.replace("\\", "/")
        self.baseDir += "/"

        self.loadUserConfig()


        #Root window
        self.root = customtkinter.CTk()
        self.root.geometry("1200x1000")
        self.root.title("Atria")
        self.root.grid_columnconfigure(0, weight= 1)
        self.root.grid_rowconfigure(0, weight= 1)
        self.root.iconbitmap(self.baseDir + "Art/AtriaLogo2.ico")

        self.sysImage = Image.open(self.baseDir + "Art/AtriaLogo2.ico")
        self.sysImage = self.sysImage.resize((25,25))
        self.sysImage = ImageTk.PhotoImage(self.sysImage)
        self.logoImage = Image.open(self.baseDir + "Art/AtriaLogo2.ico")
        self.logoImage = self.logoImage.resize((100,100))
        self.logoImage = ImageTk.PhotoImage(self.logoImage)

        #Menu
        self.menu = CTkMenuBar.CTkMenuBar(self.root, bg_color = "gray17")

        self.fileMenu = self.menu.add_cascade("File")
        self.fileDropdown = CTkMenuBar.CustomDropdownMenu(widget=self.fileMenu)
        self.fileDropdown.add_option("New Model", self.newModel)
        self.fileDropdown.add_option("Save Model", self.saveModel)
        self.fileDropdown.add_option("Save Model As...", self.saveModelAs)
        self.fileDropdown.add_option("Load Model", self.loadModel)
        self.fileDropdown.add_option("Preferences...", self.editPreferences)

        self.editMenu = self.menu.add_cascade("Edit")
        self.editDropdown = CTkMenuBar.CustomDropdownMenu(widget=self.editMenu)
        self.editDropdown.add_option("Toggle Edit Mode", self.toggleEdit)

        self.editMenu = self.menu.add_cascade("Chat")
        self.editDropdown = CTkMenuBar.CustomDropdownMenu(widget=self.editMenu)
        self.editDropdown.add_option("Save Chat", self.saveChat)
        self.editDropdown.add_option("New Chat", self.newChat)

        self.trainMenu = self.menu.add_cascade("Train")
        self.trainDropdown = CTkMenuBar.CustomDropdownMenu(widget=self.trainMenu)
        self.trainDropdown.add_option("Save and Train", self.saveAndTrain)

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
        self.chatTextbox.tag_config("center", justify = "center")

        self.newChat()

        # self.write(self.getBasePath())
        # self.write(self.baseDir)

        #Entry box and button
        self.entry = customtkinter.CTkEntry(self.mainFrame, placeholder_text= "Type anything to your model!", font = self.font)
        self.entry.grid(row = 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.entry.bind("<Return>", self.buttonPress)

        self.entryButton = customtkinter.CTkButton(self.mainFrame, text="Send", command=self.buttonPress, font = self.font)
        self.entryButton.grid(column = 1, row = 1, sticky = "nsew", padx = 5, pady = 5)

        #Grading section
        self.gradingFrame = customtkinter.CTkFrame(self.mainFrame)
        self.gradingFrame.grid(row=0, column = 2, rowspan = 2, sticky = "nsew", padx = 5, pady = 5)
        self.gradingFrame.columnconfigure(0, weight= 1)
        self.gradingFrame.rowconfigure(1, weight= 1)

        self.interactionLabel = customtkinter.CTkLabel(self.gradingFrame, text = "Interact with your model to see information here!", font = self.font)
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

        #Load plugins
        self.pluginManager = pluginManager.pluginManager(self.baseDir + "plugins")
        self.pluginManager.loadPlugins()

        try:
            self.newModel()
            self.saveDir = sys.argv[1]
            AtriaSaveLoad.loadModel(self, sys.argv[1])
        except:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.root.focus()

        #Example of running plugin
        self.pluginManager.runHook("__init__", self)

        self.root.mainloop()

        #Example of running plugin
        self.pluginManager.runHook("__close__", self)

if __name__ == "__main__":

    torch.cuda.empty_cache()
    applicationWindow = ElaeApplication()