#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendor', 'lib', 'python'))

from spiro.app import main

main()
