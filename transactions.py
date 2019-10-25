import sqlite3
path = './miniProj.db'

def cereateConn():
	try:
		conn = sqlite3.connect(path)
	except e:
		print e
	return (conn, conn.cursor())

def registerBirth(fname, lname, gender, regdate, bplace, f_fname, f_lname, m_fname, m_lname):
	conn, c = cereateConn()
	# get the next sequential regno
	if !(getPersonInfo("f_fname", "f_lname") or getPersonInfo("m_fname", "m_lname")):
		# one of the parents don't exist - this shold prompt user to enter them
		return False
	c.execute("SELECT max(births.regno) from births")
	result = c.fetchone()[0]
	regno = 0 if (result == None) else int(result) + 1
	# insert the values
	c.execute("INSERT INTO births VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",\
		(regno, fname, lname, regdate, bplace, gender, f_fname, f_lname, m_fname, m_lname))
	# close connection
	conn.commit()
	conn.close()
	return True

def getPersonInfo(fname, lname):
	conn, c = cereateConn()
	c.execute("SELECT * FROM persons WHERE fname=? AND lname=?", (fname, lname))
	result = c.fetchall()
	print result
	if result == []:
		return False
	else: return result



def main():
	# test register births
	registerBirth("sd", "asdf", "m", "2019-10-25", "daf", "sdf", "sdf", "das", "asdf")
	registerBirth("sd", "asdf", "m", "2019-10-25", "daf", "sdf", "sdf", "das", "asdf")
	getPersonInfo("sam", "smith")

if __name__ == '__main__':
    main()