from importlib import import_module

class DataSetLoader:
    def __init__(self, configuration):
        self.configuration = configuration
        self.dataset = configuration.DATASET
        self.dataset_moudle = import_module(f'datasets.vqa')

    def DataSet(self):
        return self.dataset_moudle.DataSet(self.configuration)


class EvalLoader:
    def __init__(self, __C):
        self.__C = __C

        self.dataset = __C.DATASET
        # set evaluation loader for VQA2 dataset
        # at : openvqa/datasets/vqa/eval/result_eval
        eval_moudle_path = 'openvqa.datasets.' + self.dataset + '.' + 'eval' + '.' + 'result_eval'
        self.eval_moudle = import_module(eval_moudle_path)

    def eval(self, __arg1, __arg2, __arg3, __arg4, __arg5, __arg6, __arg7):
        return self.eval_moudle.eval(self.__C, __arg1, __arg2, __arg3, __arg4, __arg5, __arg6, __arg7)
