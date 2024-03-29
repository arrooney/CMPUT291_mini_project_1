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


	def __dictionary_factory__(self, cursor, row):
    		# From lab notes - credit goes to TA's
		dict = {}
		for i, col in enumerate(cursor.description):
			dict[col[0]] = row[i]
		return dict


	""" Open the connection to the database file at <path> """
	def __openConn__(self):
		# open a database connection
		try:
			self.conn = sqlite3.connect(self.path)
			# add row factory function for ease of development
			self.conn.row_factory = self.__dictionary_factory__
		except Exception as e:
			print('Error inside __openConn__(): ' + str(e))


	""" Check that the connection is still valid """
	def checkConn(self):
		if self.conn == None:
			self.__openConn__()


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
		
		c.execute("SELECT max(births.regno) as maxReg from births")
		result = c.fetchone()['maxReg']
		regno = 0 if (result == None) else int(result) + 1
		# insert the values
		
		c.execute("INSERT INTO births VALUES(?,?,?,?,?,?,?,?,?,?)",\
			(regno, fname, lname, regdate, regplace, gender, f_fname, f_lname, m_fname, m_lname))
		result = c.fetchone()

		# close connection
		self.conn.commit()
		return True
	

	""" Make an entry to the marriage table """
	def registerMarriage(self, regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname):
		self.checkConn()
		c = self.conn.cursor()
		
		if not self.getPersonInfo(p1_fname, p1_lname) or not self.getPersonInfo(p2_fname, p2_lname):
			# Ethier partner does not exist in this case, the user needs to give the information
			print "One of these partners aren't registered"
			return False
		try:
			c.execute("SELECT max(marriages.regno) as maxReg from marriages")
			result = c.fetchone()['maxReg']
			regno = 0 if (result == None) else int(result) + 1
			# insert the values
			
			c.execute("INSERT INTO marriages VALUES(?,?,?,?,?,?,?)",\
				(regno, regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname))
			result = c.fetchone()

			# close connection
			self.conn.commit()
		except Exception as e:
			print('Error inside registerMarriage(): ' + str(e))
		return True



	""" Get info for a given marriage """
	def getMarriageInfo(self, p1_fname, p1_lname, p2_fname, p2_lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM marriages WHERE (p1_fname=? COLLATE NOCASE AND p1_lname=? COLLATE NOCASE AND p2_fname=? COLLATE NOCASE AND p2_lname=? COLLATE NOCASE)\
			OR (p2_fname=? COLLATE NOCASE AND p2_lname=? COLLATE NOCASE AND p1_fname=? COLLATE NOCASE AND p1_lname=? COLLATE NOCASE)",\
			(p1_fname, p1_lname, p2_fname, p2_lname, p1_fname, p1_lname, p2_fname, p2_lname))
		result = c.fetchall()

		if result == []:
			return False
		else: return result


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

	
	def getVehicleInfo(self, vin):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM vehicles WHERE vin=?", (vin,))
		result = c.fetchall()

		if result == []:
			return False
		else:
			return result


	""" get registration info from vin output sorted by date """
	def getVehicleRegByVIN(self, vin):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM registrations WHERE vin=? COLLATE NOCASE ORDER BY date(regdate) DESC",\
			(vin,))
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
			c.execute("SELECT max(registrations.regno) as maxReg from registrations")
			result = c.fetchone()['maxReg']
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
	

	""" Make an entry to the tickets table """
	def processPayment(self, tno, pdate, amount):
		self.checkConn()
		c = self.conn.cursor()
		
		c.execute("INSERT INTO payments VALUES(?, ?, ?)",\
			(tno, pdate, amount))
		
		self.conn.commit()
		return True 
	

	""" get ticket info for a given ticket no. """
	def getTicketNumber(self, tno):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT * FROM tickets WHERE tno=?", (tno,))
		result = c.fetchall()

		if result == []:
			return False
		else:
			return result


	""" Get ctital count of tickets """
	def getTicketTotal(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("\
		SELECT count(tno) as numTickets\
		FROM tickets r, registrations t WHERE r.regno = t.regno\
		and fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE", (fname, lname))
		result = c.fetchall()
		try:
			int(result[0]['numTickets'])
		except:
			return 0
		return int(result[0]['numTickets'])


	""" Get count of tickets from the last two years """
	def getTicketTotalLast2(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("\
		SELECT count(tno) as numTickets\
		FROM tickets r, registrations t\
		WHERE r.regno = t.regno and fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE\
		and vdate > date('now', '-2 year')", (fname, lname))
		result = c.fetchall()
		try:
			int(result[0]['numTickets'])
		except:
			return 0
		return int(result[0]['numTickets'])

	
	""" Get unordered ticket info for a given person """
	def getTicketInfo(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("\
		select t.tno, t.vdate, t.violation, t.fine, r.regno, v.make, v.model\
		from tickets t, registrations r, vehicles v\
		where t.regno = r.regno and v.vin = r.vin\
		and fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE", (fname, lname))
		result = c.fetchall()
		if result == []:
			return False
		else:
			return result


	""" Get the info for the tickets issued to a given person, ordered by date  """
	def getTicketInfoOrdered(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("\
		select t.tno, t.vdate, t.violation, t.fine, r.regno, v.make, v.model\
		from tickets t, registrations r, vehicles v\
		where t.regno = r.regno and v.vin = r.vin\
		and fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE\
		order by t.vdate", (fname, lname))
		result = c.fetchall()
		if result == []:
			return False
		else:
			return result


	""" Add a new entry to the ticket table """
	def issueTicket(self, regno, fine, violation, vdate):
		self.checkConn()
		c = self.conn.cursor()
		try:
			# get new ticket key
			# this will always be the max (see proof by contradiction)
			c.execute("SELECT max(tno) as maxTno from tickets")
			result = c.fetchone()['maxTno']
			tno = 0 if (result == None) else int(result) + 1
			c.execute("INSERT INTO tickets VALUES (?,?,?,?,?)",\
				(tno, regno, fine, violation, vdate))
			self.conn.commit()
		except Exception as e:
			print('Error inside issueTicket(): ' + str(e))
			return False
		return True


	""" Get the total number of demerit notices for a person """
	def getDemeritCount(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("\
		SELECT count(*) as allNotices\
		FROM demeritNotices\
		WHERE fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE", (fname, lname))
		result = c.fetchall()
		try:
			int(result[0]['allNotices'])
		except:
			return 0
		return int(result[0]['allNotices'])


	""" Get the number of demerit notices for a person from the last two years """
	def getDemeritCountLast2(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("\
		SELECT count(*) as allNotices\
		FROM demeritNotices\
		WHERE fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE\
		and ddate > date('now', '-2 year')", (fname, lname))
		result = c.fetchall()
		try:
			int(result[0]['allNotices'])
		except:
			return 0
		return int(result[0]['allNotices'])


	""" Get the total number of demerit poits for a given driver """
	def getDemeritPoints(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("\
		SELECT sum(points) as totalPoints\
		FROM demeritNotices WHERE fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE", (fname, lname))
		result = c.fetchall()
		try:
			int(result[0]['totalPoints'])
		except:
			return 0
		return int(result[0]['totalPoints'])


	""" Get the number of demerit points for a given person from the last two years. """
	def getDemeritPointsLast2(self, fname, lname):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("\
		SELECT sum(points) as totalPoints\
		FROM demeritNotices WHERE fname = ? COLLATE NOCASE and lname = ? COLLATE NOCASE\
		and ddate > date('now', '-2 year')", (fname, lname))
		result = c.fetchall()
		try:
			int(result[0]['totalPoints'])
		except:
			return 0
		return int(result[0]['totalPoints'])


	def getAmountPaid(self, tno):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT sum(amount) as totalAmount FROM payments WHERE tno=?", (tno,))
		result = c.fetchall()
		try:
			int(result[0]['totalAmount'])
		except:
			return 0
		return int(result[0]['totalAmount'])


	def getFineAmount(self, tno):
		self.checkConn()
		c = self.conn.cursor()
		c.execute("SELECT fine FROM tickets WHERE tno=?", (tno,))
		result = c.fetchall()
		try:
			int(result[0]['fine'])
		except:
			return 0
		return int(result[0]['fine'])

	
	""" Given one or more of make, model, year, colour, or plate, this funciton returns regristration
	 joined with vehicles for the most recent owner of the vehicle. Vehicles with no registrations are not
	 Included. """
	def getCarInfoList(self, make = None, model = None, year = None, color = None, plate = None):
		self.checkConn()
		c = self.conn.cursor()

		#query string to select all attributes of the car
		query = "SELECT v.make, v.model, v.year, v.color, v.vin, r.plate, r.regdate, r.expiry, r.fname, r.lname\
				FROM vehicles v, registrations r\
				WHERE r.vin=v.vin and "

		values = []
		valuesList = []

		#user selected attributes to search for the owner
		if make != None:
			values.append("make=? COLLATE NOCASE")
			valuesList.append(make)
		if model != None:
			values.append("model=? COLLATE NOCASE")
			valuesList.append(model)
		if year != None:
			values.append("year=?")
			valuesList.append(year)
		if color != None:
			values.append("color=? COLLATE NOCASE")
			valuesList.append(color)
		if plate != None:
			values.append("plate=? COLLATE NOCASE")
			valuesList.append(plate)
		separator = " and "
	  	queryString = separator.join(values)

		#checking if any arguments are empty
		if values == []:
			print "Please provide arguments"
			return

		#joining queries and where clauses with a group by key clause
		fullQuery = query + queryString +\
			" GROUP BY v.make, v.model, v.year, v.color, v.vin, r.plate, r.regdate, r.expiry, r.fname, r.lname\
			HAVING date(r.regdate) = (select max(date(r1.regdate)) from registrations r1 where r1.vin=r.vin)"
		
		#executing the query
		c.execute(fullQuery, tuple(valuesList))
      	
		#fetching the query results
		result = c.fetchall()
  
		return result


""" main for testing purposes """
def main():
	# test register births regno, fine, violation, vdate
	db = Database("miniProj.db")
	print db.getVehicleRegByVIN("U508")
	#print db.getVehicleReg(300)
	#print db.getAmountPaid(400)
	db.getCarInfoList(make="Chevrolet", color="red")
	db.close()


if __name__ == '__main__':
    main()