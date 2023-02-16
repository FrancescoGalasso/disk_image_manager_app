# coding: utf-8

import sys
import os
import logging
import time
import json
import traceback
from subprocess import call
from datetime import datetime
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import QProcess, Qt

from dima.dima_backend.image_manager import dcfldd_wrapper
from dima.dima_backend.drivelist import (get_drive_list, create_mock_drive)
from dima.dima_backend.exceptions import (MissingSourcePath,
                                          MissingDestinationsPath,
                                          TooManySourcePath,
                                          TooManyDestinationsPath,
                                          EmptyArguments,
                                          InputCancelWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(HERE, 'ui', 'gui.ui')
OPT_PATH = '/opt'
CONFIG_FILE = os.path.join(OPT_PATH, 'dima', 'conf', 'dima.conf')

# TODO: improve imports for PyQt5

class ModalMessageBox(QtWidgets.QMessageBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class InputMessageBox(QtWidgets.QInputDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(
            self.windowFlags()
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.X11BypassWindowManagerHint
        )

        self.setInputMode(QtWidgets.QInputDialog.TextInput)
        self.setWindowTitle('ISO NAME')
        self.setLabelText('Type image name')

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)

        self.setFont(font)    


class DimaGui(QtWidgets.QMainWindow):

    def __init__(self):
        super(DimaGui, self).__init__()
        uic.loadUi(UI_PATH, self)

        self.copy_process = None
        self.copy_process_mode = None
        self.selected_disk_image_lst = []
        self.selected_plugged_dev_lst = []
        self.dict_sources = {}
        self.plugged_devices_lst = []
        self.json_conf = {}

        self.write_btn.clicked.connect(lambda: self.start_process(mode='w'))
        self.read_btn.clicked.connect(lambda: self.start_process(mode='r'))
        self.cancel_btn.clicked.connect(self.cancel_process)
        self.refresh_btn.clicked.connect(lambda: self.refresh_devices())
        self.delete_iso_btn.clicked.connect(lambda: self.delete_selected_iso())

        self.iso_list_widget.itemSelectionChanged.connect(self.iso_list_widget_selection_changed)
        self.device_list_widget.itemSelectionChanged.connect(self.devices_list_widget_selection_changed)

        self.write_btn.installEventFilter(self)
        self.read_btn.installEventFilter(self)

        self.load_config_from_file()
        self.__init_ui()
        self.show()

    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.HoverEnter:
            self.__on_hovered(obj, True)
        elif event.type() == QtCore.QEvent.HoverLeave:
            self.__on_hovered(obj, False)
        return super(DimaGui, self).eventFilter(obj, event)

    def load_config_from_file(self):
        logging.warning(f'CONFIG_FILE path: {CONFIG_FILE}')
        with open(CONFIG_FILE, 'r') as conf_file:
            self.json_conf = json.loads(conf_file.read())
        logging.info('self.json_conf: {}'.format(self.json_conf))

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

    def show_msg_dialog(self, msg, type):

        logging.warning('calling show_msg_dialog')

        _icons = {'success': QtWidgets.QMessageBox.Information,
                  'alert': QtWidgets.QMessageBox.Critical,
                  'question': QtWidgets.QMessageBox.Question}[type]

        _dialog_btns = {'success': QtWidgets.QMessageBox.Ok,
                        'alert': QtWidgets.QMessageBox.Ok,
                        'question': QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No}[type]

        _error = True if type == 'alert' else False

        _msgbox = ModalMessageBox(parent=self)

        _msgbox.setIcon(_icons)
        _msgbox.setText(msg)
        _msgbox.setStandardButtons(_dialog_btns)
        result = _msgbox.exec_()

        if result == QtWidgets.QMessageBox.Yes:
            logging.warning('Delete ISO {}'.format(self.selected_disk_image_lst))
            cmd_ = 'sudo rm {}'.format(self.selected_disk_image_lst[0])
            logging.warning('cmd_ {}'.format(cmd_))
            os.system(cmd_)
            self.__restore_ui(error=_error)
        else:
            logging.warning('refresh UI')
            self.__restore_ui(error=_error)

    def show_input_dialog(self, msg='', title="ISO NAME"):

        iso_name_list = []
        _msgbox = InputMessageBox(parent=self)
        ok = _msgbox.exec_()

        iso_name = _msgbox.textValue() if _msgbox.textValue() != '' else []

        if ok:
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d")
            check_flag = True
            if iso_name:
                complete_iso_name = ''.join([date_time, '-', iso_name, '.iso'])
                _iso_path = self.json_conf.get('iso_path')
                path_complete_iso_name = os.path.join(_iso_path, complete_iso_name)
                iso_name_list.append(path_complete_iso_name)

        elif not ok:
            check_flag = False

        return check_flag, iso_name_list

    def cancel_process(self):

        if self.copy_process:
            self.message_label.setText('Process cancelled.')
            kill_dd_cmd = "sudo kill $(ps aux | grep 'dcfldd' | awk '/S+/ {print $2}')"
            logging.warning(f'kill_dd_cmd: {kill_dd_cmd}')
            call(kill_dd_cmd, shell=True)
            self.copy_process.readyReadStandardError.disconnect(self.handle_stderr)
            self.copy_process.finished.disconnect(self.process_finished)

            logging.warning('killing current QProcess ..')
            self.copy_process.kill()
            self.copy_process = None

            if self.copy_process_mode == 'r':
                time.sleep(.2)
                if os.path.exists(self.read_current_iso_path) and os.path.isfile(self.read_current_iso_path):
                    os.remove(self.read_current_iso_path)
                    logging.warning(f'removed {self.read_current_iso_path}')

            self.__restore_ui()

    def start_process(self, mode):
        # ~ TODO: refactor start_process (unify read and write processes)
        logging.debug(f'self.copy_process: {self.copy_process}')
        if self.copy_process is None:  # No process running.
            logging.warning('Executing process')

            self.message_label.setText('Executing process')
            self.progress_bar.setValue(0)
            self.__running_setup_bottons()

            self.copy_process = QProcess()
            self.copy_process.readyReadStandardError.connect(self.handle_stderr)
            self.copy_process.finished.connect(self.process_finished)

            try:
                # basic list for WRITE
                _source_list = self.selected_disk_image_lst
                _destinations_list = self.selected_plugged_dev_lst
                self.copy_process_mode = mode

                logging.debug(f'mode: {mode}')
                if mode == 'r':

                    # override list for READ 
                    _source_list = self.selected_plugged_dev_lst
                    _destinations_list = []

                    ok_flag, name_iso_lst = self.show_input_dialog()
                    logging.debug(f'ok_flag: {ok_flag}')
                    logging.debug(f'name_iso_lst: {name_iso_lst}')
                    if not ok_flag:
                        raise InputCancelWarning
                    if name_iso_lst:
                        _destinations_list = name_iso_lst
                        self.read_current_iso_path = name_iso_lst[0]

                logging.info(f'_source_list({len(_source_list)}): {_source_list} | type: {type(_source_list)}')
                logging.info(f'_destinations_list({len(_destinations_list)}): {_destinations_list} | type: {type(_destinations_list)}')

                dcfldd_wrapper(source=_source_list,
                               destinations=_destinations_list,
                               write_process=self.copy_process,
                               mode=mode)

            except (MissingSourcePath, MissingDestinationsPath, TooManySourcePath,
                    TooManyDestinationsPath, EmptyArguments) as excp:
                logging.error(traceback.format_exc())
                logging.error(str(excp))
                self.show_alert_dialog(msg=str(excp))

            except InputCancelWarning:
                logging.warning('InputCancelWarning ...')
                self.__restore_ui(True)
                pass

            except Exception:
                logging.error(traceback.format_exc())
            # finally:
            #     logging.warning('do finally something ...')
            #     self.__restore_ui(True)

    def refresh_devices(self):
        try:
            block_devices_list = get_drive_list(by_cmd_lsblk=True)
            logging.warning(f'block_devices_list: {block_devices_list}')
            self.__populate_device_list(block_devices_list)
        except BaseException as excp:
            logging.critical(excp)
    
    def delete_selected_iso(self):
        # self.show_alert_dialog(msg="delete me!")
        self.show_msg_dialog(msg="delete me!", type='question')

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

        if self.copy_process_mode == 'r':
            self.__populate_iso_list()
            # self.iso_list_widget_update()

    def __populate_iso_list(self):
        iso_path = None

        if 'iso_path' in self.json_conf.keys():
            iso_path = self.json_conf.get('iso_path')

        if iso_path is not None and os.path.exists(iso_path):
            for root, directories, files in os.walk(iso_path):
                for name in files:
                    if '.img' or '.iso' in name:
                        # self.iso_list_widget.addItem(str(name))
                        
                        __path = os.path.join(root, name)
                        __key = str(name)
                        self.dict_sources[__key] = __path

            self.iso_list_widget_update()

        logging.info('loaded iso paths into self.dict_sources')
        logging.debug(f'self.dict_sources: {self.dict_sources}')

    def __populate_device_list(self, block_devices_list):
        self.device_list_widget.clear()
        self.plugged_devices_lst = []

        for dev in block_devices_list:
            logging.debug(f'dev: {dev}')
            logging.debug(f'dev type: {type(dev)}')
            logging.debug(f'check_writeability: {dev.check_writeability()}')
            if dev.check_writeability():
                self.device_list_widget.addItem(str(dev.device))
                self.plugged_devices_lst.append(dev)

    # TODO: refactor (unify) widget_selection_changed??
    def devices_list_widget_selection_changed(self):
        selected_objs = self.device_list_widget.selectedItems()
        self.selected_plugged_dev_lst = []

        if len(selected_objs) > 0:

            for obj in selected_objs:
                # https://doc.qt.io/archives/qt-4.8/qlistwidgetitem.html#setData
                # https://doc.qt.io/archives/qt-4.8/qt.html#ItemDataRole-enum
                selected_dev_name = obj.text()
                logging.debug(f'selected_dev_name: {selected_dev_name}')
                _selected_dev = [plugged_dev for plugged_dev in self.plugged_devices_lst if plugged_dev.device == selected_dev_name]
                selected_dev= _selected_dev[0]
                
                obj.setData(3, selected_dev.device_path)
                
                self.selected_plugged_dev_lst.append(selected_dev.device_path)

            # ~ logging.warning(f'Selected item(s): {obj_names}')

        logging.info(f'\tself.destination_path_lst: {self.selected_plugged_dev_lst}')

    def iso_list_widget_selection_changed(self):
        selected_objs = self.iso_list_widget.selectedItems()
        self.selected_disk_image_lst = []

        if len(selected_objs) > 0:

            for obj in selected_objs:
                # ~ obj is a QListWidgetItem
                # https://doc.qt.io/archives/qt-4.8/qlistwidgetitem.html#setData
                # https://doc.qt.io/archives/qt-4.8/qt.html#ItemDataRole-enum
                obj_name = obj.text()
                obj_path = self.dict_sources[obj_name]
                obj.setData(3, obj_path)

                self.selected_disk_image_lst.append(obj_path)

        logging.info(f'\tself.source_path_lst: {self.selected_disk_image_lst}')

        if len(selected_objs) == 1:
            self.delete_iso_btn.setEnabled(True)
        else:
            self.delete_iso_btn.setEnabled(False)

    def iso_list_widget_update(self):
        logging.warning('... calling iso_list_widget_update')
        self.iso_list_widget.clear()
        for elm in self.dict_sources.keys():
            self.iso_list_widget.addItem(str(elm))
    
    # TODO: refactor (and renaming) for include also the status bar?
    def __idle_setup_bottons(self):
        self.write_btn.setDisabled(False)
        self.read_btn.setDisabled(False)
        self.refresh_btn.setDisabled(False)
        self.cancel_btn.setEnabled(False)

    def __running_setup_bottons(self):
        self.write_btn.setEnabled(False)
        self.read_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.cancel_btn.setDisabled(False)

    def __init_ui(self):
        self.setWindowTitle('D.I.M.A.')
        self.__idle_setup_bottons()
        self.__populate_iso_list()

        if self.json_conf.get('debug_device_path_list'):
            logging.warning(f'self.json_conf{type(self.json_conf)}: {self.json_conf}')
            mock_device_list = []
            for debug_dev in self.json_conf.get('debug_device_path_list'):
                mock = create_mock_drive(device_name=debug_dev, device_path=debug_dev)
                mock_device_list.append(mock)

            self.__populate_device_list(mock_device_list)

    def __restore_ui(self, error=False):
        logging.warning(f'error: {error}')

        self.__idle_setup_bottons()
        self.iso_list_widget.clearSelection()
        self.device_list_widget.clearSelection()
        self.__populate_iso_list()
        # self.iso_list_widget_update()

        if error:
            self.message_label.setText('')

        # safety
        self.copy_process = None
        self.selected_plugged_dev_lst = []
        self.selected_disk_image_lst = []

    def __on_hovered(self, obj, show=True):

        if obj == self.write_btn and show:
            self.action_tips_label.setText('WRITE SELECTED ISO INTO SELECTED DEVICE(S)\t\tISO -> DEVICE(S)')
        elif obj == self.read_btn and show:
            self.action_tips_label.setText('READ FROM SELECTED DEVICE AND CREATE ISO\t\tISO <- DEVICE')

        if not show:
            self.action_tips_label.setText('')


def main():
    fmt_ = '[%(asctime)s]%(levelname)s %(funcName)s() %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level='INFO', format=fmt_)

    app = QtWidgets.QApplication(sys.argv)
    window = DimaGui()
    app.exec_()


if __name__ == "__main__":
    main()
