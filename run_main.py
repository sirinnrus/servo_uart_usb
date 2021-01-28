# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
import PyQt5
import ui_form
import control
import configparser
from pathlib import Path


config = configparser.ConfigParser()
path = Path().absolute() / 'config.cfg'
print(path)
c = config.read(path)
for key, value in config['DEFAULT'].items():
    print(key, value)
PORT = config['DEFAULT']['port']
BR = int(config['DEFAULT']['br'])
TIMEOUT = int(config['DEFAULT']['timeout'])
# P1-04 (1-preg; 04-pval)
preg = int(config['DEFAULT']['REGISTER_P'])
pval = int(config['DEFAULT']['REGISTER_P_VAL'])


class MyWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = ui_form.Ui_Form()
        self.ui.setupUi(self)
        self.ui.spinBox.setValue(preg)
        self.ui.spinBox_2.setValue(pval)
        self.fregisters = [i for i in range(1281, 1305)]
        self.fname = [f'F{i}' for i in range(1, 25)]
        self.fregname = zip(self.fname, self.fregisters)

        self.port = PORT
        self.br = BR
        self.timeout = TIMEOUT

        for item in self.fregname:
            self.ui.comboBox.addItem(
                f'{item[0]} adr={item[1]}')

        with control.Servo(port=PORT, baudrate=BR, timeout=TIMEOUT) as serial:
            if serial is not None:
                if serial.ser.is_open is True:
                    print("Порт работает")
            else:
                print("Порт занят")

        self.ui.pushButton.clicked.connect(
            lambda: control.write_value_to_p(self))
        self.ui.pushButton_2.clicked.connect(
            lambda: control.start_servo(self))
        self.ui.pushButton_3.clicked.connect(
            lambda: control.stop_servo(self))
        self.ui.pushButton_4.clicked.connect(
            lambda: control.read_register_p(self))
        self.ui.pushButton_5.clicked.connect(
            lambda: control.read_register_f(self))
        self.ui.pushButton_6.clicked.connect(self.clear_log)

    def clear_log(self):
        self.ui.plainTextEdit.clear()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
