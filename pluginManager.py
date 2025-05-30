import importlib.util
import os
import importlib

class pluginManager:
    def loadPlugins(self):
        for filename in os.listdir(self.pluginDir):
            if filename.endswith(".py"):
                print(filename)
                moduleName = filename[:-3]
                filepath = os.path.join(self.pluginDir, filename)
                try:
                    spec = importlib.util.spec_from_file_location(moduleName, filepath)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.plugins.append(module)
                except:
                    pass
        pass

    def runHook(self, hookName, *args, **kwargs):
        results = []
        for plugin in self.plugins:
            hook = getattr(plugin, hookName, None)
            
            if callable(hook):
                result = hook(*args, **kwargs)
                results.append(result)

    def __init__(self, pluginDir):
        self.pluginDir = pluginDir
        self.plugins = []
        pass