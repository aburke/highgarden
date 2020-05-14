"""
Generate a catalog.json file for a singer_io module's tap class
"""
import os
import importlib
import subprocess
import json
import logging

from typing import List, Tuple
from argparse import ArgumentParser
from singer_io.singer_device import SProp
from utils.venv_tool import pipeline_home


def create_catalog_template(s_module: str, s_class: str) -> Tuple[dict, str]:
    ''' Create the tap catalog for the module/class pair '''
    singer_folder = 'singer_io'
    catalog_path = os.path.join(
        pipeline_home,
        singer_folder,
        'templates',
        s_module,
        '{}_{}_catalog.json'.format(s_module, s_class.lower())
    )

    module = importlib.import_module('.'.join([singer_folder, s_module]))
    Tap = getattr(module, s_class)
    tap = Tap()
    config_path = tap.create_sprop_file(SProp.config, '/tmp')
    command = ' '.join([
        tap.cmd_path,
        '--config',
        config_path,
        '--discover',
        '>',
        catalog_path
    ])

    subprocess.run(command, check=True, shell=True)
    os.remove(config_path)

    with open(catalog_path) as catalog:
        catalog_dict = json.load(catalog)

    logging.info('Catalog template created for {}.'.format(s_module))
    return catalog_dict, catalog_path


def mark_for_inclusion(catalog_dict: dict, catalog_path: str) -> None:
    ''' Updates the catalog template setting inclusion and selected to true '''
    meta = catalog_dict['streams'][0]['metadata'][0]['metadata']
    meta['inclusion'] = 'available'
    meta['selected'] = 'true'

    with open(catalog_path, 'w') as catalog:
        json.dump(catalog_dict, catalog, indent=2)

    logging.info('Updated inclusion and selected in catalog meta data.')


def remove_sdc_extra(catalog_dict: dict, catalog_path: str) -> None:
    ''' Excludes the _sdc_extra property from the catalog if one exists '''
    for i, m in enumerate(catalog_dict['streams'][0]['metadata']):
        if '_sdc_extra' in m['breadcrumb']:
            del catalog_dict['streams'][0]['metadata'][i]

    props = catalog_dict['streams'][0]['schema']['properties']
    if '_sdc_extra' in props:
        del props['_sdc_extra']

    with open(catalog_path, 'w') as catalog:
        json.dump(catalog_dict, catalog, indent=2)

    logging.info('Remove _sdc_extra field.')


def parse(args: List[str]) -> None:
    ''' Parse args to generate a catalog.json
    file for a singer_io module's tap class '''
    parser = ArgumentParser(
        prog="discover",
        description="Create a catalog file for a singer_io module's tap class"
    )

    parser.add_argument(
        's_module',
        help="The module used to generate the corresponding catalog.json",
    )

    parser.add_argument(
        's_class',
        help="Tap class for which the catalog is derived",
        nargs='?',
        default='Tap'
    )

    parser.add_argument(
        '-i', '--include',
        help="Sets inclusion and selected to true in catalog metadata",
        action='store_true'
    )

    parser.add_argument(
        '-r', '--remsdc',
        help="Excludes the _sdc_extra property from the catalog if one exists",
        action='store_true'
    )

    command_args = parser.parse_args(args)

    catalog_dict, catalog_path = create_catalog_template(
        command_args.s_module,
        command_args.s_class
    )

    if command_args.include:
        mark_for_inclusion(catalog_dict, catalog_path)

    if command_args.remsdc:
        remove_sdc_extra(catalog_dict, catalog_path)
