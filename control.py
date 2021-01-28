import time
import sys
import serial
from serial.threaded import ReaderThread, LineReader
import traceback

import time
import io

import serial.rs485
import keyboard
# запуск двигателя с клавиатуры после нажатия 0
import libscrc



def append_crc(values) -> bytearray:
    """values ->bytearray"""
    crc16b = libscrc.modbus(values).to_bytes(2, byteorder='little')
    values.append(crc16b[0])
    values.append(crc16b[1])
    return values


def write_to_serial(ser, message):
    cmd = append_crc(message)
    ser.write(cmd)
    print('ok')


def read_from_serial(ser):
    print("11!")


def start_servo(self):
    with Servo(port=self.port, baudrate=self.br, timeout=self.timeout) as serial:
        serial.write_msg(
            bytearray([0x01, 0x06, 0x01, 0x04, 0x00, 0x01]))
        response = serial.write_msg(
            bytearray([0x01, 0x03, 0x01, 0x04, 0x00, 0x01]))
        print(response)


def stop_servo(self):
    with Servo(port=self.port, baudrate=self.br, timeout=self.timeout) as serial:
        serial.write_msg(
            bytearray([0x01, 0x06, 0x01, 0x04, 0x00, 0x00]))
        response = serial.write_msg(
            bytearray([0x01, 0x03, 0x01, 0x04, 0x00, 0x01]))
        print(response)


def read_register_p(self):
    self.ui.lineEdit.clear()
    p_number = int(self.ui.spinBox.value())
    p_value = int(self.ui.spinBox_2.value())
    with Servo(port=self.port, baudrate=self.br, timeout=self.timeout) as serial:
        response_raw = serial.write_msg(
            bytearray([0x01, 0x03, p_number, p_value, 0x00, 0x01]))
        response_raw_list = [hex(i) for i in list(response_raw)]
        response = (' ').join(response_raw_list)
        self.ui.lineEdit.setText(response)
        if len(response_raw_list) == 7:
            response_raw_list = bytearray(response_raw)
            print(len(response_raw_list))
            first_byte, second_byte = serial.bytes_to_high_low(
                response_raw_list, 3, 4)
            val = (first_byte << 8) | second_byte

            self.ui.spinBox_4.setValue(val)
        else:
            self.ui.plainTextEdit.insertPlainText(
                f'\nResponse error register P \n{response_raw_list}')
            print(f'\nResponse error register P \n{response_raw_list}')


def read_register_f(self):

    self.ui.lineEdit_2.clear()
    index = self.ui.comboBox.currentIndex()
    val = self.fregisters[index]
    # из полученного значения выделяем ст и мл байт
    high = (val >> 8) & 0xff
    low = val & 0xff
    # формирование команды согласно документации
    cmd = bytearray([0x01, 0x03])
    cmd.append(high)
    cmd.append(low)
    cmd = cmd+bytearray([0x00, 0x01])
    with Servo(port=self.port, baudrate=self.br, timeout=self.timeout) as serial:
        response_raw = serial.write_msg(cmd)
        response_raw_list = bytearray(response_raw)
        response_raw_bytes = [hex(i) for i in list(response_raw)]
        # Исключаем возможные ошибки при передачу
        if len(response_raw_list) == 7:
            print(response_raw_list)
            first_byte, second_byte = serial.bytes_to_high_low(
                response_raw_list, 3, 4)
            val = (first_byte << 8) | second_byte

            self.ui.lineEdit_2.setText((" ").join(
                [hex(i) for i in response_raw_list]))
            self.ui.spinBox_5.setValue(val)
        else:
            self.ui.plainTextEdit.insertPlainText(
                f'\nResponse error register F \n{response_raw_bytes}')
            print(f'\nResponse error register f \n{response_raw_bytes}')


def write_value_to_p(self):
    """Отрицательные значения. 65535-х """
    write_value = self.ui.spinBox_3.value()
    p_number = int(self.ui.spinBox.value())
    p_value = int(self.ui.spinBox_2.value())
    cmd = bytearray([0x01, 0x06, p_number, p_value])
    if write_value < 0xff and write_value >= 0:
        cmd = cmd + bytearray([0x00, write_value])
    else:
        if write_value > 65535:
            print("Use big number")
            return
        b1 = write_value >> 8
        b2 = write_value & 0xFF
        cmd.append(b1)
        cmd.append(b2)
    with Servo(port=self.port, baudrate=self.br, timeout=self.timeout) as serial:
        response_raw = serial.write_msg(cmd)


class Servo:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.is_ok = False

    def __enter__(self):
        try:
            self.ser = serial.rs485.RS485(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            self.is_ok = True
            return self
        except:
            self.is_ok = False

    def __exit__(self, type, value, traceback):
        if self.is_ok:
            self.ser.close()

    def append_crc(self, values) -> bytearray:
        """values ->bytearray"""
        crc16b = libscrc.modbus(values).to_bytes(2, byteorder='little')
        values.append(crc16b[0])
        values.append(crc16b[1])
        return values

    def write_msg(self, msg) -> bytearray:
        cmd = self.append_crc(msg)
        self.ser.write(cmd)
        time.sleep(0.1)
        response = self.ser.readline()
        return response

    def bytes_to_high_low(self, b_arr, b1, b2) -> tuple:
        first_byte = b_arr[b1]
        second_byte = b_arr[b2]
        return (first_byte, second_byte)

    # def read_msg(self, msg) -> bytearray:
    #     response = self.ser.readline()
    #     return response


# start
# values = bytearray([0x01, 0x06, 0x01, 0x04, 0x00, 0x01, 0x08, 0x37])
# stop
# values = bytearray([0x01, 0x06, 0x01, 0x04, 0x00, 0x00, 0xC9, 0xF7])


# serw = serial.Serial('COM4', 38400, serial.EIGHTBITS,
#                      serial.PARITY_NONE, serial.STOPBITS_ONE)
# serr = serial.Serial('COM4', 38400, serial.EIGHTBITS,
#                      serial.PARITY_NONE, serial.STOPBITS_ONE)
# time.sleep(2)


if __name__ == "__main__":

    start = bytearray([0x01, 0x06, 0x01, 0x04, 0x00, 0x01])
    stop = bytearray([0x01, 0x06, 0x01, 0x04, 0x00, 0x00])
    test_response = bytearray([0x01, 0x03, 0x02, 0x00, 0x01])
    wr = bytearray([0x01, 0x03, 0x01, 0x04, 0x00, 0x01])
    cmdstart = append_crc(start)
    cmdstop = append_crc(stop)
    cmd = append_crc(wr)
    ser = serial.rs485.RS485(port='COM4', baudrate=38400, timeout=0)
    #ser = serial.rs485.RS485(port='COM4', baudrate=38400, timeout=1)
    # ser.rs485_mode = serial.rs485.RS485Settings(False,True)
    # ser.write(cmdstart)
    # ser.write(cmdstop)
    count = 0
    while 1:
        if keyboard.is_pressed('0'):
            print("press")
            isWork_without = bytearray([0x01, 0x03, 0x01, 0x04, 0x00, 0x01])
            isWork = append_crc(isWork_without)
            ser.write(isWork)
            time.sleep(0.1)
            response = ser.readline()
            print(response)
            if response == b'\x01\x03\x02\x00\x00\xb8D' or response == b'\x01\x06\x01\x04\x00\x00\xc9\xf7\x01\x03\x02\x00\x00\xb8D':
                ser.write(cmdstart)
                print("start")
                ser.readline()
            elif response == b'\x01\x03\x02\x00\x01y\x84' or response == b'\x01\x06\x01\x04\x00\x01\x087\x01\x03\x02\x00\x01y\x84':
                ser.write(cmdstop)
                print("stop")
                ser.readline()
