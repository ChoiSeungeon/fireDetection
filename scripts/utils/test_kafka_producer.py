# test_kafka_producer.py
import base64
from kafka import KafkaProducer

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'fire-test'
IMAGE_PATH = './testData/test_image1.jpg'

# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: v.encode('utf-8')
)

# 이미지 로드 및 Base64 인코딩
with open(IMAGE_PATH, 'rb') as img_file:
    encoded = base64.b64encode(img_file.read()).decode('utf-8')

# Kafka로 전송
producer.send(TOPIC, value=encoded)
producer.flush()
print("[Producer] 이미지 전송 완료")
