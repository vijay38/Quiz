from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Submit,Div

class UserForm(forms.Form):
    Name=forms.CharField(label="Name:",widget=forms.TextInput(attrs={'placeholder': 'మీ పేరు','size': '25','style': 'font-size: 2rem'}))
    Place=forms.CharField(label="Place:",widget=forms.TextInput(attrs={'placeholder': 'మీ ప్రాంతము','size': '25','style': 'font-size: 2rem'}))
    Phone=forms.CharField(label="Phone:",widget=forms.TextInput(attrs={'placeholder': 'ఫోన్ నెంబర్','minlength': '10','maxlength': '10','size': '25','style': 'font-size: 2rem'}))
    required_css_class = 'required'
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.helper=FormHelper()
        self.helper.form_method="post"
        self.helper.form_action="instructions"

        self.helper.layout=Layout(
            Div(
                "Name",
                css_class='back1'
            ),
            Div(
                "Place",
                css_class='back2'
            ),
            Div(
                "Phone",
                css_class='back1'
            ),
            Submit('submit','Next',css_class='btn-success')
        )
