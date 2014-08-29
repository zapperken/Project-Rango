import json
import urllib, urllib2

def run_query(search_terms):
    # specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    source = 'Web'
    
    # specify how many results we wish to be returned per page
    # offset specifies where in results list to start from
    # with results_per_page = 10 and offset = 11, this would start from page 2
    results_per_page = 10
    offset = 0
    
    # wrap quotes around our query terms as required by Bing API
    # query we will then user is stored within variable query
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)
    
    # construct latter part of our request's URL
    # sets format of response to JSON and sets other properties
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url, source, results_per_page,
        offset, query
    )
    
    # setup authenticatiopn with Bing servers
    # username MUST be a blank string, and put in your API key!
    username = ''
    bing_api_key = '0xh5dHIYM5i31QcZTR1uTg6+PGD2pEXaYk56MwqhOZs'
    
    # create 'password_manage' which handles authentication for us
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, bing_api_key)
    
    # create our results list which we'll populate
    results = []
    
    try:
        # prepare for connecting to Bing's servers
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        
        # connect to server and read response generated
        print search_url
        response = urllib2.urlopen(search_url).read()
        
        # convert string response to a Python dictionary object
        json_response = json.loads(response)
        
        # loop through each page returned, populating out results list
        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']})
    
    # catch a URLError exception - something went wrong when connecting!
    except urllib2.URLError, e:
        print "Error when querying the Bing API: ", e
        
    # return list of results to calling function
    return results
    
def main():
    query = raw_input("What would you like to search? ").strip()
    
    if query:
        results = run_query(query)
        
        for item, result in enumerate(results):
            print (item + 1)
            print "URL:    ", result['link']
            print "Title:  ", result['title']
            print "Summary:", result['summary']
            print 

if __name__ == '__main__':
    main()