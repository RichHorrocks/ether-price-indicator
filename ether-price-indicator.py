#!/usr/bin/env python

#	ether-price-indicator
#--------------------------------------

import sys
import gtk
import appindicator
import requests
import json
import os
import ssl

from os.path import expanduser
HOME = expanduser("~")

SETTINGSFILE = os.path.abspath(HOME+"/.local/share/applications/settingsEtherIndicator.dat")
BAD_RETRIEVE = 0.00001

class EtherPriceIndicator:
    PING_FREQUENCY = 1 # seconds
    ETHERICON = os.path.abspath(HOME+"/.local/share/applications/ethericon.png")
    APPDIR = HOME+"/.local/share/applications/"
    APPNAME = 'Ether Indicator';VERSION = '1.0'

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
        self.setRefreshMenu(self.menu)
        self.updateStatsETH()
        
        # Munu options.
        self.about = gtk.MenuItem("About") 
        self.about.connect("activate",self.menu_about_response)
        self.about.show()
        self.menu.append(self.about)
        self.quit_item = gtk.MenuItem("Quit Indicator")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def setRefreshMenu(self,menuIn):
        refreshmenu = gtk.Menu()
        refMenu = gtk.MenuItem("Set refresh rate :")
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
        data = BAD_RETRIEVE

        data = self.getEtherChainData()
     #   if data == BAD_RETRIEVE:
     #       priceNow = "TempDown"
     #   else:
     #       priceNow = str(priceNow)+" USD"
     #   if "mtgox" in self.exchange:
     #       dataOut = dataOut + ' | ' if dataOut != "" else dataOut
     #       dataOut = dataOut + "MtGox: "+priceNow
     #   self.mtgoxBTC.set_label("MtGox| "+str(priceNow))

     #   self.ind.set_label(dataOut)
        return True

    # get bter data using json
    def getEtherChainData(self):
        data = "foo"
        try :
            r = requests.get("https://btc-e.com/api/2/ltc_eur/ticker", verify=False)
            #web_page = urllib2.urlopen("https://etherchain.org/api/blocks/count").read()
            #web_page = urllib2.urlopen("http://www.bbc.co.uk/news").read()
            #data = json.loads(web_page)
            print r
        except requests.exceptions.RequestException as e:    # This is the correct syntax
            print e
        #except urllib2.HTTPError as e:
        #    print("HTTPERROR: ", e.code)
        #except urllib2.URLError as e:
        #    print("URLERROR: ", e.reason)
        return data


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
            file.close()
        f = open(SETTINGSFILE, 'r')
        lines = f.readlines()
        currDir = (lines[0].strip())
        if ".local/share/applicatins" not in currDir:
            self.setAppDir(currDir)
        print "App Directory : "+self.APPDIR
        print "Refresh rate:",int(lines[1]),"seconds"
        self.PING_FREQUENCY = int(lines[1])
        f.close()

    def setAppDir(self,currDir):
        self.ETHERICON = os.path.abspath(currDir+"/res/ethericon.png")
        self.APPDIR = currDir

	# utility function for settings file grab
    def str2bool(self,word):
        return word.lower() in ("yes", "true", "t", "1","ok")

	# save settings at quit and kill indicator
    def quit(self, widget):
        try:
            print 'Saving Last State.'
            file = open(SETTINGSFILE, 'w')
            file.write(str(self.APPDIR)+'\n')
            file.write(str(self.PING_FREQUENCY)+'\n')
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
        ad.set_comments("An Ethereum ticker indicator")
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
