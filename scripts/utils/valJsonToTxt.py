import os
import json
from glob import glob

# 📁 Validation 데이터 경로
root_dir = r"D:\fireDetection\Validation"

# 📁 YOLO 라벨 출력 위치
output_lbl_dir = r"D:\fireDetection\yolo_dataset\labels\val"
os.makedirs(output_lbl_dir, exist_ok=True)

# 클래스 매핑: JSON category_id → YOLO class_id
category_id_to_index = {2: 0, 1: 1}  # sm: 0, fl: 1

# 🔍 모든 JSON 파일 검색
json_files = glob(os.path.join(root_dir, "02.라벨링데이터", "**", "JSON", "*.json"), recursive=True)

for json_path in json_files:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    width = data["image"]["width"]
    height = data["image"]["height"]
    filename = data["image"]["filename"]
    annotations = data["annotations"]

    yolo_lines = []
    for anno in annotations:
        cat_id = anno["categories_id"]
        if cat_id not in category_id_to_index:
            continue
        class_id = category_id_to_index[cat_id]
        x, y, w, h = anno["bbox"]
        xc = (x + w / 2) / width
        yc = (y + h / 2) / height
        wn = w / width
        hn = h / height
        yolo_lines.append(f"{class_id} {xc:.6f} {yc:.6f} {wn:.6f} {hn:.6f}")

    # ✅ YOLO 형식 라벨 파일 저장
    label_name = os.path.splitext(filename)[0] + ".txt"
    label_path = os.path.join(output_lbl_dir, label_name)

    if yolo_lines:
        with open(label_path, "w") as f:
            f.write("\n".join(yolo_lines))
    else:
        # 🔸 객체가 없는 정상 이미지도 빈 txt 파일 생성 (중요!)
        open(label_path, 'w').close()

print(f"✅ 검증용 YOLO 라벨 {len(json_files)}개 생성 완료!")
