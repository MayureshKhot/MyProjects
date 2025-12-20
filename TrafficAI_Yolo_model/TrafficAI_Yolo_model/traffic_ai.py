import cv2
from ultralytics import YOLO
import time
import numpy as np

# loading model
print("[INFO] loading yolo model...")
model = YOLO("yolov8s.pt")  # will upgrade later

# video path - hardcoded for now
VIDEO_PATH = r"D:\MyProjects\TrafficAI_Yolo_model\TrafficAI_Yolo_model\data\4K Road traffic video for object detection and tracking - free download now!.mp4"

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("error: video not found or can't open")
    exit()

frame_count = 0

def is_inside_lane(point, polygon):
    poly = np.array(polygon, np.int32)
    return cv2.pointPolygonTest(poly, point, False) >= 0

# lane polygons
lanes = {
    "Lane 1": [(88, 341), (203, 354), (0, 449), (94, 330)],
    "Lane 2": [(224, 322), (361, 323), (305, 535), (108, 514)],
    "Lane 3": [(415, 326), (528, 327), (553, 518), (385, 520)],
    "Lane 4": [(644, 259), (817, 501), (899, 327), (777, 201)]
}


lane_counts = {"Lane 1": 0, "Lane 2": 0, "Lane 3":0, "Lane 4":0}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (960, 540))

    results = model(frame, conf=0.40, classes=[2,3,5,7], stream=True)

    # reset counts every frame (for density)# dynamic lane counter
    lane_counts = {lane_name: 0 for lane_name in lanes.keys()}

    for r in results:
        annotated_frame = r.plot()
        
        boxes = r.boxes

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]

            cx = int((x1 + x2) // 2)
            cy = int(y2)   # bottom-center for better lane accuracy

            for lane_name, lane_poly in lanes.items():
                if is_inside_lane((cx, cy), lane_poly):
                    lane_counts[lane_name] += 1

        # draw polygons
        for lane_name, pts in lanes.items():
            pts_np = np.array(pts, np.int32)
            cv2.polylines(annotated_frame, [pts_np], True, (0,255,0), 2)
            cv2.putText(annotated_frame, lane_name, pts[0], cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # lane counts on screen
        y_offset = 40
        for lane_name, count in lane_counts.items():
            cv2.putText(annotated_frame, f"{lane_name}: {count}", (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
            y_offset += 30

    cv2.imshow("Traffic Density", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

