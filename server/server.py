from rpyc.utils.server import ThreadedServer
from client_manager import ClientManager

PORTA=5000

#Inicializa a camada de gerenciamento dos clientes
server = ThreadedServer(ClientManager, port=PORTA)

server.start()
