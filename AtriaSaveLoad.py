import customtkinter
import json
import modelWrapper

def saveModel(application):
    if application.saveDir == "":
        application.saveDir = customtkinter.filedialog.asksaveasfilename(defaultextension=".tria", filetypes=(("Atria File", "*.tria"),))

    file = open(f"{application.saveDir}", "w+")
    file.write("{")
    for model in application.modelCol:
        file.write(f"\n\"{model.name}\" : ")
        file.write("{")
        file.write(f"\n\"identifier\" : \"{model.modelID}\",")
        file.write(f"\n\"directory\" : \"{model.modelDir}\",")
        file.write(f"\n\"name\" : \"{model.name}\",")
        file.write(f"\n\"inputToken\" : \"{model.inputToken}\",")
        file.write(f"\n\"outputToken\" : \"{model.outputToken}\",")
        tempString = model.startingContext.replace("\n", "\\n")
        file.write(f"\n\"startingContext\" : \"{tempString}\",")
        file.write(f"\n\"metrics\" : ")
        file.write("[")
        index = 0
        for metric in model.metricCol:
            tempText = metric.name.replace(" ", "_")
            if metric != model.metricCol[-1]:
                file.write(f"\n\"{tempText}\",")
            else:
                file.write(f"\n\"{tempText}\"")
            index += 1
        file.write("]")

        if model == application.modelCol[-1]:
            file.write("\n}")
        else:
            file.write("\n},")
    file.write("\n}")
    file.close()


    application.root.title(f"Atria\t{application.saveDir}")

def loadModel(application):
    # application.toggleEdit()
    application.saveDir = customtkinter.filedialog.askopenfilename(defaultextension=".tria", filetypes=(("Atria File", "*.tria"),))
    file = open(application.saveDir, "r")
    try:
        file = json.load(file)
    except:
        print("\nCould not load file")
        pass
    # print(file)
    for item in file:
        name = item
        dir = file[f"{name}"]["directory"]
        modelWrapper.modelWrapper(application, f"{name}",  f"{dir}")
        application.modelCol[-1].context = file[f"{name}"]["startingContext"]
        application.modelCol[-1].startingContext = file[f"{name}"]["startingContext"]
        application.modelCol[-1].inputToken = file[f"{name}"]["inputToken"]
        application.modelCol[-1].outputToken = file[f"{name}"]["outputToken"]
        application.addModelButton.grid(column = 0, row = len(application.modelCol) + 1, sticky = "nsew", padx = 5, pady = 5)
        for metric in file[f"{name}"]["metrics"]:
            # print(metric)
            if metric != "Overall":
                application.modelCol[-1].addMetric(metric)

    application.toggleEdit()
    application.root.title(f"Atria\t{application.saveDir}")
    pass