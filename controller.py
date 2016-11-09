#!/usr/bin/env python3

import asyncio
import logging
import sys
import time

import smtplib
from email.mime.text import MIMEText


class Controller:
    """Serves as factory, container and coordinator of Service classes"""

    class ServerProtocol(asyncio.Protocol):
        def __init__(self, controller):
            self.controller = controller
        
        def connection_made(self, transport):
            pass
        
        def connection_lost(self, exception):
            pass

        def datagram_received(self, data, addr):
            # logging.info('data from {}: {}'.format(addr, data))

            fields = data.decode().split()
            if fields[0] != "hb" or len(fields) < 2:
                logging.error('wrong format, "hb <client_id>" expected')
                return

            client_id = fields[1]
            self.controller.heartbeatReceived(client_id)

    class ClientProtocol(asyncio.Protocol):
        def __init__(self, controller):
            controller.clientProtocol = self
            self.transport = None

        def connection_made(self, transport):
            self.transport = transport
            self.peername = self.transport.get_extra_info('peername')
            logging.info('new connection to {}'.format(self.peername))

        def error_received(self, error):
            logging.error('error received: {}'.format(error))

        def write(self, msgStr):
            if self.transport:
                self.transport.sendto(msgStr.encode())

    ### Controller ###
    def __init__(self, server, port, email, client_id):
        """ server: if None, we're the server process """
        self.server = server
        self.port = port
        self.email = email
        self.client_id = client_id
        self.clientProtocol = None
        self.lastSeenTimes = {}

        if not self.server and not self.email:
            logging.error("We need a valid email address in server mode")
            print("We need a valid email address in server mode")
            sys.exit()

    def sendMail(self, client_id, upOrDown):
        if not self.email:
            return

        msg = MIMEText("Thanks...")
        msg['Subject'] = 'Client {} is {}'.format(client_id, upOrDown)
        msg['From'] = "donotreply@rits.hu"
        msg['To'] = self.email

        # Send the message via our own SMTP server.
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()


    def heartbeatReceived(self, client_id):
        if not client_id in self.lastSeenTimes:
            logging.info("Client {} is up.".format(client_id))
            self.sendMail(client_id, "UP")
        self.lastSeenTimes[client_id] = time.time()

    def checkTimeouts(self):
        now = time.time()
        todelete = set()
        for client_id in self.lastSeenTimes.keys():
            if now - self.lastSeenTimes[client_id] > 4:
                logging.info("Client {} is down.".format(client_id))
                self.sendMail(client_id, "DOWN")
                todelete.add(client_id)

        for client_id in todelete:
            del self.lastSeenTimes[client_id]

        self.eventloop.call_later(1, self.checkTimeouts)

    def sendHeartbeat(self):
        if self.clientProtocol:
            self.clientProtocol.write("hb {}\r\n".format(self.client_id))
        self.eventloop.call_later(3, self.sendHeartbeat)

    def run(self):
        logging.info("Controller startup")
        self.eventloop = asyncio.get_event_loop()

        # eventloop.set_debug(True)

        if self.server:
            logging.info("Starting as client")
            coroutine = self.eventloop.create_datagram_endpoint(lambda: Controller.ClientProtocol(self), remote_addr=(self.server, self.port))
            self.eventloop.call_later(3, self.sendHeartbeat)
        else:
            logging.info("Starting as server")
            coroutine = self.eventloop.create_datagram_endpoint(lambda: Controller.ServerProtocol(self), local_addr=('0.0.0.0', self.port))
            self.eventloop.call_later(4, self.checkTimeouts)

        self.eventloop.run_until_complete(coroutine)  # starts connection in the background


        self.eventloop.run_forever()


