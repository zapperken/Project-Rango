from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.bing_search import run_query
from datetime import datetime

def urlswap(title):
    # changes spaces to underscores
    if ' ' in title:
        return title.replace(' ','_')
    return title.replace('_',' ')

def get_category_list():
    # get all categories
    cat_list = Category.objects.all()
    # decode category URLs
    for cat in cat_list:
        cat.url = urlswap(cat.name)
    # return list of category
    return cat_list
    
def index(request):
    context = RequestContext(request)
    # get category list from helper function
    category_list = get_category_list()
    # get top viewed pages
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'cat_list':category_list,
                    'pages':page_list}
    
    if request.session.get('last_visit'):
        # the session has value for the last visit
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits',0)
        
        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
        else:
            # get returns None, and session does not have value for last visit
            request.session['last_visit'] = str(datetime.now())
            request.session['visits'] = 1            
    
    # render and return rendered response back to user
    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    import random
    context = RequestContext(request)
    what = ['happy','clever','shy']    
    context_dict = {'what': random.choice(what)}
    # get category list
    context_dict['cat_list'] = get_category_list()    
    # get number of visits from session
    context_dict['visits'] = request.session.get('visits')
    return render_to_response('rango/about.html', context_dict, context)
    
def category(request, category_name_url):
    # obtain context from HTTP request
    context = RequestContext(request)
    
    result_list = []
    
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # run our Bingp function to get the results list!
            result_list = run_query(query)
    
    # change underscores in the category to spaces
    category_name = urlswap(category_name_url)
    # create context dictionary we can pass to template rendering
    # we start by containing the name of category passed by user
    context_dict = {'category_name': category_name,
                    'category_name_url': category_name_url,
                    'result_list': result_list }
    # get category list
    context_dict['cat_list'] = get_category_list()
    try:
        # can we find category with given name?
        # if we can't, .get() method raises DoesNotExist exception
        # so .get() method returns one model instance or raise exception
        category = Category.objects.get(name=category_name)
        # retrieve all of associated pages.
        # note that filter returns >= 1 model instance
        pages = Page.objects.order_by('-views').filter(category=category)
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

@login_required                              
def add_category(request):
    # get context from the request
    context = RequestContext(request)
    # getting the cat list populated
    context_dict = {'cat_list': get_category_list()}
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
        
    context_dict['form'] = form
    # bad form (or form details), no form supplied..
    # render the form with error messages (if any)
    return render_to_response('rango/add_category.html', 
                              context_dict, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)
    
    category_name = urlswap(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        # check for valid form fields
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
                # go back and render add category form as way of saying 
                # category does not exist
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
    
    context_dict = {'category_name_url': category_name_url,
                 'category_name': category_name,
                 'form': form}
    # getting the cat list populated
    context_dict['cat_list'] = get_category_list()
    return render_to_response('rango/add_page.html',
                context_dict, context)
                 
@login_required
def profile(request):
    context = RequestContext(request)
    context_dict = {'cat_list': get_category_list()}
    u = User.objects.get(username=request.user)
    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None
        
    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render_to_response('rango/profile.html', context_dict, context)    
                    
def track_url(request):
    context = RequestContext(request)
    url = '/rango/'
    # check for page_id 
    if request.method == 'GET':
        if 'page_id' in request.GET:
            # get page_id
            page_id = request.GET['page_id']
            try:
                # try to get page using page_id
                page = Page.objects.get(id=page_id)
                # increment page view
                page.views = page.views + 1
                # get page url for redirection
                url = page.url
                # save new changes
                page.save()
            except Page.DoesNotExist:
                pass
    # redirect to url 
    return redirect(url)
                 
def register(request):
    # like before, get request context
    context = RequestContext(request)
    # a boolean value for telling template whether registration was successful
    # set false initially. code changes value to true when registration succeed
    registered = False
    # if it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        # attempt to grab information from raw form information
        # note we make use of both UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        # if two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # save user's form data to the database
            user = user_form.save()
            # now we hash the password with set_password method
            # once hashed, we can update the user object
            user.set_password(user.password)
            user.save()
            # now sort out the UserProfile instance
            # since we need to set user attribute ourselvs we set commit=False
            # this delays saving model until ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user
            # did the user provide a profile picture?
            # if so, we need to get it from input form, put it in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            # now we save the UserProfile instance
            profile.save()
            # update our variable to tell template registration successful
            registered = True
            
        # invalid form or forms - mistakes or something else?
        # print problems to terminal
        # they'll be shown to user
        else:
            print user_form.errors, profile_form.errors
            
    # not a HTTP POST so we render our form using two ModelForm instances
    # these forms be blank, ready for user input
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    # render the template depending on the context
    return render_to_response(
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form,
               'registered': registered},
            context)
            
def user_login(request):
    # like before get context for the user's request
    context = RequestContext(request)
    # context dictionary to be filled
    context_dict = {}
    # if request is HTTP POST, try pull out relevant information
    if request.method == 'POST':
        # gather username and password provided by user
        # this information is obtained from login form
        username = request.POST['username']
        password = request.POST['password']
        # use Django machinery to attempt to see the username/password
        # combination is valid - a User object is returned if it is
        user = authenticate(username=username, password=password)
        # if we have User object, details are correct
        # if none (Python's way of representing absence of value), no user
        # with matching credentials found
        if user:
            # is account active? it could been disabled
            if user.is_active:
                # if account is valid and active, we can log user in
                # we'll send user back to homepage
                login(request, user)
                url = '/rango/'
                if 'next' in request.POST:
                    url = request.POST['next']
                return redirect(url)
            else:
                # an inactive account was used - no logging in!
                context_dict['error'] = 'Your Rango account is disabled.'
        else:
            # bad login details were provided. so we can't log user in
            print "Invalid login details: {0}, {1}".format(username, password)
            context_dict['error'] = 'Invalid login details supplied.'
    
    # request is not a HTTP POST, so display login form
    # this scenario would most likely be HTTP GET
    #else: # this removed after exercises
    # no context variables to pass to template system, hence
    # blank dictionary object..
    if 'next' in request.GET:
        context_dict['next'] = request.GET['next']
    return render_to_response('rango/login.html', context_dict, context)
   
@login_required
def restricted(request):
    context = RequestContext(request)
    context_dict = {'message':"Since you're logged in, you can see this text!"}
    # getting the cat list populated
    context_dict['cat_list'] = get_category_list()
    return render_to_response('rango/restricted.html', context_dict, context)
    
@login_required
def user_logout(request):
    # since we know user is logged in, we can just log them out.
    logout(request)
    # take user back to homepage
    return redirect('/rango/')
    
def search(request):
    context = RequestContext(request)
    result_list = []
    
    if request.method == 'POST':
        query = request.POST['query'].strip()
        
        if query:
            # run our Bingp function to get the results list!
            result_list = run_query(query)

    # getting the cat list populated
    context_dict = {'cat_list': get_category_list(),
                    'result_list': result_list }
    
    return render_to_response('rango/search.html', 
                              context_dict, context)