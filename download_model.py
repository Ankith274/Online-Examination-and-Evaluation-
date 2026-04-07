import urllib.request as r
import os

os.makedirs('models', exist_ok=True)
req = r.Request('https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov3-tiny.weights', headers={'User-Agent': 'Mozilla/5.0'})
with r.urlopen(req) as response, open('models/yolov3-tiny.weights', 'wb') as out_file:
    out_file.write(response.read())
print('Weights downloaded!')

r.urlretrieve('https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg', 'models/yolov3-tiny.cfg')
print('CFG downloaded!')
r.urlretrieve('https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names', 'models/coco.names')
print('Names downloaded!')
