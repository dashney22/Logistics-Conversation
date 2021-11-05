from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Post, User, Profile, Tag, Comment
from django.contrib import messages
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _


illegal_symbols = ['!','#','$','%','^','&','*',
                   '{','}',';',':',"'","<",">",
                   "?","/","|",'"',"(",")","="]


class EditPostForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(EditPostForm,self).__init__(*args,**kwargs)

    class Meta:
        model = Post
        fields = ("title","excerpt","image","content","tags")


    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),widget= forms.CheckboxSelectMultiple)

class UserRegistrationForm(forms.Form):
    username = forms.CharField(label="Enter Username",max_length = 50,help_text= '<span style="color:grey">Enter a username with standard letters, numbers or the following symbols @, ., -, _, +  </span>')
    email = forms.EmailField(label= "Enter email address")
    first_name = forms.CharField(label = "Enter your first name")
    last_name = forms.CharField(label = "Enter your last name")
    p1 = forms.CharField(label = "Enter your password", widget = forms.PasswordInput())
    p2 = forms.CharField(label = "Confirm your password", widget = forms.PasswordInput())

    def save(self,commit= True):
        user = User.objects.create_user(username = self.cleaned_data['username'],
                                        email = self.cleaned_data['email'],
                                        first_name = self.cleaned_data['first_name'],
                                        last_name = self.cleaned_data['last_name'],
                                        password = self.cleaned_data['p2']
                                        )

        if commit:
            user.save()
        return user
    def clean_test(self):
        cleaned_data = super(UserRegistrationForm,self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        p1 = cleaned_data.get('p1')
        p2 = cleaned_data.get('p2')
        print("In user registration clean")
        if (username != ""):
            if any(c in illegal_symbols for c in username):
                self.add_error(None,ValidationError("Username contains illegal symbols, please use only letters, numbers and ',','.'"))
        else:
            self.add_error(None,ValidationError("Username cannot be blank"))
            

        if (len(User.objects.filter(username=username)) != 0):
            self.add_error(None,ValidationError("Username already exists"))

        if (len(User.objects.filter(email=email)) != 0):
            self.add_error(None,ValidationError("Email address already exists"))
        
        if (p1 != ""):
            if(len(p1)>5):
                if(p1!=p2):
                    self.add_error(None,ValidationError("Passwords do not match"))
            else:
                self.add_error(None,ValidationError("Passwords less than 5 characters"))
        else:
            self.add_error(None,ValidationError("Password cannot be empty"))


class ProfileRegistrationForm(ModelForm):
    class Meta:
        model = Profile
        fields = ()

    def save(self,user_information,commit=True):

        profile = super(ProfileRegistrationForm,self).save(commit=False)

        profile.user = user_information

        if commit:
            profile.save()
        return profile

class ProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ("About","title","position","profile_picture",)

class CreatePostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("title","excerpt","image","content","tags")

    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),widget= forms.CheckboxSelectMultiple)

    def save(self, p_author, image_file, commit = True):
        post_c = super(CreatePostForm,self).save(commit=False)
        post_c.author = p_author
        post_c.image = image_file
        
        post_c.slug = post_c.title.lower().replace(" ","-")+"-"+post_c.author.username.lower().replace(" ","-")
        if commit:
            post_c.save()
            post_c.tags.add(*self.cleaned_data['tags'])
            # post_c.save()
        return post_c

class CreateTagForm(ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"

class CreateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("body","image",)

    def save(self,author,image_file,original_post,commit=True):

        comment_c = super(CreateCommentForm,self).save(commit = False)

        comment_c.commentor = author
        comment_c.post = original_post
        comment_c.image = image_file

        if commit:
            comment_c.save()
        return comment_c

def phone_number_validator(value):
    if value[0] == "0":
        if len(value) != 10:
            raise ValidationError(_('%(value)s is not a valid phone number. Length is too long'))
        elif not value.isdecimal():
            raise ValidationError(_('%(value)s is not a valid phone number. Contains letters or symbols'))
    elif value[0] == "+":
        if len(value) != 12:
            raise ValidationError(_('%(value)s is not a valid phone number'))
        elif not value[1:].isdecimal():
            raise ValidationError(_('%(value)s is not a valid phone number. Contains letters or symbols'))



class ContactUsForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField()
    phone = forms.CharField(validators= [phone_number_validator])
    subject = forms.CharField()
    body = forms.CharField()