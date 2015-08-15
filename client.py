#!/usr/local/bin/python

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
#     specific language governing permissions and limitations
# under the License.

import requests, json, getpass, sys, logging as log

confluence_url = 'https://cwiki.apache.org/confluence'
username = None
password = None
space = 'STRATOS'
trace = 'false'

log.basicConfig(level=log.WARN)

def authenticate():
    """
    Authenticate user against the given confluence URL
    :return: True if authenticated successfully else False
    """

    global username
    if username is None:
        username = raw_input('Username: ')

    global password
    if password is None:
        password = getpass.getpass()

    print 'Authenticating...'
    url = confluence_url + '/rest/api/content'
    r = requests.get(url,
                     params={'spaceKey': space},
                     auth=(username, password))

    if (r.status_code == 200):
        print 'Authenticated successfully!'
        return True
    else:
        print 'Invalid credentials'
        username = None
        password = None
        return False


def printResponse(r):
    """
    Print response with JSON formatting
    :param r:
    :return:
    """

    if (trace == 'true' and r is not None):
        print '{} {}\n'.format(json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ': ')), r)


def get_content_recursively(url):
    """
    GET content recursively with the given URL.
    :param url:
    :return:
    """

    r = get_content(url)
    json = r.json()
    expandable_element = None

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
                    # body = item['body']['view']['value']
                except KeyError:
                    pass

                process_expandable_element(expandable_element)
            except KeyError:
                pass
        return
    else:
        process_expandable_element(expandable_element)


def process_expandable_element(expandable_element):
    """
    Process expandable element and invoke get_content_recursively() for each.
    :param expandable_element:
    :return:
    """

    for key, value in expandable_element.iteritems():
        if key == 'page':
            get_content_recursively(value)
        if key == 'children':
            get_content_recursively(value)


def get_content(url, title=None, expand=None):
    """
    GET content with the given URL,
    :param url: content URL
    :param title: title of the content, default is None
    :param expand: items to be expanded; for an example use 'space,body.view'
    to expand body of the content
    :return: HTTP response
    """

    url = confluence_url + url
    r = requests.get(url,
                     params={'spaceKey': space, 'title': title, 'expand': expand},
                     auth=(username, password))
    printResponse(r)
    return r


print '------------------------------------------'
print 'Confluence Client'
print '------------------------------------------'

add_line = False
if confluence_url is not None:
    print 'URL: ' + confluence_url
    add_line = True
else:
    confluence_url = raw_input('Confluence endpoint: ')
if space is not None:
    print 'Space: ' + space
    add_line = True
else:
    space = raw_input('Space: ')

if add_line:
    print '------------------------------------------'


while authenticate() == False:
    authenticate()

def print_menu():
    """
    Print menu options
    :return:
    """

    print ''
    print '------------------------------------------'
    print 'Confluence Client Menu'
    print '------------------------------------------'
    print '1: Find Pages Recursively'
    print '2: Find and Replace Text'
    print '3: Exit'
    print '------------------------------------------'
    print ''
    menu_no = raw_input('Select a menu item: ')
    return menu_no


def find_pages_recursively():
    """
    Find pages recursively and print their titles
    :return:
    """

    print ''
    print '------------------------------------------'
    print 'Find Pages Recursively'
    print '------------------------------------------'
    title = raw_input('Enter page title: ')
    content_url = '/rest/api/content'
    response = get_content(content_url, title)
    json = response.json()

    if(int(json['size']) > 0):
        children_url = json['results'][0]['_expandable']['children']
        print ''
        try:
            children = get_content_recursively(children_url)
            return True
        except KeyboardInterrupt:
            print 'Interrupted!'
            return False
    else:
        print 'Could not find a page with the title \'' + title + '\''
        raw_input("Press any key to continue...")
        return False

def find_and_replace_text():
    """
    Find and replace text in pages recursively
    :return:
    """

    print ''
    print '------------------------------------------'
    print 'Find and Replace Text'
    print '------------------------------------------'
    top_page_title = raw_input('Enter page title: ')
    find_text = raw_input('Find text: ')
    replace_text = raw_input('Replace with: ')
    expand = 'space,body.view'
    content_url = '/rest/api/content'
    top_page = get_content(content_url, top_page_title, expand)


def load_menu():
    """
    Load menu
    :return:
    """

    menu_no = print_menu()
    if (menu_no == '1'):
        find_pages_recursively()
        load_menu()
    elif (menu_no == '3'):
        sys.exit(0)
    else:
        print 'Sorry this feature is still not implemented'
        raw_input("Press any key to continue...")
        load_menu()

# Load menu
load_menu()
