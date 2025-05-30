def __init__(rootApplication):
    print(f"\nInit Plugin Called")
    pass

def __preprocessing__(rootApplication):
    print(f"\nPreprocessing Plugin Called")
    pass

def __on_model_query__(rootApplication):
    print(f"\nModel Query Plugin Called")
    pass

def __on_model_output__(rootApplication):
    print(f"\nModel Output Plugin Called")
    pass

def __postprocessing__(rootApplication):
    print(f"\nPostprocessing Plugin Called")
    pass

def __close__(rootApplication):
    print(f"\nClosing Plugin Called")
    pass

def __on_exception__(rootApplication):
    print(f"\nException Plugin Called")
    pass