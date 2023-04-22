import yaml
from yaml.loader import SafeLoader


data_yaml = {
    'items': ['el_1', 'el_2'],
    'item_int': 1,
    'item_dict': {'el_1': '€'}
}

with open('file.yaml', 'w') as f:
    yaml.dump(data_yaml, f, default_flow_style=False, allow_unicode=True)

with open('file.yaml') as f:
    objects = yaml.load(f, Loader=SafeLoader)
    if objects == data_yaml:
        print(True)