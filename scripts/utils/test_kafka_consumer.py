# test_kafka_consumer.py
import base64
from kafka import KafkaConsumer

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'fire-test'

# Kafka Consumer 설정
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-group',
    value_deserializer=lambda v: v.decode('utf-8')
)

print("[Consumer] 메시지 대기 중...")

for message in consumer:
    encoded_data = message.value
    img_data = base64.b64decode(encoded_data)

    with open('received_test.jpg', 'wb') as f:
        f.write(img_data)

    print("[Consumer] 이미지 수신 및 저장 완료")
    break  # 한 장만 테스트하므로 수신 후 종료
