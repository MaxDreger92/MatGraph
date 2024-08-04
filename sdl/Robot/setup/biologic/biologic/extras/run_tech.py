"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/22
"""

from __future__ import annotations

import sys
import json
import time
import logging
from argparse import ArgumentParser
from typing import TYPE_CHECKING

import biologic
from biologic.technique import TECH_ID, Technique
from biologic.runner import IndexData

if TYPE_CHECKING:
    from typing import Any, Type
    from biologic.channel import Channel
    from biologic.technique import Technique


import biologic.techniques
_techniques = { tech.tech_id : tech for tech in Technique.all_techniques() }


cli = ArgumentParser(
    description=(
        "Run a technique using parameters specified by a JSON input file."
    )
)
cli.add_argument(
    'address',
    help="Address of a Bio-Logic device.",
    metavar="ADDRESS",
)
cli.add_argument(
    '-i', '--input', default=None, dest='input',
    help="Path to input JSON file.",
    metavar="FILE",
)
cli.add_argument(
    '-v', '--verbose', action='count', default=0, dest='verbosity',
    help="Increase verbosity level, can be given multiple times.",
)
cli.add_argument(
    '--load-firmware', action='store_true', dest='force_load',
    help="Force load of channel firmware when connecting.",
)
cli.add_argument(
    '--eclab-path', default=None, dest='eclab_path',
    help="Select the directory containing EC-Lab SDK binaries.",
    metavar="DIR",
)
cli.add_argument(
    '--json', default=None, nargs='?', const='stdout', dest='json',
    help=(
        "Produce output in JSON formatted. If a filename is given, the JSON output will be written "
        "to a file. Otherwise if no argument or the special value 'stdout' is supplied, the JSON "
        "output will be dumped to standard output."
    )
)

def stop_channel(chan: Channel, timeout: float) -> None:
    start_time = time.time()
    while True:
        chan.stop()
        time.sleep(0.2)

        if not chan.is_busy():
            break

        if time.time() - start_time > timeout:
            raise TimeoutError("timeout expired while waiting for channel to stop.")


def main(args: Any = None) -> None:
    if args is None:
        args = cli.parse_args()

    levels = [ logging.WARNING, logging.INFO, logging.DEBUG ]
    level = levels[min(args.verbosity, len(levels)-1)]
    logging.basicConfig(stream=sys.stdout, level=level)

    ## Read data file
    try:
        with open(args.input, 'rt') as file:
            input_data = json.load(file)
    except BaseException as error:
        print(f"Failed to parse input file: {error}")
        sys.exit()

    techniques = []
    for item in input_data['techniques']:
        tech_str = item['tech_id']
        try:
            tech_id = TECH_ID[tech_str]
        except ValueError:
            print(f"Unrecognized TechID: {tech_str}")
            sys.exit()

        tech_type: Type[Technique] = _techniques.get(tech_id)
        if tech_type is None:
            print(f"Unsupported technique: {tech_id.name}")
            sys.exit()

        ## Construct technique and parse/validate parameters
        try:
            params = tech_type.params_type.from_json(item['params'])
        except Exception as err:
            print(f"Failed to parse technique parameters: {err}")
            sys.exit()

        techniques.append(tech_type(params))

    if not len(techniques):
        print("No techniques to run.")
        sys.exit()

    ## Connect to BioLogic
    bl = None
    try:
        bl = biologic.connect(args.address, force_load=args.force_load, eclab_path=args.eclab_path)

        ch_num = input_data['channel']
        try:
            chan = bl.get_channel(ch_num)
        except ValueError:
            print(f"Invalid channel number: {ch_num}")
            sys.exit()

        for idx, tech in enumerate(techniques):
            errors = list(tech.validate(bl.device_info))
            if len(errors) > 0:
                print(f"Technique {idx} ({tech.tech_id.name}) has invalid parameters:")
                for err in errors:
                    print(f"Parameter '{err.param}' failed validation: {err.message}")
                sys.exit()

        if chan.is_busy():
            print("Channel is busy, attempting to stop channel...")
            try:
                stop_channel(chan, 10.0)
            except TimeoutError:
                print("Timeout expired while waiting for channel to stop.")
                sys.exit()

        ## Run the technique
        print(f"Run techniques:")
        for idx, tech in enumerate(techniques):
            print(f"{idx+1}.", tech.tech_id.name, tech.param_values)

        runner = chan.run_techniques(techniques)

        result_data = { tech : [] for tech in techniques }

        try:
            for item in runner:
                if isinstance(item, IndexData):
                    tech = runner.techniques[item.tech_index]
                    result_data[tech].append(item.data)
                    print(item.data)
                    time.sleep(2*tech.get_timebase(bl))
                else:
                    # dump buffered data to stdout
                    t = time.time()

                    elapsed = time.time() - t
                    wait = 1.0 - elapsed
                    if wait > 0:
                        time.sleep(wait)

        finally:
            metadata = runner.get_metadata()
            print(metadata)
            if runner.exception:
                raise runner.exception

        if args.json is not None:
            techniques = []
            for idx, tech in enumerate(runner.techniques):
                techniques.append(dict(
                    tech_id = tech.tech_id.name,
                    tech_index = idx,
                    data = [ data.to_json() for data in result_data[tech] ]
                ))

            json_data = dict(
                metadata = metadata.to_json(),
                techniques = techniques,
            )

            if args.json == 'stdout':
                print(json.dumps(json_data, indent=4))
            else:
                with open(args.json, 'wt') as file:
                    json.dump(json_data, file, indent=2)

    finally:
        if bl is not None:
            bl.close()

if __name__ == '__main__':
    main()
