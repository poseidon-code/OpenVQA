import yaml

from models.loader import ModelConfigurationLoader
from scripts.exec import Execution

'''
## REQUIRED: external configuration parameters
MODEL = [
    'ban_4',
    'ban_8',
    'butd',
    'mcan_large',
    'mcan_small',
    'mfb',
    'mfh',
    'mmnasnet_large',
    'mmnasnet_small'
]

RUN_MODE = ['train', 'val', 'test']


## OPTIONAL: external configuration parameters
TRAIN_SPLIT = ['train', 'train+val']
# set training split

EVAL_EVERY_EPOCH = [True, False] 
# True: evaluate the val split when an epoch finished
# False: do not evaluate on local

TEST_SAVE_PRED = [True, False]
# True: save the prediction vectors
# False: do not save the prediction vectors

BATCH_SIZE = Integer
# batch size in training

GPU = Integer 
# gpu choose

SEED = Integer
# fix random seed

VERSION = String
# version control

RESUME = [True, False]
# True: use checkpoint to resume training
# False: start training with random init

CKPT_VERSION = String
# checkpoint version

CKPT_EPOCH = Integer
# checkpoint epoch

CKPT_PATH = String
# load checkpoint path
# recommended - use CKPT_VERSION and CKPT_EPOCH instead
# overrides CKPT_VERSION and CKPT_EPOCH

GRAD_ACCU_STEPS = Integer
# split batch to reduce gpu memory usage

NUM_WORKERS = Integer
# multithreaded loading to accelerate IO

PIN_MEM = [True, False]
# True: use pin memory
# False: not use pin memory

VERBOSE = [True, False]
# True: verbose print
# False: simple print
'''


options = {
    # required
    'MODEL' : 'ban_4',
    'RUN_MODE' : 'train',

    # optionals
    'TRAIN_SPLIT': 'train',
    'VERBOSE': True
}


if __name__ == "__main__":
    with open(f"configs/{options['MODEL']}.yml", 'r') as f:
        modelConfiguration = yaml.full_load(f)
    
    configuration = ModelConfigurationLoader(modelConfiguration['MODEL_USE']).load()
    modelParameters = {**modelConfiguration, **options}
    configuration.add_args(modelParameters)
    configuration.proc()
    print(configuration)

    execution = Execution(configuration)
    # execution.run(cfg.RUN_MODE)
