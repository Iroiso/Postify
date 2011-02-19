"""
Setup: Generate Executable program using py2exe

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
from distutils.core import setup
import py2exe
import glob

config = dict(script ="postify.py", dest_base = "Postify", uac_info = "requireAdministrator" )
console = [config]
files = [("", ["settings.cfg", "Readme.md",]), ("./bin", glob.glob("./bin/*.*")), ("./conf/modems", glob.glob("./conf/modems/*.ini")) ]
setup(
       data_files = files,
       version  = "0.5.0",
       description = "Setup script for postify",
       name = "Postify",
       console = console,
)
