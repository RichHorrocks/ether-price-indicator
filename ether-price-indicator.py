#!/usr/bin/env python

#	ether-price-indicator
#--------------------------------------

import sys
import gtk
import appindicator
import urllib2
import json
import os

from os.path import expanduser
HOME = expanduser("~")

SETTINGSFILE = os.path.abspath(HOME+"/.local/share/applications/settingsEtherIndicator.dat")
BAD_RETRIEVE = 0.00001

class EtherPriceIndicator:
    PING_FREQUENCY = 1 # seconds
    ETHERICON = os.path.abspath(HOME+"/.local/share/applications/ethericon.png")
    APPDIR = HOME+"/.local/share/applications/"
    APPNAME = 'Ether Indicator';VERSION = '1.0'
    ETHMODE = True; ETHInit = False;

    def __init__(self):
        self.initFromFile()
        self.ind = appindicator.Indicator("ether-indicator", self.ETHERICON,appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.menu_setup()
        self.ind.set_menu(self.menu)

    def main(self):
        self.updateStatsETH()
        gtk.timeout_add(self.PING_FREQUENCY * 1000, self.updateStatsETH)
        gtk.main()

	# setup gtk menus to toggle display of data
    def menu_setup(self):
        self.menu = gtk.Menu()
        self.BTCtickers = None
        self.btceBTC = gtk.RadioMenuItem(self.BTCtickers,"BTC-E"); 
        self.btceBTC.connect("activate", lambda x: self.toggleBTCdisplay("btce")); 
        self.btceBTC.show()
        self.BTCtickers = self.btceBTC
        self.mtgoxBTC = gtk.RadioMenuItem(self.BTCtickers,"MtGox"); 
        self.mtgoxBTC.connect("activate", lambda x: self.toggleBTCdisplay("mtgox")); 
        self.mtgoxBTC.show()
        self.BTCtickers = self.mtgoxBTC

        self.defSet = gtk.MenuItem("Choose exchange : "); self.defSet.show()
        self.menu.append(self.defSet)
        self.menu.append(self.mtgoxBTC); 
        self.menu.append(self.btceBTC) 

        self.setRefreshMenu(self.menu)

        self.updateStatsETH()
        
        self.about = gtk.MenuItem("About"); 
        self.about.connect("activate",self.menu_about_response);
        self.about.show()
        self.menu.append(self.about)
        self.quit_item = gtk.MenuItem("Quit Indicator"); 
        self.quit_item.connect("activate", self.quit); 
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def setRefreshMenu(self,menuIn):
        refreshmenu = gtk.Menu()
        refMenu =gtk.MenuItem("Set refresh rate :")
        refMenu.set_submenu(refreshmenu)

        self.refreshRates = None
        menuRefresh1 = gtk.RadioMenuItem(self.refreshRates,"3s"); menuRefresh1.connect("activate",lambda x: self.setPing(3)); menuRefresh1.show()
        self.refreshRates = menuRefresh1
        menuRefresh2 = gtk.RadioMenuItem(self.refreshRates,"10s"); menuRefresh2.connect("activate",lambda x: self.setPing(10)); menuRefresh2.show()
        self.refreshRates = menuRefresh2
        menuRefresh3 = gtk.RadioMenuItem(self.refreshRates,"30s"); menuRefresh3.connect("activate",lambda x: self.setPing(30)); menuRefresh3.show()
        self.refreshRates = menuRefresh3
        menuRefresh4 = gtk.RadioMenuItem(self.refreshRates,"1m"); menuRefresh4.connect("activate",lambda x: self.setPing(60)); menuRefresh4.show()
        self.refreshRates = menuRefresh4
        menuRefresh5 = gtk.RadioMenuItem(self.refreshRates,"5m"); menuRefresh5.connect("activate",lambda x: self.setPing(300)); menuRefresh5.show()
        self.refreshRates = menuRefresh5
        menuRefresh6 = gtk.RadioMenuItem(self.refreshRates,"10m"); menuRefresh6.connect("activate",lambda x: self.setPing(600)); menuRefresh6.show()
        self.refreshRates = menuRefresh6

        refreshmenu.append(menuRefresh1)
        refreshmenu.append(menuRefresh2)
        refreshmenu.append(menuRefresh3)
        refreshmenu.append(menuRefresh4)
        refreshmenu.append(menuRefresh5)
        refreshmenu.append(menuRefresh6)
        refMenu.show() 
        refreshmenu.show()
        menuIn.append(refMenu)

    def setPing(self,newTime):
        self.PING_FREQUENCY = newTime

	# build string to be used by indicator and update the display label
    def updateStatsETH(self):
        dataOut = ""
        priceNow = BAD_RETRIEVE

        priceNow = self.getEtherChainData("")
        if priceNow == BAD_RETRIEVE:
            priceNow = "TempDown"
        else:
            priceNow = str(priceNow)+" USD"
        if "mtgox" in self.exchange:
            dataOut = dataOut + ' | ' if dataOut != "" else dataOut
            dataOut = dataOut + "MtGox: "+priceNow
        self.mtgoxBTC.set_label("MtGox| "+str(priceNow))

        priceNow = self.getBTCEDataUSD("")
        if priceNow == BAD_RETRIEVE:
            priceNow = "TempDown"
        else:
            priceNow = str(priceNow)+" USD"
        if "btce" in self.exchange:
            dataOut = dataOut + ' | ' if dataOut != "" else dataOut
            dataOut = dataOut + "BTC-E: "+priceNow
        self.btceBTC.set_label("BTC-E | "+str(priceNow))

        self.ind.set_label(dataOut)
        return True

    # get bter data using json
    def getEtherChainData(self):
        lstBterprice = BAD_RETRIEVE
        try :
            web_page = urllib2.urlopen("https://etherchain.org/api/blocks/count").read()
            data = json.loads(web_page)
            lstBterprice = data['last']
        except urllib2.HTTPError :
            print("HTTPERROR!")
        except urllib2.URLError :
            print("URLERROR!")
        return "{0:,.2f}".format(float(lstBterprice))


    #############################################
    ##########Settings###File####################
    #############################################
	# grab settings from file
    def initFromFile(self):
        try:
            with open(SETTINGSFILE): pass
        except IOError:
            print 'Need to make new file.'
            file = open(SETTINGSFILE, 'w')
            file.write(os.getcwd()+'\n')
            file.write('10 \n')
            file.write('bter \n')
            file.write('True \n')
            file.close()
        f = open(SETTINGSFILE, 'r')
        lines = f.readlines()
        currDir = (lines[0].strip())
        if ".local/share/applicatins" not in currDir:
            self.setAppDir(currDir)
        print "App Directory : "+self.APPDIR
        print "Refresh rate:",int(lines[1]),"seconds"
        self.PING_FREQUENCY = int(lines[1])
        print "BTC Exchange :",(lines[2].strip()),"   Display :",self.str2bool(lines[3].strip())
        self.exchange = (lines[2].strip())
        self.BTCMODE = self.str2bool(lines[3].strip())
        print "LTC Exchange :",(lines[4].strip()),"   Display :",self.str2bool(lines[5].strip())
        self.exchangeLTC = (lines[4].strip())
        self.LTCMODE = self.str2bool(lines[5].strip())
        print "NMC Exchange : ",(lines[6].strip()),"   Display :",self.str2bool(lines[7].strip())
        self.exchangeNMC = (lines[6].strip())
        self.NMCMODE = self.str2bool(lines[7].strip())
        print "PPC Exchange : ",(lines[8].strip()),"   Display :",self.str2bool(lines[9].strip())
        self.exchangePPC = (lines[8].strip())
        self.PPCMODE = self.str2bool(lines[9].strip())
        print "YAC Exchange : ",(lines[10].strip()),"   Display :",self.str2bool(lines[11].strip())
        self.exchangeYAC = (lines[10].strip())
        self.YACMODE = self.str2bool(lines[11].strip())
        f.close()

    def setAppDir(self,currDir):
        self.YACICON = os.path.abspath(currDir+"/res/ethericon.png")
        self.APPDIR = currDir

	# utility function for settings file grab
    def str2bool(self,word):
        return word.lower() in ("yes", "true", "t", "1","ok")

    def quit(self, widget, data=None):
        gtk.main_quit()
	# save settings at quit and kill indicator
    def quit(self, widget):
        try:
            print 'Saving Last State.'
            file = open(SETTINGSFILE, 'w')
            file.write(str(self.APPDIR)+'\n')
            file.write(str(self.PING_FREQUENCY)+'\n')
            file.write(str(self.exchange)+'\n')
            file.write(str(self.BTCMODE)+'\n')
            file.close()
        except IOError:
            print " ERROR WRITING QUIT STATE"
        gtk.main_quit()
        sys.exit(0)

    def menu_about_response(self,widget):
        self.menu.set_sensitive(False)
        widget.set_sensitive(False)
        ad=gtk.AboutDialog()
        ad.set_name(self.APPNAME)
        ad.set_version(self.VERSION)
        ad.set_comments("A bitcoin ticker indicator")
        ad.set_license(''+
        'This program is free software: you can redistribute it and/or modify it\n'+
        'under the terms of the GNU General Public License as published by the\n'+
        'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
        'any later version.\n\n'+
        'This program is distributed in the hope that it will be useful, but\n'+
        'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
        'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
        'more details.\n\n'+
        'You should have received a copy of the GNU General Public License along with\n'+
        'this program.  If not, see <http://www.gnu.org/licenses/>.')
        ad.set_website('https://github.com/jj9btcproj/Bitcoin-Price-Indicator')
        ad.set_authors(['Written by jj9: \n If you want to tip the following are jj9 addressess \n'+
                        'BTC: 1ECXwPU9umqtsBAQesBW9981mx6sipPmyL \n '+
                        'LTC : LUJz8yaS4uL1zrzwARbA4CiMpAwbpUwWY6 \n '+
                        ' NMC: N1SKXkrcyhxVYwQGsbLTFMbGAgeqL2g9tZ \n \n'+
                        'special thanks to RichHorrocks and Zapsoda for updating setup file and some btce api calls\n\n'+
                        '---jj9'])
        ad.run()
        ad.destroy()
        self.menu.set_sensitive(True)
        widget.set_sensitive(True)

if __name__ == "__main__":
    indicator = EtherPriceIndicator()
    indicator.main()
