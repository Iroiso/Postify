"""
Postify is a simple, small and fast program that polls a database connected to
Gammu (wammu.eu) for new messages, JSONifies them and posts them
to a particular URL, It completely takes care of configuring the
modems or phones, scheduling with cron and it comes with an inbuilt
logging server that you can use to monitor activities as they occur.

Homepage and documentation: http://github.com/iroiso/postify

Licence (MIT)
-------------

    Copyright (c) 2011, Iroiso Ikpokonte .

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""
import logging
from httplib import HTTPConnection, HTTPException
from string import Template
import urlparse
import MySQLdb 



# Module setup
logging.basicConfig(level = logging.DEBUG, format = "%(asctime)s : %(funcName)s ->  %(message)s" )

    
# Module data
__author__ = "Iroiso Ikpokonte <http://twitter.com/iroiso>"
__version__ = "0.5.0"
__all__ = ["post",]


# Module variables
template = template = Template(u""" Message : { sender : "$SenderNumber", text : "$Text", smsc : "$SMSCNumber", date : "$ReceivingDateTime" } """)
header = {"Content-type": "application/json", "Accept" : "text/plain"}
settings = {"user" : None , "password" : None , "host" : None , "db" : None }  # Initialized from configuration file at runtime.



# Module level functions
def post( dictionary , address):
    """ Do a HTTP POST to the specified address with dictionary  as its JSONified payload
        @return boolean to signify success or failure
    """
    logging.info("Posting: {0} to {1}".format(dictionary, address))
    try:
        # Do template substituiton
        logging.debug("Doing substitution")
        posted = False
        body = template.substitute(dictionary)
        logging.info("JSON : {body}".format(body = body))

        # Do post
        logging.debug("Finished substitution, Doing Post ")
        URL = urlparse.urlparse(address)
        connection = HTTPConnection(URL.netloc)
        connection.request("POST", URL.path, body, header)

        # Read response
        logging.debug("Finished Post; Reading and verifying Response")
        response = connection.getresponse()

        if response.status in (200,201,202,):
            
            logging.info("Response Code : {status} , Body : {body},".format(status = response.status, body = str(response.read())))
            posted = True
            return True
        
        else:
            logging.debug("Response not OK..")
            return False
        
    # Clean up and exception handling
    except(ValueError,KeyError) as TemplateError:
        logging.error("An error occurred during the Template Substitution : %s " % TemplateError )
        return False

    except (HTTPException) as PostError:
        logging.error("An error occured when posting the message to {address}: {error}".format(address = address, error = PostError))
        return False

    finally:
        logging.debug("Cleaning up after HTTP POST")
        try:
            connection.close()
            if not posted:
                return False
            
        except UnboundLocalError: # Catch exception when socket is not bound
            logging.error("Error closing HTTP Connection, Not Bound")
        
    


def each( host = settings['host'] , user = settings['user'], password = settings['password'], db = settings['db']):
    """ Yields each unprocessed message as a dictionary
        @yield dictionary
    """
    try:
        logging.debug("Connecting to the database")
        conn = MySQLdb.connect(host,user,password,db)
        cursor = conn.cursor()

        logging.debug("Selecting messages")
        cursor.execute("SELECT ID,SenderNumber,Text,SMSCNumber,ReceivingDateTime FROM inbox WHERE processed = false")

        logging.debug("Found : %s unprocessed messages" % cursor.rowcount)
        for row in cursor:
            yield { "ID": row[0], "SenderNumber": row[1], "Text" : row[2], "SMSCNumber" : row[3], "ReceivingDateTime": row[4]}
    
        conn.close()
        
    except (MySQLdb.Error, MySQLdb.OperationalError) as DBError:
        logging.error("MySQL is not responding : %s" % DBError )


def tag(Id):
    """ Tag a particular message as processed """
    pass


# The only point of coupling     
def run():
    """ Main routine of this script """
    pass














        
