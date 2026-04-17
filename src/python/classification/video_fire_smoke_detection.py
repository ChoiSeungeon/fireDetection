from pathlib import Path

import cv2
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image


class FireClassifier(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        base_model = models.resnet18(pretrained=True)
        base_model.fc = nn.Linear(base_model.fc.in_features, num_classes)
        self.model = base_model

    def forward(self, x):
        return self.model(x)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
input_video_path = PROJECT_ROOT / "input" / "fire_test.mp4"
output_video_path = PROJECT_ROOT / "output" / "fire_detection_result.mp4"
model_path = PROJECT_ROOT / "models" / "best_fire_img_classifier_acc96.10.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = T.Compose([T.Resize((224, 224)), T.ToTensor()])

model = FireClassifier(num_classes=3).to(device)
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

output_video_path.parent.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(str(input_video_path))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = cap.get(cv2.CAP_PROP_FPS)
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
out = cv2.VideoWriter(str(output_video_path), fourcc, fps, frame_size)

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    input_tensor = transform(img_pil).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        pred = output.argmax(dim=1).item()

    if pred == 0:
        color = (255, 0, 0)
        label = "Smoke"
    elif pred == 1:
        color = (0, 0, 255)
        label = "Fire"
    else:
        color = None
        label = "Normal"

    if color is not None:
        cv2.rectangle(frame, (5, 5), (frame_size[0] - 5, frame_size[1] - 5), color, 4)
        cv2.putText(frame, label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

    out.write(frame)
    frame_idx += 1
    if frame_idx % 30 == 0:
        print(f"처리 중... {frame_idx}프레임")

cap.release()
out.release()
print("✅ 영상 저장 완료:", output_video_path)

