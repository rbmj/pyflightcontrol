#!/usr/bin/env python3

import socket
import select

class SelectServer(object):
    def __init__(self, port, action):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1',port))
        self.sock.listen(5)
        self.inset = [self.sock]
        self.action = action

    def __del__(self):
        for s in self.inset:
            s.close()

    def run(self):
        ready,_,_ = select.select(self.inset, [], [])
        for s in ready:
            if s == self.sock:
                client,_ = self.sock.accept()
                self.inset.append(client)
            else:
                self.action(self, s.makefile())

    def closeConnection(self, sock):
        self.inset.remove(sock)
        sock.close()

