import datetime
import os
import shutil
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as Data
from models.loader import ModelLoader
from utils.optim import adjust_lr, get_optim

from scripts.test_engine import ckpt_proc, test_engine


def train_engine(configuration, dataset, dataset_eval=None):
    data_size = dataset.data_size
    token_size = dataset.token_size
    ans_size = dataset.ans_size
    pretrained_emb = dataset.pretrained_emb

    net = ModelLoader(configuration).Net(
        configuration,
        pretrained_emb,
        token_size,
        ans_size
    )
    net.cuda()
    net.train()

    if configuration.N_GPU > 1:
        net = nn.DataParallel(net, device_ids=configuration.DEVICES)

    # Define Loss Function
    loss_fn = eval(f'torch.nn.{configuration.LOSS_FUNC_NAME_DICT[configuration.LOSS_FUNC]}(reduction="{configuration.LOSS_REDUCTION}").cuda()')

    # Load checkpoint if resume training
    if configuration.RESUME:
        print(' ========== Resume training')
        if configuration.CKPT_PATH is not None:
            print('Warning: Now using CKPT_PATH args, CKPT_VERSION and CKPT_EPOCH will not work')
            path = configuration.CKPT_PATH
        else:
            path = f'{configuration.CKPTS_PATH}/ckpt_{configuration.CKPT_VERSION}/epoch{str(configuration.CKPT_EPOCH)}.pkl'
        print(f'Loading ckpt from {path}')
        ckpt = torch.load(path)
        print('Finish!')

        if configuration.N_GPU > 1:
            net.load_state_dict(ckpt_proc(ckpt['state_dict']))
        else:
            net.load_state_dict(ckpt['state_dict'])
        start_epoch = ckpt['epoch']

        # Load the optimizer paramters
        optim = get_optim(configuration, net, data_size, ckpt['lr_base'])
        optim._step = int(data_size / configuration.BATCH_SIZE * start_epoch)
        optim.optimizer.load_state_dict(ckpt['optimizer'])
        
        if (f'ckpt_{configuration.VERSION}') not in os.listdir(configuration.CKPTS_PATH):
            os.mkdir(f'{configuration.CKPTS_PATH}/ckpt_{configuration.VERSION}')

    else:
        if ('ckpt_' + configuration.VERSION) not in os.listdir(configuration.CKPTS_PATH):
            os.mkdir(f'{configuration.CKPTS_PATH}/ckpt_{configuration.VERSION}')

        optim = get_optim(configuration, net, data_size)
        start_epoch = 0

    loss_sum = 0
    named_params = list(net.named_parameters())
    grad_norm = np.zeros(len(named_params))

    # Define multi-thread dataloader
    # if configuration.SHUFFLE_MODE in ['external']:
    #     dataloader = Data.DataLoader(
    #         dataset,
    #         batch_size=configuration.BATCH_SIZE,
    #         shuffle=False,
    #         num_workers=configuration.NUM_WORKERS,
    #         pin_memory=configuration.PIN_MEM,
    #         drop_last=True
    #     )
    # else:
    dataloader = Data.DataLoader(
        dataset,
        batch_size=configuration.BATCH_SIZE,
        shuffle=True,
        num_workers=configuration.NUM_WORKERS,
        pin_memory=configuration.PIN_MEM,
        drop_last=True
    )

    logfile = open(f'{configuration.LOG_PATH}/log_run_{configuration.VERSION}.txt', 'a+')
    logfile.write(str(configuration))
    logfile.close()

    # Training script
    for epoch in range(start_epoch, configuration.MAX_EPOCH):
        logfile = open(f'{configuration.LOG_PATH}/log_run_{configuration.VERSION}.txt', 'a+')
        logfile.write(
            '=====================================\n' +
            f"nowTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        logfile.close()

        # Learning Rate Decay
        if epoch in configuration.LR_DECAY_LIST:
            adjust_lr(optim, configuration.LR_DECAY_R)

        # Externally shuffle data list
        # if configuration.SHUFFLE_MODE == 'external':
        #     dataset.shuffle_list(dataset.ans_list)

        time_start = time.time()
        # Iteration
        for step, (
                frcn_feat_iter,
                grid_feat_iter,
                bbox_feat_iter,
                ques_ix_iter,
                ans_iter
        ) in enumerate(dataloader):
            optim.zero_grad()

            frcn_feat_iter = frcn_feat_iter.cuda()
            grid_feat_iter = grid_feat_iter.cuda()
            bbox_feat_iter = bbox_feat_iter.cuda()
            ques_ix_iter = ques_ix_iter.cuda()
            ans_iter = ans_iter.cuda()

            loss_tmp = 0
            for accu_step in range(configuration.GRAD_ACCU_STEPS):
                loss_tmp = 0

                sub_frcn_feat_iter = \
                    frcn_feat_iter[accu_step * configuration.SUB_BATCH_SIZE:
                                  (accu_step + 1) * configuration.SUB_BATCH_SIZE]
                sub_grid_feat_iter = \
                    grid_feat_iter[accu_step * configuration.SUB_BATCH_SIZE:
                                  (accu_step + 1) * configuration.SUB_BATCH_SIZE]
                sub_bbox_feat_iter = \
                    bbox_feat_iter[accu_step * configuration.SUB_BATCH_SIZE:
                                  (accu_step + 1) * configuration.SUB_BATCH_SIZE]
                sub_ques_ix_iter = \
                    ques_ix_iter[accu_step * configuration.SUB_BATCH_SIZE:
                                 (accu_step + 1) * configuration.SUB_BATCH_SIZE]
                sub_ans_iter = \
                    ans_iter[accu_step * configuration.SUB_BATCH_SIZE:
                             (accu_step + 1) * configuration.SUB_BATCH_SIZE]

                pred = net(
                    sub_frcn_feat_iter,
                    sub_grid_feat_iter,
                    sub_bbox_feat_iter,
                    sub_ques_ix_iter
                )

                loss_item = [pred, sub_ans_iter]
                loss_nonlinear_list = configuration.LOSS_FUNC_NONLINEAR[configuration.LOSS_FUNC]
                for item_ix, loss_nonlinear in enumerate(loss_nonlinear_list):
                    if loss_nonlinear in ['flat']:
                        loss_item[item_ix] = loss_item[item_ix].view(-1)
                    elif loss_nonlinear:
                        loss_item[item_ix] = eval(f'F.{loss_nonlinear}(loss_item[item_ix], dim=1)')

                loss = loss_fn(loss_item[0], loss_item[1])
                if configuration.LOSS_REDUCTION == 'mean':
                    # only mean-reduction needs be divided by grad_accu_steps
                    loss /= configuration.GRAD_ACCU_STEPS
                loss.backward()

                loss_tmp += loss.cpu().data.numpy() * configuration.GRAD_ACCU_STEPS
                loss_sum += loss.cpu().data.numpy() * configuration.GRAD_ACCU_STEPS

            if configuration.VERBOSE:
                if dataset_eval is not None:
                    mode_str = f"{configuration.SPLIT['train']} -> {configuration.SPLIT['val']}"
                else:
                    mode_str = f"{configuration.SPLIT['train']} -> {configuration.SPLIT['test']}"

                print("\r[Version %s][Model %s][Dataset %s][Epoch %2d][Step %4d/%4d][%s] Loss: %.4f, Lr: %.2e" % (
                    configuration.VERSION,
                    configuration.MODEL_USE,
                    configuration.DATASET,
                    epoch + 1,
                    step,
                    int(data_size / configuration.BATCH_SIZE),
                    mode_str,
                    loss_tmp / configuration.SUB_BATCH_SIZE,
                    optim._rate
                ), end='          ')

            # Gradient norm clipping
            if configuration.GRAD_NORM_CLIP > 0:
                nn.utils.clip_grad_norm_(
                    net.parameters(),
                    configuration.GRAD_NORM_CLIP
                )

            # Save the gradient information
            for name in range(len(named_params)):
                norm_v = torch.norm(named_params[name][1].grad).cpu().data.numpy() \
                    if named_params[name][1].grad is not None else 0
                grad_norm[name] += norm_v * configuration.GRAD_ACCU_STEPS
                # print('Param %-3s Name %-80s Grad_Norm %-20s'%
                #       (str(grad_wt),
                #        params[grad_wt][0],
                #        str(norm_v)))

            optim.step()

        time_end = time.time()
        elapse_time = time_end-time_start
        print(f'Finished in {int(elapse_time)}s')
        epoch_finish = epoch + 1

        # Save checkpoint
        if configuration.N_GPU > 1:
            state = {
                'state_dict': net.module.state_dict(),
                'optimizer': optim.optimizer.state_dict(),
                'lr_base': optim.lr_base,
                'epoch': epoch_finish
            }
        else:
            state = {
                'state_dict': net.state_dict(),
                'optimizer': optim.optimizer.state_dict(),
                'lr_base': optim.lr_base,
                'epoch': epoch_finish
            }
        torch.save(state, f'{configuration.CKPTS_PATH}/ckpt_{configuration.VERSION}/epoch{str(epoch_finish)}.pkl')

        # Logging
        logfile = open(f'{configuration.LOG_PATH}/log_run_{configuration.VERSION}.txt', 'a+')
        logfile.write(
            f'Epoch: {str(epoch_finish)}, Loss: {str(loss_sum / data_size)}, Lr: {str(optim._rate)}\n'
            f'Elapsed time: {str(int(elapse_time))}, Speed(s/batch): {str(elapse_time / step)} \n\n'
        )
        logfile.close()

        # Eval after every epoch
        if dataset_eval is not None:
            test_engine(
                configuration,
                dataset_eval,
                state_dict=net.state_dict(),
                validation=True
            )

        # if self.configuration.VERBOSE:
        #     logfile = open(
        #         self.configuration.LOG_PATH +
        #         '/log_run_' + self.configuration.VERSION + '.txt',
        #         'a+'
        #     )
        #     for name in range(len(named_params)):
        #         logfile.write(
        #             'Param %-3s Name %-80s Grad_Norm %-25s\n' % (
        #                 str(name),
        #                 named_params[name][0],
        #                 str(grad_norm[name] / data_size * self.configuration.BATCH_SIZE)
        #             )
        #         )
        #     logfile.write('\n')
        #     logfile.close()

        loss_sum = 0
        grad_norm = np.zeros(len(named_params))
