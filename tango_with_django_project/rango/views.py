from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

def index(request):
    context = RequestContext(request)
    context_dict = {'boldmessage': "I am bold font from the context"}
    return render_to_response('rango/index.html', context_dict, context)
    #return HttpResponse('Rango says hello world! <a href="/rango/about/">About</a>')

def about(request):
    return HttpResponse('Rango Says: Here is the about page. <a href="/rango/">Home</a>')