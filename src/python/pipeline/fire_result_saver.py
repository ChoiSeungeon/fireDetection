import base64
import json
import os
import sqlite3
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, messaging
from kafka import KafkaConsumer

PROJECT_ROOT = Path(__file__).resolve().parents[3]
service_account_path = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT", str(PROJECT_ROOT / "firebase_service_account.json")
)
fcm_token = os.getenv("FIREBASE_FCM_TOKEN", "")

firebase_enabled = False
if os.path.exists(service_account_path):
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    firebase_enabled = True

KAFKA_BROKER = "localhost:9092"
TOPIC = "fire-results"

conn = sqlite3.connect(PROJECT_ROOT / "fire_results.db")
cur = conn.cursor()

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="fire-db-group-v2",
)

print("🔥 DB 저장용 Kafka Consumer 실행 중...")

for message in consumer:
    data = message.value

    ts = data["timestamp"]
    cam = data["camera_id"]
    lat = data["location"]["latitude"]
    lon = data["location"]["longitude"]
    image_data = base64.b64decode(data["annotated_frame"])

    cur.execute(
        """
        INSERT INTO fire_events (
            timestamp, camera_id, latitude, longitude, annotated_image
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (ts, cam, lat, lon, image_data),
    )
    conn.commit()
    print(f"✅ 프레임 저장 완료: {cam} @ {ts}")

    for det in data.get("detections", []):
        label = det.get("label", "").lower()
        print(f"🧪 감지됨: {label}")

        if label == "fl":
            alert_label = "🔥 불꽃"
        elif label == "sm":
            alert_label = "💨 연기"
        else:
            continue

        if not firebase_enabled or not fcm_token:
            continue

        message = messaging.Message(
            data={
                "title": f"{alert_label} 감지!",
                "body": f"{cam}에서 {alert_label}이(가) 감지되었습니다.",
            },
            token=fcm_token,
        )

        try:
            response = messaging.send(message)
            print("📢 알림 전송 성공:", response)
        except Exception as e:
            print("❌ 알림 전송 실패:", e)

