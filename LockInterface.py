# initial required libraries
import cv2
import os
import numpy as np
import face_recognition
import pickle
import time
from pyzbar.pyzbar import decode
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import config
import logging
from datetime import datetime
import timeout_decorator

LOG_FILENAME = datetime.now().strftime('logs/log_%H_%M_%S_%d_%m_%Y.log')
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,
                   format="%(levelname)s:%(asctime)s %(message)s")

# To Include Servo Libraries
factory = PiGPIOFactory()

# Set Servo Pulse
servo = Servo(15, min_pulse_width=0.45/1000, max_pulse_width=2.4/1000, pin_factory=factory)
servo.max()


# import functions from config.py
cursor = config.mysql.cursor()

# variables
cap = ""
sus = ""
VCCapW = 640
VCCapH = 480

def main():
	if config.mysql.is_connected() == True:
		print("[INFO] Initialized Lock Interface")
		logging.info("[INFO] Initialized Lock Interface")
		QRCapture()
	else:
		print("[ERROR] MySQL Database cant be connected (either you didnt create database or didnt install mysql)")
		logging.error("[ERROR] MySQL Database cant be connected (either you didnt create database or didnt install mysql)")
		quit()

def QRCapture():
	print("[INFO] Entering QR Code Capture (Part 1/2)")
	logging.info("[INFO] Entering QR Code Capture (Part 1/2)")
	global cap
	cap = cv2.VideoCapture(0)
	cap.set(3,VCCapW)
	cap.set(4,VCCapH)

	while True:
		ret, frame = cap.read()
		for barcode in decode(frame):
			myData = barcode.data.decode("utf-8")
			pts = np.array([barcode.polygon], np.int32)
			pts = pts.reshape((-1,1,2))
			cv2.polylines(frame,[pts], True, (255, 0, 255), 5)
			pts2 = barcode.rect
			query = "SELECT username FROM access WHERE roomKey = " + "'" + myData + "'"
			cursor.execute(query)
			queries = cursor.fetchone()
			if queries != None:
				cv2.putText(frame, queries[0], (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX,
					0.9, (255, 0, 255), 2)
				cap.release()
				cv2.destroyWindow("Please Show Your QR Code")
				print("[INFO] Detected QR for {}".format(queries[0]))
				logging.info("[INFO] Detected QR for {}".format(queries[0]))
				try:
					sus = faceCapture(queries[0])
				except timeout_decorator.TimeoutError:
					print("[INFO] Face Capture Timeout Detected")
					logging.info("[INFO] Face Capture Timeout Detected")
					cap.release()
					cv2.destroyAllWindows()
					QRCapture()
				except Exception:
					cap.release()
					cv2.destroyAllWindows()
					QRCapture()
				if sus == True:
					servoNow()
				else:
					pass
			else:
				cv2.putText(frame, "Invalid QR Code", (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX,
					0.9, (255, 0, 255), 2)

		cv2.imshow("Please Show Your QR Code", frame)
		key = cv2.waitKey(1)
		if key % 256 == 27:
			print("Escape hit, closing...")
			logging.info("Escape hit, closing...")
			quit()

@timeout_decorator.timeout(120)
def faceCapture(username):
    
	print("[INFO] Entering Face Recognition (Part 2/2)")
	logging.info("[INFO] Entering Face Recognition (Part 2/2)")

	currentname = "unknown"
	facePickle = "facePickle.pickle"
	cascade = "cascades/haarcascade_frontalface_default.xml"

	data = pickle.loads(open(facePickle, "rb").read())
	detector = cv2.CascadeClassifier(cascade)
	font = cv2.FONT_HERSHEY_SIMPLEX
	global cap
	cap = cv2.VideoCapture(0)
	cap.set(3,VCCapW)
	cap.set(4,VCCapH)
	
	while True:
		ret, frame = cap.read()
		names = []
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		rect = detector.detectMultiScale(gray, scaleFactor=1.1, 
			minNeighbors=5, minSize=(30, 30),
			flags=cv2.CASCADE_SCALE_IMAGE)

		boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rect]

		encodings = face_recognition.face_encodings(rgb, boxes)

		for encoding in encodings:
			matches = face_recognition.compare_faces(data["encodings"],
				encoding)
			name = "Unknown"

			if True in matches:
				matchedIds = [i for (i, b) in enumerate(matches) if b]
				counts = {}

				for num in matchedIds:
					name = data["names"][num]
					counts[name] = counts.get(name, 0) + 1

				name = max(counts, key=counts.get)

				if currentname != name:
					currentname = name
					if currentname == username:
						cap.release()
						cv2.destroyWindow("Please Show Your Face")
						return True

			names.append(name)

		for ((top, right, bottom, left), name) in zip(boxes, names):
			cv2.rectangle(frame, (left, top), (right, bottom),
				(0, 255, 0), 2)
			y = top - 15 if top - 15 > 15 else top + 15
			if currentname == username:
				cv2.putText(frame, currentname, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
					.8, (255, 0, 0), 2)
			else:
				cv2.putText(frame, "Unknown", (left, y), cv2.FONT_HERSHEY_SIMPLEX,
					.8, (255, 0, 0), 2)
		cv2.imshow("Please Show Your Face", frame)
		key = cv2.waitKey(1)
		if key % 256 == 27:
			print("[INFO] Escape hit, closing face...")
			logging.info("[INFO] Escape hit, closing face...")
			raise Exception
			#cap.release()
			#cv2.destroyAllWindows()
			#QRCapture()

def servoNow():
	print("[INFO] Unlocking for 45 Seconds")
	logging.info("[INFO] Unlocking for 45 Seconds")
	servo.mid()
	time.sleep(45)
	print("[INFO] 45 Seconds Passed. Locking Now")
	logging.info("[INFO] 45 Seconds Passed. Locking Now")
	servo.max()
	QRCapture()

if __name__ == "__main__":
    main()
