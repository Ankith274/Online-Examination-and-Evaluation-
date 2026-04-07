import cv2
import numpy as np
import os

class ProctoringEngine:
    def __init__(self):
        # We use standard OpenCV cascade since mediapipe solutions drops support on Python 3.14+
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        
        # Load YOLOv3-tiny for object detection
        self.yolo_net = None
        yolo_cfg = "models/yolov3-tiny.cfg"
        yolo_weights = "models/yolov3-tiny.weights"
        if os.path.exists(yolo_cfg) and os.path.exists(yolo_weights):
            self.yolo_net = cv2.dnn.readNetFromDarknet(yolo_cfg, yolo_weights)
            
            # Setup DNN Backend
            self.yolo_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.yolo_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        
        self.cell_phone_class_id = 67 # COCO dataset index for cell phone

    def analyze_frame(self, frame):
        """
        Analyzes a single frame for suspicious behavior using OpenCV Haarcascades and DNN.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Equalize histogram to improve contrast for Haar cascades
        gray = cv2.equalizeHist(gray)
        
        # Detect frontal and profile faces with softer parameters to avoid flickering
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=2, minSize=(40, 40))
        profiles = self.profile_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=2, minSize=(40, 40))
        
        analysis = {
            "face_detected": False,
            "looking_away": False,
            "suspicious_status": "Normal",
            "cell_phone_detected": False,
            "multiple_faces_detected": False
        }

        if len(faces) > 1:
            analysis["multiple_faces_detected"] = True

        if len(faces) > 0:
            analysis["face_detected"] = True
            # Found frontal face, student is looking at the screen
        elif len(profiles) > 0:
            analysis["face_detected"] = True
            analysis["looking_away"] = True
            analysis["suspicious_status"] = "Looking Sideways"
        else:
            # Neither frontal nor strictly profile detected. 
            # Could be looking down/up or away completely.
            analysis["face_detected"] = False
            analysis["suspicious_status"] = "No Face Detected"

        # YOLOv3-tiny Object Detection
        if self.yolo_net is not None:
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
            self.yolo_net.setInput(blob)
            
            # Get the output layer names
            layer_names = self.yolo_net.getLayerNames()
            output_layers = [layer_names[i - 1] for i in self.yolo_net.getUnconnectedOutLayers()]
            
            # Forward pass
            outputs = self.yolo_net.forward(output_layers)
            
            # Check detections
            prohibited_classes = {67, 65, 63} # 67: cell phone, 65: remote, 63: laptop
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if class_id in prohibited_classes and confidence > 0.15:
                        analysis["cell_phone_detected"] = True
                        analysis["suspicious_status"] = "Cell Phone/Prohibited Item Detected"
                        break
                if analysis["cell_phone_detected"]:
                    break
                        
        if analysis["multiple_faces_detected"]:
            analysis["suspicious_status"] = "Multiple People Detected"

        return analysis

# Example usage (standalone test)
if __name__ == "__main__":
    engine = ProctoringEngine()
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        
        analysis = engine.analyze_frame(frame)
        print(analysis)
        
        cv2.imshow('EvalFlow AI Proctoring Test', frame)
        if cv2.waitKey(5) & 0xFF == 27: break
    cap.release()
