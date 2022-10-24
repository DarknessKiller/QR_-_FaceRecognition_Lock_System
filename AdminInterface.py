import cv2
import os
from imutils import paths
import face_recognition
import pickle
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import random
import config
from passlib.hash import bcrypt
from datetime import datetime

# import functions from config.py
cursor = config.mysql.cursor()

window = None

VCCapW = 640
VCCapH = 480

def main():
	if config.mysql.is_connected() == False:
		messagebox.showerror("MySQL Database",  "MySQL Database cant be connected (either you didnt create database or didnt install mysql)")
	else:
		LoginScreen()

def Login(username, password):
	if username == "" or password == "":
		messagebox.showerror("Login Error",  "Empty Credentials")
	else:
		query = "SELECT username, password FROM admin WHERE username = " + "'" + username + "'"
		cursor.execute(query)
		queries = cursor.fetchone()
		if queries != None:
			if bcrypt.verify(password, queries[1]):
				window.destroy()
				AdminPanel(queries[0])
			else:
				messagebox.showerror("Login Error",  "Invalid Password")
		else:
			messagebox.showerror("Login Error",  "Invalid Credentials")

def submitQuery(customer, key, checkout):
	if customer == "" or key == "" or checkout == "":
		messagebox.showerror("Query",  "Invalid Query")
	else:
		if checkCustomerExists(customer) == False:
			pass
		else:
			query = "SELECT username FROM access WHERE username = " + "'" + customer + "'"
			cursor.execute(query)
			queries = cursor.fetchone()
			if queries == None:
				query = "SELECT roomKey FROM access WHERE roomKey = " + "'" + key + "'"
				cursor.execute(query)
				queries = cursor.fetchone()
				if queries == None:
					checkout_valid = True
					try:
						entry = datetime.strptime(checkout, "%Y-%m-%d %H:%M:%S")
						present = datetime.now()
						if entry.date() >= present.date():
							query = "INSERT INTO access (username, roomKey, checkout_at) VALUES (" + "'" + customer + "'" + ", " + key + ", " + "'" + checkout + "'" + ")"
							cursor.execute(query)
							config.mysql.commit()
							message = "Added Successful, " + customer + ", will checkout at " + checkout + "."
							messagebox.showinfo("Access Keyguard", message)
						else:
							print("Old Date Detected")
					except ValueError:
						messagebox.showerror("Checkout Query",  "Incorrect checkout string format")
				else:
					messagebox.showinfo("Access Keyguard", "This Room Key has been used")
			else:
				messagebox.showinfo("Access Keyguard", "{} has already have access".format(customer))


def checkCustomerExists(customer):
	if customer == "":
		messagebox.showerror("Check Customers", "Empty Credentials")
		return False
	else:
		query = "SELECT username FROM users WHERE username = " + "'" + customer + "'"
		cursor.execute(query)
		queries = cursor.fetchone()
		if queries != None:
			return True
		else:
			messagebox.showerror("Customer Not Found", "Customer '{}' Not Found In Database.".format(customer))
			return False     

def captureFaceData():
	Capture = True
	customer = simpledialog.askstring("Capture Face Date Input", "Enter customer username: ", parent=window)
	if checkCustomerExists(customer) == False:
		pass
	else:
		if os.path.isdir("dataset/{}".format(customer)) == False:
			cmd = "mkdir dataset/" + customer
			os.system(cmd)
		if os.path.isfile("dataset/{}/image_0.jpg".format(customer)) == True:
			proceed = messagebox.askyesno('Face Recognition', 'Old Customer Face Data Detected. Do you want to use previous face data?')
			if proceed == True:
				Capture = False
				messagebox.showinfo('Completed', 'You have completed all the steps.')
			elif proceed == False:
				pass
			else:
				Capture = False
				messagebox.showerror('Error', 'Something went wrong!')

		while Capture == True:
			cap = cv2.VideoCapture(0)
			cap.set(3, VCCapW)
			cap.set(4, VCCapH)
			windowName = "Press Spacebar to take photo"
			cv2.namedWindow(
				"Press Spacebar to take photo",
				 cv2.WINDOW_NORMAL)
			img_counter = 0

			while True:
				ret, frame = cap.read()
				if not ret:
					messagebox.showerror("Video Capture", "Failed to grab frame")
				cv2.imshow(
					"Press Spacebar to take photo", frame)

				key = cv2.waitKey(1)
				if key % 256 == 27:
					# Escape
					Capture = False
					cap.release()
					cv2.destroyAllWindows()
					messagebox.showinfo("Escape Detected", "Escape hit, closing...")
					break
				elif key % 256 == 32:
					# Spacebar pressed
					img_name = "dataset/" + customer + "/image_{}.jpg".format(img_counter)
					cv2.imwrite(img_name, frame)
					print("{} written!".format(img_name))
					img_counter += 1
					cv2.setWindowTitle(windowName, "Press Spacebar to take photo, Photo {}/5".format(img_counter))
					#messagebox.showinfo("Image Counter", "Images {}/5".format(img_counter))
					if img_counter == 5:
						Capture = False
						cap.release()
						cv2.destroyAllWindows()
						messagebox.showinfo("Image Counter", "Done!, you have provided enough images")
						messagebox.showinfo("Training Models", "Please wait as we processing the models.")
						startTrainModels()
						break
			cap.release()
			cv2.destroyAllWindows()

def startTrainModels():
	print("[INFO] Proccessing Faces...")
	imagePaths = list(paths.list_images("dataset"))

	knownFaces = []
	knownNames = []

	for (i, imagePath) in enumerate(imagePaths):
		print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
		name = imagePath.split(os.path.sep)[-2]

		image = cv2.imread(imagePath)
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		boxes = face_recognition.face_locations(rgb, model="hog")

		encodings = face_recognition.face_encodings(rgb, boxes)

		for encoding in encodings:
			knownFaces.append(encoding)
			knownNames.append(name)

	# dump the facial encodings + names to disk
	print("[INFO] serializing encodings…")
	data = {"encodings": knownFaces, "names": knownNames}
	f = open("facePickle.pickle", "wb")
	f.write(pickle.dumps(data))
	f.close()
	messagebox.showinfo("Training Models", "Done!!")

def Logout():
	window.withdraw()
	messagebox.showinfo("Lock Admintration Panel", "Logged Out Successfully")
	window.destroy()
	main()

def LoginScreen():
	global window
	window = tk.Tk()
	window.title("Welcome")
	window.geometry("240x180")
	window.eval('tk::PlaceWindow . center')
	greeting = tk.Label(text="Welcome to Lock Admintration Panel")
	greeting.pack()
	userLbl = tk.Label(text="Username")
	userEntry = tk.Entry()
	userLbl.pack()
	userEntry.pack()
	pwdLbl = tk.Label(text="Password")
	pwdEntry = tk.Entry(show="*")
	pwdLbl.pack()
	pwdEntry.pack()
	loginButton = tk.Button(text="Login", command= lambda: Login(userEntry.get(), pwdEntry.get()))
	loginButton.pack()
	window.mainloop()

def AdminPanel(username):
	global window
	window = tk.Tk()
	window.title("Lock System Admintration Panel")
	window.geometry("640x480")
	window.eval('tk::PlaceWindow . center')
	greeting = tk.Label(text="Welcome to Lock Admintration Panel, My Name is {}".format(username))
	greeting.pack()
	userLbl = tk.Label(text="Username")
	userEntry = tk.Entry()
	userLbl.pack()
	userEntry.pack()
	keyLbl = tk.Label(text="Room Key (Use or Regen)")
	keyEntry = tk.Entry()
	keyEntry.insert(0, random.randint(000000, 999999))
	keyLbl.pack()
	keyEntry.pack()
	checkLbl = tk.Label(text="Checkout Date & Time (YYYY-MM-DD HH:MM:SS)")
	checkEntry = tk.Entry()
	checkLbl.pack()
	checkEntry.pack()
	createButton = tk.Button(text="Create", command= lambda: submitQuery(userEntry.get(), keyEntry.get(), checkEntry.get()))
	createButton.pack()
	regButton = tk.Button(text="Regen Key", command= lambda: [keyEntry.delete(0, tk.END), keyEntry.insert(0, random.randint(000000, 999999))])
	regButton.pack()
	faceButton = tk.Button(text="Create Face Data", command= lambda: captureFaceData())
	faceButton.pack()
	logoutButton = tk.Button(text="Logout", command= lambda: Logout())
	logoutButton.pack()
	window.mainloop()

if __name__ == "__main__":
	main()