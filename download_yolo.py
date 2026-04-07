import urllib.request as r
import os

os.makedirs('models', exist_ok=True)

# Create opener with User-Agent
opener = r.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')]
r.install_opener(opener)

print("Downloading yolov3-tiny.weights...")
r.urlretrieve('https://pjreddie.com/media/files/yolov3-tiny.weights', 'models/yolov3-tiny.weights')
print("Downloaded weights!")

print("Downloading cfg...")
r.urlretrieve('https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg', 'models/yolov3-tiny.cfg')
print("Downloaded cfg!")

print("Downloading coco.names...")
r.urlretrieve('https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names', 'models/coco.names')
print("Downloaded names!")
