from django import forms
from django.forms import widgets
from todoapp.apps.manager.models import *
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist



class UserAddForm(forms.ModelForm):
    password1=forms.CharField(label='Passowrd',widget=forms.PasswordInput)
    password2=forms.CharField(label='Passowrd Confirmation',widget=forms.PasswordInput)

    class Meta:
        model = User
        fields=('username','first_name','email',)
        labels = {
            'first_name': 'Full name',
        }
        help_texts={
            'username':'',
        }

    def clean_username(self):
        username=self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('This username already exists. Try another.')

    def clean_password2(self):
        password1=self.cleaned_data.get('password1')
        password2=self.cleaned_data.get('password2')

        if password1 and password2 and password1!=password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2
    def save(self, commit=True):
        user=super(UserAddForm,self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


