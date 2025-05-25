import customtkinter

class modelEditWindow:
    def addModelButtonPress(self, * args):
        self.returnArgs = []
        self.returnArgs.append(self.name.get())
        self.returnArgs.append(self.modelDir)

        self.onClose()
    
    def browseModelDir(self):
        self.modelDir = customtkinter.filedialog.askdirectory()
        # self.dir.configure(placeholder_text = self.modelDir)
        self.dir.insert(0, self.modelDir)
        self.root.focus()

    def onClose(self):
        self.root.destroy()
        return self.returnArgs

    def __init__(self, *args):
        self.font = customtkinter.CTkFont(family= "Segoe UI", size= 18)
        self.smallFont = customtkinter.CTkFont(family= "Segoe UI", size= 14)

        self.returnArgs = []

        self.root = customtkinter.CTkToplevel()
        self.root.geometry("800x200")
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.title("Add or Edit Model")
        self.root.focus()
        self.root.columnconfigure(1, weight= 1)

        self.nameLabel = customtkinter.CTkLabel(self.root, text = "Name", font = self.font)
        self.nameLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)
        self.name = customtkinter.CTkEntry(self.root, placeholder_text= "Enter the name of your model", font = self.font)
        self.name.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
        self.name.bind("<Return>", self.addModelButtonPress)

        self.modelDir = ""
        self.dirLabel = customtkinter.CTkLabel(self.root, text = "Model Location", font = self.font)
        self.dirLabel.grid(row = 1, column = 0, sticky = "n", padx = 5, pady = 5)
        self.dir = customtkinter.CTkEntry(self.root, placeholder_text= "Enter the directory of your model", font = self.font)
        self.dir.grid(row = 1, column = 1, sticky = "nsew", padx = 5, pady = 5)
        self.browseModelButton = customtkinter.CTkButton(self.root, text="Browse", command=self.browseModelDir, font = self.font)
        self.browseModelButton.grid(row = 1, column = 2, sticky = "nsew", padx = 5, pady = 5)

        self.addModelButton = customtkinter.CTkButton(self.root, text="Add Model", command=self.addModelButtonPress, font = self.font)
        self.addModelButton.grid(column = 0, row = 2, sticky = "nsew", padx = 5, pady = 5)

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

        self.nameLabel = customtkinter.CTkLabel(self.root, text = "Name", font = self.font)
        self.nameLabel.grid(row = 0, column = 0, sticky = "n", padx = 5, pady = 5)
        self.name = customtkinter.CTkEntry(self.root, placeholder_text= "Enter the name of your model", font = self.font)
        self.name.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
        self.name.bind("<Return>", self.addMetricButtonPress)
        self.name.focus()

        self.addMetricButton = customtkinter.CTkButton(self.root, text="Add Metric", command=self.addMetricButtonPress, font = self.font)
        self.addMetricButton.grid(column = 0, row = 2, sticky = "nsew", padx = 5, pady = 5)

        self.root.wait_window()