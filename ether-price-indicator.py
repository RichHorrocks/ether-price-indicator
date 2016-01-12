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
import time
import datetime
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

    # A dictionary representing the available price converstions.
    price_dict = { "usdeth": "None",
                   "btceth": "None",
                   "ethusd": "None",
                   "ethbtc": "None" }

    # Global variables for setting values in sub-menus.
    refresh_frequency = 3
    exchange = 'usdeth'

    def __init__(self):
        """Initialise."""
        self.init_from_file()
        self.ind = appindicator.Indicator(
            "ether-indicator", 
            self.ICON_FILE,
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

    def init_callback(self):
        """Call-back whenever the timer tells us to."""
        self.set_user_output()
        self.menu_setup()

        # Must return true for the timeout_add function to work.
        return True

    def init_from_file(self):
        """Initialise from the settings file, if it exists."""
        try:
            with open(SETTINGS_FILE): pass
        except IOError:
            self.create_log("Need to make new file.")
            file = open(SETTINGS_FILE, 'w')
            file.write(os.getcwd() + '\n')
            file.write('30\n')
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
        """Set the directory where the application is stored."""
        self.ICON_FILE = os.path.abspath(currDir + "/res/ether_icon.png")
        self.APP_DIR = currDir

    def main(self):
        """Kick things off."""
        self.init_callback()
        gtk.timeout_add(self.refresh_frequency * 1000, self.init_callback)
        gtk.main()

    def menu_setup_add_separator(self, menu):
        """Create a menu separator."""
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

    def menu_setup(self):
        """Create the drop-down GTK menu."""
        self.menu = gtk.Menu()

        # Add data for the latest block.
        self.block_item = gtk.MenuItem("Last block we know about:")
        self.block_item.show()
        self.menu.append(self.block_item)

        for key, value in self.block_dict.iteritems():
            item = gtk.MenuItem("    " + key + ":  " + str(value))
            item.show()
            self.menu.append(item)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        self.update = gtk.MenuItem("Update block data...") 
        self.update.connect("activate", self.menu_update_response)
        self.update.show()
        self.menu.append(self.update)

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
    # TODO: Find some way to incorporate this into a loop.
    #
    def menu_exchange_create(self, menuIn):
        """Create the menu for controlling what exchange mechanism to use."""
        exchangeMenu = gtk.Menu()
        exMenu = gtk.MenuItem("Set exchange:")
        exMenu.set_submenu(exchangeMenu)
        
        self.ETHtickers = None
        menuUSDETH = gtk.RadioMenuItem(self.ETHtickers,"USD / ETH"); 
        menuUSDETH.connect("activate", 
                           lambda x: self.menu_exchange_response("usdeth")); 
        menuUSDETH.show()        
        if (self.exchange == "usdeth"):
            menuUSDETH.set_active(True)
        self.ETHtickers = menuUSDETH;
        menuBTCETH = gtk.RadioMenuItem(self.ETHtickers,"BTC / ETH"); 
        menuBTCETH.connect("activate", 
                           lambda x: self.menu_exchange_response("btceth")); 
        menuBTCETH.show()
        if (self.exchange == "btceth"):
            menuBTCETH.set_active(True)
        self.ETHtickers = menuBTCETH;
        menuETHUSD = gtk.RadioMenuItem(self.ETHtickers,"ETH / USD"); 
        menuETHUSD.connect("activate", 
                           lambda x: self.menu_exchange_response("ethusd")); 
        menuETHUSD.show()
        if (self.exchange == "ethusd"):
            menuETHUSD.set_active(True)
        self.ETHtickers = menuETHUSD;
        menuETHBTC = gtk.RadioMenuItem(self.ETHtickers,"ETH / BTC"); 
        menuETHBTC.connect("activate", 
                           lambda x: self.menu_exchange_response("ethbtc")); 
        menuETHBTC.show()
        if (self.exchange == "ethbtc"):
            menuETHBTC.set_active(True)
        self.ETHtickers = menuETHBTC;

        exchangeMenu.append(menuUSDETH);
        exchangeMenu.append(menuBTCETH);        
        exchangeMenu.append(menuETHUSD);
        exchangeMenu.append(menuETHBTC);
        exMenu.show() 
        exchangeMenu.show()
        menuIn.append(exMenu)

    #
    # TODO: Find some way to incorporate this into a loop.
    #
    def menu_refresh_create(self, menuIn):
        """Create the menu for controlling how often the data is refreshed."""
        refreshmenu = gtk.Menu()
        refMenu = gtk.MenuItem("Set refresh rate:")
        refMenu.set_submenu(refreshmenu)

        self.refreshRates = None
        menuRefresh1 = gtk.RadioMenuItem(self.refreshRates,"30s"); 
        menuRefresh1.connect("activate",
                             lambda x: self.menu_refresh_response(30)); 
        menuRefresh1.show()
        if (self.refresh_frequency == 30):
            menuRefresh1.set_active(True)
        self.refreshRates = menuRefresh1
        menuRefresh2 = gtk.RadioMenuItem(self.refreshRates,"1m"); 
        menuRefresh2.connect("activate",
                             lambda x: self.menu_refresh_response(60)); 
        menuRefresh2.show()
        if (self.refresh_frequency == 60):
            menuRefresh2.set_active(True)
        self.refreshRates = menuRefresh2
        menuRefresh3 = gtk.RadioMenuItem(self.refreshRates,"5m"); 
        menuRefresh3.connect("activate",
                             lambda x: self.menu_refresh_response(300)); 
        menuRefresh3.show()
        if (self.refresh_frequency == 300):
            menuRefresh3.set_active(True)
        self.refreshRates = menuRefresh3
        menuRefresh4 = gtk.RadioMenuItem(self.refreshRates,"10m"); 
        menuRefresh4.connect("activate",
                             lambda x: self.menu_refresh_response(600)); 
        menuRefresh4.show()
        if (self.refresh_frequency == 600):
            menuRefresh4.set_active(True)
        self.refreshRates = menuRefresh4

        refreshmenu.append(menuRefresh1)
        refreshmenu.append(menuRefresh2)
        refreshmenu.append(menuRefresh3)
        refreshmenu.append(menuRefresh4)
        refMenu.show() 
        refreshmenu.show()
        menuIn.append(refMenu)    

    def menu_update_response(self, widget):
        """Handle the update menu selection."""        
        self.create_log("Updating block data")
        self.init_callback()

    def menu_refresh_response(self, newTime):
        """Handle the refresh menu selection."""
        self.create_log("Setting refresh to " + str(newTime))
        self.refresh_frequency = newTime

    def menu_exchange_response(self, exch):
        """Handle an exchange selection."""
        self.create_log("Setting exchange to " + exch)
        self.exchange = exch
        output = self.set_price_data_user()
        self.ind.set_label(output)             

    def menu_quit_response(self, widget):
        """Handle the quit menu selection."""
        try:
            self.create_log("Saving Last State.")
            file = open(SETTINGS_FILE, 'w')
            file.write(str(self.APP_DIR) + '\n')
            file.write(str(self.refresh_frequency) + '\n')
            file.write(str(self.exchange))
            file.close()
        except IOError:
            self.create_log("ERROR WRITING QUIT STATE")
        gtk.main_quit()
        sys.exit(0)

    def menu_about_response(self, widget):
        """Handle the about menu selection."""
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
        
    def get_api_data(self):
        """Get the data by calling the external API."""
        data = BAD_RETRIEVE
        try :
            r = requests.get("https://etherchain.org/api/basic_stats", 
                             verify=True)
            data = r.json()            
        except requests.exceptions.RequestException as e:
            print e

        return data

    def set_price_data_user(self):
        """Output the price data to the user."""
        output = {
           'usdeth': self.price_dict['usdeth'],
           'btceth': self.price_dict['btceth'],
           'ethusd': self.price_dict['ethusd'],
           'ethbtc': self.price_dict['ethbtc']
        }.get(self.exchange, "Bad conversion") 

        return output       

    def set_price_data(self, data):
        """Cache the price data in a dictionary."""

        # Calculate and cache the current price conversions.
        # Note that we're rounding to 4 d.p.
        self.price_dict['usdeth'] = '$ ' + "{0:.4f}".format(data['usd'])
        self.price_dict['btceth'] = u'\u0243' + "{0:.4f}".format(data['btc'])
        self.price_dict['ethusd'] = u'\u039E' + \
                                    "{0:.4f}".format(1 / data['usd']) + ' / $'
        self.price_dict['ethbtc'] = u'\u039E' + \
                                    "{0:.4f}".format(1 / data['btc']) + \
                                    ' / ' + u'\u0243'

    def set_block_data(self, data):
        """Add the information about the latest block to the drop-down menu.
        This data doesn't form any selectable menu items.
        """
        self.block_dict["Block"] = data['number']
        t = time.strptime(data['time'], "%Y-%m-%dT%H:%M:%S.000Z")
        self.block_dict["Timestamp"] = time.asctime(t)
        self.block_dict["Difficulty"] = data['difficulty']
        self.block_dict["Gas"] = data['gasUsed']
        self.block_dict["Blocktime"] = data['blockTime']

    def set_user_output(self):
        """Create user output."""
        # Get the data.
        data = self.get_api_data()
        
        # Output the currency data to the indicator bar.
        if data == BAD_RETRIEVE or data["status"] != 1:
            output = "Temp Down"
        else:
            self.set_price_data(data['data']['price'])
            output = self.set_price_data_user()
            self.set_block_data(data['data']['blockCount'])
        self.ind.set_label(output)             

    def create_log(self, str):
        print "{:%Y-%m-%d %H:%M:%S} - ".format(datetime.datetime.now()) + str

if __name__ == "__main__":
    indicator = EtherPriceIndicator()
    indicator.main()
