import yaml

from models.loader import ModelConfigurationLoader



RUN_MODE = ['train', 'val', 'test']
TRAIN_SPLIT = ['train', 'train+val']
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


options = {
    'RUN_MODE' : RUN_MODE[1],
    'TRAIN_SPLIT': TRAIN_SPLIT[1],
    'MODEL' : MODEL[0]
}


if __name__ == "__main__":
    with open(f"configs/{options['MODEL']}.yml", 'r') as f:
        modelConfiguration = yaml.full_load(f)
    
    configuration = ModelConfigurationLoader(modelConfiguration['MODEL_USE']).load()
    modelParameters = {**modelConfiguration, **options}
    configuration.add_args(modelParameters)
    print(configuration)

    # execution = Execution(cfg)
    # execution.run(cfg.RUN_MODE)
