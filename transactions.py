import sqlite3
path = './miniProj.db'

class Database(object):

	def __init__(self):
		# Initializing the class
		self.conn = None

	# def __del__(self):
	# 	self.conn.commit()
	# 	self.conn.close()

	def openConn(self):
		# open a database connection
		try:
			self.conn = sqlite3.connect(path)
		except Exception as e:
			print( 'Error inside openConn() : ' + str(e))

	def checkConn(self):
		if self.conn == None:
			self.openConn()

	def close(self):
		self.conn.commit()
		self.conn.close()

	def registerBirth(self, fname, lname, gender, regdate, regplace, f_fname, f_lname, m_fname, m_lname):
		self.checkConn()
		c = self.conn.cursor()
		# get the next sequential regno
		if not(self.getPersonInfo("f_fname", "f_lname") or self.getPersonInfo("m_fname", "m_lname")):
			# one of the parents don't exist - this shold prompt user to enter them
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
		#vself.conn.commit()
		#self.conn.close()
		return True

	def setPersonInfo(self, fname, lname, bdate, bplace, address, phone):
		self.checkConn()
		c = self.conn.cursor()
		try:
			c.execute("INSERT INTO persons VALUES (?,?,?,?,?,?)",\
				(fname, lname, bdate, bplace, address, phone))
		except Exception as e:
			print( 'Error inside setPersonInfo() : ' + str(e))


	def getPersonInfo(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM persons WHERE fname=? AND lname=?", (fname, lname))
		result = c.fetchall()

		if result == []:
			return False
		else: return result

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