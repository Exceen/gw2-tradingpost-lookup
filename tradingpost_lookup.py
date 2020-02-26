#!/usr/bin/python
from gw2api import gw2api
from collections import defaultdict
        
# http://gw2tno.com/api/finditemidbyname/*
class Item(object):
    def __init__(self, id):
        self.id = str(id)
        self.name = gw2api.get_item_details(id)['name']

        self.ingredients = []
        self.disciplines = []
        self.__set_ingredients()

        self.crafting_information = None
        self.buying_cheaper_than_crafting()

    def __set_ingredients(self):
        recipe_id = gw2api.get_recipe_by_output(self.id)
        if len(recipe_id) != 0:
            recipe = gw2api.get_recipe_details(recipe_id[0])
            self.disciplines = recipe['disciplines']
            for ingredient in recipe['ingredients']:
                self.ingredients.append([Item(ingredient['item_id']), ingredient['count']])
    def __str__(self):
        return 'Item@\'' + self.name + '\''
    def __repr__(self):
        return self.__str__()
    def print_recipe_highlighted(self, items, n=0, c=1, m=1):
        if n > 0:
            if self.id in items:    
                spacing = ' -  ' + (' '*((n-1)*4))
            else:
                spacing = (' '*(n*4))
            print spacing + self.name, str(c) + 'x', '(' + str(c*m) + 'x)'#, tradable(self.id)
        for ingredient in self.ingredients:
            ingredient[0].print_recipe_highlighted(items, n+1, ingredient[1], c)

    def get_item_list(self):
        item_list = self.__get_item_list()

        d = defaultdict(int)
        for k, v in item_list: # I don't really understand this either
            d[k] += v

        # print '-------'
        # print d
        # print '-------'
        # print d.iteritems()
        # print '-------'

        result = [[k, v] for k, v in d.iteritems()]

        return result
    def __get_item_list(self, c=1, l=[]):
        for ingredient in self.ingredients:
            l.append([ingredient[0], ingredient[1]*c])
            ingredient[0].__get_item_list(ingredient[1], l)
        return l
    def get_cheapest_way(self, n=1):
        r = []
        items = self.crafting_information[1]

        for item in items:
            r.append(item[0])

        if len(r) == 0: # if crafting is more expensive than just buying it from the TP
            r.append(self)

        return r
    def buying_cheaper_than_crafting(self):
        if tradable(self.id):
            bp = get_price(self.id)
            cp = 0
            if len(self.ingredients) > 0:
                for ingredient in self.ingredients:
                    if tradable(ingredient[0].id):
                        cp += get_price(ingredient[0].id) * ingredient[1]
                    else:
                        cp += ingredient[0].crafting_information[0]

                if bp < cp:
                    self.crafting_information = [bp, [[self, 1]]]
                else:
                    self.crafting_information = [cp, self.ingredients]

                return bp < cp
            else:
                self.crafting_information = [bp, [[self, 1]]]
                return True
        else:
            cp = 0
            for ingredient in self.ingredients:
                if tradable(ingredient[0].id):
                    cp += get_price(ingredient[0].id) * ingredient[1]
                else:
                    cp += ingredient[0].crafting_information[0]
            self.crafting_information = [cp, self.ingredients]
            return False

def main():
    item = select_item()# = {'name': 'Bolt of Damask', 'item_id': '46741'}

    print '\nRecipe for', item['name'] + ' (' + str(item['data_id']) + '):'
    n = Item(item['data_id'])
    
    final_list = process_data(n)
    n.print_recipe_highlighted([item[0].id for item in final_list])

    total_costs = 0
    print
    print 'Required Items:'
    for item in final_list:
        price = get_price(item[0].id) * item[1]
        total_costs += price

        formatted_price = get_formatted_price(price)

        print ' '*3, item[1], item[0].name, '|', formatted_price if price != 0 else 'Unkown'
    print 
    print 'Disciplines:', ', '.join(n.disciplines)
    print
    print 'Costs:', get_formatted_price(total_costs)

    if tradable(n.id):
        print 'Profit:', get_formatted_price(int(gw2api.get_prices(n.id)['sells']['unit_price'] * 0.85) - total_costs)
        print
        print 'Price:', get_formatted_price(get_price(n.id))
        print 'Listing:', get_formatted_price(gw2api.get_prices(n.id)['sells']['unit_price'])
    else:
        print 'This item is not tradable.'
    
def select_item():
    # Returns an item, selected by the user from a given query
    queue = raw_input('Search: ')

    n = 0
    result_list = gw2api.find_item_id_by_name(queue)
    if len(result_list) == 0:
        print 'Nothing found.'
        quit()
    elif len(result_list) == 1:
        pass #n = 0
    elif len(result_list) > 1:
        for result in result_list:
            item = gw2api.get_item_details(result['data_id'])
            print '['+str(n)+']', item['name'], '|', item['type'], '|', item['rarity']
            n+=1
        n = raw_input('> ')

    return result_list[int(n)]
def process_data(n):
    data = n.crafting_information
    item_list = [item[0] for item in data[1]]
    full_item_list = n.get_item_list()

    final_list = []
    if len(item_list) == 1 and item_list[0] == n:
        final_list.append([n, 1])
    else:
        for ing in get_items_without_amounts(item_list):
            for item in full_item_list:
                if item[0] == ing:
                    final_list.append(item)
    return final_list

def get_items_without_amounts(l, n=0, m=False):
    r = []
    for item in l:
        bar = item.get_cheapest_way()

        if bar == l:
            return l

        foo = get_items_without_amounts(bar)
        r.append(foo)

    cont = True
    while cont:
        r2 = []
        for item in r:
            if type(item) == Item:
                r2.append(item)
            elif type(item) == list:
                for i in item:
                    r2.append(i)

        cont = False
        for item in r2:
            if type(item) == list:
                cont = True

    return r2

def tradable(id):
    try:
        if gw2api.get_prices(id) != None:
            return True
        else:
            return False
    except Exception, e: #throws some weird exception sometimes
        return False
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

    r = price_g + 'g ' + price_s + 's ' + price_c + 'c'
    if int(price) < 0:
        r = '-' + r.replace('-', '')
    return r
def get_price(_id):
    if not tradable(_id):
        return 0
    r = gw2api.get_prices(_id)['buys']['unit_price']
    if r == 0:
        r = gw2api.get_prices(_id)['sells']['unit_price']
    return r

if __name__ == '__main__':
    main()