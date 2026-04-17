from pathlib import Path

import aiosqlite
import base64
from fastapi import FastAPI

app = FastAPI()
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "fire_results.db"


@app.get("/fires")
async def get_all_fires():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT timestamp, camera_id, latitude, longitude, annotated_image
            FROM fire_events
            ORDER BY timestamp DESC
            """
        ) as cursor:
            rows = await cursor.fetchall()
            results = []

            for row in rows:
                image_base64 = base64.b64encode(row["annotated_image"]).decode("utf-8")
                results.append(
                    {
                        "timestamp": row["timestamp"],
                        "camera_id": row["camera_id"],
                        "latitude": row["latitude"],
                        "longitude": row["longitude"],
                        "image": image_base64,
                    }
                )

            return results

