"""
This is a working example of the active record pattern as applied to a simple
gradebook schema. This Python module has been created to supplement the talk
given by Chris Mitchell at the Oregon Academy of Sciences meeting on
2011-02-26. 

During the talk, the balance between simplicity and the DRY (do not repeat
yourself) principle was mentioned. This example showcases the DRY principle;
we have a superclass called ActiveRecord that uses metadata provided by
children classes (in class variables) so that the children classes
automatically get working generic methods. 

If we were to reimplement this using the simple approach, we'd reimplement all
of the ActiveRecord methods in each of the children classes, but without using
the class variables. That way, the parameterized SQL queries would be
completely hand-written and not procedurally generated. We could then remove
the ActiveRecord superclass.
"""
import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)

class Database(object):
	"""A helper class to maintain a database connection and execute queries."""
	def __init__(self, database_name):
		"""
		Create a Database object for interacting with the sqlite3 db file `database_name`. The Datbase object is automatically connected and ready to use.
		"""
		self.database_name = database_name
		self.con = self.connect()

	def init_db(self):
		""" 
		Set up the database with instructions from schema.sql and testdata.sql
		"""
		for filename in ["schema.sql", "testdata.sql"]:
			with open(filename) as f:
				self.con.cursor().executescript(f.read())

	def connect(self):
		"""Return a connection to the gradebook database"""
		connection = sqlite3.connect(self.database_name)
		# This row factory enables accessing row values by column-name
		connection.row_factory = sqlite3.Row
		# Default compiles of sqlite do not enforce foreign key constraints.
		# Since the gradebook schema uses foreign key constraints and the "ON
		# DELETE CASCADE" feature, we ensure constraint enforcement is on.
		connection.execute("PRAGMA foreign_keys=ON")
		return connection

	def close(self):
		self.con.commit()
		self.con.close()

	def execute(self, query, args=None, commit=False):
		"""
		Execute a query with the supplied query parameters.

		By default, we don't commit after each call to execute for performance
		reasons. By not committing, sqlite3 automatically creates and commits
		transactions when necessary (like before a SELECT statement).  This is
		very useful when doing many sequential AR saves because one big
		transaction is MUCH faster than many small transactions.
		"""
		cur = self.con.cursor()
		# Uncomment the following line to log to the screen the SQL that is executed
		logging.debug(str(query) + "; " + str(args))
		cur.execute(query, args or ())
		if commit:
			self.con.commit()
		return cur


class ActiveRecord(object):
	"""
	This superclass allows children AR classes to automatically get working
	generic methods like get(), all(), save(), etc, if they define the class
	variables describing the table.

	These class variables are _table_name, _column_names, and _default_order.
	_table_name is simply the name of the table in the database, _column_names
	is a list of the columns that should be part of the active record pattern
	(except for pk, which is assumed by this implementation of AR), and
	_default_order s a list of column names in the order that they should be
	applied for sorting lists of AR instances (like with .all()). Remember
	that this implementation of AR expects the primary key attribute of a
	table to be named 'pk'.
	"""
	_table_name = None
	_default_order = None
	_column_names = None

	def __init__(self, **kwargs):
		"""
		Create a new active record instance with the provided properties.

		Example: Student(first_name="Alan", last_name="Turning")
		"""
		if set(kwargs.keys()) - set(self._column_names + ['pk']):
			raise TypeError("{0} was given arguments for column names it does not know about.".format(self.__class__.__name__))
		for column in self._column_names + ['pk']:
			setattr(self, column, kwargs.get(column))
		self._in_db = False

	def __repr__(self):
		return "<{0}: {1}>".format(self.__class__.__name__, self.pk)

	@classmethod
	def _from_row(cls, row_dict):
		"""
		A convienence method for instantiating instances of an AR class
		from a row object from the database. The instance is automatically
		tagged as coming from the database.
		"""
		obj = cls(**row_dict)
		obj._in_db = True
		return obj

	@classmethod
	def get(cls, pk):
		"""Get a single AR instance for the row with the given pk"""
		query = "SELECT * FROM {0} WHERE pk=? LIMIT 1".format(cls._table_name)
		cur = db.execute(query, (pk, ))
		row = cur.fetchone()
		obj = cls._from_row(row)
		return obj

	@classmethod
	def where(cls, **kwargs):
		"""
		Like .all(), but one can add conditions to filter the results.

		Example: Grade.where(points=0)
		"""
		items = kwargs.items()
		columns = [i[0] for i in items]
		values = [i[1] for i in items]
		sql_conditions = '=? and '.join(columns) + '=?'
		query = "SELECT * FROM {0} WHERE {1}".format(cls._table_name,
				sql_conditions)
		cur = db.execute(query, values)
		rows = cur.fetchall()
		objs = [cls._from_row(row) for row in rows]
		return objs

	@classmethod
	def all(cls, order=None):
		"""
		Return a list of AR objects; one for each row in the table.
		
		The order of the list items can be changed by passing in a list of
		column names. Minus symbols may be prepended to the column names to
		change the direction of the sort.
		"""
		order = order or cls._default_order
		if order:
			query = "SELECT * FROM {0} ORDER BY {1} COLLATE NOCASE"
			query = query.format(cls._table_name, order)
		else:
			query = "SELECT * FROM {0}".format(cls._table_name)
		cur = db.execute(query)
		rows = cur.fetchall()
		objs = [cls._from_row(row) for row in rows]
		return objs

	def save(self):
		"""Save the AR instance back into the database."""
		if self._in_db:
			sql_attributes = '=?, '.join(self._column_names) + '=?'
			query = "UPDATE {} SET {} WHERE pk=?".format(self._table_name,
					sql_attributes)
			values = [getattr(self, attr) for attr in self._column_names] + [self.pk]
			db.execute(query, values)
		else:
			columns = ', '.join(self._column_names)
			placeholders = ', '.join(['?'] * len(self._column_names))
			values = [getattr(self, attr) for attr in self._column_names]
			query = "INSERT INTO {} ({}) VALUES ({})".format(self._table_name,
					columns, placeholders)
			cur = db.execute(query, values)
			self._in_db = True
			self.pk = cur.lastrowid

	def delete(self):
		"""Delete the corresponding row from the database"""
		if self._in_db:
			query = "DELETE FROM {0} WHERE pk=?".format(self._table_name)
			args = (self.pk, )
			db.execute(query, args)
			self._in_db = False
			self.pk = None


class Student(ActiveRecord):
	_table_name = 'student'
	_default_order = 'first_name, last_name, pk'
	_column_names = ['first_name', 'last_name', 'alias']

	@property
	def full_name(self):
		full_name = ' '.join([self.first_name, self.last_name])
		return full_name.strip()

	def get_grades(self):
		return Grade.where(student_pk=self.pk)


class Assignment(ActiveRecord):
	_table_name = 'assignment'
	_default_order = '-due_date, name, pk'
	_column_names = ['name', 'due_date', 'points']

	def get_grades(self):
		return Grade.where(assignment_pk=self.pk)


class Grade(ActiveRecord):
	# Note how just this table metadata is enough for the superclass to give
	# us a working active record class
	_table_name = 'grade'
	_default_order = 'pk'
	_column_names = ['student_pk', 'assignment_pk', 'points', 'comment']


db = Database('./gradebook.db')
db.connect()

if __name__ == '__main__':
	print "Remember to call db.close() when you're done so that any commands\
that weren't yet automatically committed will get commited."
