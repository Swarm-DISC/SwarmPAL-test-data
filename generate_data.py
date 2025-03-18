import argparse
import yaml
from pathlib import Path
import hashlib

from datetime import timedelta

import swarmpal.toolboxes
from swarmpal.io import create_paldata, PalDataItem

def str_to_timedelta(time):
    '''Convert strings that match 'HH:MM:SS' to datetime.timedelta ojbects.'''
    hours, minutes, seconds = (int(part) for part in time.split(":"))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

def calc_md5sum(filename):
    '''Calculate the md5sum of the content of a file'''
    return hashlib.md5(open(filename, 'rb').read()).hexdigest()

def main(args):

    with open(args.data_params) as f:
        datasets = yaml.safe_load(f)
    
    registry = {}
    for name, dataset in datasets.items():
        data_spec = dataset['data']
        provider, config = data_spec['provider'], data_spec['config']
        print(f"Downloading '{name}' from {provider}")

        # Convert pad_times from strings to timedelta objects
        if 'pad_times' in config:
            config['pad_times'] = [
                str_to_timedelta(time)
                for time in config['pad_times']
            ]

        # Download the data
        if provider == 'vires':
            options = dict(asynchronous=False, show_progress=False)
            data = create_paldata(PalDataItem.from_vires(options=options, **config))
        elif provider == 'hapi':
            options = dict(logging=False)
            data = create_paldata(PalDataItem.from_hapi(options=options, **config))
        else:
            print(f'Unknown provider {provider}')
            continue
        
        # Apply processes
        for process in dataset.get('processes', []):
            #for process_name, process_config in dataset.get('processes', {}).items():
            process_name, process_config = process['name'], process['config']
            process = swarmpal.toolboxes.make_toolbox(process_name, config=process_config)
            data = process(data)

        # Save the results as a NetCDF file
        filename = f'{name}.nc4'
        filepath = args.data_dir / filename

        data.to_netcdf(filepath)
        registry[filename] = calc_md5sum(filepath)

    with open(args.registry, 'w') as f:
        for filename, md5sum in registry.items():
            f.write(f'{filename} md5:{md5sum}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='generate_data.py',
        description='Downloads test data using swarmpal',
    )
    parser.add_argument('-d', '--data-dir', default='data', type=Path, 
        help='Directory where files will be saved to.'
    )
    parser.add_argument('-r', '--registry', default='registry.txt',
        help='Filename for the pooch registry file'
    )
    parser.add_argument('data_params', 
        help='A filename for YAML formatted descriptions of each data set to generate.'
    )
    args = parser.parse_args()

    main(args)
