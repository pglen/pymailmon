#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, random, time, warnings, regex
import traceback

from pymenu import  *

sys.path.append('../pycommon')

from pgutil import  *
from pgui import  *
from pgsimp import  *
#from htmledit import  *
from pgwkit import  *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

# Fields become editable
fields = ("Name:From", "Email:From", "Name:To", "Email:To",  "Date",
            "Len", "Subject",  "Pos", "UUID",  )

# Fields become editable
fields2 = ("Name:From", "Email:From", "Name:To", "Email:To",  "Date",
            "Len", "Subject",  "ChkSum", "UUID",  )

mainfile = "/home/peterglen/.thunderbird/nnj07ki9.default-release/Mail/pop.gmail.com/Inbox"

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self):

        self.exiting = False
        self.status_cnt = 0

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        #self = Gtk.Window(Gtk.WindowType.TOPLEVEL)

        #Gtk.register_stock_icons()

        self.set_title("PyMailMon")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        #ic = Gtk.Image(); ic.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.ICON_SIZE_BUTTON)
        #window.set_icon(ic.get_pixbuf())

        www = Gdk.Screen.width(); hhh = Gdk.Screen.height();

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print( disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();

        if www / hhh > 2:
            self.set_default_size(5*www/8, 7*hhh/8)
        else:
            self.set_default_size(7*www/8, 7*hhh/8)

        '''self.set_flags(Gtk.CAN_FOCUS | Gtk.SENSITIVE)

        self.set_events(  Gdk.POINTER_MOTION_MASK |
                            Gdk.POINTER_MOTION_HINT_MASK |
                            Gdk.BUTTON_PRESS_MASK |
                            Gdk.BUTTON_RELEASE_MASK |
                            Gdk.KEY_PRESS_MASK |
                            Gdk.KEY_RELEASE_MASK |
                            Gdk.FOCUS_CHANGE_MASK )
        '''
        self.connect("destroy", self.OnExit)
        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.button_press_event)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        vbox = Gtk.VBox();

        merge = Gtk.UIManager()
        #self.mywin.set_data("ui-manager", merge)

        aa = create_action_group(self)
        merge.insert_action_group(aa, 0)
        self.add_accel_group(merge.get_accel_group())

        merge_id = merge.new_merge_id()

        try:
            mergeid = merge.add_ui_from_string(ui_info)
        except GLib.GError as msg:
            print("Building menus failed: %s" % msg)

        self.mbar = merge.get_widget("/MenuBar")
        #self.mbar.show()

        self.tbar = merge.get_widget("/ToolBar");
        #self.tbar.show()

        bbox = Gtk.VBox()
        bbox.pack_start(self.mbar, 0, 0, 0)
        bbox.pack_start(self.tbar, 0, 0, 0)
        vbox.pack_start(bbox, 0, 0, 0)

        hbox2 = Gtk.HBox()
        lab3 = Gtk.Label(" ");  hbox2.pack_start(lab3, 0, 0, 0)
        lab4 = Gtk.Label("Top");  hbox2.pack_start(lab4, 1, 1, 0)
        lab5 = Gtk.Label(" ");  hbox2.pack_start(lab5, 0, 0, 0)
        vbox.pack_start(hbox2, False, 0, 0)

        hbox3 = Gtk.HBox()
        #self.edit = SimpleEdit();
        #self.edit = Gtk.Label(" Main ")
        #hbox3.pack_start(self.edit, True, True, 6)

        tt = type(""); fff = []
        for ccc in range(len(fields)):
            fff.append(tt)

        tt2 = type(""); fff2 = []
        for ccc in range(len(fields2)):
            fff2.append(tt2)

        self.model = Gtk.TreeStore(*fff)
        self.tree = Gtk.TreeView(self.model)
        self.tree.connect("cursor-changed", self.row_activate)

        self.model2 = Gtk.TreeStore(*fff2)
        self.tree2 = Gtk.TreeView(self.model2)

        self.cells = []; cntf = 0

        for aa in fields:
            col = Gtk.TreeViewColumn(aa, self.cellx(cntf), text=cntf)
            self.tree.append_column(col)
            cntf += 1

        for aa in fields2:
            col = Gtk.TreeViewColumn(aa, self.cellx(cntf), text=cntf)
            self.tree2.append_column(col)
            cntf += 1

        self.hpane = Gtk.HPaned()
        ww,hh = self.get_default_size()
        self.hpane.set_position(ww-500)

        #self.text = Gtk.TextView()
        #self.text = SimpleEdit()
        #self.text = Gtk.Label("tttttt")
        self.main = HtmlEdit(False)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll2 = Gtk.ScrolledWindow()
        self.scroll3 = Gtk.ScrolledWindow()
        self.scroll4 = Gtk.ScrolledWindow()
        self.scroll5 = Gtk.ScrolledWindow()
        self.scroll6 = Gtk.ScrolledWindow()

        self.scroll.add(self.tree)
        #self.scroll2.add(self.text)
        self.scroll2.add(self.main)
        self.scroll4.add(self.tree2)

        self.tabx =  Gtk.Notebook()
        self.tabx.append_page(self.scroll, Gtk.Label("Mail"))
        self.tabx.append_page(self.scroll4, Gtk.Label("Conversations"))

        self.html = HtmlEdit(True)

        self.scroll3.add(self.html)

        self.tabx2 =  Gtk.Notebook()
        self.tabx2.append_page(self.scroll2, Gtk.Label("e-Mail Body"))
        self.tabx2.append_page(Gtk.Label("History here"), Gtk.Label("History"))

        self.bodyx = SimpleEdit() #Gtk.Label("Header here")
        self.scroll5.add(self.bodyx)

        self.tabx2.append_page(self.scroll5, Gtk.Label("Raw"))
        self.hpane.add(self.tabx2)

        self.headx = SimpleEdit() #Gtk.Label("Header here")
        self.scroll6.add(self.headx)
        self.tabx2.append_page(self.scroll6, Gtk.Label("Header"))

        self.hpane.add(self.scroll3)

        self.vpane = Gtk.VPaned()
        self.vpane.set_position(300)

        self.vpane.add(self.tabx)
        self.vpane.add(self.hpane)

        vbox.pack_start(self.vpane, True, True, 2)

        hbox4 = Gtk.HBox()
        lab1 = Gtk.Label("   ");  hbox4.pack_start(lab1, 0, 0, 0)

        # buttom row
        lab2a = Gtk.Label(" buttom ");  hbox4.pack_start(lab2a, 1, 1, 0)
        lab2a.set_xalign(0)
        self.status = lab2a

        butt1 = Gtk.Button.new_with_mnemonic("    _New    ")
        #butt1.connect("clicked", self.show_new, window)
        hbox4.pack_start(butt1, False, 0, 2)

        butt2 = Gtk.Button.new_with_mnemonic("    E_xit    ")
        butt2.connect("clicked", self.OnExit, self)
        hbox4.pack_start(butt2, False, 0, 2)

        lab2b = Gtk.Label("  ");  hbox4.pack_start(lab2b, 0, 0, 0)

        vbox.pack_start(hbox4, False, 0, 6)

        GLib.timeout_add(200,  self.load)
        GLib.timeout_add(1000, self.timer)

        self.add(vbox)
        self.show_all()

    def row_activate(self, arg1):
        sel = self.tree.get_selection()
        tree, curr = sel.get_selected()
        if not curr:
            return

        print("row_activate",  curr)
        ppp = self.model.get_path(curr)
        row = self.model[ppp]
        print(row[1], row[3], row[4], row[0])
        #print("position", row[7])

        self.cnt = 0
        re_from = regex.compile("From - ")
        # Fill
        fh = open(mainfile, "rt")
        fh.seek(int(row[7]))
        cnt = 0;  accum = ""; skip = 0
        while 1:
            try:
                aa = fh.readline()
                pos = fh.tell()
                if not aa:
                    break
                mmm = re_from.match(aa)
                if mmm != None:
                    if not skip:
                        skip = True
                        accum = aa
                        continue

                    if accum:
                        self.main.get_view().load_html(self.body(accum), None)
                        self.headx.set_text(self.header(accum), None)
                        self.bodyx.set_text(self.body(accum))
                    break
                    accum = aa
                    cnt += 1
                else:
                    accum += aa
            except:
                print("readfile error", sys.exc_info())






    def text_edited(self, widget, path, text, idx):
        pass

    def cellx(self, idx):
        cell = Gtk.CellRendererText()
        #cell.set_property("editable", True)
        cell.connect("edited", self.text_edited, idx)
        self.cells.append(cell)
        return cell

    def  OnExit(self, arg, srg2 = None):
        self.exit_all()

    def exit_all(self):
        self.exiting = True
        Gtk.main_quit()

    def key_press_event(self, win, event):
        #print( "key_press_event", win, event)
        pass

    def button_press_event(self, win, event):
        #print( "button_press_event", win, event)
        pass

    def activate_action(self, action):

        #dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
        #    Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE,
        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        #dialog.connect ("response", lambda d, r: d.destroy())
        #dialog.show()

        warnings.simplefilter("ignore")
        strx = action.get_name()
        warnings.simplefilter("default")

        print ("activate_action", strx)

    def activate_quit(self, action):
        print( "activate_quit called")
        self.OnExit(False)

    def activate_exit(self, action):
        print( "activate_exit called" )
        self.OnExit(False)

    def activate_about(self, action):
        print( "activate_about called")
        pass

    def header(self, accum):
        #re = regex.compile("^\n")
        head = ""
        for aa in accum.split("\n"):
            #print("aa", "'"+aa+"'")
            head += aa + "\n"
            #mm = re.match(aa)
            #if mm != None:
            if not aa:
                #print ("head", head)
                break
        return head

    def body(self, accum):
        flag = False;  body = ""
        for aa in accum.split("\n"):
            #print("aa", "'"+aa+"'")
            if flag:
                body += aa + "\n"
            if not aa:
                flag = True
        return body

    def proc_field(self, rexpr, head):
        re = regex.compile(rexpr)
        cc = ["", ""]
        for aa in head.split("\n"):
            try:
                #print(aa)
                mm = re.match(aa)
                if mm:
                    aa = aa[mm.end():]
                    bb = aa.strip()
                    cc = bb.split("<")
                    if len(cc) == 1:
                        cc = bb.split("[")
                        if len(cc) == 1:
                            cc.append(cc[0])
                            cc[0] = ""
                        cc[1] = cc[1].split("]")[0]
                    else:
                        cc[1] = cc[1].split(">")[0]
                    if len(cc) == 1:
                        cc.append(cc[0])
                        cc[0] = ""
                    cc[0] = cc[0].strip(' \"')
            except:
                print("err:", sys.exc_info())
                pass
        return cc

    def one_message(self, accum, pos):
        #print("acc")
        #print(accum)
        head = self.header(accum)
        cc = self.proc_field("^From:",  head)
        dd = self.proc_field("^To:",    head)
        ee = self.proc_field("^Date:",  head)
        ff = self.proc_field("^Subject:",  head)

        body = self.body(accum)
        #print("header", head)
        #print("body", body)

        #print("parsed", cc, dd, ee)
        self.model.append(None, ( cc[0], cc[1], dd[0], dd[1], ee[1], str(len(body)), ff[1], str(pos), "uuid"))

        # Make exception, looks faster
        if self.cnt == 30:
            usleep(10)

        #if self.cnt % 50 == 49:
        #    usleep(10)

        self.cnt += 1
        #print("acc END")

    def timer(self):
        #print("Called timer %d" % self.status_cnt)
        self.status_cnt += 1
        if self.status_cnt > 5:
            self.status.set_text("Idle.")
        return True

    def load(self):
        #print("Called load")
        self.cnt = 0
        re_from = regex.compile("From - ")
        # Fill
        fh = open(mainfile, "rt")
        cnt = 0;  accum = ""; pos = 0
        while 1:
            try:
                beg = fh.tell()
                aa = fh.readline()
                if not aa:
                    break

                mmm = re_from.match(aa)
                if mmm != None:
                    if accum:
                        self.one_message(accum, pos)
                    pos = beg
                    accum = aa
                    cnt += 1
                else:
                    accum += aa

                if self.exiting:
                    break

                # Limit for testing
                if cnt > 300:
                    break

                if cnt % 30 == 29:
                    self.status.set_text("Loading message: %d" % cnt)
                    self.status_cnt = 0

            except:
                print("err:", traceback.print_exc(), "line=", aa)

        fh.close()
        self.status.set_text("All messages loaded, %d messages" % self.cnt)
        self.status_cnt = 0

        self.cnt = cnt
        return False

# ------------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    Gtk.main()

# EOF