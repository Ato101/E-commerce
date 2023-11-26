from django import forms

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password',
        'class': 'form-control'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confrim password',
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
    def __init__(self,*args,**kwargs):
        super(RegisterForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegisterForm,self).clean()
        password = cleaned_data.get('password1')
        comfirm_password = cleaned_data.get('password2')
        if password != comfirm_password:
            raise forms.ValidationError(
                'Password is not the same'
            )






