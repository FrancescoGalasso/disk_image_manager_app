# coding: utf-8

'''
This module manages the writing and reading of disk images.
The module requires the debian pkg "dcfldd".
https://linux.die.net/man/1/dcfldd

'''

import subprocess
import logging
import queue
import os
import time
import signal

from dima.dima_backend.exceptions import (MissingSourcePath,
                                          MissingDestinationsPath,
                                          TooManySourcePath,
                                          TooManyDestinationsPath,
                                          EmptyArguments,
                                          )

def dcfldd_wrapper(source=None, destinations=None, write_process=None, mode='w'):
    '''
    Does the actual writing, this can be called from either the command
    line or the GUI
    '''

    # if mode == 'w':
    #     if len(source) > 1:
    #         raise TooManySourcePath(f'Expected 1 selected source path: passed {len(source)} instead')
    # elif mode == 'r':
    #     if len(destinations) > 1:
    #         raise TooManyDestinationsPath(f'Expected 1 selected destination path: passed {len(destinations)} instead')

    if source and (destinations is None or not destinations):
        raise MissingDestinationsPath(f'Expected existing destinations: passed {destinations} - Missing destinations list')
    if destinations and (source is None or not source):
        raise MissingSourcePath(f'Expected existing path: passed {source} - Missing source path')
    if not source and not destinations:
        raise EmptyArguments('Passed empty arguments (source and destionations)')
    if len(source) > 1:
            raise TooManySourcePath(f'Expected 1 selected source path: passed {len(source)} instead')

    cmd_ = [
        'sudo',
        'dcfldd',
        'bs=131072',
        f'if={source[0]}',
    ]

    if destinations:
        for dest in destinations:
            cmd_.append(f'of={dest}')

    cmd_.append('sizeprobe=if')
    cmd = ' '.join([str(elem) for elem in cmd_])
    logging.warning(f'cmd: {cmd}')

    # If we have a QProcess to write with (passed in from the GUI)
    if write_process:
        write_process.start(cmd)
    else:
        logging.warning('... no write_process ...')
        status = subprocess.check_output(cmd, shell=True).decode("utf-8")
        logging.warning(f'status: {status}')
