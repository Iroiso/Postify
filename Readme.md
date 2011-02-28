# Postify : A dumb modem listener that JSONifies and Posts SMS messages
Postify is a collection of tools that allow you to configure and listen for incoming sms messages from a modem;
It stores this messages in a MySQL based backend and does a HTTP POST of received messages to 
a specified URL in JSON. Postify was built for common modems in Nigeria; add other modem configurations in the
conf/ directory to use them.

## To Get the source.
Download the most stable version from github at (http://github.com/iroiso/postify)
or from the prompt

$ git clone git://github.com/iroiso/postify.git

## Dependencies
Postify depends on the following modules most of which you can install using "pip"

+ [bottle](http://bottle.paws.de),
+ [MySQLdb](http://pypi.python.org/pypi/mysqldb)
+ [py2exe](http://py2exe.org)
+  Python 2.7+ 
+ [MySQL Server ](http://mysql.org)


## Building the bleeding edge
Once you've gotten the source and installed dependencies; change to the source directory
and build it like a normal py2exe executable i.e.
$ python setup.py py2exe

You should have a dist directory in your current directory. simply move the files 
in the newly created dist directory to a suitable directory on your computer and you are good to go !!

Now you can follow the run instructions and run postify. If you did not get any of this; simply
send me an email or a DM and a I'll reply you with a link to download an executable I've already prebuilt


## Installation and Running
To figure out how to install and run just type

$ Postify --help or Postify -h

and you'll get a list of options for installing and running postify
Type:

$ Postify -i -r or Postify --install --run

This will install and run postify ( Note: you can type each command line switch to the same effect )
to remove type ( make sure that postify is not running ):

$ Postify -c or Postify --clean   #Don't worry your data is still safe.

## Settings
Postify uses the .ini file format. Look in the settings.ini file to see
available options. They are pretty easy to understand.

- modem -> the model of your modem; simply look behind it 
- url -> the url to post new messages to
- user, password, host, db -> these are parameters to the MySQLdb you want to use for postify
- And that is it.. Happy Posting...


## Acknowledgements
Postify would not have existed if not for this people and projects:
+ Aliyu Agama : For pushing my lazy ass to do this in the first place
+ Michael Cihar ( michael@cihar.com ) : for his amazing Gammu Project

## Author
+ Iroiso < http://twitter.com/iroiso >
