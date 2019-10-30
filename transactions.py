import sqlite3


"""
Class: Database
	API
		-At the top of any new function being created, call the self.checkConn() funciton
		that will check that the connection is still valid.
		-At the end of the function, call self.conn.commit() to commit changes to DB.
		-When using an instatiation of the class, be sure to call the close() method when all
		transactions are finished
"""
class Database(object):

	""" Constructor """
	def __init__(self, dbfile):
		# Initializing the class
		self.conn = None
		self.path = dbfile


	""" Open the connection to the database file at <path> """
	def openConn(self):
		# open a database connection
		try:
			self.conn = sqlite3.connect(self.path)
		except Exception as e:
			print('Error inside openConn(): ' + str(e))


	""" Check that the connection is still valid """
	def checkConn(self):
		if self.conn == None:
			self.openConn()


	""" Close the connection at the end of the program """
	def close(self):
		self.conn.commit()
		self.conn.close()


	""" Get all of the user info from the DB """
	def getUserInfo(self, username, password):
		self.checkConn()
		c = self.conn.cursor()

		try:
			c.execute("SELECT * FROM users WHERE pwd=? AND uid=? COLLATE NOCASE",\
				(password, username))
			result = c.fetchone()
			self.conn.commit()
		except Exception as e:
			# assume that there is no such user - it could have been
			# some other failure, but it's safe to treat any failure the same.
			return False
		if result != []:
			return result
		return False


	""" Register a new birth - will auto increment the regno """
	def registerBirth(self, fname, lname, gender, regdate, regplace, f_fname, f_lname, m_fname, m_lname):
		self.checkConn()
		c = self.conn.cursor()
		
		# get the next sequential regno
		if not self.getPersonInfo(f_fname, f_lname) or not self.getPersonInfo(m_fname, m_lname):
			# one of the parents don't exist - this shold prompt user to enter them
			# user should implement checks so that this never actually happens though
			print "One of these parents aren't registered"
			return False
		
		c.execute("SELECT max(births.regno) from births")
		result = c.fetchone()[0]
		regno = 0 if (result == None) else int(result) + 1
		# insert the values
		
		c.execute("INSERT INTO births VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",\
			(regno, fname, lname, regdate, regplace, gender, f_fname, f_lname, m_fname, m_lname))
		result = c.fetchone()

		# close connection
		self.conn.commit()
		return True
	

	def registerMarriage(self, regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname):
		self.checkConn()
		c = self.conn.cursor()
		
		if not self.getPersonInfo(p1_fname, p1_lname) or not self.getPersonInfo(p2_fname, p2_lname):
			# Ethier partner does not exist in this case, the user needs to give the information
			print "One of these partners aren't registered"
			return False
		
		c.execute("SELECT max(marriages.regno) from marriages")
		result = c.fetchone()[0]
		regno = 0 if (result == None) else int(result) + 1
		# insert the values
		
		c.execute("INSERT INTO marriages VALUES(?, ?, ?, ?, ?, ?, ?)",\
			(regno, regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname))
		result = c.fetchone()

		# close connection
		self.conn.commit()
		return True


	""" Add a new person to the DB """
	def setPersonInfo(self, fname, lname, bdate, bplace, address, phone):
		self.checkConn()
		c = self.conn.cursor()
		
		try:
			c.execute("INSERT INTO persons VALUES (?,?,?,?,?,?)",\
				(fname, lname, bdate, bplace, address, phone))
			self.conn.commit()
		except Exception as e:
			print('Error inside setPersonInfo(): ' + str(e))


	""" Given the first and last name, find the info for a given person, return False if they
		don't yet exist in the DB """
	def getPersonInfo(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM persons WHERE fname=? COLLATE NOCASE AND lname=? COLLATE NOCASE", (fname, lname))
		result = c.fetchall()

		if result == []:
			return False
		else: return result


	""" get registration info from a given regno """
	def getVehicleReg(self, regno):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM registrations WHERE regno=?", (regno,))
		result = c.fetchall()

		if result == []:
			return False
		else:
			return result

	
	""" get registration info from vin, fname and lname - this is a 
	valid candidate key  """
	def getVehicleRegByVIN(self, vin, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM registrations WHERE vin=? COLLATE NOCASE AND fname=? COLLATE NOCASE AND lname=? COLLATE NOCASE",\
			(vin, fname, lname))
		result = c.fetchall()

		if result == []:
			return False
		else:
			return result

	
	""" insert a new entry to registrations table - automatically increment the regno """
	def setNewRegistration(self, regdate, expiry, plate, vin, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		try:
			c.execute("SELECT max(registrations.regno) from registrations")
			result = c.fetchone()[0]
			regno = 0 if (result == None) else int(result) + 1
			c.execute("INSERT INTO registrations VALUES (?,?,?,?,?,?,?)",\
				(regno, regdate, expiry, plate, vin, fname, lname))
			self.conn.commit()
		except Exception as e:
			print('Error inside setNewRegistration(): ' + str(e))
			return False
		return True


	""" update the expiry on a given registration entry """
	def setRegistrationExpiry(self, regno, expiry):
		self.checkConn()
		c = self.conn.cursor()
		try:
			c.execute("UPDATE registrations SET expiry=? WHERE regno=?", (expiry, regno))
			self.conn.commit()
		except Exception as e:
			print('Error inside setRegistrationExpiry(): ' + str(e))
			return False
		return True
	

	def processPayment(self, tno, pdate, amount):
		self.checkConn()
		c = self.conn.cursor()
		
		c.execute("INSERT INTO payments VALUES(?, ?, ?)",\
			(tno, pdate, amount))
		
		self.conn.commit()
		return True 
	

	def getTicketNumber(self, tno):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM tickets WHERE tno=?", (tno,))
		result = c.fetchall()

		if result == []:
			return False
		else:
			return result


	def getTicketTotal(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT count(tno) FROM tickets r, registrations t WHERE r.regno = t.regno and fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE", (fname, lname))
		result = c.fetchall()
		try:
			int(result[0][0])
		except:
			return 0
		return int(result[0][0])


	def getAmountPaid(self, tno):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT sum(amount) FROM payments WHERE tno=?", (tno,))
		result = c.fetchall()
		try:
			int(result[0][0])
		except:
			return 0
		return int(result[0][0])


	def getFineAmount(self, tno):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT fine FROM tickets WHERE tno=?", (tno,))
		result = c.fetchall()
		try:
			int(result[0][0])
		except:
			return 0
		return int(result[0][0])


""" main for testing purposes """
def main():
	# test register births
	db = Database("miniProj.db")
	print db.getVehicleReg(746328)
	db.close()


if __name__ == '__main__':
    main()