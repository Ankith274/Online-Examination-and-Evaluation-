import cv2
import urllib.request
import numpy as np
from proctoring import ProctoringEngine

engine = ProctoringEngine()
url = "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?ixlib=rb-4.0.3&auto=format&fit=crop&w=416&q=80" # Person holding phone
req = urllib.request.urlopen(url)
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)

analysis = engine.analyze_frame(img)
print(analysis)
