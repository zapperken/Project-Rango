from django import forms
from django.contrib.auth.models import User
from rango.models import Category, Page, UserProfile

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    # an inline class to provide additional information on the form
    class Meta:
        # provide association between ModelForm and model
        model = Category
        
class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    class Meta:
        # provide association between ModelForm and model
        model = Page
        
        # what fields do we want to include in form?
        # this way we don't need every field in model present
        # some fields may allow NULL values, we may not want to include them..
        # here, we are hiding the foreign key.
        fields = ('title', 'url', 'views')
        
    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        
        # if url is not empty and doesn't start with 'http://', prepend 'http://'
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url
            
        return cleaned_data
        
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('website')
        
        # if website url is not empty and doesn't start with 'http://', prepend 'http://'
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['website'] = url
            
        return cleaned_data