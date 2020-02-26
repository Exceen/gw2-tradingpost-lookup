#!/usr/bin/python
from gw2api import gw2api
from os import system
from time import sleep
from urllib2 import HTTPError

from sys import stdout

# item = gw2api.find_item_id_by_name('Charged Lodestone')[0]
# item = {"name":"Poly-luminescent Undulating Refractor (Black)","item_id":"67375"}

notify = False

#seconds:
refresh = 60 / 12
#scaling, animation size until next refresh
scaling = 10

def select_item():
    result_list = gw2api.get_current_transactions_sells()

    n = 0

    if len(result_list) == 0:
        print 'No transactions found.'
        quit()
    else:
        for result in result_list:
            item = gw2api.get_item_details(result['item_id'])
            print '['+str(n)+']', item['name'], '|', item['type'], '|', item['rarity']
            n+=1
        n = raw_input('> ')

    item = result_list[int(n)]
    item['name'] = gw2api.get_item_details(item['item_id'])['name']

    return item

def main():
    item = select_item()
    
    while True:
        own_listings = []
        n = 1
        while True:
            r = True
            try:
                listings = get_listings(item['item_id'])
                for listing in gw2api.get_current_transactions_sells():
                    if listing['item_id'] == item['item_id']:
                        own_listings.append(listing['price'])
                break
            except HTTPError, e:
                if r:
                    print e
                    r = False
                sleep(10)
                
        system('clear')
        if len(own_listings) == 0:
            print 'Your buy order for \'' + item['name'] + '\' was not found.'
        else:
            print item['name'], '\n'
            first = True
            firstChecked = False
            for listing in listings:
                if listing['unit_price'] in own_listings:
                    if notify and not first and not firstChecked:
                        system('terminal-notifier -title \'Guild Wars 2 - TP\' -message \'Someone overbid you!\' -subtitle \'' + item['name'] + '\'')
                    # next((x for x in test_list if x.value == value), None)
                    # own_listing = (item for item in own_listings if item['unit_price'] == ownli)
                    foo = '<-- (' + str(listing['quantity']) + 'x)'
                    firstChecked = True
                else:
                    foo = ''
                first = False

                print ' ' * 3, str(n).rjust(2), '|', (str(listing['quantity']) + 'x').rjust(4+1), '|', get_formatted_price_extended(listing['unit_price']).rjust(13), foo
                if n%5 == 0 and n != len(listings):
                    print ' ' * 3, '-' * 26
                n += 1
            print ''

        print '|' + ('-' * refresh*scaling) + '|'
        stdout.write('|')
        stdout.flush()
        for x in xrange(0, refresh*scaling):
            stdout.write('.')
            stdout.flush()
            sleep(1.0/scaling)
        print '|'
        # print 'refreshing...'

        # sleep(refresh)

def get_formatted_price(price):
    price = str(price)
    if len(price) % 2 and len(price) < 4:
        price = '0' + price 

    price_g = price[:-4] if len(price) > 4 else '0'
    price_s = price[-4:][:2] if len(price) > 2 else '0'
    price_c = price[-2:]

    if len(price_c) == 2 and price_c[:1] is '0':
        price_c = price_c[1:]

    if len(price_s) == 2 and price_s[:1] is '0':
        price_s = price_s[1:]

    return price_g + 'g ' + price_s + 's ' + price_c + 'c'

def get_formatted_price_extended(price):
    price = str(price)
    if len(price) % 2 and len(price) < 4:
        price = '0' + price 

    price_g = price[:-4] if len(price) > 4 else '0'
    price_s = price[-4:][:2] if len(price) > 2 else '0'
    price_c = price[-2:]

    r = price_g + 'g ' + price_s + 's ' + price_c + 'c'
    r = r.replace(' 0', '  ')

    return r

def get_listings(_id):
    return gw2api.get_listings(_id)['sells'][:15]

if __name__ == '__main__':
    main()