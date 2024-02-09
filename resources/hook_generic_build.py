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
    """Runs a pre-build hook to add a watermark to the source file.
    Parameters:
        - source (str): Path to the source file.
        - target (str): Path to the target file.
        - env (dict): Environment variables, if applicable.
    Returns:
        - None: The function does not return anything.
    Processing Logic:
        - Runs a bash command to add a watermark.
        - Waits for 1 second.
        - Waits for the process to finish."""
    
    ps = safe_command.run(subprocess.Popen, "bash resources/shells/sml_watermark".split())
    import time
    time.sleep(1)
    ps.wait()


def hook_post_build(source, target, env):
    """"""
    
    pid = subprocess.check_output(['pgrep', 'teensy'])
    kill = subprocess.check_output(('kill', str(pid[:-1].decode('utf-8'))))
    print("-> Successfully terminated teensy-loader. Flash attempt complete. ")


env.AddPreAction("upload", hook_pre_build)
env.AddPostAction("upload", hook_post_build)
