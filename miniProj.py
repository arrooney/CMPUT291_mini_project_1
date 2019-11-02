import os, sys, tty, termios, time, signal, re
from transactions import Database
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


# globals
users = None
db = None
clear = lambda: os.system('clear')


def registryMainMenu():
	# main menu for a registry agen
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
			""" Main menu options """
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
			elif selection == 6:
				getDriverAbstract()
			elif selection == 7:
				break
	return


def officerMainMenu():
	# main menu for a user of type 'Officer'
	while True:
		prettyPrint("Select an action:")
		menuSelect = raw_input("[1] Issue a ticket\n[2] Find a car owner\n[3] Quit\n->")
		if not menuSelect.isdigit():
			print "Please choose a number from the menu:"
		elif int(menuSelect) < 1 or int(menuSelect) > 3:
			print "Please select a number 1-7"
		else:
			# input is valid, continue
			selection = int(menuSelect)
			""" Main goal is to uncomment each of these """
			if selection == 1:
				issueTicket()
			elif selection == 2:
			 	findCarOwner()
			if selection == 3:
				break
	return


def issueTicket():
	prettyPrint("Issue a Ticket")
	regno = raw_input("Enter registration number: ")
	owner = db.getVehicleReg(regno)
	while not owner:
		print "Something went wrong, check the registration number..."
		regno = raw_input("Enter registration number: ")
		owner = db.getVehicleReg(regno)
	owner = owner[0]
	vin = owner['vin']
	vehicleInfo = db.getVehicleInfo(vin)
	while not vehicleInfo:
		# vehicle listed under registration doesn't exist
		print "Sorry! Something went wrong..."
		return
	vehicleInfo = vehicleInfo[0]
	print "-- Owner Info --"
	print "Given name: " + owner['fname'] + "\nSurname: " + owner['lname'] +\
		"\nMake: " + vehicleInfo['make'] + "\nModel: " + vehicleInfo['model'] +\
		"\nYear: " + str(vehicleInfo['year']) + "\nColour: " + vehicleInfo['color'] +\
		"\nPlate: " + str(owner['plate'])
	print "--	--	--"

	# Validate selection
	if raw_input("Is this correct? (Y/N) ") in "nN":
		prettyPrint("Cancelled", 0.3)
		return 
	# this is the correct information, continue
	clear()
	vdate = getDate("Violation date (yyyy-mm-dd): ")
	violation = raw_input("Violation info: ")
	fine = numericInputRadix("Amount: ")
	if db.issueTicket(regno, fine, violation, vdate):
		# otherwise something went wrong, hard to know what
		prettyPrint("Success", 0.3)
	return


def processBOS():
	prettyPrint("Process Bill of Sale")
	vin = nonNullInput("Enter vehicle VIN: ")
	o_fname = nonNullInput("Current owner given name: ")
	o_lname = nonNullInput("Current owner surname: ")
	vehicle = db.getVehicleRegByVIN(vin, o_fname, o_lname)

	while not vehicle:
		print "Owner does not match VIN..."
		vin = nonNullInput("Enter vehicle VIN: ")
		o_fname = nonNullInput("Current owner given name: ")
		o_lname = nonNullInput("Current owner surname: ")
		vehicle = db.getVehicleRegByVIN(vin, o_fname, o_lname)
	vehicle = db.getVehicleRegByVIN(vin, o_fname, o_lname)[0]

	# set the current registration of the vehicle to expire today
	regno = vehicle['regno']
	vin = vehicle['vin'] # just so that the case is more consistent
	db.setRegistrationExpiry(regno, datetime.date(datetime.now()))
	p_fname = nonNullInput("Purchaser given name: ")
	p_lname = nonNullInput("Purchaser surname: ")
	plate = nonNullInput("New license plate: ")

	# create new registration with new name, same old VIN
	# regdate is today, and expiry is a year from now
	today = date.today()
	regdate = datetime.date(datetime.now()) # today
	expiry = date(today.year + 1, today.month, today.day) # year from now

	if not db.setNewRegistration(regdate, expiry, plate, vin, p_fname, p_lname):
		prettyPrint("Something went wrong")
		return
	prettyPrint("Success", 0.3)


def registerBirth():
	prettyPrint("Register a birth")
	print "Please supply the information...\n"
	fname = nonNullInput("Baby's given name: ")
	lname = nonNullInput("Baby's surname: ")
	if db.getPersonInfo(fname, lname):
		prettyPrint("This person already exists", 0.5)
		return
	gender = raw_input("Gender (M/F): ")
	while gender not in "mMfF" or len(gender) != 1:
		gender = raw_input("Gender (M/F): ")
	bdate = getDate("Date of birth (yyyy-mm-dd): ")
	bplace = nonNullInput("Place of birth: ")
	f_fname = nonNullInput("Father's first name: ")
	f_lname = nonNullInput("Father's last name: ")
	if not db.getPersonInfo(f_fname, f_lname):
		print "Father not found, please enter more info..."
		registerPerson(f_fname, f_lname)
	m_fname = nonNullInput("Mother's first name: ")
	m_lname = nonNullInput("Mother's last name: ")
	motherInfo = db.getPersonInfo(m_fname, m_lname)
	if not motherInfo:
		print "Mother not found, please enter more info..."
		registerPerson(m_fname, m_lname)
	# We should have mother info now!
	motherInfo = db.getPersonInfo(m_fname, m_lname)[0]
	# update the persons table - give baby same phone and address of mother
	registerPerson(fname, lname, bdate, bplace, motherInfo['address'], motherInfo['phone'], acceptNull=True)
	# update the births table:
	regdate = date.today()
	regplace = users['city'] # location of user
	db.registerBirth(fname, lname, gender, regdate, regplace, f_fname, f_lname, m_fname, m_lname)
	prettyPrint("Success", 0.3)


def getDriverAbstract():
	prettyPrint("Get a driver's abstract")
	fname = raw_input ("Enter the driver's first name: ")
	lname = raw_input ("Enter the driver's last name: ")
	person = db.getPersonInfo(fname, lname)
	while not person:
		print "Person not found..."
		fname = raw_input ("Enter the driver's first name: ")
		lname = raw_input ("Enter the driver's last name: ")
		person = db.getPersonInfo(fname, lname)
	print "Number of tickets obtained in total:", (db.getTicketTotal(fname, lname))
	print "Number of tickets obtained in the last 2 years:", (db.getTicketTotalLast2(fname, lname))
	print "Number of demerits obtained in total:", (db.getDemeritCount(fname, lname))
	print "Number of demerits obtained in the last 2 years:", (db.getDemeritCountLast2(fname, lname))
	print "Number of demerit points obtained in total:", (db.getDemeritPoints(fname, lname))
	print "Number of demerit points obtained in the last 2 years:", (db.getDemeritPointsLast2(fname, lname))
	tickNum = 1
	viewChoice = raw_input("Would you like to view the tickets ordered by date? (y/n)")
	while True:
		if viewChoice == 'n':
			tickets = db.getTicketInfo(fname, lname)
			break
		elif viewChoice == 'y':
			tickets = db.getTicketInfoOrdered(fname, lname)
			break
		else:
			viewChoice = raw_input("Please enter y or n!")
	if not db.getTicketInfo(fname, lname):
		print "No tickets were found!"
	else:
		sub_list = [tickets[x:x+5] for x in xrange(0, len(tickets), 5)]
		clear()
		for tickets in sub_list:
			for ticket in tickets:
				print ("")
				print "Info for ticket", tickNum
				tickNum+=1
				for k, v in ticket.iteritems():
					print k, ":", v, ',',
			print ("")
			raw_input("Press enter to see 5 more"),


def registerMarriage():
	prettyPrint("Register a marriage")
	print "Please input the partners...\n"
	# get partner one details...
	p1_fname = nonNullInput("Partner 1's first name: ")
	p1_lname = nonNullInput("Partner 1's last name: ")
	if not db.getPersonInfo(p1_fname, p1_lname):
		print "Partner 1 is not in the database, please enter more info..."
		registerPerson(p1_fname, p1_lname) 
	# get partner 2 details...
	p2_fname = nonNullInput("Partner 2's first name: ")
	p2_lname = nonNullInput("Partner 2's last name: ")
	if not db.getPersonInfo(p2_fname, p2_lname):
		print "Partner 2 is not in the database, please enter more info..."
		registerPerson(p2_fname, p2_lname) 

	# update the marriages table:
	regdate = date.today()
	regplace = users['city'] # location of user
	if db.getMarriageInfo(p1_fname, p1_lname, p2_fname, p2_lname):
		prettyPrint("Union already exists", 0.5)
		return
	db.registerMarriage(regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname)
	prettyPrint("Success", 0.5)


def registerPerson(fname=None, lname=None, bdate=None, bplace=None, address=None, phone=None, acceptNull=False):
	# TODO: let values be null
	if fname == None and not acceptNull:
		prettyPrint("Register a person")
		fname = nonNullInput("Enter first name: ")
	if lname == None and not acceptNull:
		lname = nonNullInput("Enter last name: ")
	if bdate == None and not acceptNull:
		bdate = getDate("Date of birth: ")
	if bplace == None and not acceptNull:
		bplace = maybeNullInput("Place of birth: ")
	if address == None and not acceptNull:
		address = maybeNullInput("Address: ")
	if phone == None and not acceptNull:
		phone = phoneInput("Phone: ")
	db.setPersonInfo(fname, lname, bdate, bplace, address, phone)


def renewRegistration():
    #Input of registraion number for vehicle
    prettyPrint("Renew a Registration")
    print "Please supply the information..."
    regno = integerInput("Registration Number of Vehicle: ")
    ticket = db.getVehicleReg(regno)
    while not db.getVehicleReg(regno):
        print "Vehicle Registration Number not found..."
        regno = raw_input("Registration Number of Vehicle: ")
    
    vehicle = db.getVehicleReg(regno)[0]
    
    #getting expiry date for vehicle and todays date
    expiry = datetime.strptime(vehicle['expiry'], "%Y-%m-%d").date()
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
    prettyPrint("success")
    print "Your new vehicle registration expiry date is " + str(expiry) + "."
    time.sleep(1)


def processPayment():
	prettyPrint("Process a payment")
	tno = raw_input("Ticket Number: ")
	ticket = db.getTicketNumber(tno)
	while not ticket:
		print "Ticket Number not found..."
		tno = raw_input("Ticket Number: ")
		ticket = db.getTicketNumber(tno)
	payment = numericInputRadix("Please enter the amount to be paid: ")
	while int(payment) + db.getAmountPaid(tno) > db.getFineAmount(tno):
		print "You have paid more than the fine amount, please try again"
		payment = raw_input("Please enter the amount to be paid: ")
	db.processPayment(tno, date.today(), payment)


def findCarOwner():
    prettyPrint("Find Car Owner")
    print "Please supply the information..."
 
	#taking input of the columns to search for
    make_car = maybeNullInput("Enter the make of the Car: ")
    model_car = maybeNullInput("Enter the model of the Car: ")
    year_car = maybeNullInput("Enter the year of the Car: ")
    color_car = maybeNullInput("Enter the color of the Car: ")
    plate_car = maybeNullInput("Enter the plate of the Car: ")
    if make_car == None and model_car == None and year_car == None and color_car == None and plate_car == None:
    		prettyPrint("No information provided", 0.5)
    		return
    #calling function to get the result from the query
    cars = db.getCarInfoList(make_car, model_car, year_car, color_car, plate_car)
    
    #getting the length of the list i.e all the results
    length_results = len(cars)
    
    #printing the results found on screen
    if length_results >= 4:
        for i in range(length_results):
            
            print "\n\nCar Number " + str(i+1) + "\n"
            
            for key in cars[i]:
                
                if key == 'make' or key == 'model' or key == 'year' or key == 'color' or key == 'vin':
					print key + ":" + str(cars[i][key]),
   
    
	#nonNullInput("Please enter the ")
    time.sleep(30)
    


def getDate(prompt):
    #TODO: check for date semantics
	bdate = raw_input(prompt)
	if bdate == "":
		bdate = None
		return bdate
	while not re.search("^[0-9]{4,}-[0-9]{2,}-[0-9]{2,}$", bdate):
		bdate = raw_input(prompt)
	return bdate


def numericInputRadix(prompt):
	# validate numeric input with decimal point
	numeric = raw_input(prompt)
	while not re.search("^[0-9]+.?[0-9]*$", numeric):
		numeric = raw_input(prompt)
	return numeric


def phoneInput(prompt):
	# validate a phone number with some regex
	# it can, in general, be null
	phone = raw_input(prompt)
	if phone == "":
		phone = None
		return phone
	while not re.search("^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$", phone):
		phone = raw_input(prompt)
	return phone


def integerInput(prompt):
	integer = raw_input(prompt)
	while not re.search("^[0-9]+$", integer):
		integer = raw_input(prompt)
	return integer


def nonNullInput(prompt):
	# enforce that something (anything) be input
	inp = raw_input(prompt)

	while inp == "":
		print "Please provide input"
		inp = raw_input(prompt)
	return inp


def maybeNullInput(prompt):
	# return null if string is empty
	inp = raw_input(prompt)
	if inp == "":
		inp = None
	return inp


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
		# the following is a little extra safety for passwords (although, placeholders should protect from injections)
		if users and re.search("^[a-zA-Z!@#$%\\^&*()1-9]*$", userName) and re.search("^[a-zA-Z!@#$%\\^&*()1-9]*$", password):
			return
		else:
			prettyPrint("Incorrect", 0.3)


def prettyPrint(output, timeout=0):
	# output a nice header, with an optional timeout parameter
	clear()
	print "====================================="
	print "\t" + output
	print "====================================="
	time.sleep(timeout)


def getch():
	# this code is based on the following stack overflow posting
	# https://stackoverflow.com/questions/27631629/masking-user-input-in-python-with-asterisks
	# allows us to get input without displaying it
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def receiveSignal(signalNumber, frame):
	# handle a ^C signal - this puts the user back at the sign in screen
    prettyPrint("Cancelled", 0.3)
    os.execl(sys.executable, sys.executable, *sys.argv)
    return


def main():
	# validate database file, and disbatch based on user type
	if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
		print "Please supply valid database file name!"
		return

	global db
	db = Database(sys.argv[1])
	# validate the user
	passwordAuth()
	# to get here, user has signed in successfully
	prettyPrint("Welcome, " + users['uid'] + " (" + users['fname'] + " "  + users['lname'] + ")", 0.5)
	userType = users['utype']
	if userType == 'a':
		# user is an agent
		registryMainMenu()
	elif userType == 'o':
		# user is an officer
		officerMainMenu()
	else:
		prettyPrint("Something went wrong: invalid user type '" + userType + "'" , 1)

	# transactions finished, close DB
	db.close()
	return


if __name__ == "__main__":
	signal.signal(signal.SIGINT, receiveSignal)
	main()
