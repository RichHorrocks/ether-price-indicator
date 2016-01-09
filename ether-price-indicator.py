#!/usr/bin/env python

#  ether-price-indicator
#--------------------------------------

import sys
import gtk
import appindicator
import requests
import OpenSSL
import cryptography
import pyasn1
import json
import os
from ndg import httpsclient
from os.path import expanduser

HOME = expanduser("~")
APP_DIR = HOME + "/.local/share/applications/"
SETTINGS_FILE = os.path.abspath(APP_DIR + "ether_indicator_settings.dat")
ICON_FILE = os.path.abspath(APP_DIR + "ether_icon.png")
APP_NAME = 'Ether Indicator';
APP_VERSION = '1.0'

BAD_RETRIEVE = 0xDEADBEEF

class EtherPriceIndicator:
    # A dictionary representing the block details to be output.
    block_dict = { "Block": 0,
                   "Timestamp": 0,
                   "Difficulty": 0,
                   "Gas": 0,
                   "Blocktime": 0 }

    # Global variables for setting values in sub-menus.
    refresh_frequency = 3
    exchange = 'usdeth'

    #
    # Initialisation and callback functions.
    #
    def __init__(self):
        self.init_from_file()
        self.ind = appindicator.Indicator(
            "ether-indicator", 
            self.ICON_FILE,
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

    def init_callback(self):
        self.set_user_output()
        self.menu_setup()

        # Must return true for the timeout_add function to work.
        return True

    def init_from_file(self):
        try:
            with open(SETTINGS_FILE): pass
        except IOError:
            print 'Need to make new file.'
            file = open(SETTINGS_FILE, 'w')
            file.write(os.getcwd() + '\n')
            file.write('10\n')
            file.write('usdeth')
            file.close()
        f = open(SETTINGS_FILE, 'r')
        lines = f.readlines()
        currDir = (lines[0].strip())
        if ".local/share/applications" not in currDir:
            self.set_app_dir    (currDir)
        print "App Directory : " + self.APP_DIR
        print "Refresh rate:", int(lines[1]), " seconds"
        self.refresh_frequency = int(lines[1])
        self.exchange = lines[2].strip()
    
        f.close()

    def set_app_dir(self, currDir):
        self.ICON_FILE = os.path.abspath(currDir + "/res/ether_icon.png")
        self.APP_DIR = currDir

    def main(self):
        self.init_callback()
        gtk.timeout_add(self.refresh_frequency * 1000, self.init_callback)
        gtk.main()


    #
    # Create the drop-down GTK menu.
    #
    def menu_setup(self):
        self.menu = gtk.Menu()

        # Add data for the latest block.
        self.block_item = gtk.MenuItem("Last block:")
        self.block_item.show()
        self.menu.append(self.block_item)

        for key, value in self.block_dict.iteritems():
            item = gtk.MenuItem("    " + key + ":  " + str(value))
            item.show()
            self.menu.append(item)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        # Create exchange sub-menu.        
        self.menu_exchange_create(self.menu)

        # Create refresh rate sub-menu.
        self.menu_refresh_create(self.menu)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)
        
        # Add general munu options at the bottom.
        self.about = gtk.MenuItem("About") 
        self.about.connect("activate", self.menu_about_response)
        self.about.show()
        self.menu.append(self.about)
        self.quit_item = gtk.MenuItem("Quit Indicator")
        self.quit_item.connect("activate", self.menu_quit_response)
        self.quit_item.show()
        self.menu.append(self.quit_item)

        self.ind.set_menu(self.menu)

        return True

    
    #
    # Create the menu for controlling what exchange mechanism to use.
    # TODO: Find some way to incorporate this into a loop.
    #
#    def set_exchange_menu(self, menuIn):
#        sub_menu = gtk.Menu()
#        par_menu = gtk.MenuItem("Set exchange:")
#        par_menu.set_submenu(sub_menu)

#        sub_group = None
#        values = [("usdeth", "USD / ETH"), 
#                  ("btceth", "BTC / ETH"), 
#                  ("ethusd", "ETH / USD"), 
#                  ("ethbtc", "ETH / BTC")]

 #       for a, b in values:
#            sub_item = gtk.RadioMenuItem(sub_group, b); 
#            sub_item.connect("activate",lambda x: self.set_exchange(a)); 
#            sub_item.show()
#            sub_group = sub_item   
#            sub_menu.append(sub_item)

#        par_menu.show() 
#        sub_menu.show()
#        menuIn.append(par_menu)


    def menu_exchange_create(self, menuIn):
        exchangeMenu = gtk.Menu()
        exMenu = gtk.MenuItem("Set exchange:")
        exMenu.set_submenu(exchangeMenu)
        
        self.ETHtickers = None
        menuUSDETH = gtk.RadioMenuItem(self.ETHtickers,"USD / ETH"); 
        menuUSDETH.connect("activate", 
                           lambda x: self.menu_exchange_response("usdeth")); 
        menuUSDETH.show()        
        self.ETHtickers = menuUSDETH;
        menuBTCETH = gtk.RadioMenuItem(self.ETHtickers,"BTC / ETH"); 
        menuBTCETH.connect("activate", 
                           lambda x: self.menu_exchange_response("btceth")); 
        menuBTCETH.show()
        self.ETHtickers = menuBTCETH;
        menuETHUSD = gtk.RadioMenuItem(self.ETHtickers,"ETH / USD"); 
        menuETHUSD.connect("activate", 
                           lambda x: self.menu_exchange_response("ethusd")); 
        menuETHUSD.show()
        self.ETHtickers = menuETHUSD;
        menuETHBTC = gtk.RadioMenuItem(self.ETHtickers,"ETH / BTC"); 
        menuETHBTC.connect("activate", 
                           lambda x: self.menu_exchange_response("ethbtc")); 
        menuETHBTC.show()
        self.ETHtickers = menuETHBTC;

        exchangeMenu.append(menuUSDETH);
        exchangeMenu.append(menuBTCETH);        
        exchangeMenu.append(menuETHUSD);
        exchangeMenu.append(menuETHBTC);
        exMenu.show() 
        exchangeMenu.show()
        menuIn.append(exMenu)

    #
    # Create the menu for controlling how often the data is refreshed.
    # TODO: Find some way to incorporate this into a loop.
    #
    def menu_refresh_create(self, menuIn):
        refreshmenu = gtk.Menu()
        refMenu = gtk.MenuItem("Set refresh rate:")
        refMenu.set_submenu(refreshmenu)

        self.refreshRates = None
        menuRefresh1 = gtk.RadioMenuItem(self.refreshRates,"30s"); 
        menuRefresh1.connect("activate",
                             lambda x: self.menu_refresh_response(30)); 
        menuRefresh1.show()
        self.refreshRates = menuRefresh1
        menuRefresh2 = gtk.RadioMenuItem(self.refreshRates,"1m"); 
        menuRefresh2.connect("activate",
                             lambda x: self.menu_refresh_response(60)); 
        menuRefresh2.show()
        self.refreshRates = menuRefresh2
        menuRefresh3 = gtk.RadioMenuItem(self.refreshRates,"5m"); 
        menuRefresh3.connect("activate",
                             lambda x: self.menu_refresh_response(300)); 
        menuRefresh3.show()
        self.refreshRates = menuRefresh3
        menuRefresh4 = gtk.RadioMenuItem(self.refreshRates,"10m"); 
        menuRefresh4.connect("activate",
                             lambda x: self.menu_refresh_response(600)); 
        menuRefresh4.show()
        self.refreshRates = menuRefresh4

        refreshmenu.append(menuRefresh1)
        refreshmenu.append(menuRefresh2)
        refreshmenu.append(menuRefresh3)
        refreshmenu.append(menuRefresh4)
        refMenu.show() 
        refreshmenu.show()
        menuIn.append(refMenu)

    #
    # Handle the refresh menu selection.
    #
    def menu_refresh_response(self, newTime):
        self.refresh_frequency = newTime

    #
    # Handle an exchange selection.
    #
    def menu_exchange_response(self, exch):
        self.exchange = exch

    #
    # Handle the quit menu selection.
    #  
    def menu_quit_response(self, widget):
        try:
            print 'Saving Last State.'
            file = open(SETTINGS_FILE, 'w')
            file.write(str(self.APP_DIR) + '\n')
            file.write(str(self.refresh_frequency) + '\n')
            file.write(str(self.exchange))
            file.close()
        except IOError:
            print " ERROR WRITING QUIT STATE"
        gtk.main_quit()
        sys.exit(0)

    #
    # Handle the about menu selection.
    #  
    def menu_about_response(self, widget):
        self.menu.set_sensitive(False)
        widget.set_sensitive(False)
        
        ad = gtk.AboutDialog()
        ad.set_name(APP_NAME)
        ad.set_version(APP_VERSION)
        ad.set_comments("An Ethereum ticker indicator")
        ad.set_license(''+
        'This program is free software: you can redistribute it and/or\n' +
        'modify it under the terms of the GNU General Public License as\n' +
        'published by the Free Software Foundation, either version 3 of\n' +
        'the License, or (at your option) any later version.\n\n' +
        'This program is distributed in the hope that it will be useful,\n' +
        'but WITHOUT ANY WARRANTY; without even the implied warranty of\n' + 
        'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU\n' +
        'General Public License for more details.\n\n' +
        'You should have received a copy of the GNU General Public License\n' +
        'along with this program. If not, see <http://www.gnu.org/licenses/>.')
        ad.set_website('https://github.com/RichHorrocks/ether-price-indicator')
        ad.set_authors(['Written by RichHorrocks.\n' +
                        'Based on code by jj9.\n' +
                        'Tips appreciated! \n\n' +
                        'BTC: 1HCAo4UeQjQrtxCBUzatYxzt8u1UyafPi5\n' +
                        'ETH: I should really get a wallet...\n' ])
        ad.run()
        ad.destroy()
        self.menu.set_sensitive(True)
        widget.set_sensitive(True)
        
    #
    # Get the data by calling the external API.
    #
    def get_api_data(self):
        data = BAD_RETRIEVE
        try :
            r = requests.get("https://etherchain.org/api/basic_stats", 
                             verify=True)
            data = r.json()
            #print r.json()['data']['price']['usd']            
        except requests.exceptions.RequestException as e:
            print e

        return data

    #
    # Output data to the top indicator bar.
    # This is just the currency price, not the block information.    
    #
    def set_price_data(self, data):
        print self.exchange
        output = {
           'usdeth': '$ ' + str(data['usd']),
           'btceth': u'\u0243' + str(data['btc']),
           'ethusd': u'\u039E' + str(1 / data['usd']) + ' / $',
           'ethbtc': u'\u039E' + str(1 / data['btc']) + ' / ' + u'\u0243',
        }.get(self.exchange, "Bad conversion") 

        return output    

    #
    # Add the information about the latest block to the drop-down menu.
    # This data doesn't form any selectable menu items.
    # TODO: Add some post-processing to the numbers being output. For example,
    #       limit to a certain number of significant figures.
    #
    def set_block_data(self, data):
        print data['number']
        self.block_dict["Block"] = data['number']
        self.block_dict["Timestamp"] = data['time']
        self.block_dict["Difficulty"] = data['difficulty']
        self.block_dict["Gas"] = data['gasUsed']
        self.block_dict["Blocktime"] = data['blockTime']

    #
    # Parent function to create user output.
    # TODO: Add caching to allow output to be updated without waiting until
    # the next API poll.
    #
    def set_user_output(self):
        # Get the data.
        data = self.get_api_data()
        
        # Output the currency data to the indicator bar.
        if data == BAD_RETRIEVE or data["status"] != 1:
            output = "Temp Down"
        else:
            output = self.set_price_data(data['data']['price'])
            self.set_block_data(data['data']['blockCount'])
        self.ind.set_label(output)             


if __name__ == "__main__":
    indicator = EtherPriceIndicator()
    indicator.main()
