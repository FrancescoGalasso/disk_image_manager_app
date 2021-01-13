# coding: utf-8

'''
This module manages the writing and reading of disk images.
The module requires the debian pkgs "dd" and "pv" installed.

'''

import subprocess
import logging
import queue
import os
import time
import signal

def write_image_(source, destination, size='15G'):
    # https://stackoverflow.com/a/39292586

    output_q = queue.Queue()
    in_file_size = os.path.getsize(source)
    # cmd = [
    #     'sudo',
    #     'pv',
    #     '-f',
    #     '-s',
    #     size,
    #     source,
    #     '|',
    #     'dd',
    #     f'of={destination}',
    #     'bs=1M'
    # ]

    cmd = [
        'sudo',
        'dd', 
        'if=' + source,
        'of=' + destination,
        'bs=1M'
    ]

    import sys
    import time
    import signal
    from subprocess import Popen, PIPE

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT,
                     universal_newlines=True)
    for line in iter(p.stdout.readline, ""):
        sys.stdout.write(line.rstrip('\n'))
        sys.stdout.flush()

    # kw_args = {
    #     'stdout': subprocess.PIPE,
    #     'stderr': subprocess.PIPE,
    #     'shell': False,
    # }
    # dd_process = subprocess.Popen(cmd, **kw_args)
    # logging.warning('dd_process: {}'.format(dd_process))
    # while dd_process.poll() is None:
    #         logging.warning('inside while ...')
    #         dd_iso_image_readoutput(dd_process, in_file_size, output_q)
    # logging.warning('outside while ...')


    #        initial 
    # p0 = subprocess.Popen(cmd,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE,
    #                 universal_newlines=True)
    #                 # shell=False)
    # for line in iter(p0.stdout.readline, ""):
    #     print(f'line: {line.decode()}')


    # p = subprocess.Popen(args) # Success!


    # for line in subprocess.run(cmd, stdout=subprocess.PIPE).stdout.split('\n'):
    #     print(f'line: {line}')
    # subprocess.run(cmd, stdout=subprocess.PIPE)

    return cmd


def write_dd(source, destination, other_destinations=[], write_process=None):
    '''
    Does the actual writing, this can be called from either the command
    line or the GUI
    '''

    # TODO: refactor to have only 1 destination argument

    status = 0
    # cmd_ = [
    #     'sudo',
    #     'dd', 
    #     'bs=1M',
    #     'status=progress',
    #     'oflag=sync',
    #     f'if={source}',
    #     '| pee',
    #     f'"dd of={destination}"',
    #     # f'of={destination}'
    # ]

    # TODO: check dcfldd implementation
    cmd_ = [
        'sudo',
        'dcfldd',
        # 'bs=1048576',
        # 'bs=1M',
        'bs=131072',
        f'if={source}',
        f'of={destination}'
    ]

    if other_destinations:
        for other_dest in other_destinations:
            cmd_.append(f'of={other_dest}')
            # cmd_.append(f'"dd of={other_dest}"')
    cmd_.append('sizeprobe=if')
    cmd = ' '.join([str(elem) for elem in cmd_])
    logging.warning(f'cmd: {cmd}')

    # If we have a QProcess to write with (passed in from the GUI)
    if write_process:
        logging.warning(f'cmd: {cmd}')
        status = write_process.start(cmd)
        logging.warning(f'status: {status}')
    else:
        logging.warning('... no write_process ...')
        status = subprocess.check_output(cmd, shell=True).decode("utf-8")

    return write_process if write_process else None

# TODO: check if keep this wrapper
# def write_image(source, destination, write_process = None):
#     write_dd(source, destination, write_process = None)

# TODO: check if keep this wrapper
# def read_image(source, destination, write_process = None):
#     write_dd(source, destination, write_process = None)

if __name__ == "__main__":
    path_sample_file = '/media/dati_condivisi/alfaberry/2020-02-02-raspbian-buster-lite-alfa.img'
    size_sample_file = os.path.getsize(path_sample_file)
    size_kb = int(size_sample_file/(1024*1024))
    _destination = '/media/dati_condivisi/alfaberry/test.img'
    # write_image(source, destination, size='15G')
    # write_image(path_sample_file, _destination)
    write_dd(source=path_sample_file, destination=_destination)