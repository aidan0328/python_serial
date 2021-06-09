#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import serial
import threading
import time

# 指定 logging 的格式 
FORMAT = '[%(levelname)s] %(message)s \t@M:%(module)s F:%(funcName)s() L:#%(lineno)s'

# logging.basicConfig(level=logging.NOTSET, format=FORMAT)

# 只顯示 logging.error() 與 logging.critical()
logging.basicConfig(level=logging.ERROR, format=FORMAT)

# 只顯示 logging.critical()
# logging.basicConfig(level=logging.CRITICAL, format=FORMAT)


def GetSerialPorts():
    """ 取得所有的 Serial Port

    Returns:
        取得的結果，如果都沒有就返回 None
    """
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return ports
    except Exception as e:
        logging.critical(e)
        return None


def PortIsExixt(port):
    """ 檢查 Port 是否存在

    Args:
        port str: 要檢查的 port

    Returns:
        bool: 如果存在就返回 True，否則 False
    """
    try:
        ports = GetSerialPorts()
        if len(ports) <= 0:
            return False
        else:
            for p in ports:
                logging.info(p.device)
                if port in p.device:
                    return True
        return False
    except Exception as e:
        logging.critical(e)
        return False


# class SerialRxThread(threading.Thread):
    # def __init__(self, ser=None, callback=None):
    #     threading.Thread.__init__(self)
    #     self.__serial = ser
    #     self.__rxTick = time.time()
    #     self.__callback = callback
    #     self.packet = bytearray()
    #     self.packet_size = 0

    # def run(self, callback=None):
    #     print('Start Serial listen')
    #     count = 0
    #     while True:
    #         if self.__serial != None:
    #             if self.__serial.rx_bytes > 0:
    #                 b = self.__serial.read_bytes()
    #                 self.packet_size += len(b)
    #                 self.packet += bytearray(b)
    #                 self.__rxTick = time.time()
    #             else:
    #                 now = time.time()
    #                 if (now - self.__rxTick) >= 0.005\
    #                         and self.packet_size > 0:
    #                     if self.__callback != None:
    #                         self.__callback(self, self.__serial)


class Serial(threading.Thread):
    def __init__(self,
                 port="None",
                 baudrate=115200,
                 rx_threadhold=0,
                 rx_timeout_callback=None,
                 check_packet_callback=None,
                 read_timeout=None,
                 write_timeout=None):
        if PortIsExixt(port) == False:
            return None
        threading.Thread.__init__(self)
        self.__serial = serial.Serial()
        self.__serial.port = port
        self.__serial.baudrate = baudrate

        self.__rx_threadhold = rx_threadhold
        self.__rx_timeout_callback = rx_timeout_callback
        self.__check_packet_callback = check_packet_callback
        self.__serial.timeout = read_timeout
        self.__serial.write_timeout = write_timeout

        self.__rxTick = time.time()
        self.packet = bytearray()
        self.packet_size = 0
        logging.info(self.__serial)

    @property
    def rx_bytes(self):
        return self.__serial.in_waiting

    def run(self, callback=None):
        print('Start Serial listen')
        while True:
            if self.__serial != None:
                result = False
                if self.__serial.in_waiting > 0:
                    b = self.__serial.read()
                    self.packet_size += len(b)
                    self.packet += bytearray(b)
                    self.__rxTick = time.time()
                    if self.__rx_threadhold != 0:
                        if self.packet_size >= self.__rx_threadhold:
                            result = True
                else:
                    now = time.time()
                    if (now - self.__rxTick) >= 0.005\
                            and self.packet_size > 0:
                        if self.__rx_timeout_callback != None:
                            result = True

                # 有收到封包，而封包的大小 >= rx threadhold 或已經發生 timeout， result 就為 True
                if result == True:
                    check = None
                    if self.__check_packet_callback != None:
                        check = self.__check_packet_callback(self.packet)
                    if self.__rx_timeout_callback != None:
                        self.__rx_timeout_callback(self.packet, check)

    def discard_rx_packet(self):
        self.packet = bytearray()
        self.packet_size = 0

    def open(self):
        try:
            if self.__serial != None \
                    and self.__serial.port != None \
                    and self.__serial.is_open == False:
                self.__serial.open()
                return True
            return False
        except Exception as e:
            logging.error(e)
            return False

    def close(self):
        try:
            if self.__serial != None\
                    and self.__serial.port != None\
                    and self.__serial.is_open == True:
                self.__serial.close()
        except Exception as e:
            logging.error(e)

    def write_string(self, str):
        try:
            if self.__serial != None\
                    and self.__serial.port != None\
                    and self.__serial.is_open == True:
                return self.__serial.write(str.encode('utf-8'))
        except Exception as e:
            logging.error(e)
            return -1

    def write_bytes(self, bytes):
        try:
            if self.__serial != None\
                    and self.__serial.port != None\
                    and self.__serial.is_open == True:
                return self.__serial.write(bytes)
        except Exception as e:
            logging.error(e)
            return -1

    def read_bytes(self, size=1):
        try:
            if self.__serial != None\
                    and self.__serial.port != None\
                    and self.__serial.is_open == True:
                return self.__serial.read(size)
        except Exception as e:
            logging.error(e)
            return -1
