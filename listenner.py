import logging
import json
import functools
import threading
from datetime import datetime
from database.connection import DatabaseConnect
from event import rabbitMQClass


def ack_message(ch, delivery_tag):
    if ch.is_open:
        ch.basic_ack(delivery_tag=delivery_tag)


def reject_message_no_requeue(ch, delivery_tag):
    if ch.is_open:
        ch.basic_reject(delivery_tag, requeue=False)


def reject_message(ch, delivery_tag):
    if ch.is_open:
        ch.basic_reject(delivery_tag)


class Listener:
    def __init__(self, service_name, host, user, password, database_name, rmq_config):
        self.logger = logging.getLogger(__name__)
        self.service_name = service_name
        self.db_conn = DatabaseConnect(host, user, password, database_name)
        self.rmq_config = rmq_config

    def _parse_async_processing_message(self, body):
        try:
            json_message = json.loads(body.decode('utf-8'))
            return json_message
        except Exception:
            self.logger.exception(
                "Failed to parse async processing message")
            return None

    def listener_event_callback(self, ch, method, properties, body):
        message = self._parse_async_processing_message(body)
        if not message:
            reject_message_no_requeue(ch, method.delivery_tag)
        manage_message_thread = threading.Thread(target=self.execute_async_processing, args=(ch, method, message))
        manage_message_thread.start()

    def post_to_error_exchange(self, exchange, message):
        rmc = rabbitMQClass(
            self.rmq_config['host'],
            self.rmq_config['user'],
            self.rmq_config['pass']
        )
        rmc.post_exchange(exchange, message)

    def execute_async_processing(self, ch, method, message):
        try:
            db_conn = self.db_conn.connect()
            if (message):
                print('The message is:', message)
                cb = functools.partial(ack_message, ch, method.delivery_tag)
                ch.connection.add_callback_threadsafe(cb)
            else:
                cb = functools.partial(reject_message_no_requeue, ch, method.delivery_tag)
                ch.connection.add_callback_threadsafe(cb)
                return
        except Exception as e:
            self.logger.exception(e)
            self.post_to_error_exchange("error_exchange", json.dumps({
                "services": self.service_name,
                "errored_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error_message": str(e),
                "data": message
            }))
            cb = functools.partial(reject_message_no_requeue, ch, method.delivery_tag)
            ch.connection.add_callback_threadsafe(cb)
            return
        finally:
            try:
                db_conn.close()
            except:
                pass
