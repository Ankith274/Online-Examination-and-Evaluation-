import cv2
import numpy as np
from proctoring import ProctoringEngine

engine = ProctoringEngine()
frame = np.zeros((480, 640, 3), dtype=np.uint8)
analysis = engine.analyze_frame(frame)
print(analysis)
