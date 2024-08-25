from event import rabbitMQClass
from configparser_ import config
from listenner import Listener
import threading
import health

def start_rabbit_mq_async_processing(config_dict):

    rmc = rabbitMQClass(
        config_dict['rabbitMQ']['host'],
        config_dict['rabbitMQ']['user'],
        config_dict['rabbitMQ']['pass']
    )

    if rmc.get_connection() == -1:
        return -1

    async_processing_listener = Listener(
        config_dict['microservice']['service_name'],
        config_dict['database']['host'],
        config_dict['database']['user'],
        config_dict['database']['password'],
        config_dict['database']['name'],
        config_dict['rabbitMQ'],
    )

    rmc.exchnage_queue_setup(
        config_dict['rabbitMQ']['exchange'],
        config_dict['rabbitMQ']['queue']
    )

    rmc.read_queue(config_dict['rabbitMQ']['queue'],
                   async_processing_listener.listener_event_callback
                   )

def main():
    thread_handler_health = threading.Thread(target=health.run_health)
    thread_handler_health.start()
    try:
        thread_handler_rabbitmq = threading.Thread(target=start_rabbit_mq_async_processing, args=[config])
        thread_handler_rabbitmq.start()

        health.set_thread(thread_handler_rabbitmq)

        thread_handler_rabbitmq.join()
    except Exception:
        print("Failed to start microservice")

main()
