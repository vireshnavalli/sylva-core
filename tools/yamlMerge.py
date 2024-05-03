#!/usr/bin/python3
#
# This script takes multiple YAML files as inputs, merges them
# as Helm would do for values, and outputs the result on stdout as YAML or JSON.

from optparse import OptionParser

from copy import deepcopy
import sys
import yaml
import json


def recursive_dict_combine(base_dict, additional_dict, debug_fn):
    _base_dict = deepcopy(base_dict)
    for key, new_value in additional_dict.items():
        if new_value is None:
            # emulate Helm behavior: if value is set to null in overrides, remove the key/value entirely
            # see https://helm.sh/docs/chart_template_guide/values_files/#deleting-a-default-key
            debug_fn(f"{key} set to null, removing")
            continue

        current_value = _base_dict.get(key)
        debug_fn("key: %s, value: %s (new: %s)" % (key, current_value, new_value))

        if not current_value:
            debug_fn("no value yet, using overriding value")
            _base_dict[key] = new_value
            continue

        # dict combine recursion case
        if isinstance(current_value, dict) and isinstance(new_value, dict):
            _base_dict.update({key: recursive_dict_combine(current_value, new_value, debug_fn)})
            continue

        # baseline case
        debug_fn("new overrides current")
        _base_dict[key] = new_value

    return _base_dict


def do_nothing(*args, **xargs):
    pass


if __name__ == "__main__":

    parser = OptionParser(usage="""

%prog [options] file1 file2 ...

Merge multiple YAML files, emulating Helm behavior when merging values,
and output result in stdout as JSON or YAML
    """)
    parser.add_option("-o", "--output", choices=["yaml", "json"],
                      default="yaml",
                      help='output format')
    parser.add_option("-d", "--debug", action="store_true",
                      default=False,
                      help='debug')

    (options, args) = parser.parse_args()

    input_data = []
    for filename in args:
        with open(filename, 'r') as file:
            input_data.append(yaml.safe_load(file))

    if options.debug:
        debug_fn = print
    else:
        debug_fn = do_nothing

    # merge
    result = input_data.pop(0)
    while input_data:
        result = recursive_dict_combine(result, input_data.pop(0), debug_fn)

    if options.output == "yaml":
        yaml.dump(result, sys.stdout, indent=2)
    else:  # json
        json.dump(result, sys.stdout, indent=2)
