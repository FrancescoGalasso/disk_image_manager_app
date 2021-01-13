# coding: utf-8

import sys
import os
import logging
import time
import json
from subprocess import call
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QProcess, Qt

from dima.dima_backend.image_manager import write_dd

HERE = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(HERE, 'gui.ui')
CONFIG_FILE = os.path.join(os.path.dirname(HERE), 'dima.conf')

# TODO: improve imports for PyQt5

class ModalMessageBox(QtWidgets.QMessageBox):
    # def __init__(self):
    #     super(ModalMessageBox, self).__init__()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        # self.resize(800, 400)
        self.setWindowModality(1)

        self.setStyleSheet(
            """
                QMessageBox {
                    font-size: 20px;
                    font-family: monospace;
                    border: 2px solid #999999;
                    border-radius: 4px;
                    background-color: #FEFEFE;
                }
            """
        )

        self.setWindowFlags(
            self.windowFlags()
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.X11BypassWindowManagerHint
        )
        # logging.warning('*args: {}'.format(*args))
        # logging.warning('**kwargs: {}'.format(**kwargs))

class DimaGui(QtWidgets.QMainWindow):
    def __init__(self):
        super(DimaGui, self).__init__()
        uic.loadUi(UI_PATH, self)

        self.copy_process = None
        self.source_path = []
        self.destination_path = None
        self.source_file_size = None
        self.dict_sources = {}

        # self.write_btn.setDisabled(False)
        # self.cancel_btn.setEnabled(False)
        self.write_btn.clicked.connect(lambda: self.start_process(mode='w'))
        self.cancel_btn.clicked.connect(self.cancel_process)
        self.iso_list_widget.itemSelectionChanged.connect(self.iso_list_widget_selection_changed)

        self.__idle_setup_bottons()
        self.populate_iso_list()
        self.show()

        # TODO: create config attribute??

    def show_alert_dialog(self, msg, title="ALERT"):
        logging.warning('calling show_alert_dialog')

        def button_clicked():
            self.__restore_ui(error=True)

        _msgbox = ModalMessageBox(parent=self)

        _msgbox.setIcon(QtWidgets.QMessageBox.Critical)
        _msgbox.setText(msg)
        _msgbox.setWindowTitle(title)

        _msgbox.buttonClicked.connect(button_clicked)

        _msgbox.exec()

        # WORKING
        # QtWidgets.QMessageBox.critical(self, 'Błąd', 'Błędne hasło!', QtWidgets.QMessageBox.Ok)

    def show_success_dialog(self, msg, title="SUCCESS"):
        logging.warning('calling show_success_dialog')

        def button_clicked():
            self.__restore_ui(error=False)

        _msgbox = ModalMessageBox(parent=self)

        _msgbox.setIcon(QtWidgets.QMessageBox.Information)
        _msgbox.setText(msg)
        _msgbox.setWindowTitle(title)

        _msgbox.buttonClicked.connect(button_clicked)

        _msgbox.exec()

    def cancel_process(self):

        if self.copy_process:
            self.message_label.setText('Process cancelled.')
            kill_dd_cmd = "kill $(ps aux | grep 'dcfldd' | awk '/S+/ {print $2}')"
            logging.warning(f'kill_dd_cmd: {kill_dd_cmd}')
            call(kill_dd_cmd, shell=True)
            self.copy_process.readyReadStandardError.disconnect(self.handle_stderr)
            self.copy_process.finished.disconnect(self.process_finished)

            logging.warning('killing current QProcess ..')
            self.copy_process.kill()
            self.copy_process = None
            # self.cancel_btn.setEnabled(False)
            # self.write_btn.setDisabled(False)

            self.__restore_ui()
            # TODO: self.destination_path to list; parse elem and delete them
            if '/dev/sd' not in self.destination_path and os.path.exists(self.destination_path):
                time.sleep(1)
                os.remove(self.destination_path)
                logging.warning(f'removed {self.destination_path}')

    def start_process(self, mode):
        logging.debug(f'self.copy_process: {self.copy_process}')
        if self.copy_process is None:  # No process running.
            logging.warning('Executing process')

            # self.cancel_btn.setDisabled(False)
            # self.write_btn.setEnabled(False)
            self.message_label.setText('Executing process')
            self.progress_bar.setValue(0)
            self.__running_setup_bottons()

            self.copy_process = QProcess()
            self.copy_process.readyReadStandardError.connect(self.handle_stderr)
            self.copy_process.finished.connect(self.process_finished)

            error_flag = False

            # _source = '/media/dati_condivisi/alfaberry/2020-11-25-raspbian-buster-lite-alfa.img'
            _destination = '/media/dati_condivisi/alfaberry/test.img'
            _destination_2 = '/media/dati_condivisi/alfaberry/test2.img'

            if mode == 'w':
                logging.warning(f'mode: {mode}')
                logging.warning(f'self.source_path({len(self.source_path)}): {self.source_path}')
                if len(self.source_path) > 1:
                    error_flag = True
                    mode_w_err_msg = '  ERROR ON START WRITE PROCESS  \n\n  PLEASE SELECT ONLY 1 ISO  \n'
                    self.show_alert_dialog(mode_w_err_msg)
                elif not self.source_path:
                    error_flag = True
                    mode_w_err_msg = '  ERROR ON START WRITE PROCESS  \n\n  PLEASE SELECT AN ISO  \n'
                    self.show_alert_dialog(mode_w_err_msg)

            if not error_flag: 
                _source = self.source_path[0]
                self.source_file_size = os.path.getsize(_source)
                logging.warning(f'self.source_file_size: {self.source_file_size}')
                self.destination_path = _destination
                write_dd(source=_source,
                         destination=_destination,
                         other_destinations=[_destination_2],
                         write_process=self.copy_process)
                # write_dd(_source, _destination, write_process=self.copy_process)

    def update_progress(self, stderr_data_decoded):
        data_list = stderr_data_decoded.split() 

        if data_list:
            raw_data = data_list[0]
            current_progress = raw_data[1:-1]
            try:
                curr_progress = int(current_progress)
                self.progress_bar.setValue(curr_progress)
            except ValueError:
                # dcfldd finished but return a no int castable value
                # e.g. -> 22037+1 records in
                pass          

    def handle_stderr(self):
        stderr_data = self.copy_process.readAllStandardError()
        stderr_data_decoded = bytes(stderr_data).decode("utf8")
        logging.debug(f'stderr: {stderr_data_decoded}')
        self.plain_txt.setPlainText(stderr_data_decoded.rstrip('\n'))
        self.update_progress(stderr_data_decoded)

    def process_finished(self):

        logging.warning('Process finished.')
        self.message_label.setText('Process finished.')
        self.copy_process = None
        self.progress_bar.setValue(100)
        self.cancel_btn.setEnabled(False)
        self.write_btn.setDisabled(False)

        mode_success_msg = '  PROCESS COMPLETED SUCCESSFULLY \n'
        self.show_success_dialog(mode_success_msg)

    def populate_iso_list(self):

        logging.warning(f'CONFIG_FILE: {CONFIG_FILE}')
        iso_path = None
        with open(CONFIG_FILE, 'r') as conf_file:
            json_conf = json.loads(conf_file.read())

        if 'iso_path' in json_conf.keys():
            iso_path = json_conf.get('iso_path')

        if iso_path is not None and os.path.exists(iso_path):
            for root, directories, files in os.walk(iso_path):
                for name in files:
                    # print(name)
                    if '.img' in name:
                        self.iso_list_widget.addItem(str(name))
                        
                        __path = os.path.join(root, name)
                        __key = str(name)
                        self.dict_sources[__key] = __path

        logging.debug(f'self.dict_sources: {self.dict_sources}')

    def iso_list_widget_selection_changed(self):
        selected_objs = self.iso_list_widget.selectedItems()
        self.source_path = []

        if len(selected_objs) > 0:
            obj_names = []

            for obj in selected_objs:
                obj_names.append(obj.text())
                # https://doc.qt.io/archives/qt-4.8/qlistwidgetitem.html#setData
                # https://doc.qt.io/archives/qt-4.8/qt.html#ItemDataRole-enum
                obj_name = obj.text()
                obj_path = self.dict_sources[obj_name]
                obj.setData(3, obj_path)

                self.source_path.append(obj_path)

            logging.warning(f'Selected item(s): {obj_names}')

        logging.warning(f'\tself.source_path: {self.source_path}')

    def iso_list_widget_update(self):
        logging.warning('... calling iso_list_widget_update')
        self.iso_list_widget.clear()
        for elm in self.dict_sources.keys():
            self.iso_list_widget.addItem(str(elm))

    # TODO: refactor (and renaming) for include also the status bar?
    def __idle_setup_bottons(self):
        self.write_btn.setDisabled(False)
        self.copy_btn.setDisabled(False)
        self.refresh_btn.setDisabled(False)
        self.cancel_btn.setEnabled(False)

    def __running_setup_bottons(self):
        self.write_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.cancel_btn.setDisabled(False)

    def __restore_ui(self, error=False):
        logging.warning(f'error: {error}')
        # self.cancel_btn.setEnabled(False)
        # self.write_btn.setDisabled(False)
        self.__idle_setup_bottons()
        self.iso_list_widget.clearSelection()

        self.iso_list_widget_update()

        if error:
            self.message_label.setText('')

        # safety
        self.copy_process = None

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DimaGui()
    app.exec_()
