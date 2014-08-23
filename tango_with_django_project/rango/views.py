from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

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
    import random
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
    context_dict = {'category_name': category_name,
                    'category_name_url': category_name_url}
    
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
    return render_to_response('rango/category.html', 
                              context_dict, context)
    
def add_category(request):
    # get context from the request
    context = RequestContext(request)
    
    # HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        # have we been provided with valid form?
        if form.is_valid():
            # save new category to the database
            form.save(commit=True)
            
            # now call index() view
            # the user will be shown the homepage
            return index(request)
        else:
            # supplied form contained errors - just print them to terminal
            print form.errors
    else:
        # if request was not POST, display the form to enter details
        form = CategoryForm()
        
    # bad form (or form details), no form supplied..
    # render the form with error messages (if any)
    return render_to_response('rango/add_category.html', 
                              {'form':form}, context)

def add_page(request, category_name_url):
    context = RequestContext(request)
    
    category_name = urlswap(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            # this time we can't commit straight away
            # not all fields are automatically populated
            page = form.save(commit=False)
            
            # retrieve the associated Category object so we can add it
            # wrap code in try block - check category actually exist
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # if we get here, category does not exist
                # go back and render add category form as way of saying category does not exist
                return render_to_response('rango/add_category.html', {}, context)
            
            # also create a default value for number of views
            page.views = 0
            
            # with this we can save our new model instance
            page.save()
            
            # now that page is saved, display category instead
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()
        
    return render_to_response('rango/add_page.html',
                {'category_name_url': category_name_url,
                 'category_name': category_name,
                 'form': form}, context)