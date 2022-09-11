import os

class Paths:
    def __init__(self):
        self.DATA_ROOT = './data'
        self.DATA_PATH = self.DATA_ROOT
        self.FEATS_PATH = {
            'train' : self.DATA_PATH + '/feats' + '/train2014',
            'val'   : self.DATA_PATH + '/feats' + '/val2014',
            'test'  : self.DATA_PATH + '/feats' + '/test2015'
        }
        self.RAW_PATH = {
            'train'         : self.DATA_PATH + '/raw' + '/v2_OpenEnded_mscoco_train2014_questions.json',
            'train-anno'    : self.DATA_PATH + '/raw' + '/v2_mscoco_train2014_annotations.json',
            'val'           : self.DATA_PATH + '/raw' + '/v2_OpenEnded_mscoco_val2014_questions.json',
            'val-anno'      : self.DATA_PATH + '/raw' + '/v2_mscoco_val2014_annotations.json',
            'test'          : self.DATA_PATH + '/raw' + '/v2_OpenEnded_mscoco_test2015_questions.json',
        }
        self.SPLITS = {
            'train' : '',
            'val'   : 'val',
            'test'  : 'test',
        }
        self.RESULT_PATH    = './results/result_test'
        self.PRED_PATH      = './results/pred'
        self.CACHE_PATH     = './results/cache'
        self.LOG_PATH       = './results/log'
        self.CKPTS_PATH     = './ckpts'

        
        if 'result_test' not in os.listdir('./results'):
            os.mkdir('./results/result_test')
        if 'pred' not in os.listdir('./results'):
            os.mkdir('./results/pred')
        if 'cache' not in os.listdir('./results'):
            os.mkdir('./results/cache')
        if 'log' not in os.listdir('./results'):
            os.mkdir('./results/log')
        if 'ckpts' not in os.listdir('./'):
            os.mkdir('./ckpts')


    def check_path(self):
        print('Checking dataset ........')
        for item in self.FEATS_PATH:
            if not os.path.exists(self.FEATS_PATH[item]):
                print(self.FEATS_PATH[item], 'NOT EXIST')
                exit(-1)
        for item in self.RAW_PATH:
            if not os.path.exists(self.RAW_PATH[item]):
                print(self.RAW_PATH[item], 'NOT EXIST')
                exit(-1)
        print('Finished!')



if __name__ == "__main__":
    p = Paths()
    p.check_path()