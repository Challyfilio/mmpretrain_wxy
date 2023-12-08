_base_ = [
    '../_base_/datasets/imagenet_bs256_simmim_192.py',
    '../_base_/default_runtime.py',
]

# >>>>>>>>>>>>>>> 在此重载数据设置 >>>>>>>>>>>>>>>>>>>
train_dataloader = dict(
    dataset=dict(
        type='CustomDataset',
        data_root='/workspace/pycharm_project/Dataset/pretrain/',  # 改路径..........
        ann_file='',  # 我们假定使用子文件夹格式，因此需要将标注文件置空
        data_prefix='',  # 使用 `data_root` 路径下所有数据
        with_label=False,
    )
)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
pretrained_tiny = 'https://github.com/SwinTransformer/storage/releases/download/v1.0.0/swin_tiny_patch4_window7_224.pth'  # noqa

# model settings
model = dict(
    type='SimMIM',
    backbone=dict(
        type='SimMIMSwinTransformer',
        arch='tiny',
        img_size=192,
        stage_cfgs=dict(block_cfgs=dict(window_size=6)),
        init_cfg=dict(type='Pretrained', checkpoint=pretrained_tiny)),
    neck=dict(
        type='SimMIMLinearDecoder', in_channels=128 * 2 * 3, encoder_stride=32),  # 128 * 2**3
    head=dict(
        type='SimMIMHead',
        patch_size=4,
        loss=dict(type='PixelReconstructionLoss', criterion='L1', channel=3)))

# optimizer wrapper
optim_wrapper = dict(
    type='AmpOptimWrapper',
    optimizer=dict(
        type='AdamW',
        lr=2e-4 * 2048 / 512,
        betas=(0.9, 0.999),
        weight_decay=0.05),
    clip_grad=dict(max_norm=5.0),
    paramwise_cfg=dict(
        custom_keys={
            'norm': dict(decay_mult=0.0),
            'bias': dict(decay_mult=0.0),
            'absolute_pos_embed': dict(decay_mult=0.),
            'relative_position_bias_table': dict(decay_mult=0.)
        }))

# learning rate scheduler
param_scheduler = [
    dict(
        type='LinearLR',
        start_factor=1e-6 / 2e-4,
        by_epoch=True,
        begin=0,
        end=10,
        convert_to_iter_based=True),
    dict(
        type='CosineAnnealingLR',
        T_max=90,
        eta_min=1e-5 * 2048 / 512,
        by_epoch=True,
        begin=10,
        end=100,
        convert_to_iter_based=True)
]

# runtime
train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=100)
default_hooks = dict(
    # only keeps the latest 3 checkpoints
    checkpoint=dict(type='CheckpointHook', interval=10, max_keep_ckpts=3))

# NOTE: `auto_scale_lr` is for automatically scaling LR
# based on the actual training batch size.
auto_scale_lr = dict(base_batch_size=2048)
