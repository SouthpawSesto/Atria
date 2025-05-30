import customtkinter

def saveModel(application):
    if application.saveDir == "":
        application. saveDir = customtkinter.filedialog.asksaveasfilename(defaultextension=".tria", filetypes=(("Atria File", "*.tria"),))

    file = open(f"{application.saveDir}", "w+")
    file.write("{")
    for model in application.modelCol:
        file.write(f"\n\"{model.name}\" : ")
        file.write("{")
        file.write(f"\n\"identifier\" : \"{model.modelID}\",")
        file.write(f"\n\"directory\" : \"{model.modelDir}\",")
        file.write(f"\n\"name\" : \"{model.name}\",")
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

def loadModel(application):
    pass