#!/usr/bin/python3

import sys
import json
import yaml

json.dump(yaml.safe_load(sys.stdin), sys.stdout, indent=2)
