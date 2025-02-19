import argparse
import yaml
from pathlib import Path

from datetime import timedelta

from swarmpal.io import create_paldata, PalDataItem

def str_to_timedelta(time):
    '''Convert strings that match 'HH:MM:SS' to datetime.timedelta ojbects.'''
    hours, minutes, seconds = (int(part) for part in time.split(":"))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

def main(args):

    with open(args.data_params) as f:
        datasets = yaml.safe_load(f)
    
    for name, dataset in datasets.items():
        provider = dataset.get('provider', 'none')
        print(f"Downloading '{name}' from {provider}")

        print(name, dataset)
        # Convert pad_times from strings to timedelta objects
        if 'pad_times' in dataset['params']:
            dataset['params']['pad_times'] = [
                str_to_timedelta(time)
                for time in dataset['params']['pad_times']
            ]

        if provider == 'vires':
            options = dict(asynchronous=False, show_progress=False)
            data = create_paldata(PalDataItem.from_vires(options=options, **dataset['params']))
        elif provider == 'hapi':
            options = dict(logging=False)
            data = create_paldata(PalDataItem.from_hapi(options=options, **dataset['params']))
        else:
            print(f'Unknown provider {provider}')
            continue

        filename = f'{name}.nc4'
        data.to_netcdf(args.data_dir / filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='generate_data.py',
        description='Downloads test data using swarmpal',
    )
    parser.add_argument('-d', '--data-dir', default='data', type=Path, 
        help='Directory where files will be saved to.'
    )
    parser.add_argument('data_params', 
        help='A filename for YAML formatted descriptions of each data set to generate.'
    )
    args = parser.parse_args()

    main(args)
