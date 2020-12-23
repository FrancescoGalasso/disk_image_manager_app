# coding: utf-8

from context import drivelist


if __name__ == "__main__":

    test_path = './drivelist.txt'
    drivelist.get_drive_list(by_cmd_lsblk=False, from_file_path=test_path)

