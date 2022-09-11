from core.configuration import Configuration

class ModelConfiguration(Configuration):
    def __init__(self):
        super(ModelConfiguration, self).__init__()

        self.IMG_FEAT_SIZE = 2048
        self.HIDDEN_SIZE = 512
        self.DROPOUT_R = 0.2
        self.CLASSIFER_DROPOUT_R = 0.5
        self.FLAT_OUT_SIZE = 1024
