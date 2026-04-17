import os

# 경로 설정 (여기엔 학습용 이미지 폴더 경로 넣기)
image_folder = r"C:\fireDetection\data\images\train_sampled"

# 이미지 확장자 필터
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

# 총 이미지 개수 및 용량 계산
total_size_bytes = 0
total_images = 0

for root, _, files in os.walk(image_folder):
    for file in files:
        if any(file.lower().endswith(ext) for ext in image_extensions):
            filepath = os.path.join(root, file)
            total_size_bytes += os.path.getsize(filepath)
            total_images += 1

total_size_mb = total_size_bytes / (1024 * 1024)
total_size_gb = total_size_mb / 1024

print(f"이미지 수: {total_images}장")
print(f"총 메모리 예상 사용량: {total_size_mb:.2f} MB ({total_size_gb:.2f} GB)")
