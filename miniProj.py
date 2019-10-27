import os, sys, tty, termios, time, signal, re
from transactions import Database
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


# globals
users = None
db = None
clear = lambda: os.system('clear')


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
			elif selection == 2:
				registerMarriage()
			elif selection == 3:
				renewRegistration()
			elif selection == 4:
				processBOS()
			elif selection == 5:
				processPayment()
			# elif selection == 6:
			# 	getDriverAbstract()
			elif selection == 7:
				break
	return


def processBOS():
	vin = raw_input("Enter vehicle VIN: ")
	o_fname = raw_input("Current owner given name: ")
	o_lname = raw_input("Current owner surname: ")
	vehicle = db.getVehicleRegByVIN(vin, o_fname, o_lname)
	while not vehicle:
		print "Owner does not match VIN..."
		vin = raw_input("Enter vehicle VIN: ")
		vehicle = db.getVehicleRegByVIN(vin, fname, lname)
	vehicle = db.getVehicleRegByVIN(vin, fname, lname)[0]
	# set the current registration of the vehicle to expire today
	db.setRegistrationExpiry(vehicle[0], datetime.date(datetime.now()))
	p_fname = raw_input("Purchaser given name: ")
	p_lname = raw_input("Purchaser surname: ")
	

def registerBirth():
	prettyPrint("Register a birth")
	print "Please supply the information...\n"
	fname = raw_input("Baby's given name: ")
	lname = raw_input("Baby's surname: ")
	gender = raw_input("Gender (M/F): ")
	while gender not in "mMfF" or len(gender) != 1:
		gender = raw_input("Gender (M/F): ")
	bdate = getDate("Date of birth (yyyy-mm-dd): ")
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
	regplace = users[5] # location of user
	db.registerBirth(fname, lname, gender, regdate, regplace, f_fname, f_lname, m_fname, m_lname)
	prettyPrint("Success!")

	
def registerMarriage():
	prettyPrint("Register a marriage")
	print "Please input the partners...\n"
	p1_fname = raw_input("Partner 1's first name: ")
	p1_lname = raw_input("Partner 1's last name: ")
	if not db.getPersonInfo(p1_fname, p1_lname):
		print "Partner 1 is not in the database, please enter more info..."
		gender = raw_input("Gender (M/F): ")
		while gender not in "mMfF" or len(gender) != 1:
			gender = raw_input("Gender (M/F): ")
		bdate = getDate("Date of birth (yyyy-mm-dd): ")
		bplace = raw_input("Place of birth: ")
		registerPerson(p1_fname, p1_lname, bdate, bplace) 

	p2_fname = raw_input("Partner 2's first name: ")
	p2_lname = raw_input("Partner 2's last name: ")
	if not db.getPersonInfo(p2_fname, p2_lname):
		print "Partner 2 is not in the database, please enter more info..."
		gender = raw_input("Gender (M/F): ")
		while gender not in "mMfF" or len(gender) != 1:
			gender = raw_input("Gender (M/F): ")
		bdate = getDate("Date of birth (yyyy-mm-dd): ")
		bplace = raw_input("Place of birth: ")
		registerPerson(p1_fname, p2_lname, bdate, bplace) 

	# update the marriages table:
	regdate = date.today()
	regplace = users[5] # location of user
	db.registerMarriage(regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname)
	prettyPrint("Success!")

def registerPerson(fname=None, lname=None, bdate=None, bplace=None, address=None, phone=None):
	if fname == None:
		prettyPrint("Register a person")
		fname = raw_input("Enter first name: ")
	if lname == None:
		lname = raw_input("Enter last name: ")
	if bdate == None:
		bdate = getDate("Date of birth: ")
	if bplace == None:
		bplace = raw_input("Place of birth: ")
	if address == None:
		address = raw_input("Address: ")
	if phone == None:
		phone = raw_input("Phone: ")
	db.setPersonInfo(fname, lname, bdate, bplace, address, phone)


def renewRegistration():
    #Input of registraion number for vehicle
    prettyPrint("Renew a Registration")
    print "Please supply the information..."
    regno = raw_input("Registration Number of Vehicle: ")
    ticket = db.getVehicleReg(regno)
    while not db.getVehicleReg(regno):
        print "Vehicle Registration Number not found..."
        regno = raw_input("Registration Number of Vehicle: ")
    
    vehicle = db.getVehicleReg(regno)[0]
    
    #getting expiry date for vehicle and todays date
    expiry = time.strptime(vehicle[2], "%d-%m-%Y")
    today = date.today()
    
    #checking if registration is expired
    is_expired = False
    if today >= expiry:
        is_expired = True
    
    #incrementing a year onto vehicle registration if registration has expired
    if is_expired:
    	expiry = today + relativedelta(years=1)
    else:
        expiry += relativedelta(years=1)
    
    #updating registration expiry
    db.setRegistrationExpiry(regno, expiry)


def processPayment():
	prettyPrint("Process a payment")
	tno = raw_input("Ticket Number: ")
	ticket = db.getTicketNumber(tno)
	while not ticket:
		print "Ticket Number not found..."
		tno = raw_input("Ticket Number: ")
		ticket = db.getTicketNumber(tno)
	payment = raw_input("Please enter the amount to be paid: ")
	while int(payment) + db.getAmountPaid(tno) > db.getFineAmount(tno):
		print "You have paid more than the fine amount, please try again"
		payment = raw_input("Please enter the amount to be paid: ")
	db.processPayment(tno, date.today(), payment)
	
def getDate(prompt):
    
    #check for date validity
    
	bdate = raw_input(prompt)
	while not re.search("^[0-9]{4,}-[0-9]{2,}-[0-9]{2,}$", bdate):
		bdate = raw_input(prompt)
	return bdate


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