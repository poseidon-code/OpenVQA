from importlib import import_module


class ModelLoader:
    def __init__(self, __C):
        self.model_use = __C.MODEL_USE
        model_moudle_path = 'models.' + self.model_use + '.net'
        self.model_moudle = import_module(model_moudle_path)

    def Net(self, __arg1, __arg2, __arg3, __arg4):
        return self.model_moudle.Net(__arg1, __arg2, __arg3, __arg4)


class ModelConfigurationLoader:
    def __init__(self, model):
        self.configurationModule = import_module(f'models.{model}.model_cfgs')

    def load(self): 
        return self.configurationModule.ModelConfiguration()
