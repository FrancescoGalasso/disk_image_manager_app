# coding: utf-8

import pytest
import os
from context import image_manager


def _create_sample_file():
    size_kb = 1024 * 1024 * 128         # 128 MB
    path_sample_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_file.txt'))
    print(path_sample_file)
    with open(path_sample_file, 'wb') as sample_file:
        sample_file.write(os.urandom(size_kb))

    source_file_size_kb = os.path.getsize(path_sample_file)/1024

    return path_sample_file, source_file_size_kb

def test_write_dd_single_destination():

    source_file_path, source_file_size_kb = _create_sample_file()
    destination_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_file_copy.txt'))
    result = image_manager.write_dd(source_file_path, destination_file_path)
    result = image_manager.write_dd(source=source_file_path,
                                    destination=destination_file_path,)

    destination_file_size_kb = os.path.getsize(destination_file_path)/1024

    assert result == None

    assert source_file_size_kb == destination_file_size_kb

    if os.path.exists(source_file_path):
        os.remove(source_file_path)
    if os.path.exists(destination_file_path):
        os.remove(destination_file_path)

def test_write_dd_multiple_destination():

    source_file_path, source_file_size_kb = _create_sample_file()
    destination_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_file_copy.txt'))
    destination_file_path_2 = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_file_copy_2.txt'))
    result_single_destination = image_manager.write_dd(source_file_path, destination_file_path, [destination_file_path_2])
    result = image_manager.write_dd(source=source_file_path,
                                    destination=destination_file_path,
                                    other_destinations=[destination_file_path_2],)

    destination_file_size_kb = os.path.getsize(destination_file_path)/1024
    destination_file_size_kb_2 = os.path.getsize(destination_file_path_2)/1024

    assert result_single_destination == None

    assert source_file_size_kb == destination_file_size_kb == destination_file_size_kb_2

    if os.path.exists(source_file_path):
        os.remove(source_file_path)
    if os.path.exists(destination_file_path):
        os.remove(destination_file_path)
    if os.path.exists(destination_file_path_2):
        os.remove(destination_file_path_2)
