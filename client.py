import requests, json, getpass

confluence_url = 'https://cwiki.apache.org/confluence'
space = 'STRATOS'

print '------------------------------'
print 'Stratos Wiki Client'
print '------------------------------'
username = raw_input('Username: ')
password = getpass.getpass()
print 'Reading content...'

def printResponse(r):
	pass #print '{} {}\n'.format(json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ': ')), r)

def get_content_recursively(url):
    #print '----- children recursive: ' + url
    
    r = get_content(url)
    json = r.json()
    expandable_element = None
    title = None
    type = None
    
    try:
        expandable_element = json['_expandable']
        title = json['title']
        print '=== ' + title + ' ==='
        type = json['type']
    except KeyError:
        pass
    
    if expandable_element is None:
        try:
            results_element = r.json()['results']
        except KeyError: pass
        #print '--- results ---'
        for item in results_element:
            try:
                expandable_element = item['_expandable']

                try:
                    title = item['title']
                    #body = item['body']['view']['value']
                    print '=== ' + title + ' ==='
                    #print body
                except KeyError: pass

                process_expandable_element(expandable_element)
            except KeyError: pass
        return
    else:
        process_expandable_element(expandable_element)


def process_expandable_element(expandable_element):

    for key, value in expandable_element.iteritems():
        if key == 'page':
            #print '--- expandable page found: ' + value
            get_content_recursively(value)
        if key == 'children':
            #print '--- expandable children found: ' + value
            get_content_recursively(value)

def get_content(url):
    return get_content_by_title(url, None)
    
def get_content_by_title(url, title):
    #print '==== get-content: ' + url
    url = confluence_url + url
    r = requests.get(url,
	    params={'spaceKey' : space, 'title' : title }, #, 'expand' : 'space,body.view'},
	    auth=(username, password))    
    printResponse(r)
    return r
    
top_page_url = '/rest/api/content'
top_page = get_content_by_title(top_page_url, 'Stratos 4.1.0')

children_url = top_page.json()['results'][0]['_expandable']['children']

children = get_content_recursively(children_url)


#parentPage = r.json()['results'][0]
#pageData = {'type':'comment', 'container':parentPage,
#	'body':{'storage':{'value':"<p>A new comment</p>",'representation':'storage'}}}
#r = requests.post('http://localhost:8080/confluence/rest/api/content',
#	data=json.dumps(pageData),
#	auth=('admin','admin'),
#	headers=({'Content-Type':'application/json'}))
#printResponse(r)

