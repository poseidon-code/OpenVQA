import torch
import torch.nn as nn
from core.dataset import BaseAdapter
from utils.make_mask import make_mask


class Adapter(BaseAdapter):
    def __init__(self, configuration):
        super(Adapter, self).__init__(configuration)
        self.configuration = configuration


    def vqa_init(self, configuration):
        pass

    def vqa_forward(self, feat_dict):
        frcn_feat = feat_dict['FRCN_FEAT']
        bbox_feat = feat_dict['BBOX_FEAT']
        img_feat_mask = make_mask(frcn_feat)

        return frcn_feat, img_feat_mask
