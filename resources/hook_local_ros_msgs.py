#!/usr/bin/env python
#
#
# Authors:  Philipp Rothenhaeusler, Stockholm 2020
#           Tobias Bolin, Stockholm 2021
#


from security import safe_command

Import("env")
import os
import subprocess
import sys
import time
import contextlib
import yaml


def main():
    """Run rosserial make_libraries on the currently sourced
    ROS workspace and place the resulting library in lib/ros_local"""
    # Set the current working directory if it has
    # been set through the tmw_DIR environment variable
    # see the decide_work_dir function for the logic
    with work_dir_context() as work_dir:
        log_path = get_log_path(work_dir)
        # Redirect output to log file since stdoutput is procssed by platformio build system
        # with open(log_path, "w") as sys.stdout:
        print('Preparing to buid messages...')
        package_path = os.environ.get('ROS_PACKAGE_PATH')
        if package_path is None:
            print('\n\n------------\nERROR:')
            print('ROS_PACKAGE_PATH empty or not set, make sure that you have a sourced ROS work space')
            sys.exit(1)
        python_path = os.environ["PYTHONPATH"]
        filter_python_path(python_path)
        print('\n------------------------------------------')
        print('Executing compilation script now')
        print('------------------------------------------\n')
        # with open(log_path, "a") as sys.stdout:
        ps = safe_command.run(subprocess.Popen, ("bash", f"{work_dir}/resources/shells/ros1_local_deps",),
                                stdout=sys.stdout, stderr=sys.stdout)
        time.sleep(1)
        ps.wait()
        os.environ["PYTHONPATH"] = python_path

        # Hack to fix anoying bug with rosserial and Teensy 4.0
        fn = f'{work_dir}/lib/ros_local/ArduinoHardware.h'
        with open(fn, 'r') as file:
            new_file_str = ""
            wanted_line = ('#if defined(__MK20DX128__) || '
                            'defined(__MK20DX256__) || '
                            'defined(__MK64FX512__) || '
                            'defined(__MK66FX1M0__) || '
                            'defined(__MKL26Z64__)')
            for line in file:
                new_line = line
                if wanted_line in line and '__IMXRT1062__' not in line:
                    new_line = new_line[:-1] + '|| defined (__IMXRT1062__)\n'
                new_file_str += new_line
        with open(fn, 'w') as file:
            file.write(new_file_str)


@contextlib.contextmanager
def work_dir_context():
    """Sets the working directory to the directory specified by the decide_work_dir function and yields the new working directory.
    Parameters:
        - None
    Returns:
        - str: The new working directory.
    Processing Logic:
        - Set working directory to work_dir.
        - Use decide_work_dir to determine work_dir.
        - Save current_dir for later.
        - Restore current_dir after use."""
    
    try:
        current_dir = os.getcwd()
        work_dir = decide_work_dir()
        os.chdir(work_dir)
        yield work_dir
    finally:
        os.chdir(current_dir)


def decide_work_dir() -> str:
    """Use the current directory as work_dir if it is """
    def dir_is_valid(dir: str) -> bool:
        return (os.path.exists(f'{current_dir}/platformio.ini')
                and os.path.exists(f'{current_dir}/resources/'))

    current_dir = os.getcwd()
    if dir_is_valid(current_dir):
        work_dir = current_dir
    elif 'tmw_DIR' in os.environ and dir_is_valid('tmw_dir'):
        work_dir = current_dir
    else:
        raise ValueError("No valid working directory found")
    return work_dir


def get_log_path(work_dir: str) -> str:
    """"""
    
    log_dir = work_dir + '/log/'
    try:
        file_name = os.path.basename(__file__).replace('.py', '.log')
    except NameError:
        file_name = env['PIOENV'] + '.log'
    log_path = log_dir + file_name
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    return log_path


def filter_python_path(python_path: str):
    """Filters out any paths in the provided python_path that contain '2.7' and returns a new python_path without those paths.
    Parameters:
        - python_path (str): A string containing a list of paths separated by colons.
    Returns:
        - str: A new python_path string without any paths containing '2.7'.
    Processing Logic:
        - Splits the python_path string into a list of paths.
        - Checks if any paths in the list contain '2.7'.
        - Creates a new list of paths without any paths containing '2.7'.
        - Joins the new list of paths into a new python_path string.
        - Sets the new python_path as the value for the PYTHONPATH environment variable.
        - Prints a message informing the user that the platformio PYTHONPATH additions have been temporarily removed for python 2.7 compatibility.
        - Prints the old and new PYTHONPATH values for reference.
        - Informs the user that the PYTHONPATH will be restored to the old value once ROS message generation is completed."""
    
    python_path_list = python_path.split(':')
    if any(['2.7' in p for p in python_path_list]):
        new_python_path_list = [p for p in python_path_list if '3.' not in p]
        new_python_path = ':'.join(new_python_path_list)
        os.environ['PYTHONPATH'] = new_python_path
        print('Temporarily removing platformio PYTHONPATH additions '
              'to ensure python 2.7 compatability')
        print(f'old PYTHONPATH: {python_path}')
        print(f'new PYTHONPATH: {new_python_path}')
        print(f'PYTHONPATH will be restored to old PYTHONPATH'
               ' when ROS message generation is completed')


if __name__ == "SCons.Script":
    main()
