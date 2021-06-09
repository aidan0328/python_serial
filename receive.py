import sys
import threading
import time

from Serial import Serial

PORT_NAME = '/dev/ttyUSB0'
BAUDRATE = 115200
READ_TIMEOUT = 0.1


def chcek_packet(packet):
    return packet == b'1234567890'


def rx_callback(packet, check_result=None):
    ser.write_bytes(packet)
    if check_result == False:
        print(f'Error packet size : {len(packet)}, {packet}')

    ser.packet = bytearray()
    ser.packet_size = 0


if __name__ == '__main__':
    ser = Serial.Serial(port=PORT_NAME,
                        baudrate=BAUDRATE,
                        rx_threadhold=0,
                        rx_timeout_callback=rx_callback,
                        check_packet_callback=chcek_packet,
                        read_timeout=READ_TIMEOUT)
    ser.open()
    ser.start()

    # print(f"Arguments count: {len(sys.argv)}")
    # for i, arg in enumerate(sys.argv):
    #     print(f"Argument {i:>6}: {arg}")
