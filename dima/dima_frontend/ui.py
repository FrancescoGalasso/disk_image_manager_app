from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QPlainTextEdit, 
                                QVBoxLayout, QWidget)
from PyQt5.QtCore import QProcess
import sys
import os
import logging

from dima.dima_backend.image_manager import write_dd


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.p = None

        self.btn = QPushButton("Execute")
        self.btn.pressed.connect(self.start_process)
        self.btn_2 = QPushButton("CANCEL")
        self.btn_2.pressed.connect(self.cancel_process)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        l = QVBoxLayout()
        l.addWidget(self.btn)
        l.addWidget(self.btn_2)
        l.addWidget(self.text)

        w = QWidget()
        w.setLayout(l)

        self.setCentralWidget(w)

    def message(self, s):
        self.text.appendPlainText(s)

    def cancel_process(self):

        if self.p:
            
            kill_dd_cmd = "kill $(ps aux | grep 'dd if' | awk '/S+/ && /dd if/ {print $2}')"
            # os.system(kill_dd_cmd)
            from subprocess import call
            logging.warning(f'kill_dd_cmd: {kill_dd_cmd}')
            call(kill_dd_cmd, shell=True)
            self.p.readyReadStandardError.disconnect(self.handle_stderr)

            logging.warning('killing current QProcess ..')
            self.p.kill()
            self.p = None
            


    def start_process(self):
        if self.p is None:  # No process running.
            self.message("Executing process")
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            # self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            # self.p.start("python3", ['dummy_script.py'])

            _source = '/media/dati_condivisi/alfaberry/2020-11-25-raspbian-buster-lite-alfa.img'
            _destination = '/media/dati_condivisi/alfaberry/test.img'

            cmd_ = [
                # 'sudo',
                'dd', 
                f'if={_source}',
                f'of={_destination}',
                'bs=1M',
                'status=progress',
                'oflag=sync'
            ]

            cmd = ' '.join([str(elem) for elem in cmd_]) 
            print(f'cmd: {cmd}')

            self.p.start(cmd)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {   
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.p = None        


app = QApplication(sys.argv)

w = MainWindow()
w.show()

app.exec_()