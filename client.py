#!/usr/local/bin/python

import requests, json, getpass, sys

confluence_url = 'https://cwiki.apache.org/confluence'
username = None
password = None
space = 'STRATOS'
trace = 'false'

def authenticate():
    global username 
    username = raw_input('Username: ')
    
    global password 
    password = getpass.getpass()
    print 'Authenticating...'
    url = confluence_url + '/rest/api/content'
    r = requests.get(url,
	    params={'spaceKey' : space},
	    auth=(username, password))
    if(r.status_code == 200):
        print 'Authenticated successfully!'
    else:
        print 'Invalid credentials'
        sys.exit(0)
        
def printResponse(r):
    if(trace == 'true' and r is not None):
	    print '{} {}\n'.format(json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ': ')), r)

def get_content_recursively(url):    
    r = get_content(url)
    json = r.json()
    
    expandable_element = None
    title = None
    
    try:
        expandable_element = json['_expandable']
        title = json['title']
        print '=== ' + title + ' ==='
    except KeyError:
        pass
    
    if expandable_element is None:
        try:
            results_element = r.json()['results']
        except KeyError: 
            pass

        for item in results_element:
            try:
                expandable_element = item['_expandable']

                try:
                    title = item['title']
                    print '=== ' + title + ' ==='
                    #body = item['body']['view']['value']
                except KeyError: 
                    pass

                process_expandable_element(expandable_element)
            except KeyError: 
                pass
        return
    else:
        process_expandable_element(expandable_element)


def process_expandable_element(expandable_element):
    for key, value in expandable_element.iteritems():
        if key == 'page':
            get_content_recursively(value)
        if key == 'children':
            get_content_recursively(value)

def get_content(url):
    return get_content_by_title(url, None)
    
def get_content_by_title(url, title):
    url = confluence_url + url
    r = requests.get(url,
	    params={'spaceKey' : space, 'title' : title }, #, 'expand' : 'space,body.view'},
	    auth=(username, password))    
    printResponse(r)
    return r
    
print '------------------------------'
print 'Confluence Client'
print '------------------------------'
authenticate()

def print_menu():
    print ''
    print '------------------------------'
    print 'Confluence Client Menu'
    print '------------------------------'
    print '1: Find Pages Recursively'
    print '2: Find and Replace Text'
    print '3: Exit'
    print '------------------------------'
    print ''
    menu_no = raw_input('Select a menu item: ')
    return menu_no

def find_pages_recursively():
    print ''
    print '------------------------------'
    print 'Find Pages Recursively'
    print '------------------------------'
    top_page_title = raw_input('Enter page title: ')
    print ''
    content_url = '/rest/api/content'
    top_page = get_content_by_title(content_url, top_page_title)
    children_url = top_page.json()['results'][0]['_expandable']['children']
    children = get_content_recursively(children_url)

def load_menu():
    menu_no = print_menu()
    if (menu_no == '1'):
        find_pages_recursively()
        load_menu()
    elif (menu_no == '3'):
        sys.exit(0)
    else:
        print 'Not implemented!'
        load_menu()
        
load_menu()
    
