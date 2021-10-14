import rpyc

PORTA = 5000
SERVER = 'localhost'

#Camada responsável pelo acesso do cliente ao servidor
class ClientAccess():

    def __init__(self) -> None:
        self.conn = rpyc.connect(SERVER, PORTA)

    #Função responsavel por obter a lista de tópicos que já foram criados
    def get_topic_list(self):
        return self.conn.root.get_topic_list()


    #Função responsavel por adicionar um novo tópico a lista de tópicos existentes
    def add_topic(self, topic):
        self.conn.root.add_topic(topic)


    #Função responsavel por remover um tópico a lista de tópicos existentes
    def remove_topic(self, topic):
        self.conn.root.remove_topic(topic)


    #Função responsável por definir o nome de usuário para o cliente
    def set_user(self):
        user_candidate = input('Digite seu nome de usuario:\n')
        fail, user = self.conn.root.set_user(user_candidate)
        #recebe do servidor a mensagem se o nome de usuário é valido ou não, e apenas aceita nomes de usuários válidos
        while fail:
            user_candidate = input('O nome escolhido ja esta em uso, escolha outro nome de usuario:\n')
            fail, user = self.conn.root.set_user(user_candidate)
        
        return user
    
    #Função responsável por remover um usuário da lista de usuários
    def remove_user(self, user):
        fail = self.conn.root.set_user(user)
        if fail:
            print('Usuario nao existe')


    #Chamam os métodos que encerram a conexão com o servidor
    def end(self, user):
        self.conn.root.remove_user(user)
        self.conn.close()
