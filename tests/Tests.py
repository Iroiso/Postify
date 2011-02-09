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
# Tests for the Postify Module


from unittest import *
from bottle import Bottle, run, abort,request
from postify import *
import logging


# TestSuite
def suite():
    return TestLoader().loadTestsFromNames(["Tests.TestPost", "Tests.TestDbFunctions"])


# Module configuration
logging.basicConfig(level = logging.DEBUG, format = "%(asctime)s : %(funcName)s ->  %(message)s" )
dictionary = { "SenderNumber" : "UBA", "SMSCNumber" : "Fake", "Text" : "We're dying, please take all your money out" ,\
               "ReceivingDateTime": "From the Future" }


# Test Server
bottle = Bottle()

# Test Server Functions
@bottle.route("/accept", method = "POST" ) 
def acceptPosts():
    """ Accepts posts to this bottle server """
    print "Got Post..Yipee!"
    print "Request Body : " + request.body.read()
    return "Post Accepted"



@bottle.route("/deny", method = "POST")
def denyPosts():
    """ Deny all posts sent to this url """
    print("Denied a request...aborting")
    abort( 401, "Sorry you cannot post to this URL")




# TestCases 
class TestPost(TestCase):
    """ Test the Post function """

    def setUp(self):
        """ Setup a bottle server, This server should die on its own when the test completes"""
        from threading import Thread # quite dirty I hope this does backfire
        self.thread = Thread(target = lambda : run(app = bottle, host = "localhost", port = 8080))
        self.thread.daemon = True
        self.thread.start()


    def testAccept(self):
        """ Test an available URL """
        self.assertTrue(post(dictionary, "http://localhost:8080/accept"))
    

    def testDeny(self):
        """ Test a URL that deny's requests"""
        self.assertFalse(post(dictionary, "http://localhost:8080/deny"))


    def testUnavailable(self):
        """ Test an unavailable URL """
        self.assertFalse(post(dictionary, "http://localhost:9000"))
        


class TestDbFunctions(TestCase):
    """ Test functions that deal with the database backend """

    def setUp(self):
        """ Setup a MySQL database with an inbox table """
        pass

    def testEach(self):
        """ Tests if the dictionary dictionary works """
        pass

    def testTag(self):
        """ Tests if the tag function works """
        pass
     
