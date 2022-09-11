import os
import random
from types import MethodType

import numpy as np
import torch

from core.paths import Paths


class Configuration(Paths):
    def __init__(self):
        super(Configuration, self).__init__()

        self.BATCH_SIZE = 64
        self.BBOX_NORMALIZE = False
        self.CKPT_EPOCH = 0
        self.CKPT_PATH = None
        self.SEED = random.randint(0, 9999999)
        self.VERSION = str(self.SEED)
        self.CKPT_VERSION = self.VERSION
        self.DATASET = 'vqa'
        self.EVAL_EVERY_EPOCH = True
        self.FEAT_SIZE = {
            'FRCN_FEAT_SIZE': (100, 2048),
            'BBOX_FEAT_SIZE': (100, 5),
        }
        self.GPU = '0'
        self.GRAD_ACCU_STEPS = 1
        self.GRAD_NORM_CLIP = -1
        self.LOSS_FUNC = ''
        self.LOSS_REDUCTION = ''
        self.LR_BASE = 0.0001
        self.LR_DECAY_LIST = [10, 12]
        self.LR_DECAY_R = 0.2
        self.MAX_EPOCH = 13
        self.MODEL = ''
        self.MODEL_USE = ''
        self.NUM_WORKERS = 8
        self.OPT = ''
        self.OPT_PARAMS = {}
        self.PIN_MEM = True
        self.RESUME = False
        self.RUN_MODE = ''
        self.TEST_SAVE_PRED = False
        self.TRAIN_SPLIT = 'train'
        self.USE_GLOVE = True
        self.VERBOSE = True
        self.WORD_EMBED_SIZE = 300
        self.WARMUP_EPOCH = 3


    def add_args(self, args_dict):
        for arg in args_dict : setattr(self, arg, args_dict[arg])


    def proc(self):
        assert self.RUN_MODE in ['train', 'val', 'test']

        # ------------ Devices setup
        os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU
        self.N_GPU = len(self.GPU.split(','))
        self.DEVICES = [_ for _ in range(self.N_GPU)]
        torch.set_num_threads(2)


        # ------------ Path check
        self.check_path()

        # ------------ Seed setup
        # fix pytorch seed
        torch.manual_seed(self.SEED)
        if self.N_GPU < 2:
            torch.cuda.manual_seed(self.SEED)
        else:
            torch.cuda.manual_seed_all(self.SEED)
        torch.backends.cudnn.deterministic = True

        # fix numpy seed
        np.random.seed(self.SEED)

        # fix random seed
        random.seed(self.SEED)

        if self.CKPT_PATH is not None:
            print("Warning: you are now using 'CKPT_PATH' args, "
                  "'CKPT_VERSION' and 'CKPT_EPOCH' will not work")
            self.CKPT_VERSION = self.CKPT_PATH.split('/')[-1] + '_' + str(random.randint(0, 9999999))


        # ------------ Split setup
        self.SPLIT = self.SPLITS
        self.SPLIT['train'] = self.TRAIN_SPLIT
        if self.SPLIT['val'] in self.SPLIT['train'].split('+') or self.RUN_MODE not in ['train']:
            self.EVAL_EVERY_EPOCH = False

        if self.RUN_MODE not in ['test']:
            self.TEST_SAVE_PRED = False


        # ------------ Gradient accumulate setup
        assert self.BATCH_SIZE % self.GRAD_ACCU_STEPS == 0
        self.SUB_BATCH_SIZE = int(self.BATCH_SIZE / self.GRAD_ACCU_STEPS)

        # Set small eval batch size will reduce gpu memory usage
        self.EVAL_BATCH_SIZE = int(self.SUB_BATCH_SIZE / 2)


        # ------------ Loss process
        assert self.LOSS_FUNC in ['ce', 'bce', 'kld', 'mse']
        assert self.LOSS_REDUCTION in ['none', 'elementwise_mean', 'sum']

        self.LOSS_FUNC_NAME_DICT = {
            'ce': 'CrossEntropyLoss',
            'bce': 'BCEWithLogitsLoss',
            'kld': 'KLDivLoss',
            'mse': 'MSELoss',
        }

        self.LOSS_FUNC_NONLINEAR = {
            'ce': [None, 'flat'],
            'bce': [None, None],
            'kld': ['log_softmax', None],
            'mse': [None, None],
        }

        self.TASK_LOSS_CHECK = {
            'vqa': ['bce', 'kld'],
            'gqa': ['ce'],
            'clevr': ['ce'],
        }

        assert self.LOSS_FUNC in self.TASK_LOSS_CHECK, \
            self.DATASET + 'task only support' + str(self.TASK_LOSS_CHECK) + 'loss.' + \
            'Modify the LOSS_FUNC in configs to get a better score.'


        # ------------ Optimizer parameters process
        assert self.OPT in ['Adam', 'Adamax', 'RMSprop', 'SGD', 'Adadelta', 'Adagrad']
        optim = getattr(torch.optim, self.OPT)
        default_params_dict = dict(zip(optim.__init__.__code__.co_varnames[3: optim.__init__.__code__.co_argcount],
                                       optim.__init__.__defaults__[1:]))

        def all(iterable):
            for element in iterable:
                if not element:
                    return False
            return True
        assert all(list(map(lambda x: x in default_params_dict, self.OPT_PARAMS)))

        for key in self.OPT_PARAMS:
            if isinstance(self.OPT_PARAMS[key], str):
                self.OPT_PARAMS[key] = eval(self.OPT_PARAMS[key])
            else:
                print("To avoid ambiguity, set the value of 'OPT_PARAMS' to string type")
                exit(-1)
        self.OPT_PARAMS = {**default_params_dict, **self.OPT_PARAMS}

    def __str__(self):
        __C_str = ''
        for attr in dir(self):
            if not attr.startswith('__') and not isinstance(getattr(self, attr), MethodType):
                __C_str += '{ %-17s }->' % attr + str(getattr(self, attr)) + '\n'

        return __C_str
