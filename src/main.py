import os, sys

from PyQt5.QtGui import QFont

from script import get_answer

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

import os
import subprocess, re

from ansi2html import Ansi2HTMLConverter

from PyQt5.QtCore import QThread, Qt, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QVBoxLayout, QWidget, QTextBrowser, QGroupBox, \
    QComboBox, QSpinBox, QLineEdit, QFormLayout, QMessageBox

from chatWidget import Prompt, ChatBrowser
from findPathWidget import FindPathWidget

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support

QApplication.setFont(QFont('Arial', 12))


class ReadyModelThread(QThread):
    updated = pyqtSignal(str)

    def __init__(self, **common_args):
        super(ReadyModelThread, self).__init__()
        self.__common_args = common_args

    def run(self):
        try:
            conv = Ansi2HTMLConverter()

            model = self.__common_args['model']
            num_shard = self.__common_args['num_shard']
            volume = self.__common_args['volume']
            token = self.__common_args['token']
            port = 8080

            # remove already allocated port
            # container_name = 'pensive_wright'

            # command = docker container ls
            # result = command.result
            # command = docker rm -f container_id

            token = token if token else None
            command = f'docker run --gpus all --shm-size 1g -e HUGGING_FACE_HUB_TOKEN={token} -p {port}:80 -v {volume}:/data ghcr.io/huggingface/text-generation-inference:latest --model-id {model} --num-shard {num_shard}'

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                errors='replace'
            )

            while True:
                realtime_output = process.stdout.readline()
                # print(realtime_output)
                if realtime_output == '' and process.poll() is not None:
                    print('Thread end for a variant of reasons')
                    break
                if realtime_output:
                    if realtime_output.find('Starting Webserver') != -1:
                        print('Starting Webserver')
                    elif realtime_output.find('port is already allocated') != -1:
                        print(f'Port {port} is already allocated.')
                    self.updated.emit(conv.convert(realtime_output.strip()))
        except Exception as e:
            print('Error')
            raise Exception(e)


class ConversationThread(QThread):
    replyGenerated = pyqtSignal(str, bool)

    def __init__(self, client, question):
        super(ConversationThread, self).__init__()
        self.__client = client
        self.__question = question

    def run(self):
        try:
            answer = get_answer(self.__client, self.__question).strip()
            self.replyGenerated.emit(answer, False)
        except Exception as e:
            raise Exception(e)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__client = None

    def __initUi(self):
        self.setWindowTitle('Text Generation Inference GUI')
        self.__readyModelBtn = QPushButton('Ready')
        self.__readyModelBtn.clicked.connect(self.__run)
        self.__optionGrpBox = QGroupBox()
        # model = 'bigscience/bloom-560m'
        models = ['tiiuae/falcon-7b-instruct']

        num_shard = 1
        volume = f'{os.getcwd()}\data'
        token = None

        self.__modelCmbBox = QComboBox()
        self.__modelCmbBox.addItems(models)

        self.__numShardSpinBox = QSpinBox()
        self.__numShardSpinBox.setRange(1, 4)
        self.__numShardSpinBox.setValue(num_shard)

        self.__volumeFindPathWidget = FindPathWidget()
        self.__volumeFindPathWidget.setAsDirectory(True)
        self.__volumeFindPathWidget.getLineEdit().setText(volume)

        self.__tokenLineEdit = QLineEdit()
        self.__tokenLineEdit.setText(token)
        self.__tokenLineEdit.setEchoMode(QLineEdit.Password)

        lay = QFormLayout()
        lay.addRow('Model', self.__modelCmbBox)
        lay.addRow('Number of Shards', self.__numShardSpinBox)
        lay.addRow('Path to Save Model', self.__volumeFindPathWidget)
        lay.addRow('Token', self.__tokenLineEdit)

        self.__optionGrpBox.setLayout(lay)

        self.__optionGrpBox.setTitle('Option')

        self.__readyModelBrowser = QTextBrowser()
        self.__readyModelBrowser.setStyleSheet('QTextBrowser { background-color: #333; }')
        self.__readyModelBrowser.setVisible(False)

        self.__browser = ChatBrowser()
        prompt = Prompt()

        self.__lineEdit = prompt.getTextEdit()
        self.__lineEdit.returnPressed.connect(self.__generateResponse)
        self.__lineEdit.setPlaceholderText('Write some text...')

        lay = QVBoxLayout()
        lay.addWidget(self.__optionGrpBox)
        lay.addWidget(self.__readyModelBtn)
        lay.addWidget(self.__readyModelBrowser)
        lay.addWidget(self.__browser)
        lay.addWidget(prompt)
        lay.setAlignment(Qt.AlignTop)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

        self.resize(640, 800)

    def __run(self):
        common_args = {
            'model': self.__modelCmbBox.currentText(),
            'num_shard': self.__numShardSpinBox.value(),
            'volume': self.__volumeFindPathWidget.getLineEdit().text(),
            'token': self.__tokenLineEdit.text(),
        }
        self.__t = ReadyModelThread(**common_args)
        self.__t.started.connect(self.__started)
        self.__t.updated.connect(self.__updated)
        self.__t.finished.connect(self.__finished)
        self.__t.start()

    def __started(self):
        self.__readyModelBrowser.setVisible(True)
        self.__readyModelBtn.setEnabled(False)

    def __updated(self, text):
        self.__readyModelBrowser.append(text)

    def __finished(self):
        self.__readyModelBtn.setEnabled(True)

        # run the server
        from text_generation import Client

        self.__client = Client("http://127.0.0.1:8080", timeout=30)

    def __generateResponse(self):
        if self.__client:
            self.__lineEdit.setEnabled(False)
            question = self.__lineEdit.toPlainText().strip()
            self.__browser.showText(question, True)
            self.__t = ConversationThread(client=self.__client, question=question)
            self.__t.replyGenerated.connect(self.__browser.showText)
            self.__lineEdit.clear()
            self.__t.start()
            self.__t.finished.connect(self.__afterGenerated)
        else:
            QMessageBox.critical(self, 'Error', 'Server is not running.')

    def __afterGenerated(self):
        self.__lineEdit.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())