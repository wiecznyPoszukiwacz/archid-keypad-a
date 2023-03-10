import time
import picokeypad as keypad
import network
import socket 
import errno


#---------------------------------------------------------- config read
with open('config.txt', 'r') as f:
    deviceId = f.readline().strip()
    ssid = f.readline().strip()
    password = f.readline().strip()

#---------------------------------------------------------- keypad

last_button_states = 0

keypad.init()
keypad.set_brightness(0.5)
keypad.clear()

keypad.illuminate(0, 0x1a, 0x97, 0xde)

keypad.update()

#---------------------------------------------------------- wifi connection
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)
while not wifi.isconnected():
    pass

ip = wifi.ifconfig()[0]

keypad.illuminate(1, 0x1a, 0x97, 0xde)
keypad.update()


#---------------------------------------------------------- creating server
server = socket.socket()
server.bind(('0.0.0.0', 12001))
server.listen(1)
server.setblocking(False)


#---------------------------------------------------------- broadcast

def broadcast():

    msg = 'archi-keypad-a,' + deviceId

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, 0x20, 1)
    sock.bind((ip,0))
    sock.sendto(msg.encode(), ("255.255.255.255", 12000))
    sock.close()

broadcast()


#---------------------------------------------------------- main loop helpers

def initKeypad():
    keypad.clear()
    keypad.update()


#---------------------------------------------------------- main loop


while True:
    try:
        client = server.accept()[0]
        initKeypad()

        while True:

            button_states = keypad.get_button_states()
            if last_button_states != button_states:
                client.send(str(button_states).encode('utf-8'))
                client.send(b',')
                last_button_states = button_states
                if button_states == 4105:
                    broadcast()

            try:
                data = client.recv(15).decode('utf-8')

                if data == '':
                    break

                else:

                    [op, r, g, b] = data.split('.')
                    iop = int(op)
                    ir = int(r)
                    ig = int(g)
                    ib = int(b)
                    keypad.illuminate(iop, ir, ig, ib)
                    keypad.update()

            except OSError as e:
                err = e.args[0]

                if err == errno.EAGAIN:
                    pass

                elif err == errno.EBADF:
                    raise

                elif err == errno.ECONNRESET:
                    raise

                else:
                    print(e)

    except OSError as e:
        err = e.args[0]

        # ignoruj
        if err == errno.EAGAIN:
            time.sleep(0.1)

        elif err == errno.ECONNRESET:
            time.sleep(0.1)

        else:
            print('error in outer loop')
            print(e)

