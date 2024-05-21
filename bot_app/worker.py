import pika

RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'telegram_messages'

def callback(ch, method, properties, body):
    print(f"Получено сообщение: {body.decode()}")
    # Обработка сообщения

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)
    print('Ожидание сообщений. Для выхода нажмите CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()
