import pika
import multiprocessing

from pika.spec import Access
from client_access import ClientAccess
from ctypes import c_char_p


class Client():

    #Construtor da classe Client, nele inicializamos:
    #   - uma instância da nossa classe de acesso ao servidor
    #   - uma instancia do objeto de conexão do nosso middleware, que vai estabelecer uma conexão com o fluxo de mensagens
    #   - uma instancia do canal de comunicação e sua exchange, que é a forma que o RabbitMQ vai usar para fazer o roteamento das mensagens
    def __init__(self) -> None:
        self.access = ClientAccess()

        self.consumer_process = None
        self.subscriptions = []

        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost')) #inicializa a conexão com o fluxo de mensagens
        self.channel = self.conn.channel() #inicializa o canal
        self.channel.exchange_declare(exchange='messages', exchange_type='direct') #cria a "exchange" de mensagens, uma exchange é a estrutura responsavel pelo roteamento no RabbitMQ
    

    #Define o nome de usuário e a fila de mensagens do cliente. Na nossa aplicação, o nome da fila vai ser igual ao nome do usuario
    def set_user(self):
        self.user = self.access.set_user()
        self.channel.queue_declare(queue=self.user)
        self.channel.basic_consume(queue=self.user, auto_ack=True, on_message_callback=self.recieve_message)

    
    #Chama nossa classe de acesso ao servidor para remover o usuário da lista de usuários ativos
    def remove_user(self, user):
        self.access.remove_user(user)

    #Callback que vai ser chamado quando uma nova mensagem chegar para o cliente
    def recieve_message(self, channel, method, properties, body):
        body_str = body.decode('utf-8')
        print('>> Novo post do tópico ' + method.routing_key + ':')
        print(body_str)


    #Chama nossa classe de acesso ao servidor para criar um novo tópico e adiciona-lo a lista de tópicos existentes
    def create_topic(self, topic):
        self.access.add_topic(topic)


    #Chama nossa classe de acesso ao servidor para recuperar a lista de tópicos existentes e exibi-la para o usuário
    def show_topics(self):
        valid_topics = self.access.get_topic_list()
        if len(valid_topics) == 0:
            print('>> Ainda não há tópicos criados')
            return
        print('>> Os tópicos válidos são:')
        for topic in valid_topics:
            print('>> ' + topic)


    #Se inscreve em um novo tópico, caso ele exista
    def subscribe(self, topic):
        if topic not in self.access.get_topic_list(): #verifica se o tópico está na lista de tópicos existentes
            print('>> Esse tópico não existe')
        else:
            #Faz o bind do tópico com a fila, no RabbitMQ isso faz com que a exchange entenda que a fila do usuário está interessada em ouvir mensagens daquela routin_key
            self.channel.queue_bind(queue=self.user, routing_key=topic, exchange='messages')
            self.subscriptions.append(topic)
            print('Sucesso! você agora está inscrito em: ' + topic)


    #Verifica de o tópico pertence a lista de tópicos nos quais o usuário está inscrito
    def check_if_subscribed(self, topic):
        if topic not in self.access.get_topic_list():
            print('>> Esse tópico não existe')
            return False
        if topic not in self.subscriptions:
            print('>> Você não está inscrito nesse tópico')
            return False
        
        return True


    #Faz com que um usuário não esteja mais incrito em um tópicp
    def unsubscribe(self, topic):
        if self.check_if_subscribed(topic): #Verifica se o usuário está inscrito
            self.channel.queue_unbind(queue=self.user, routing_key=topic, exchange='messages') #faz o unbind da routing_key do tópico na fila do usuário
            self.subscriptions.remove(topic) #remove o tópico da lista de inscrições do usuário
            print('>> Você não está mais inscrito em ' + topic)

    
    #Exibe os tópicos nos quais o usuário está inscrito
    def show_subscription(self):
        print('>> Os tópicos inscritos são:')
        for topic in self.subscriptions:
            print('>> ' + topic)

    
    #Publica uma nova mensagem em um determinado tópico
    def publish(self, topic, post):
        if self.check_if_subscribed(topic):
            self.channel.basic_publish(exchange='messages', routing_key=topic, body=post)


    #Função onde se localiza o fluxo de execução do cliente
    def start(self):
        #criamos um novo processo onde será executada o método de escuta da nossa fila, como a escuta é bloqueante na conexão que usamos, alocamos um processo exclusivo para escutar por novas mensagens
        self.consumer_process = multiprocessing.Process(target=self.channel.start_consuming)
        self.consumer_process.start()
        
        #loop que aguarda inputs do usuário para executar as ações de cada comando
        while True:
            msg = input('>> Digite um coomando (Digite /help para obter uma lista de comando validos):\n')

            if msg == '/get_topics':
                self.show_topics()
            
            if msg == '/add_topic':
                topic = input('>> Diga o tópico que deseja criar:\n')
                self.create_topic(topic)
            
            if msg == '/sub':
                topic = input('>> Diga o tópico no qual você quer se inscrever: ')
                self.subscribe(topic)

            if msg == '/unsub':
                topic = input('>> Diga o tópico no qual você quer deixar de ser isncrito: ')
                self.unsubscribe(topic)

            if '/post' in msg:
                topic = input('>> Diga o tópico no qual você quer postar: ')
                post = input('>> Escreva a sua publicação: ')
                self.publish(topic, post)

            if '/get_subs' == msg:
                self.show_subscription()
            
            if msg == '/help':
                print('>> Comandos Validos:')
                print('>> /get_topics: Fornece uma lista com todos os tópicos existentes')
                print('>> /get_subs: Fornece uma lista com todos os tópicos inscritos')
                print('>> /add_topic: Cria um novo topico')
                print('>> /sub: Se inscreve em um topico')
                print('>> /unsub: Deixa se estar inscrito em um topico')
                print('>> /post: Publica uma mensagem em um topico')

            if msg == '/quit':
                self.consumer_process.terminate()
                self.conn.close()
                self.access.end(self.user)
                return