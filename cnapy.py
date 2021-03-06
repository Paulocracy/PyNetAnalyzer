#!/usr/bin/env python3
#
# Copyright 2019 PSB & ST
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from cnapy.cellnetanalyzer import CellNetAnalyzer
import configparser
import os
import appdirs
conf_path = os.path.join(appdirs.user_config_dir(
    "cnapy", roaming=True, appauthor=False), "cnapy-config.txt")
configParser = configparser.RawConfigParser()
configParser.read(conf_path)

if (os.path.isfile(os.environ.get('OCTAVE_EXECUTABLE', '')) == False) and configParser.has_option('cnapy-config', 'OCTAVE_EXECUTABLE'):
    oe = configParser.get('cnapy-config', 'OCTAVE_EXECUTABLE')
    if os.path.isfile(oe):
        os.environ['OCTAVE_EXECUTABLE'] = oe

cna = CellNetAnalyzer()
