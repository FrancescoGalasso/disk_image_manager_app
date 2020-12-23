import pytest
from context import drivelist


def test_get_drive_list():
    test_path = './drivelist.txt'
    lista = drivelist.get_drive_list(by_cmd_lsblk=False, from_file_path=test_path)

    assert len(lista) != 0
    assert len(lista) == 3

    for el in lista:
        assert isinstance(el, drivelist.Drive) == True

    assert lista[0].device == '/dev/sda'
    assert lista[0].check_writeability()

    assert lista[1].device == '/dev/sdb'
    assert lista[1].check_writeability()

    assert lista[2].device == '/dev/mmcblk0'
    assert lista[2].check_writeability() == False
