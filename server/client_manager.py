import rpyc

#Lista de topicos
topic_list = []

#Lista de usuarios
user_list = []

#Camada responsavel por centralizar as informações que cada cliente pode querer um sobre o outro
class ClientManager(rpyc.Service):

    def on_connect(self, conn):
        print("Conexao iniciada:")

    def on_disconnect(self, conn):
        print("Conexao finalizada:")

    #Retorna a lista de todos os usuários
    def exposed_get_topic_list(self):
        return topic_list
    
    def exposed_remove_topic(self, topic):
        if topic in topic_list:
            topic_list.remove(topic)
    
    def exposed_add_topic(self, topic):
        if topic not in topic_list:
            topic_list.append(topic)

    #verifica se o nome de usuário já está em uso, caso esteja, retorna um erro, caso contrário, cria o novo usuário
    def exposed_set_user(self, new_user):
        if new_user in user_list:
            return 1, ''
        else:
            user_list.append(new_user)
            return 0, new_user
    
    #Remove o usuário da lista de usuários no servidor
    def exposed_remove_user(self, user):
        if user not in user_list:
            return 1
        else:
            user_list.remove(user)
            return 0