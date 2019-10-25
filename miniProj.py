import sys, tty, termios, transactions
users = {"arrooney" : "password", "sudo" : "1234"}

def mainMenu():
	while True:
		print "Select an action:"
		menuSelect = raw_input("[1] Register a birth\n[2] Register a marriage\n[3] Renew a vehicle registration\n[4] Process a bill of sale\n[5] Process a payment\n[6] Get a driver abstract\n[7] Quit\n")
		if not menuSelect.isdigit():
			print "Please choose a number from the menu:"
		elif int(menuSelect) < 1 or int(menuSelect) > 7:
			print "please select a number 1-7"
		else:
			# input is valid, continue
			selection = int(menuSelect)
			# if selection == 1:
			# 	registerBirth()
			# elif selection == 2:
			# 	registerMarriage()
			# elif selection == 3:
			# 	renewRegistration()
			# elif selection == 4:
			# 	processBOS()
			# elif selection == 5:
			# 	processPayment()
			# elif selection == 6:
			# 	getDriverAbstract()
			if selection == 7:
				break
	return

def registerBirth():
	

def passwordAuth():
	while True:
		userName = raw_input("Username: ")
		if userName in users.keys():
			password = ''
			print "Password: ",
			while True:
			    char = getch()
			    if char == '\r':
			    	print ""
			        break
			    password += char
			    sys.stdout.write('*')
			if password == users[userName]:
				return
			else:
				print("Incorrect password")
		else:
			print("Incorrect username")		

def getch():
	# this code is based on the following stack overflow posting
	# https://stackoverflow.com/questions/27631629/masking-user-input-in-python-with-asterisks
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
	passwordAuth()
	mainMenu()
	return

if __name__ == "__main__":
	main()