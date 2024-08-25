import pika
import logging
from pika.exceptions import ConnectionWrongStateError


class rabbitMQConnect(object):
    def __init__(self, host, user, password):
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.user = user
        self.password = password
        self.connection = self.connect()
        super().__init__()

    def get_connection(self):
        return self.connection

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self.host,
                credentials=credentials,
                heartbeat=60,
                socket_timeout=None
            ))

            self.connection = connection
            return self.connection
        except:
            self.logger.exception("Failed to connect to broker")
            self.connection = -1

    def disconnect(self):
        try:
            self.connection.close()
        except ConnectionWrongStateError:
            pass


class rabbitMQChannel(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super().__init__()

    def channel_connect(self):
        try:
            connection = self.get_connection()
            channel = connection.channel()
            return channel

        except pika.exceptions.StreamLostError:
            self.logger.exception("Failed to connect to channel. Try reconnecting")
            try:
                self.connect()
                connection = self.get_connection()
                channel = connection.channel()
                return channel
            except Exception:
                return -1

        except Exception:
            self.logger.exception("Failed to connect to channel")
            return -1

    def channel_close(self, channel):
        try:
            channel.close()
            return 1

        except Exception:
            self.logger.exception("Failed to close channel")
            return -1


class rabbitMQExchangeSetup(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super().__init__()

    def exchnage_queue_setup_(self, exchange_name, queue_name):
        try:
            channel = self.channel_connect()
            channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
            channel.queue_declare(queue=queue_name)
            channel.queue_bind(exchange=exchange_name, queue=queue_name)
            self.channel_close(channel)
            return 1
        except Exception:
            self.logger.exception("Failed to setup exchange and queue")
            self.channel_close(channel)
            return -1

    def exchange_setup_(self, exchange_name):
        try:
            channel = self.channel_connect()
            channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
            self.channel_close(channel)
            return 1
        except Exception:
            self.logger.exception("Failed to setup exchange")
            self.channel_close(channel)
            return -1


class rabbitMQRead(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super().__init__()

    def read_queue_(self, queue_name, function):
        try:
            channel = self.channel_connect()
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=queue_name, on_message_callback=function)
            channel.start_consuming()
            self.channel_close(channel)
            return 1

        except Exception:
            self.logger.exception("Failed to listen/read queue")
            channel.stop_consuming()
            self.channel_close(channel)
            return -1


class rabbitMQPost(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super().__init__()

    def post_exchange_(self, exchange_name, message):
        try:
            channel = self.channel_connect()
            channel.basic_publish(exchange=exchange_name, routing_key='', body=message)
            self.channel_close(channel)
            return 1
        except Exception:
            self.logger.exception("Failed to post to exchange")
            self.channel_close(channel)
            return -1

    def post_queue_(self, exchange_name, queue_name, message):
        try:
            channel = self.channel_connect()
            channel.basic_publish(exchange=exchange_name, routing_key=queue_name, body=message)
            self.channel_close(channel)
            return 1
        except Exception:
            self.logger.exception("Failed to post to queue")
            self.channel_close(channel)
            return -1


class rabbitMQClass(
    rabbitMQConnect,
    rabbitMQChannel,
    rabbitMQExchangeSetup,
    rabbitMQRead,
    rabbitMQPost
):

    def __init__(self, host, user, password):
        self.logger = logging.getLogger(__name__)
        super().__init__(host, user, password,)

    def exchnage_queue_setup(self, exchange_name, queue_name):
        return self.exchnage_queue_setup_(exchange_name, queue_name)

    def exchange_setup(self, exchange_name):
        return self.exchange_setup_(exchange_name)

    def read_queue(self, queue_name, function):
        return self.read_queue_(queue_name, function)

    def post_exchange(self, exchange_name, message):
        return self.post_exchange_(exchange_name, message)

    def post_queue(self, exchange_name, queue_name, message):
        return self.post_queue_(exchange_name, queue_name, message)
