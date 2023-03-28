import ssl
import socket
import threading

class ProxyServer:
    def __init__(self, proxy_address):
        self.proxy_address = proxy_address
        self.proxy = proxy_address.split(":")[0]
        self.port = int(proxy_address.split(":")[1])

    def handle_client(self, client_socket):
        request = client_socket.recv(1024)
        if request.startswith(b"GET") or request.startswith(b"POST") or request.startswith(b"CONNECT"):
            if request.startswith(b"CONNECT"):
                hostport = request.decode().split()[1]
                host = hostport.split(":")[0]
                port = hostport.split(":")[1]
                dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dest_socket = ssl.create_default_context().wrap_socket(sock=dest_socket, server_hostname=host)
                pp = int(port)
                dest_socket.connect((host, pp))
                client_socket.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                with open("requests.log", "a") as f:
                    f.write("=" * 50 + "\n")
                    try:
                        f.write("Request headers:\n{}\n".format(self.prettify_request(request)))
                    except:
                        pass
                    try:
                        f.write("Request body:\n{}\n".format(body.decode("utf-8")))
                    except:
                        pass                    
                    try:
                        f.write("Response headers:\n{}\n".format(self.prettify_request(headers)))
                    except:
                        pass                        
                    try:
                     f.write("Request body:\n{}\n".format(body.decode("utf-8")))
                    except:
                        pass     
                    try:               
                        f.write("Response body:\n{}\n".format(body.decode("utf-8")))
                    except:
                        pass 
                    f.write("=" * 50 + "\n")
            else:
                dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = request.decode().split("\r\n")[1].split(": ")[1].split(":")[0]
                port = 80
                if "https://" in request.decode().split("\r\n")[1]:
                    port = 443
                    dest_socket = ssl.create_default_context().wrap_socket(sock=dest_socket, server_hostname=host)
                pp = int(port)
                dest_socket.connect((host, pp))
                dest_socket.send(request)
                response = dest_socket.recv(4096)
                headers, body = response.split(b"\r\n\r\n")[0], response.split(b"\r\n\r\n")[1]
                client_socket.send(response)
                with open("requests.log", "a") as f:
                    f.write("=" * 50 + "\n")
                    try:
                        f.write("Request headers:\n{}\n".format(self.prettify_request(request)))
                    except:
                        pass
                    try:
                        f.write("Request body:\n{}\n".format(body.decode("utf-8")))
                    except:
                        pass                    
                    try:
                        f.write("Response headers:\n{}\n".format(self.prettify_request(headers)))
                    except:
                        pass                        
                    try:
                     f.write("Request body:\n{}\n".format(body.decode("utf-8")))
                    except:
                        pass                    
                    f.write("Response body:\n{}\n".format(body.decode("utf-8")))
        else:
            client_socket.send(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
        dest_socket.close()
        client_socket.close()

    def prettify_request(self, request):
        """Prettify an HTTP request by adding line breaks and indentation."""
        return request.replace(b"\r\n", b"\r\n\t").decode("utf-8")

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(self.proxy, self.port)
        server_socket.bind((self.proxy, self.port))

        server_socket.listen(5)
        print("Proxy server listening on {}:{}".format(self.proxy, self.port))

        while True:
            client_socket, client_address = server_socket.accept()
            print("Accepted connection from {}:{}".format(client_address[0], client_address[1]))

            t = threading.Thread(target=self.handle_client, args=(client_socket,))
            t.start()
if __name__ == '__main__':
    proxy_address = f'{socket.gethostbyname(socket.gethostname())}:8080'  
    proxy_server = ProxyServer(proxy_address)
    proxy_server.run()


