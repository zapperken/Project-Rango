from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from rango.models import Category, Page
import random


def urlswap(title):
    # changes spaces to underscores
    if ' ' in title:
        return title.replace(' ','_')
    return title.replace('_',' ')

def index(request):
    # obtain context from HTTP request
    context = RequestContext(request)
    
    # query database for a list of ALL categories 
    # order categories by no. of likes in DESC order
    # retrieve top 5 only - or all if less than 5
    # place list in context_dict to be passed to the template
    category_list = Category.objects.order_by('-likes')[:5]
    # retrieve top 5 viewed pages
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories':category_list,
                    'pages':page_list}
    
    # the ff two lines are new.
    # we loop through each category returned and create URL attribute
    # this attribute stores an encoded URL (e.g. spaces replaced with underscores)
    for category in category_list:
        category.url = urlswap(category.name)
    
    # render response and send it back!
    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    context = RequestContext(request)
    what = ['happy','clever','shy']
    context_dict = {'what': random.choice(what)}
    return render_to_response('rango/about.html', context_dict, context)
    
def category(request, category_name_url):
    # obtain context from HTTP request
    context = RequestContext(request)
    
    # change underscores in the category to spaces
    # URLs don't handle spaces well, so encode them as underscores
    # we can simply replace underscores again to get the name
    category_name = urlswap(category_name_url)
    
    # create context dictionary we can pass to template rendering
    # we start by containing the name of category passed by user
    context_dict = {'category_name': category_name}
    
    try:
        # can we find category with given name?
        # if we can't, .get() method raises DoesNotExist exception
        # so .get() method returns one model instance or raise exception
        category = Category.objects.get(name=category_name)
        
        # retrieve all of associated pages.
        # note that filter returns >= 1 model instance
        pages = Page.objects.filter(category=category)
        
        # adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # we also add category object from database to context dictionary
        # we'll use this in the template to verify that category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # we get here if we didn't find specified category.
        # don't do anything - template displays "no category" message
        pass

    # go render the response and return it to the client.
    return render_to_response('rango/category.html', context_dict, context)