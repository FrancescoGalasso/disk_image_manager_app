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


def dcfldd_wrapper(source=None, destinations=[], write_process=None):
    '''
    Does the actual writing, this can be called from either the command
    line or the GUI
    '''

    cmd_ = [
        'sudo',
        'dcfldd',
        'bs=131072',
        f'if={source}',
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
