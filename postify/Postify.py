
# Author : Iroiso => http://twitter.com/iroiso 

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
import sqlite3 as sqlite
from string import Template
from httplib import HTTPException,HTTPConnection



# To-do configure logging here.
# To-do review the post function, write the mark function, write unittests


# Module level variables
required = ["address", "dbFile"]
settings = {}
template = Template(" Message : { sender : $SenderNumber, text : $Text , smsc : $SMSCNumber, date : $ReceivingDateTime } ") # Template for JSONifying
headers = {"Content-type": "application/json", "Accept" : "text/plain"}




# Module level functions
def init(dictionary):
    """ Sets up postify with  @dictionary, you have to call this method before you use this module """
    logging.info("Verifying settings dictionary")
    for e in required:
        assert settings[e]
    settings = dictionary



# A simple routine that shows the expressive power of python
def run( ):
    """ Main routine: read all unprocessed messages and post them """
    for i in each():
        logging.info("Trying to post a new message: %s " % i )
        post(row = i)
        
            
    

def each():
    """ Read each unprocessed message from the backend and yield it
        @return dictionary
    """
    connection = sqlite.connect(settings["dbFile"])
    connection.row_factory = sqlite.Row
    cursor = connection.cursor()
    cursor.execute("select * from inbox where Processed = false order by ReceivingDateTime")
    
    logging.info("Found : %s new messages \n" % cursor.rowcount )
    for row in cursor:
        yield row   # release them one by one

    connection.close()


def mark(id):
    """ Marks the message with this ID as processed """
    logging.info("Marking message with ID: %s as Processed" % str(id))
    
    connection = sqlite.connect(settings["dbFile"])
    cursor = connection.cursor()
    cursor.execute("update inbox set Processed = true where id = ?", (id,))
    connection.commit()
    connection.close()


def post( row ):
    """ Serialize and Post the contents in body to the url provided above
        @param row = sqlite3.Row which is a dict like object
    """
    try:
        # preliminary stuff
        logging.info("Converting Row to JSON : %s" % row.keys())
        body = template.substitute(row)  # catch an exception for this guy
        logging.info("Conversion complete...")

        # post here
        logging.info("Posting to the remote address")
        url = settings[address]  # DOES NOT VALIDATE URLS !!!
        connection = HTTPConnection(url)
        connection.request("POST", body, headers)
        logging.info("Post successful; Reading response")
        response = connection.getresponse()
        logging.info("Received response: %s : %s" % (response.status,response.reason))

        
    except (KeyError,ValueError, HTTPException) as e:
        # do clean up here
        logging.error("An Exception occured during post : %s " % str(e))
        logging.info("Falling back because of the exception")
        fallback(row["ID"])
        
    finally:
        # First things first.
        connection.close()
        # check if I got the correct response, if yes mark message..
        if response.status in (200,201,202,):
            logging.info("Marking processed message")
            mark(row["ID"])
        else:
            logging.error("Oops, Your postal address did not return an appropriate response")
    

if __name__ == "__main__":
    run()
