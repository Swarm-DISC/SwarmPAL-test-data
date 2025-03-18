import argparse
import yaml
from pathlib import Path
import hashlib

from datetime import timedelta

import swarmpal
from swarmpal.io import create_paldata

def calc_md5sum(filename):
    '''Calculate the md5sum of the content of a file'''
    return hashlib.md5(open(filename, 'rb').read()).hexdigest()

def main(args):

    with open(args.data_params) as f:
        datasets = yaml.safe_load(f)
    
    registry = {}
    for name, dataset in datasets.items():
        print(name)
        print(f"  Downloading from {dataset['data']['provider']}")

        data = swarmpal.get_data(**dataset['data'])
        data = create_paldata(data) # TODO should create_paldata go in get_data?

        # Apply processes
        for process_spec in dataset.get('processes', []):
            print(f"  Applying {process_spec['process_name']}")
            process = swarmpal.make_process(**process_spec)
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
