#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import requests, json as json, getpass, sys, logging as log, html

endpoint = 'https://cwiki.apache.org/confluence'
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
    url = endpoint + '/rest/api/content'
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
        print generate_json(r)


def generate_json(r):
    return '{} {}\n'.format(json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ': ')), r)


def traverse_recursively(url, find_text, replace_text):
    """
    Traverse content recursively with the given URL.
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
                    if(find_text is not None and replace_text is not None):
                        print 'Updating page: ' + title
                        update_page(item, find_text, replace_text)
                except KeyError:
                    pass

                process_expandable_element(expandable_element, find_text, replace_text)
            except KeyError:
                pass
        return
    else:
        process_expandable_element(expandable_element, find_text, replace_text)


def process_expandable_element(expandable_element, find_text, replace_text):
    """
    Process expandable element and invoke get_content_recursively() for each.
    :param expandable_element:
    :return:
    """

    for key, value in expandable_element.iteritems():
        if key == 'page':
            traverse_recursively(value, find_text, replace_text)
        if key == 'children':
            traverse_recursively(value, find_text, replace_text)


def get_content(url, title=None, expand=None):
    """
    GET content with the given URL,
    :param url: content URL
    :param title: title of the content, default is None
    :param expand: items to be expanded; for an example use 'space,body.view'
    to expand body of the content
    :return: HTTP response
    """

    url = endpoint + url
    r = requests.get(url,
                     params={'spaceKey': space, 'title': title, 'expand': expand},
                     auth=(username, password))
    printResponse(r)
    return r

def update_content(url, data):
    """
    Update content
    :param url: content URL
    :param data: data to be updated
    :return:
    """
    if(trace == 'true'):
        print 'Updating ' + url
        print data

    url = endpoint + url
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.put(url,
                 data,
                 headers=headers,
                 auth=(username, password))

    print_line()
    print 'Status Code: ' + str(r.status_code)
    print_line()
    if(r.status_code != 200):
        print 'ERROR: ' + r._content
        print_line()
    return r

def print_line():
    line = ''
    for i in range(1, 50):
        line = '-' + line
    print line

print_line()
print 'Confluence Client'
print_line()

add_line = False
if endpoint is not None:
    print 'Endpoint: ' + endpoint
    add_line = True
else:
    endpoint = raw_input('Confluence endpoint: ')
if space is not None:
    print 'Space: ' + space
    add_line = True
else:
    space = raw_input('Space: ')

if add_line:
    print_line()


while authenticate() == False:
    authenticate()

def print_menu():
    """
    Print menu options
    :return:
    """

    print ''
    print_line()
    print 'Confluence Client Menu'
    print_line()
    print '1: Find Pages Recursively'
    print '2: Find and Replace Text'
    print '3: Exit'
    print_line()
    print ''
    menu_no = raw_input('Select a menu item: ')
    return menu_no


def find_pages_recursively(find_text = None, replace_text = None):
    """
    Find pages recursively and print their titles
    :return:
    """

    print ''
    print_line()
    print 'Find Pages Recursively'
    print_line()
    title = raw_input('Enter page title: ')
    content_url = '/rest/api/content'
    response = get_content(content_url, title)
    json = response.json()

    if(int(json['size']) == 0):
        print 'Could not find a page with the title \'' + title + '\''
        raw_input("Press any key to continue...")
        return False

    children_url = json['results'][0]['_expandable']['children']
    print ''
    try:
        traverse_recursively(children_url, find_text, replace_text)
        return True
    except KeyboardInterrupt:
        print 'Interrupted!'
        return False


def find_and_replace_text():
    """
    Find and replace text in pages recursively
    :return:
    """

    print ''
    print_line()
    print 'Find and Replace Text'
    print_line()
    title = raw_input('Enter page title: ')

    expand = 'space,body.view,version'
    content_url = '/rest/api/content'
    response = get_content(content_url, title, expand)
    json_dict = response.json();
    if(int(json_dict['size']) == 0):
        print 'Could not find a page with the title \'' + title + '\''
        raw_input("Press any key to continue...")
        return

    find_text = raw_input('Find text: ')
    replace_text = raw_input('Replace with: ')

    page = json_dict["results"][0]
    update_page(page, find_text, replace_text)

    children_url = json_dict['results'][0]['_expandable']['children']
    traverse_recursively(children_url, find_text, replace_text)

def update_page(page, find_text, replace_text):
    """
    Update page by replacing text
    :param page:
    :param find_text:
    :param replace_text:
    :return:
    """
    url = page['body']['view']['_expandable']['content']
    body = page['body']['view']['value']
    # Update page body

    # regexp = "&.+?;"
    # list_of_html = re.findall(regexp, body) #finds all html entites in page
    # for e in list_of_html:
    #     h = HTMLParser.HTMLParser()
    #     unescaped = h.unescape(e) #finds the unescaped value of the html entity
    #     body = body.replace(e, unescaped)

    body = body.replace(find_text, replace_text)

    page['body']['storage'] = {"value": body, "representation": "storage"}
    page['body']['view']['value'] = None
    # Update version
    version = page['version']
    version['number'] = int(version['number']) + 1
    page['version'] = version
    page['version']['by'] = None
    page['version']['message'] = 'Replacing text ' + find_text + ' with ' + replace_text
    json_dict = json.dumps(page, ensure_ascii=False).encode('utf-8')
    update_content(url, json_dict)


def load_menu():
    """
    Load menu
    :return:
    """

    menu_no = print_menu()
    if (menu_no == '1'):
        find_pages_recursively()
        load_menu()
    elif (menu_no == '2'):
        find_and_replace_text()
        load_menu()
    elif (menu_no == '3'):
        sys.exit(0)
    else:
        print 'Sorry this feature is still not implemented'
        raw_input("Press any key to continue...")
        load_menu()

# Load menu
load_menu()
