import pika
import multiprocessing

from pika.spec import Access
from client_access import ClientAccess
from ctypes import c_char_p


class Client():

    def __init__(self) -> None:
        self.access = ClientAccess()

        self.consumer_process = None
        self.subscriptions = []

        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.conn.channel()
        self.channel.exchange_declare(exchange='messages', exchange_type='direct')
    

    def set_user(self):
        self.user = self.access.set_user()
        self.channel.queue_declare(queue=self.user)
        self.channel.basic_consume(queue=self.user, auto_ack=True, on_message_callback=self.recieve_message)

    
    def remove_user(self, user):
        self.access.remove_user(user)

    
    def recieve_message(self, channel, method, properties, body):
        body_str = body.decode('utf-8')
        print('>> Novo post do tópico ' + method.routing_key + ':')
        print(body_str)


    def create_topic(self, topic):
        self.access.add_topic(topic)


    def show_topics(self):
        valid_topics = self.access.get_topic_list()
        if len(valid_topics) == 0:
            print('>> Ainda não há tópicos criados')
            return
        print('>> Os tópicos válidos são:')
        for topic in valid_topics:
            print('>> ' + topic)


    def subscribe(self, topic):
        if topic not in self.access.get_topic_list():
            print('>> Esse tópico não existe')
        else:
            self.channel.queue_bind(queue=self.user, routing_key=topic, exchange='messages')
            self.subscriptions.append(topic)
            print('Sucesso! você agora está inscrito em: ' + topic)


    def check_if_subscribed(self, topic):
        if topic not in self.access.get_topic_list():
            print('>> Esse tópico não existe')
            return False
        if topic not in self.subscriptions:
            print('>> Você não está inscrito nesse tópico')
            return False
        
        return True


    def unsubscribe(self, topic):
        if self.check_if_subscribed(topic):
            self.channel.queue_unbind(queue=self.user, routing_key=topic, exchange='messages')
            self.subscriptions.remove(topic)
            print('>> Você não está mais inscrito em ' + topic)

    
    def show_subscription(self):
        print('>> Os tópicos inscritos são:')
        for topic in self.subscriptions:
            print('>> ' + topic)

    
    def publish(self, topic, post):
        if self.check_if_subscribed(topic):
            self.channel.basic_publish(exchange='messages', routing_key=topic, body=post)


    def start(self):
        self.consumer_process = multiprocessing.Process(target=self.channel.start_consuming)
        self.consumer_process.start()
        
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