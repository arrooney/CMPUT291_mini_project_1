import os, sys, tty, termios, time, signal
from transactions import Database
from datetime import date
users = None
clear = lambda: os.system('clear')
db = None

def mainMenu():
	while True:
		prettyPrint("Select an action:")
		menuSelect = raw_input("[1] Register a birth\n[2] Register a marriage\n[3] Renew a vehicle registration\n[4] Process a bill of sale\n[5] Process a payment\n[6] Get a driver abstract\n[7] Quit\n->")
		if not menuSelect.isdigit():
			print "Please choose a number from the menu:"
		elif int(menuSelect) < 1 or int(menuSelect) > 7:
			print "please select a number 1-7"
		else:
			# input is valid, continue
			selection = int(menuSelect)

			""" Main goal is to uncomment each of these """
			if selection == 1:
				registerBirth()
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
			elif selection == 7:
				break
	return

def registerBirth():
	prettyPrint("Register a birth")
	print "Please supply the information...\n"
	fname = raw_input("Baby's given name: ")
	lname = raw_input("Baby's surname: ")
	gender = raw_input("Gender (M/F): ")
	while gender not in "mMfF" or len(gender) > 1:
		gender = raw_input("Gender (M/F): ")
	bdate = raw_input("Date of birth: ")
	bplace = raw_input("Place of birth: ")
	f_fname = raw_input("Father's first name: ")
	f_lname = raw_input("Father's last name: ")
	if not db.getPersonInfo(f_fname, f_lname):
		print "Father not found, please enter more info..."
		registerPerson(f_fname, f_lname)
	m_fname = raw_input("Mother's first name: ")
	m_lname = raw_input("Mother's last name: ")
	motherInfo = db.getPersonInfo(m_fname, m_lname)
	if not motherInfo:
		print "Mother not found, please enter more info..."
		registerPerson(m_fname, m_lname)
	# We should have mother info now!
	motherInfo = db.getPersonInfo(m_fname, m_lname)[0]
	# update the persons table - give baby same phone and address of mother
	if not db.getPersonInfo(fname, lname):
		registerPerson(fname, lname, bdate, bplace, motherInfo[4], motherInfo[5])
	# update the births table:
	regdate = date.today()
	regplace = "Edmonton" # this should actually be the place of the user
	db.registerBirth(fname, lname, gender, regdate, regplace, f_fname, f_lname, m_fname, m_lname)
	prettyPrint("Success!")


def registerPerson(fname=None, lname=None, bdate=None, bplace=None, address=None, phone=None):
	if fname == None:
		prettyPrint("Register a person")
		fname = raw_input("Enter first name: ")
	if lname == None:
		lname = raw_input("Enter last name: ")
	if bdate == None:
		bdate = raw_input("Date of birth: ")
	if bplace == None:
		bplace = raw_input("Place of birth: ")
	if address == None:
		address = raw_input("Address: ")
	if phone == None:
		phone = raw_input("Phone: ")
	db.setPersonInfo(fname, lname, bdate, bplace, address, phone)


def passwordAuth():
	while True:
		clear()
		userName = raw_input("Username: ")
		password = ''
		print "Password: ",
		while True:
			char = getch()
			if char == '\r':
				print ""
				break
			password += char
			sys.stdout.write('*')
		global users
		users = db.getUserInfo(userName, password)
		if users:
			return
		else:
			prettyPrint("Incorrect", 0.3)


def prettyPrint(output, timeout=0):
	clear()
	print "====================================="
	print "\t" + output
	print "====================================="
	time.sleep(timeout)


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

def receiveSignal(signalNumber, frame):
    prettyPrint("Cancelled", 0.3)
    os.execl(sys.executable, sys.executable, *sys.argv)
    return

def main():
	if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
		print "Please supply valid database file name!"
		return

	global db
	db = Database(sys.argv[1])
	passwordAuth()
	prettyPrint("Welcome, " + users[0], 1)
	mainMenu()
	db.close()
	return

if __name__ == "__main__":
	signal.signal(signal.SIGINT, receiveSignal)
	main()