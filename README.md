# Server Heartbeat Detector

## Introduction

**Purpose**: detect hosts being down / unavailable.

You need a server and one or more clients. Clients periodically send UDP
packets to the server, identifying themselves. Upon first message seen, server
registers the client, and reports further outages via email.

## Installation

Use the enclosed minipex.sh script to create a binary. It just needs to be run
- e.g. from /etc/rc.local.

Also make sure the server has a working email server.

### Server Mode

...into /etc/rc.local:

  `/bin/su - USER -c "/home/USER/bin/serverheartbeat PORT EMAIL" 2>/dev/null &`
...where:

    *  USER is local username
    *  PORT is UDP port opened
    *  EMAIL is the email address where notifications are sent

### Client Mode

...into /etc/rc.local:

(sleep 120; /bin/su - USER -c "/home/USER/bin/serverheartbeat SERVER_IP PORT CLIENT_ID" 2>/dev/null ) &

...where:

    *  USER is local username
    *  SERVER_IP is server's IP
    *  PORT is UDP port (same as specified on server's command line)
    *  CLIENT_ID is unique text ID of the client (will be used in emails sent)


## Caveats

This script is intentionally very basic, all timeouts, logfile location, etc
hardcoded. Fits the purpose though :)
