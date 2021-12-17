#!/usr/bin/env python

import os, sys, glob, getopt, time, string, signal, stat, shutil
import traceback

#import warnings; warnings.simplefilter("ignore");
#import Gtk; warnings.simplefilter("default")

from pymenu import  *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# ------------------------------------------------------------------------
# Handle command line. Interpret optarray and decorate the class;
# Uses UNIX getopt for compatibility;
#
# Option parameters:
#
# option, long_option,  var_name,   initial_value, function
#
# Option with parameters:   add trailing colon (:)
# Long opt with parameters: add training equal sign (=)
#
# Example:
#
#optarr = \
#    ["d:",    "debug=",      "pgdebug",  0,              None],      \
#    ["p:",    "port",        "port",     9999,           None],      \
#    ["v",     "verbose",     "verbose",  0,              None],      \
#    ["t",     "test",        "test",     "x",            None],      \
#    ["V",     "version",     None,       None,           pversion],  \
#    ["h",     "help",        None,       None,           phelp],     \
#    ["i:",    "input=",      "input",      "-",          None],     \

class ConfigLong:

    def __init__(self, optarr):
        self.optarr = optarr
        self.err = None

        # Create defaults:
        for bb in range(len(self.optarr)):
            if self.optarr[bb][2]:
                #print("init", optarr[bb][2], optarr[bb][3])
                # Coerse type
                if type(self.optarr[bb][2]) == type(0):
                    self.__dict__[self.optarr[bb][2]] = int(self.optarr[bb][3])
                else:
                    self.__dict__[self.optarr[bb][2]] = str(self.optarr[bb][3])

    def printvars(self):
        for aa in dir(self):
            try:
                if aa[:2] != "__" and aa != "optarr" and  aa != "comline" and \
                                    aa != "printvars" :
                    ff = getattr(self, aa)
                    if type(ff) == type(self.printvars):
                        ff = "function"
                    print(aa, ff)
            except:
                pass

    def comline(self, argv):
        optletters = "";  longopt = []
        for aa in self.optarr:
            if aa[0] in optletters:
                print ("Warning: duplicate option", "'" + aa[0] + "'")
            #if len(aa[0]) > 1 and aa[0][1] != ':':
            optletters += aa[0]
            longopt.append(aa[1])

        #print("optleters", optletters, "longopt", longopt)

        try:
            opts, args = getopt.getopt(argv, optletters, longopt)
        #except getopt.GetoptError, err:
        except getopt.GetoptError as err:
            self.err =  str("Invalid option(s) on command line: %s" % err)
            return None

        #print ("opts", opts, "args", args)
        for aa in opts:
            for bb in range(len(self.optarr)):
                ddd = None
                if aa[0][1] == "-":
                    ddd = "--" + self.optarr[bb][0]
                    eee = "--" + self.optarr[bb][1]
                elif aa[0][0] == "-":
                    ddd = "-" + self.optarr[bb][0]
                    eee = "-" + self.optarr[bb][1]
                else:
                    ddd = self.optarr[bb]
                if ddd[-1:] == "=":
                    ddd = ddd[:-1]
                    eee = eee[:-1]
                if ddd[-1:] == ":":
                    ddd = ddd[:-1]
                    eee = eee[:-1]

                #print ("aa",  aa, "one opt", self.optarr[bb][:-1], ddd, eee)
                if aa[0] == ddd or aa[0] == eee:
                    #print ("match", aa, ddd)
                    if len(self.optarr[bb][0]) > 1:
                        #print ("arg", self.optarr[bb][2], self.optarr[bb][3], aa)
                        if self.optarr[bb][3] != None:
                            if type(self.optarr[bb][3]) == type(0):
                                if aa[1][:2] == "0x" or aa[1][:2] == "0X":
                                    self.__dict__[self.optarr[bb][2]] = int(aa[1][2:], 16)
                                else:
                                    self.__dict__[self.optarr[bb][2]] = int(aa[1])
                                    pass

                            elif type(self.optarr[bb][2]) == type(""):
                                self.__dict__[self.optarr[bb][2]] = str(aa[1])
                    else:
                        #print ("set", self.optarr[bb][1], self.optarr[bb][2])
                        if self.optarr[bb][3] != None:
                            self.__dict__[self.optarr[bb][1]] = 1
                        #print ("call", self.optarr[bb][3])
                        if self.optarr[bb][4] != None:
                            self.optarr[bb][4]()
        return args

# ------------------------------------------------------------------------
# Print an exception as the system would print it

def print_exception(xstr):
    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print ("Could not print trace stack. ", sys.exc_info())
    print (cumm)

# ------------------------------------------------------------------------
# Never mind

def cmp(aa, bb):
    aaa = os.path.basename(aa);  bbb = os.path.basename(bb)
    pat = re.compile("[0-9]+")
    ss1 = pat.search(aaa)
    ss2 = pat.search(bbb)

    if(ss1 and ss2):
        aaaa = float(aaa[ss1.start(): ss1.end()])
        bbbb = float(bbb[ss2.start(): ss2.end()])
        #print (aaa, bbb, aaaa, bbbb)
        if aaaa == bbbb:
            return 0
        elif aaaa < bbbb:
            return -1
        elif aaaa > bbbb:
            return 1
        else:
            #print ("crap")
            pass
    else:
        if aaa == bbb:
            return 0
        elif aaa < bbb:
            return -1
        elif aaa > bbb:
            return 1
        else:
            #print ("crap")
            pass

# ------------------------------------------------------------------------
# Show a regular message:
'''
def xmessage(strx, title = None, icon = Gtk.MESSAGE_INFO):

    dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
        icon, Gtk.BUTTONS_CLOSE, strx)

    if title:
        dialog.set_title(title)
    else:
        dialog.set_title("ePub Reader")

    # Close dialog on user response
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.show()
'''

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

'''def  usleep(msec):

    got_clock = time.clock() + float(msec) / 1000
    #print (got_clock)
    while True:
        if time.clock() > got_clock:
            break
        Gtk.main_iteration_do(False)
'''

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

def  usleep(msec):

    if sys.version_info[0] < 3 or \
        (sys.version_info[0] == 3 and sys.version_info[1] < 3):
        timefunc = time.clock
    else:
        timefunc = time.process_time

    got_clock = timefunc() + float(msec) / 1000
    #print( got_clock)
    while True:
        if timefunc() > got_clock:
            break
        #print ("Sleeping")
        Gtk.main_iteration_do(False)


# -----------------------------------------------------------------------
# Call func with all processes, func called with stat as its argument
# Function may return True to stop iteration

def withps(func, opt = None):

    ret = False
    dl = os.listdir("/proc")
    for aa in dl:
        fname = "/proc/" + aa + "/stat"
        if os.path.isfile(fname):
            ff = open(fname, "r").read().split()
            ret = func(ff, opt)
        if ret:
            break
    return ret

# ------------------------------------------------------------------------
# Find

def find(self):

    head = "Find in text"

    dialog = Gtk.Dialog(head,
                   None,
                   Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.RESPONSE_REJECT,
                    Gtk.STOCK_OK, Gtk.RESPONSE_ACCEPT))
    dialog.set_default_response(Gtk.RESPONSE_ACCEPT)

    try:
        dialog.set_icon_from_file("epub.png")
    except:
        print ("Cannot load find dialog icon", sys.exc_info())

    self.dialog = dialog

    # Spacers
    label1 = Gtk.Label("   ");  label2 = Gtk.Label("   ")
    label3 = Gtk.Label("   ");  label4 = Gtk.Label("   ")
    label5 = Gtk.Label("   ");  label6 = Gtk.Label("   ")
    label7 = Gtk.Label("   ");  label8 = Gtk.Label("   ")

    warnings.simplefilter("ignore")
    entry = Gtk.Entry();
    warnings.simplefilter("default")
    entry.set_text(self.oldfind)

    entry.set_activates_default(True)

    dialog.vbox.pack_start(label4)

    hbox2 = Gtk.HBox()
    hbox2.pack_start(label6, False)
    hbox2.pack_start(entry)
    hbox2.pack_start(label7, False)

    dialog.vbox.pack_start(hbox2)

    dialog.checkbox = Gtk.CheckButton("Search _Backwards")
    dialog.checkbox2 = Gtk.CheckButton("Case In_sensitive")
    dialog.vbox.pack_start(label5)

    hbox = Gtk.HBox()
    #hbox.pack_start(label1);  hbox.pack_start(dialog.checkbox)
    #hbox.pack_start(label2);  hbox.pack_start(dialog.checkbox2)
    hbox.pack_start(label3);
    dialog.vbox.pack_start(hbox)
    dialog.vbox.pack_start(label8)

    label32 = Gtk.Label("   ");  label33 = Gtk.Label("   ")
    label34 = Gtk.Label("   ");  label35 = Gtk.Label("   ")

    hbox4 = Gtk.HBox()

    hbox4.pack_start(label32);
    dialog.vbox.pack_start(hbox4)

    dialog.show_all()
    response = dialog.run()
    self.srctxt = entry.get_text()

    dialog.destroy()

    if response != Gtk.RESPONSE_ACCEPT:
        return None

    return self.srctxt, dialog.checkbox.get_active(), \
                dialog.checkbox2.get_active()

# ------------------------------------------------------------------------
# Count lead spaces

def leadspace(strx):
    cnt = 0;
    for aa in range(len(strx)):
        bb = strx[aa]
        if bb == " ":
            cnt += 1
        elif bb == "\t":
            cnt += 1
        elif bb == "\r":
            cnt += 1
        elif bb == "\n":
            cnt += 1
        else:
            break
    return cnt





