from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Event


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user
            
            
class OwnerForm(ModelForm):
    class Meta:
      model = User
      fields = ['username', 'email', 'first_name']
  

class EventForm(ModelForm):
    class Meta:
      model = Event
      fields = ['event_name', 'event_content']
    

class AddVendorForm(forms.ModelForm):
    vendor = forms.ModelMultipleChoiceField(queryset=None,widget=forms.CheckboxSelectMultiple(), required=False)
    class Meta:
        model = Event
        fields = ['vendor',]
class AdduserForm(forms.Form):
    email = forms.EmailField()
    ID = (
        ('owner','owner'),
        ('vendor','vendor'),
        ('guest','guest'),
        )
    identity = forms.ChoiceField(widget = forms.RadioSelect,choices = ID,label = "Identity")


class AddUserForm(forms.ModelForm):
    owner = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)
    vendor = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)
    invite = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)
  
    class Meta:
       model = Event
       fields = ['owner', 'vendor', 'invite']
    
class AcceptUserForm(forms.Form):
    button = forms.CharField()  
  
class QuestionForm(forms.Form):
    name = forms.CharField(label='name')
class ChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('extra')
        super(ChoiceForm,self).__init__(*args, **kwargs)
        for i in range(0,extra):
            self.fields['choice_%s' % i] = forms.CharField(label = 'CHOICE%s'%(i+1),required=False)
    
class EssayForm(forms.Form):
    answer = forms.CharField(widget = forms.Textarea) 
   
