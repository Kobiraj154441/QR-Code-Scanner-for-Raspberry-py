import cv2
import cv2.cv as cv
import zbarlight
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import numpy
import RPi.GPIO as GPIO

# set up gpio
GPIO.setmode(GPIO.BCM)
pins = {
    "red": 18,
    "green": 17,
    "yellow": 27,
    "blue": 22
    }
for color, pin in pins.iteritems():
    GPIO.setup(pin, GPIO.OUT)

# initialize picamera
camera = PiCamera()
resolution = (200, 100)
camera.resolution = resolution
raw_capture = PiRGBArray(camera, size = resolution)
time.sleep(0.1)

colors = {
    "red": (0,0,255),
    "green": (0,255,0),
    "yellow": (0,255,255),
    "blue": (255,0,0)
    }

def qrCheck(arg):
    """ Check an image for a QR code, return as string """
    image_string = arg.tostring()
    try:
        code = zbarlight.qr_code_scanner(image_string, 200, 100)
        return code
    except:
        return


for frame in camera.capture_continuous(raw_capture,
                                       format = "bgr",
                                       use_video_port = True):
    # grab image as numpy array
    image = frame.array
        
    # convert image to grayscale and decode
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    decoded = qrCheck(gray)

    for color, pin in pins.iteritems():
        if decoded == color:
            GPIO.output(pin, True)
        else:
            GPIO.output(pin, False)
    
    # write decoded output to frame
    cv2.putText(image,
                decoded,
                (30,30),
                cv.CV_FONT_HERSHEY_SIMPLEX,
                1,
                colors.get(decoded),
                2)

    # show frame
    cv2.imshow("frame", image)
    key = cv2.waitKey(60) & 0xFF
    raw_capture.truncate(0)

    # quit if q is pressed
    if key == ord('q'):
        break
cv2.destroyAllWindows()
GPIO.cleanup()
