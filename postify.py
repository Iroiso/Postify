"""
Postify is a simple, small and fast program that polls a database connected to
Gammu (wammu.eu) for new messages, JSONifies them and posts them
to a particular URL, It completely takes care of configuring the
modems or phones.

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
import os
import sys
import getpass
import logging
from subprocess import Popen, PIPE
from httplib import HTTPConnection, HTTPException
from string import Template
import urlparse
import MySQLdb
from optparse import OptionParser
from ConfigParser import ConfigParser

# Todo
# Exeify with Py2exe
# Test
# Package
# Upload to Drop box and call aliyu.

# Module setup
logging.basicConfig(level = logging.DEBUG, format = "%(asctime)s : %(funcName)s ->  %(message)s")

    
# Module data
__author__ = "Iroiso Ikpokonte <http://twitter.com/iroiso>"
__version__ = "0.5.0.stable"
__all__ = ["post","each","tag",]

# Data Directory and synchronization files, Postified related stuff should be stored here regardless
binDir = "./bin"
daemon = os.path.join(binDir, "gammu-smsd")
baseDir = r"C:\Users\{home}\Postify".format(home = getpass.getuser())
logFile = os.path.join(baseDir,"Events.log")
installLock = os.path.join(baseDir, "installed")  # Another lock to tell me if postify has been sucessfully installed before
baseSettings = os.path.join(baseDir, "base.ini")  # Universal settings used by the daemon
configFile = "settings.cfg"

# setup, run, and remove from the console
# Usage Variables
usage = " %prog [options] ; for more detailed help read the documentation (Readme.md)"


# Module variables
template = Template(u""""Message" : { "sender" : "$SenderNumber", "text" : "$TextDecoded", "smsc" : "$SMSCNumber", "date" : "$ReceivingDateTime" } """)
header = {"Content-type": "application/json", "Accept" : "text/plain"}
settings = {}  # Initialized from configuration file at runtime.



# Module level functions
def post( dictionary , address):
    """ Do a HTTP POST to the specified address with dictionary  as its JSONified payload
        @return boolean to signify success or failure
    """
    try:
##        logging.info("Posting %s to %s" % (dictionary,address))
        # Do template substituiton
        posted = False
        body = template.substitute(dictionary)
        
        # Do post
        URL = urlparse.urlparse(address)
        connection = HTTPConnection(URL.netloc)
        connection.request("POST", URL.path, body, header)

        # Read response
        response = connection.getresponse()

        if response.status in (200,201,202,):
            logging.info("Response Code : {status} , Body : {body},".format(status = response.status, body = str(response.read())))
            posted = True
            return True
        else:
            logging.info("Response not OK..")
            return False
        
    # Clean up and exception handling
    except (ValueError,KeyError) as TemplateError:
        logging.info("An error occurred during the Template Substitution : %s " % TemplateError )
        return False

    except (HTTPException) as PostError:
        logging.info("An error occured when posting the message to {address}: {error}".format(address = address, error = PostError))
        return False

    finally:
        try:
            connection.close()
            if not posted:
                return False
        except UnboundLocalError: # Catch exception when socket is not bound
            logging.info("Error closing HTTP Connection, Not Bound")
            return False
        

def each( host , user , password , db ):
    """ Yields each unprocessed message as a dictionary
        @yield dictionary like object
    """
    try:
        # A DictCursor object is just appropriate instead of a home grown solution
        conn = MySQLdb.connect(host,user,password,db)
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM {db}.inbox WHERE processed = 'false'".format(db = db))
        logging.info("Found : %s unprocessed messages" % cursor.rowcount)

        for row in cursor:
            yield row
            
        cursor.close()
        conn.close()
        
    except (MySQLdb.Error, MySQLdb.OperationalError) as e :
        logging.error("MySQL Error during operation %d : %s" % (e.args[0], e.args[1],) )


def tag(Id,host , user , password , db ):
    """ Tag a particular message as processed """
    print ("In tag")
    try:
        logging.info("Tagging Id : %s as Processed " % Id )
        conn = MySQLdb.connect(host,user,password,db)
        cursor = conn.cursor()
        cursor.execute("UPDATE {db}.inbox SET processed = 'true' WHERE ID = {Id}".format(db = db, Id = Id))
        cursor.close()
        conn.commit()
        conn.close()
        return True
    
    except MySQLdb.Error as Error:
        logging.error("MySQL Error during operation %d : %s" % (Error.args[0], Error.args[1],))
        return False


def run():
    """ Loops constantly and polls the data base for new messages every 5secs"""
    import time
    
    if not os.path.isfile(installLock): # checks to see if the service is installed
        logging.info("Postify has not been installed. type : postify --install")
        sys.exit(1)
        
    try:
        print "Running Postify Loop..."
        while True:
            # do read() and post()
            address = settings["url"]  # I do not do URL validation
            for row in each(host = settings["host"], user = settings["user"], password = settings["password"], db = settings["database"]):
                if post(row, address):
                    result = tag(row["ID"], host = settings["host"], user = settings["user"], password = settings["password"], db = settings["database"])
                    if result: print("Message was successfully posted to the remote URL")
            
            time.sleep(5) # sleep for 5secs
            
    except KeyboardInterrupt:
        print "Closing Postify..."
    
    
        
        
# Installation and utility functions
def init():
    """ Module initialization routine """
    global settings
    parser = ConfigParser()
    parser.read(configFile)
    settings = dict(parser.items("settings"))
    settings["logfile"] = logFile
   
def call( arguments ):
    """ Uses subprocess to invoke an external program; returns true or false signify success """
    try:
        popen = Popen(arguments, stdout = PIPE, stdin = PIPE)
        popen.wait() # Wait for the external program to finish and examine its return code.
        if popen.returncode == 0:
            return True
        else:
            return False
    except :
        logging.debug("An error occured when invoking: %s" % arguments )
        return False
    

def main():
    """ Main routine of this script, read passsed in options and deal with them appropriately """
    # Command Line Parsing
    parser = OptionParser(usage = usage)
    parser.add_option("-i","--install", action = "store_true", dest = "install",
                      help = "Install Postify: configures the modem, and creates a Service that listens to it ")
    parser.add_option("-r", "--run", action = "store_true", dest = "run", help = "Run Postify..")
    parser.add_option("-c", "--clean", action = "store_true", dest = "clean", help = "Put humpty together again")
    parser.add_option("-s", "--status", action = "store_true", dest = "status", help = "Check if Postify is Installed or Not Installed")
    options, args = parser.parse_args()
    init()
    parser.print_usage()
        
    if options.install:
        install()

    if options.run:
        run()

    if options.clean:
        clean()

    if options.status:
        status()
    
    
# Execution functions
def status():
    """ Check if postify is installed or not """
    if os.path.isfile(installLock):
        print("Postify has been installed; Please use Postify --run to start postify")
    else:
        print("Not Installed yet; Please use Postify --install to install postify")


        
    
def clean():
    """ Remove stuff from previous installations of postify"""
    import shutil
    try:
        removed = False
        logging.info("Removing install Lock file")
        os.remove(installLock) # remove the lock file first
        logging.info("Trying to remove the Windows service")
        removed = call([daemon,"-c" , baseSettings, "-u"])
        if removed:
            logging.info("Windows service removed successfully")
        else:
            logging.info("Something happened during clean")
        
        logging.info("Removing base directory")
        shutil.rmtree(baseDir)

    except Exception as e:
        logging.error("Exception occurred: %s " % str(e))

    finally:
        if removed:
            logging.info("Clean completed successfully. humpty is back together again: Please restart your computer")
        else:
            logging.info("Clean could not complete successfully please contact the author")
            

# SOME SERIOUS HACKING, PRIME CANDIDATE FOR REFACTORING
def install():
    """ Installation procedure
    0. Check if lock file exists... Simply exit if true.
    1. Create base directory
    2. Read settings dictionary and construct Global configuration from it
    2.5 Create Necessary MySQL tables 
    3. Install the Gammu Service with Global configuration
    4. Start service
    5. Create installed lock and exit """
    import glob
    import MySQLdb
    
    logging.debug("Starting installation...")
    # 0.
    if os.path.exists(installLock):
        logging.info("Postify has been already been previously installed.")
        sys.exit(1)
    # 1.
    if not os.path.isdir(baseDir):
        os.mkdir(baseDir) # I'm putting logs, lock files and configuration here !!!
    try:
        pathToModems = os.path.join(".", "conf", "modems", settings["modem"])
        path = glob.glob(pathToModems + "*")[0]   # this should find only one match
        conf = ConfigParser()
        
        # Fill the new ConfigParser object with information
        if os.path.exists(path):
            conf.read(path)  # the modem file should have the [gammu] section and constant values from the [smsd] section
            for key,value in settings.iteritems():
                if key == "port":
                    conf.set("gammu", key, value )  # BUG FIX TO ACCOMODATE FOR ADDITION OF PORTS.
                    continue         # Avoid Duplicate writing
                
                if key not in ["modem", "url"]:  # Filter information we should not write to the Global configuration file
                    conf.set("smsd",key, value)            
        else:
            raise Exception("Modem's configuration could not be found") #just jump to the catch block

        # Write this configuration to Global config
        with open(baseSettings, 'wb') as File:
            logging.info("Writing Global Configuration")
            conf.write(File)
            File.flush() # Just being defensive

        logging.info("Creating Database: Opening MySQL")
        try:
            db = MySQLdb.connect(settings['host'], settings['user'], settings['password'], settings['database'])
            logging.info("Found data for previous installation, Moving along")
        except:
            logging.info("Preparing backend")
            preparedb()
        
        # 3. and 4. Create windows Service
        logging.info("Creating windows service")
        if call([daemon, "-c", baseSettings , "-i"]) and call([daemon, '-c', baseSettings, '-s']):
            logging.debug("Service installed and Started Successfully")
    
        else:
            logging.error("Error occured when trying to create windows service")
            raise Exception("Error when Creating and installing Windows service")

        # 5. Create Lock file
        logging.debug("Creating installed lock file")
        open(installLock, 'w').close()
        
        logging.debug("Installation successful")
        
    except Exception as e:
        # Do clean up here.
        logging.error("Exception occured during installation: " + str(e))
        

def preparedb():
    """ Prepare MySQL for gammu """
    import sqlparse
    logging.info("Creating Database: Opening MySQL")
    db = MySQLdb.connect(settings['host'], settings['user'], settings['password'])
    cursor = db.cursor()
    logging.info("Creating Database: {db}".format(db = settings['database']))
    cursor.execute("create database if not exists {db}".format(db = settings['database']))
    cursor.execute("use {db}".format(db = settings['database']))

    logging.info("Reading SQL script")
    with open("./conf/scripts/mysql.sql") as scriptFile:  # Thanks to rescommunes at stackoverflow
        sql = scriptFile.read()
        sql_parts = sqlparse.split( sql )
        for sql_part in sql_parts:
            if sql_part.strip() ==  '':
                continue
            cursor.execute( sql_part )

    cursor.close()
    db.commit()
    db.close()
    



        
######################### Main Routine #################################
if __name__ == "__main__":
    main()
