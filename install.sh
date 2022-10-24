echo "Welcome to Project QR Code & Face Lock Setup Wizard"

step1() {
	echo "Installing OpenCV & Required Python Libaries..."
	sudo apt update && sudo apt install libzbar-dev libzbar0 cmake -y && pip install -r requirements.txt && echo "Installed Successfully OpenCV & Required Python Libraries" && step2 || echo "Failed to install OpenCV & Required Libaries" && exit 1
	}

step2() {
	echo "Installing 'XAMPP' Server for Raspberry Pi"
	sudo apt install apache2 php mariadb-server php-mysql -y && echo "Installed XAMPP Server for Raspberry Pi" && echo "Setup MySQL" && sudo mysql_secure_installation && step3 || echo "Failed to install XAMPP Server for Raspberry Pi" && exit 1
	}

step3() {
	echo "Installing PhpMyAdmin"
	sudo apt install phpmyadmin -y && echo "Installed PhpMyAdmin" && echo "Setup MySQL" && sudo phpenmod mysqli && step4 || echo "Failed to install PhpMyAdmin" && exit 1
	}

step4() {
	echo "Restarting Apache2 Server"
	sudo service apache2 restart
	step5
	}

step5() {
  echo "Installing Service File for Automated Bookings Delete..."
  sudo cp installation_files/auto_delete_old_booking.service /etc/systemd/system/auto_delete_old_booking.service && echo "Successfully Installed Service File for Automated Booking Delete." && echo "Starting Service" && sudo systemctl start auto_delete_old_booking && echo   "Enabling Service" && sudo systemctl enable auto_delete_old_booking && step6 || echo "Failed to install service file for automated booking delete" && exit 1
	}
 
step6() {
  echo "Starting PiGPIO Daemon Service..."
  sudo systemctl start pigpiod && sudo systemctl enable pigpiod && echo "Started PiGPIO Daemon Service" || echo "Failed to start PiGPIO Daemon Service" && exit 1


step1

echo "Done..."
