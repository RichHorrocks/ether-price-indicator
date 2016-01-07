import requests

def getEtherChainData():
    try :
#        r = requests.get("https://btc-e.com/api/2/ltc_eur/ticker", verify=False)
        r = requests.get("https://etherchain.org/api/blocks/count", verify=False)
            #web_page = urllib2.urlopen("http://www.bbc.co.uk/news").read()
            #data = json.loads(web_page)
        print r
    except requests.exceptions.RequestException as e:    # This is the correct syntax
        print e
        #except urllib2.HTTPError as e:
        #    print("HTTPERROR: ", e.code)
        #except urllib2.URLError as e:
        #    print("URLERROR: ", e.reason)

getEtherChainData();
