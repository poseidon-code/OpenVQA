from importlib import import_module


class ModelLoader:
    def __init__(self, configuration):
        self.model_use = configuration.MODEL_USE
        self.model_moudle = import_module(f'models.{self.model_use}.net')

    def Net(self, __arg1, __arg2, __arg3, __arg4):
        return self.model_moudle.Net(__arg1, __arg2, __arg3, __arg4)


class ModelConfigurationLoader:
    def __init__(self, model):
        self.configurationModule = import_module(f'models.{model}.model_cfgs')

    def load(self): 
        return self.configurationModule.ModelConfiguration()
