import copy
import os

from datasets.loader import DataSetLoader

from scripts.test_engine import test_engine
from scripts.train_engine import train_engine


class Execution:
    def __init__(self, configuration):
        self.configuration = configuration
        print('Loading dataset........')
        self.dataset = DataSetLoader(configuration).DataSet()

        self.dataset_eval = None
        if configuration.EVAL_EVERY_EPOCH:
            configuration_eval = copy.deepcopy(configuration)
            setattr(configuration_eval, 'RUN_MODE', 'val')
            print('Loading validation set for per-epoch evaluation........')
            self.dataset_eval = DataSetLoader(configuration_eval).DataSet()

    def run(self, run_mode):
        if run_mode == 'train':
            if self.configuration.RESUME is False:
                self.empty_log(self.configuration.VERSION)
            train_engine(self.configuration, self.dataset, self.dataset_eval)
        elif run_mode == 'val':
            test_engine(self.configuration, self.dataset, validation=True)
        elif run_mode == 'test':
            test_engine(self.configuration, self.dataset)
        else: exit(-1)

    def empty_log(self, version):
        print('Initializing log file........')
        logFileName = f'{self.configuration.LOG_PATH}/log_run_{version}.txt'
        if (os.path.exists(logFileName)): os.remove(logFileName)
        print('Finished!')
