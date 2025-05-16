import customtkinter
import CTkMenuBar
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import datetime

import ElaeModel

class metricSlider:
    def __init__(self, caller, root, text , r, c, scoreIndex):
        self.caller = caller
        self.scoreIndex = scoreIndex
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)
        self.frame = customtkinter.CTkFrame(root)
        self.frame.grid(row = r, column = c, sticky = "nsew", padx = 5, pady = 5)
        self.sliderLabel = customtkinter.CTkLabel(self.frame, text = f"{text}", font = self.smallFont)
        self.sliderLabel.grid(row = 0, column = 0, sticky = "new", padx = 5, pady = 5)
        self.slider = customtkinter.CTkSlider(self.frame, from_=0, to=100, command = self.innerSliderEvent)
        self.slider.grid(row = 0, column = 1, sticky = "new", padx = 5, pady = 5)
        self.slider.set(0)
        self.sliderValLabel = customtkinter.CTkLabel(self.frame, text = f"0", font = self.smallFont)
        self.sliderValLabel.grid(row = 0, column = 2, sticky = "new", padx = 5, pady = 5)

    def innerSliderEvent(self, * args):
        self.caller.responseCol[self.caller.interactionIndex].scoreVector[self.scoreIndex] = round(args[0], 0)
        self.sliderValLabel.configure(text = f"{self.caller.responseCol[self.caller.interactionIndex].scoreVector[self.scoreIndex]}")

    def update(self):
        self.slider.set(self.caller.responseCol[self.caller.interactionIndex].scoreVector[self.scoreIndex])
        self.sliderValLabel.configure(text = f"{self.caller.responseCol[self.caller.interactionIndex].scoreVector[self.scoreIndex]}")
        pass

    # def set(self, val):
    #     self.slider.configure(command = None)
    #     self.slider.set(val)
    #     self.sliderValLabel.configure(text = f"{self.caller.responseCol[self.caller.interactionIndex].scoreVector[self.scoreIndex]}")
    #     self.slider.configure(command = self.innerSliderEvent)

class interactionInstance:
    def __init__(self):
        self.innerContext = ""
        self.outerContext = ""
        self.innerResponse = ""
        self.outerResponse = ""
        self.id = None
        self.time = datetime.datetime.now()
        self.scoreVector = [0,0,0,0,0]
        pass

class ElaeApplication:
    #Generic write to the chat window that keeps the window disabled for the user
    def write(self, text, justify):
        self.chatTextbox.configure(state = "normal")
        self.chatTextbox.insert("end", f"{text}\n", justify)
        self.chatTextbox.configure(state = "disabled")

    def gradeWrite(self, intext, outtext):

        newInteraction = interactionInstance()
        newInteraction.innerResponse = intext
        newInteraction.outerResponse = outtext
        newInteraction.id = self.interactionID
        self.responseCol.append(newInteraction)


        self.interactionIndex = self.interactionID
        self.interactionID += 1
        self.interactionLabel.configure(text = f"Interaction {newInteraction.id}")

        self.innerOverallSlider.update()
        self.innerRelevanceSlider.update()
        self.outerOverallSlider.update()
        self.outerRelevanceSlider.update()
        self.outerCoheranceSlider.update()

        self.innerResponse.configure(state = "normal")
        self.innerResponse.delete("0.0", "end")
        self.innerResponse.insert("end", f"{self.responseCol[-1].innerResponse}\n")
        self.innerResponse.configure(state = "disabled")

        self.outerResponse.configure(state = "normal")
        self.outerResponse.delete("0.0", "end")
        self.outerResponse.insert("end", f"{self.responseCol[-1].outerResponse}\n")
        self.outerResponse.configure(state = "disabled")

        if len(self.responseCol) > 1:
            self.backInteractionButton.configure(state = "normal")

    #Command for sending a query
    def buttonPress(self, * args):
        text = self.entry.get()
        self.entry.delete(0, "end")
        self.write(text, "right")
        innerResponse, externalResponse = self.Elae.chatQuery(text)
        self.write(f"Internal: {innerResponse}", "left")
        self.write(f"External: {externalResponse}", "left")
        self.gradeWrite(innerResponse, externalResponse)

    def nextInteractionPress(self):

        if len(self.responseCol) > 1 and self.interactionIndex != len(self.responseCol) - 1:
            self.interactionIndex += 1

        self.innerOverallSlider.update()
        self.innerRelevanceSlider.update()
        self.outerOverallSlider.update()
        self.outerRelevanceSlider.update()
        self.outerCoheranceSlider.update()

        self.innerResponse.configure(state = "normal")
        self.innerResponse.delete("0.0", "end")
        self.innerResponse.insert("end", f"{self.responseCol[self.interactionIndex].innerResponse}\n")
        self.innerResponse.configure(state = "disabled")


        self.outerResponse.configure(state = "normal")
        self.outerResponse.delete("0.0", "end")
        self.outerResponse.insert("end", f"{self.responseCol[self.interactionIndex].outerResponse}\n")
        self.outerResponse.configure(state = "disabled")

        self.interactionLabel.configure(text = f"Interaction {self.responseCol[self.interactionIndex].id}")

        if self.interactionIndex == len(self.responseCol) - 1:
            self.nextInteractionButton.configure(state = "disabled")
        
        self.backInteractionButton.configure(state = "normal")

    def backInteractionPress(self):

        if len(self.responseCol) > 1 and self.interactionIndex != 0:
                self.interactionIndex -= 1

        self.innerOverallSlider.update()
        self.innerRelevanceSlider.update()
        self.outerOverallSlider.update()
        self.outerRelevanceSlider.update()
        self.outerCoheranceSlider.update()

        self.innerResponse.configure(state = "normal")
        self.innerResponse.delete("0.0", "end")
        self.innerResponse.insert("end", f"{self.responseCol[self.interactionIndex].innerResponse}\n")
        self.innerResponse.configure(state = "disabled")

        self.outerResponse.configure(state = "normal")
        self.outerResponse.delete("0.0", "end")
        self.outerResponse.insert("end", f"{self.responseCol[self.interactionIndex].outerResponse}\n")
        self.outerResponse.configure(state = "disabled")

        self.interactionLabel.configure(text = f"Interaction {self.responseCol[self.interactionIndex].id}")

        if self.interactionIndex == 0:
            self.backInteractionButton.configure(state = "disabled")
        
        self.nextInteractionButton.configure(state = "normal")
        
    #Closing hook
    def onClosing(self):
        timeStamp = datetime.datetime.now()
        timeStampString = f"{timeStamp.date()}_{timeStamp.hour}_{timeStamp.minute}"
        timeStampString.replace("-", "_")
        # file = open(f"./transcripts/{timeStampString}_Transcript.txt", "w+")
        # file.write(self.Elae.promptHistory)
        # file.close()
        self.root.destroy()
        pass

    def __init__(self):
        self.responseCol = []
        self.interactionID = 0
        self.interactionIndex = 0

        #Root window
        self.root = customtkinter.CTk()
        self.root.geometry("800x800")
        self.root.title("Elae")
        # self.root.iconbitmap()
        self.root.grid_columnconfigure(0, weight= 1)
        self.root.grid_rowconfigure(0, weight= 1)

        #Menu
        self.menu = CTkMenuBar.CTkMenuBar(self.root, bg_color = "gray17")

        self.fileMenu = self.menu.add_cascade("File")
        self.fileDropdown = CTkMenuBar.CustomDropdownMenu(widget=self.fileMenu)
        self.fileDropdown.add_option("Open")
        self.fileDropdown.add_option("Save")
        self.fileDropdown.add_option("Save As...")

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

        self.interactionLabel = customtkinter.CTkLabel(self.gradingFrame, text = "Interact with Elae to see information here!", font = self.font)
        self.interactionLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)

        #Inner Response Frame
        self.innerResponseFrame = customtkinter.CTkFrame(self.gradingFrame)
        self.innerResponseFrame.columnconfigure(0, weight= 1)
        self.innerResponseFrame.grid(row = 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.innerLabel = customtkinter.CTkLabel(self.innerResponseFrame, text = "Inner Response", font = self.smallFont)
        self.innerLabel.grid(row = 0, column = 0, columnspan = 2, sticky = "nw", padx = 5, pady = 5)
        self.innerResponse = customtkinter.CTkTextbox(self.innerResponseFrame, height = 100, font = self.smallFont, wrap = "word")
        self.innerResponse.grid(row = 1, column = 0, columnspan = 2, sticky = "nsew", padx = 5, pady = 5)
        self.innerResponse.configure(state = "disabled")

        self.innerOverallSlider = metricSlider(self, self.innerResponseFrame, "Overall", 2, 0, 0)
        self.innerRelevanceSlider = metricSlider(self, self.innerResponseFrame, "Relevance", 3, 0, 1)

        self.outerResponseFrame = customtkinter.CTkFrame(self.gradingFrame)
        self.outerResponseFrame.columnconfigure(0, weight= 1)
        self.outerResponseFrame.grid(row = 2, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.outerLabel = customtkinter.CTkLabel(self.outerResponseFrame, text = "External Response", font = self.smallFont)
        self.outerLabel.grid(row = 0, column = 0, sticky = "nw", padx = 5, pady = 5)
        self.outerResponse = customtkinter.CTkTextbox(self.outerResponseFrame, height = 100, font = self.smallFont, wrap = "word")
        self.outerResponse.grid(row = 1, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.outerResponse.configure(state = "disabled")

        self.outerOverallSlider = metricSlider(self, self.outerResponseFrame, "Overall", 2, 0, 2)
        self.outerRelevanceSlider = metricSlider(self, self.outerResponseFrame, "Relevance", 3, 0, 3)
        self.outerCoheranceSlider = metricSlider(self, self.outerResponseFrame, "Coherance", 4, 0, 4)

        self.buttonFrame = customtkinter.CTkFrame(self.gradingFrame)
        self.buttonFrame.columnconfigure(0, weight= 1)
        self.buttonFrame.columnconfigure(1, weight= 1)
        self.buttonFrame.grid(row = 3, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.backInteractionButton = customtkinter.CTkButton(self.buttonFrame, text = "Back", command = self.backInteractionPress, font = self.smallFont)
        self.backInteractionButton.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.backInteractionButton.configure(state = "disabled")
        self.nextInteractionButton = customtkinter.CTkButton(self.buttonFrame, text = "Next", command = self.nextInteractionPress, font = self.smallFont)
        self.nextInteractionButton.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
        self.nextInteractionButton.configure(state = "disabled")


        #Spinning up Elae
        self.Elae = ElaeModel.Elae()
        # self.Elae = None

        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.root.mainloop()

if __name__ == "__main__":
    torch.cuda.empty_cache()
    applicationWindow = ElaeApplication()