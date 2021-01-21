# coding: utf-8
'''
This module provides a list of devices detected by the OS.
The module is designed to run in *nix environments.

'''

# pylint: disable=logging-fstring-interpolation
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-branches

import logging
import subprocess
import json
from types import SimpleNamespace
from typing import Optional

# reference: https://stackoverflow.com/a/57916747


class Drive(SimpleNamespace):
    ''' Drive Class '''
    device: str
    device_model: Optional[str] = None
    device_sn: Optional[str] = None
    device_path: str
    device_vendor: Optional[str] = None
    device_size: int
    is_read_only: bool
    is_removable: bool
    is_usb: bool

    def check_writeability(self):
        """
        Check Drive writeability

        Returns:
        check (bool): flag for writeability

        """
        check = False

        if self.is_usb and self.is_removable and not self.is_read_only:
            check = True

        return check


def get_drive_list(by_cmd_lsblk=True, from_file_path=None):
    """
    A wrapper for get_list_block_devices() and
    transform_block_device_to_drive() returning a list of Drive objs

    Parameters:
    by_cmd_lsblk (bool): Flag to use the linux cmd lsblk
    from_file_path (str): path for the file generated by lsblk
                          usefull only for tests

    Returns:
    lista_drive (list[Drive]): Returning Drive objs list

    """
    logging.debug(f'by_cmd_lsblk: {by_cmd_lsblk} | from_file_path: {from_file_path}')

    block_devices_list = get_list_block_devices(cmd_lsblk=by_cmd_lsblk, file_path=from_file_path)
    logging.debug(f'block_devices_list: {block_devices_list}')
    lista_drive = transform_block_device_to_drive(block_devices_list)
    logging.warning(f'lista_drive: {lista_drive}')

    return lista_drive


def transform_block_device_to_drive(block_devices_list):
    """
    Convert each "block devices" inside block_devices_list into
    Drive objs, append them into a new list and returning it.

    Parameters:
    block_devices_list (list[str]): list containing block devices.

    Returns:
    drive_list (list[Drive]): Returning Drive objs list.

   """

    drive_list = []

    if block_devices_list:
        for datum in block_devices_list:
            drive_datum = Drive(
                device=datum.get('name'),
                device_model=datum.get('model'),
                device_sn=datum.get('serial'),
                device_path=datum.get('path'),
                device_vendor=datum.get('vendor'),
                device_size=datum.get('size'),
                is_read_only=datum.get('ro'),
                is_removable=datum.get('hotplug'),
                is_usb=True if datum.get('tran') == 'usb' else False,     # pylint: disable=simplifiable-if-expression
            )
            drive_list.append(drive_datum)

            logging.debug(f'drive_datum: {drive_datum}')

    return drive_list


def get_list_block_devices(cmd_lsblk=True, file_path=None):
    """
    Retrieve the list of block devices from the output of lsblk or from file generated by lsblk
    (eg. $ lsblsk > drivelist.txt), filter the list to skip devices loop, ram, sr
    Then return the block devices filtered as list.

    Parameters:
    cmd_lsblk (bool): Flag to use the linux cmd lsblk.
    file_path (str): path for the file generated by lsblk
                     usefull only for tests.

    Returns:
    blockdevices_list_filtered (list[str]): Returning filtered list containing block devices.

    """

    blockdevices_list_filtered = []

    try:

        if cmd_lsblk is False and file_path is not None and file_path:
            with open(file_path) as devices_file:
                data_json = json.load(devices_file)
                if data_json is not None and 'blockdevices' in data_json.keys():
                    blockdevices_list = data_json.get('blockdevices')

                    for elem in blockdevices_list:
                        if not elem.get('name').startswith(("/dev/loop", "/dev/sr", "/dev/ram")):
                            blockdevices_list_filtered.append(elem)

                    logging.debug(f'blockdevices_list_filtered({type(blockdevices_list_filtered)}): {blockdevices_list_filtered}')

        elif cmd_lsblk is True and file_path is None:
            # https://helpmanual.io/help/lsblk/
            command_list = [
                'lsblk',
                '--bytes',
                '--all',
                '--json',
                '--paths',
                '--output-all',
            ]
            os_cmd_reply = subprocess.check_output(command_list, shell=False, stderr=subprocess.STDOUT).decode()
            data_json = json.loads(os_cmd_reply)
            if data_json is not None and 'blockdevices' in data_json.keys():
                blockdevices_list = data_json.get('blockdevices')

                for elem in blockdevices_list:
                    if not elem.get('name').startswith(("/dev/loop", "/dev/sr", "/dev/ram")):
                        blockdevices_list_filtered.append(elem)

                logging.debug(f'blockdevices_list_filtered({type(blockdevices_list_filtered)}): {blockdevices_list_filtered}')

        else:
            logging.critical(f'Inconsistent parameters! cmd_lsblk:{cmd_lsblk} | file_path:{file_path}')

    except IOError:
        err_msg = f'File {file_path} not accessible'
        logging.error(err_msg)

    except subprocess.CalledProcessError as exc:
        err_code = exc.returncode
        err_output = exc.output.decode().rstrip()
        logging.error(f'command_list "{command_list}" FAILED ({err_code}) | reason: {err_output}')

    finally:

        return blockdevices_list_filtered       # pylint: disable=lost-exception


def create_mock_drive(device_name='',   # pylint: disable=too-many-arguments, missing-function-docstring
                      device_path='', device_size=1,
                      is_read_only=False, is_removable=True,
                      is_usb=True):

    drive_datum = Drive(
        device=device_name,
        device_path=device_path,
        device_size=device_size,
        is_read_only=is_read_only,
        is_removable=is_removable,
        is_usb=is_usb,
    )

    return drive_datum


if __name__ == "__main__":
    get_drive_list(by_cmd_lsblk=True)
