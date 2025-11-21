import cv2

points = []

def click_event(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(points)

video_path = r"D:\Projects\Resume Projects\Object Detection using Yolo\data\4K Road traffic video for object detection and tracking - free download now!.mp4"
cap = cv2.VideoCapture(video_path)

ret, frame = cap.read()
frame = cv2.resize(frame, (960, 540))  # same size as your detection script

cv2.imshow("Click to draw polygon", frame)
cv2.setMouseCallback("Click to draw polygon", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()

print("\nFinal polygon coordinates:")
print(points)
