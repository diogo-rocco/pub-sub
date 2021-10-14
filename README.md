# pub-sub
Aplicação de publish subscribe para a disciplina de sistemas distribuidos

1) Para rodar a aplicação, primeiro é necessário instanciar um servidor do RabitMQ que vai gerenciar o fluxo de mensagens. Para isso, basta rodar a seguinte linha em um prompt de comando:

`docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management`

2) Depois iniciar servidor rodando o programa:

`server.py`

3) e finalmente iniciar o cliente rodando o programa:

`client.py`
