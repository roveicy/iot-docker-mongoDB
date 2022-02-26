import yaml

from sensors import ASDSensor, GPSSensor

if __name__ == '__main__':
    with open('../config/config.yaml', 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
        print(config)

    GPSSensor.load_assets()
    ASDSensor.load_assets()
    print(ASDSensor.wave_data[0])
