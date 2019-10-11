import socket
import SocketServer

class StoppableTCPServer(SocketServer.TCPServer):
    def server_bind(self):
        SocketServer.TCPServer.server_bind(self)
        self.socket.settimeout(1)
        self.run = True

    def get_request(self):
        while self.run:
            try:
                sock, addr = self.socket.accept()
                sock.settimeout(None)
                return (sock, addr)
            except socket.timeout:
                pass
        self.socket.close()

    def stop(self):
        self.run = False

    def serve(self):
        while self.run:
            try:
                self.handle_request()
            except KeyboardInterrupt:
                break
            except Exception:
                break



