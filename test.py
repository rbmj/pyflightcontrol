#!/usr/bin/env python3

from SelectServer import SelectServer

def handle(srv, f):
    x = f.recv(1000)
    f.send(x)
    srv.closeConnection(f)

server = SelectServer(31337, handle)

while True:
    server.run()
