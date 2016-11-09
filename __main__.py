#!/usr/bin/env python3

import logging
import os
import sys
import time
import traceback

from controller import Controller

def initLog(log_file, log_level):

    # disable http request info logs:
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    log_format = '%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    try:
        logging.basicConfig(filename=log_file,
                            level=log_level,
                            format=log_format,
                            datefmt=log_datefmt)
    except OSError:  # we prepare for read-only filesystem here, fall back to console:
        print("Logging: fallback to stdout")
        logging.basicConfig(stream=sys.stdout,
                            level=log_level,
                            format=log_format,
                            datefmt=log_datefmt)

def createController():
    server = ''
    port = 0
    client_id = ''
    email = ''
    if len(sys.argv) == 4:
        server = sys.argv[1]
        port = sys.argv[2]
        client_id = sys.argv[3]
    elif len(sys.argv) == 3:
        port = sys.argv[1]
        email = sys.argv[2]
    else:
        print("Usage (client mode):")
        print("    " + sys.argv[0] + " <server> <port> <clientid>")
        print("Usage (server mode):")
        print("    " + sys.argv[0] + " <port> <alert_email_address>")
        sys.exit()

    return Controller(server, port, email, client_id)


if __name__ == '__main__':

    log_file = "/tmp/serverheartbeat.log"
    # -- see logging's source (DEBUG=10, INFO=20, WARNING=30, ERROR=40)
    initLog(log_file, logging.DEBUG)

    logging.info("--------- Init ---------")
    c = createController()

    firstrun = True
    while True :
        try:
            if not firstrun:
                time.sleep(30)
            firstrun = False
            c.run()
        except KeyboardInterrupt:
            logging.info("Exiting after KeyboardInterrupt")
            sys.exit()
        except SystemExit:
            logging.info("Exiting after sys.exit()")
            sys.exit()
        except:
            logging.error(traceback.format_exc())
            print(traceback.format_exc())
            logging.error("Unexpected error, waiting and restarting...")
            print("Unexpected error, waiting and restarting...")
            #logging.error("Unexpected error", sys.exc_info()[0])
            #print("Unexpected error" + sys.exc_info()[0], file = sys.stderr)

