import sqlite3
path = './miniProj.db'

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
	def __init__(self):
		# Initializing the class
		self.conn = None


	""" Open the connection to the database file at <path> """
	def openConn(self):
		# open a database connection
		try:
			self.conn = sqlite3.connect(path)
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


	""" Register a new birth - will auto increment the regno """
	def registerBirth(self, fname, lname, gender, regdate, regplace, f_fname, f_lname, m_fname, m_lname):
		self.checkConn()
		c = self.conn.cursor()
		# get the next sequential regno
		if not self.getPersonInfo(f_fname, f_lname) or not self.getPersonInfo(m_fname, m_lname):
			# one of the parents don't exist - this shold prompt user to enter them
			print "One of these parents aren't registered"
			return False
		c.execute("SELECT max(births.regno) from births")
		result = c.fetchone()[0]
		regno = 0 if (result == None) else int(result) + 1
		# insert the values
		c.execute("INSERT INTO births VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",\
			(regno, fname, lname, regdate, regplace, gender, f_fname, f_lname, m_fname, m_lname))
		result = c.fetchone()
		print result
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


	""" Given the first and last name, fine the info for a given person, return False if they
		don't yet exist in the DB """
	def getPersonInfo(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM persons WHERE fname=? AND lname=?", (fname, lname))
		result = c.fetchall()

		if result == []:
			return False
		else: return result


""" main for testing purposes """
def main():
	# test register births
	db = Database()
	print "asdf"
	db.registerBirth("sd", "asdf", "m", "2019-10-25", "daf", "sdf", "sdf", "das", "asdf")
	db.registerBirth("sd", "asdf", "m", "2019-10-25", "daf", "sdf", "sdf", "das", "asdf")
	print db.getPersonInfo("sam", "smith")
	db.close()

if __name__ == '__main__':
    main()