import sqlite3
path = './miniProj.db'

def cereateConn():
	try:
		conn = sqlite3.connect(path)
	except e:
		print e
	return conn

def registerBirth(fname, lname, gender, regdate, bplace, f_fname, f_lname, m_fname, m_lname):
	conn = cereateConn()
	c = conn.cursor()
	# get the next sequential regno
	c.execute("SELECT max(births.regno) from births")
	result = c.fetchone()[0]
	regno = 0 if (result == None) else int(result) + 1
	# insert the values
	c.execute("INSERT INTO births VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",\
		(regno, fname, lname, regdate, bplace, gender, f_fname, f_lname, m_fname, m_lname))
	# close connection
	conn.commit()
	conn.close()


def main():
	# test register births
	registerBirth("sd", "asdf", "m", "2019-10-25", "daf", "sdf", "sdf", "das", "asdf")
	registerBirth("sd", "asdf", "m", "2019-10-25", "daf", "sdf", "sdf", "das", "asdf")

if __name__ == '__main__':
    main()