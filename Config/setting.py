#/usr/bin/env python
# -*- coding: utf-8 -*-
import os, pathlib, sys
sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))


from Config.yaml_generator import Config


yaml_filepath=parent_path/"config.yml"

Info = Config.from_yaml(yaml_filepath.as_posix())