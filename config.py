# Statement for enabling the development environment
DEBUG = True

# Define the application directory
# Define the database - we are working with
# SQLite for this example
#SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://%s:%s@%s/%s' % ('login','password','server','db')
#DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 8

# Secret key for signing cookies
SECRET_KEY = '\xd0Y\xa3\x13AO$\xd8\x80\xc5,\xe7]\xd6Q\xae\xcd\xee\r\x8f\xe1\x17Q\xbc'
