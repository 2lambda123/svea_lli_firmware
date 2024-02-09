#!/usr/bin/env python3

import subprocess
from security import safe_command

Import("env")

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

config = configparser.ConfigParser()
config.read("platformio.ini")


def hook_pre_build(source, target, env):
    ps = safe_command.run(subprocess.Popen, "bash resources/shells/sml_watermark".split())
    import time
    time.sleep(1)
    ps.wait()


def hook_post_build(source, target, env):
    pid = subprocess.check_output(['pgrep', 'teensy'])
    kill = subprocess.check_output(('kill', str(pid[:-1].decode('utf-8'))))
    print("-> Successfully terminated teensy-loader. Flash attempt complete. ")


env.AddPreAction("upload", hook_pre_build)
env.AddPostAction("upload", hook_post_build)
