from distutils.command import check
from wsgiref import validate
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Post, User, Profile, Tag, Comment
from django.contrib import messages
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email

common_passwords = ['password','1234','qwerty','asdfg','4321','iloveyou','11111','123123','abc123',
					'qwerty','1q2w3e4r','admin','qwertyuiop','lovely','princess','dragon']

"""
Symbols that are to be excluded from usernames by convention to prevent sql injections and other 
potential problems
"""
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
	checked = forms.BooleanField(label= "Agree Disclaimer")

	def save(self,commit= True):
		user = User.objects.create_user(username = self.cleaned_data['username'],
										email = self.cleaned_data['email'],
										first_name = self.cleaned_data['first_name'],
										last_name = self.cleaned_data['last_name'],
										checked = self.cleaned_data['checked'],
										password = self.cleaned_data['p2']
										)

		if commit:
			user.save()
		return user


	def clean_username(self):
		
		username = self.cleaned_data['username']
		r = User.objects.filter(username=username)
		if r.count():
			self.add_error(None,ValidationError("Username already exists"))
			# raise forms.ValidationError("Username already exists")
		for symbol in illegal_symbols:
			if username.find(symbol) != -1:
				self.add_error(None,ValidationError("Username contains an illegal symbol: {}. Please remove it".format(symbol)))
				# raise forms.ValidationError("Username contains an illegal symbol: {}. Please remove it.".format(symbol))
		
		if username.find(" ")!=-1:
			self.add_error(None,ValidationError("Username contains a space symbol. Please remove it"))

		if len(username) < 4:
			self.add_error(None,ValidationError("Username is too short. Please enter a username with 4 or more values"))
		return username

	"""
	Clean email is used to test that an email address has been entered and follows the normal conventions of containing
	an @ symbol
	"""
	def clean_email(self):
		email = self.cleaned_data['email']
		if email == None:
			self.add_error(None,ValidationError("Email is empty"))
			# raise forms.ValidationError("Email is empty")
		if email.find('@') == -1:
			self.add_error(None,ValidationError("@ symbol is missing in email address"))
		try:
			validate_email(email)
		except ValidationError as e:
			self.add_error(None,ValidationError("The email address entered is not acceptable"))

		return email	

	"""
	Clean password is used to compare the first and second password that was entered to ensure that they are the same,
	to ensure that the password does not contain any of the words in the list of illegal words, that the password is 
	longer than 7 letters and that the person has not used their name or surname in the password
	"""
	def clean_p2(self):
		print("HERER")
		p1 = self.cleaned_data['p1']
		p2 = self.cleaned_data['p2']
		name = self.cleaned_data['first_name'].lower()
		sname = self.cleaned_data['last_name'].lower()
		if p1 and p2 and p1 != p2:
			print("Don't match")
			self.add_error(None,ValidationError("Passwords don't match"))
			# raise forms.ValidationError("Passwords don't match")
		if len(p2) <7:
			self.add_error(None,ValidationError("Passwords are too short"))
			# raise forms.ValidationError("Passwords too short")
		for password in common_passwords:
			if p2.lower().find(password) != -1:
				print("In list")
				self.add_error(None,ValidationError("Password is too simple"))
				# raise forms.ValidationError("Password is too simple")
		if p2.lower().find(name) != -1 or p2.lower().find(sname) != -1:
			self.add_error(None,ValidationError("Please do not use your name or surname in password"))	
		return p2

	"""
	Clean first name is used to ensure that a first name was entered on the form
	"""
	def clean_first_name(self):
		first_name = self.cleaned_data['first_name']

		if first_name == None:
			self.add_error(None,ValidationError("First name not entered"))
			# raise forms.ValidationError("First name not entered")
		return first_name

	"""
	Clean last name is used to make sure that a last name was entered on the form
	"""
	def clean_last_name(self):
		last_name = self.cleaned_data['last_name']

		if last_name == None:
			self.add_error(None,ValidationError("Last name not entered"))
			# raise forms.ValidationError("Last name not entered")
		return last_name
	def clean_checked(self):
		checked = self.cleaned_data['checked']

		if checked == False:
			self.add_error(None,ValidationError("You must agree to the POPI act in order to gain access to the Logistics Conversation Portal"))
		return checked
	# def clean_test(self):
	# 	cleaned_data = super(UserRegistrationForm,self).clean()
	# 	username = cleaned_data.get('username')
	# 	email = cleaned_data.get('email')
	# 	checked = cleaned_data.get('checked')
	# 	p1 = cleaned_data.get('p1')
	# 	p2 = cleaned_data.get('p2')
	# 	print("In user registration clean")

	# 	if(not checked):
	# 		self.add_error(None,ValidationError("Please Agree to the Disclaimer"))
	# 		return False


	# 	if (username != ""):
	# 		if any(c in illegal_symbols for c in username):
	# 			self.add_error(None,ValidationError("Username contains illegal symbols, please use only letters, numbers and ',','.'"))
	# 			return False
	# 	else:
	# 		self.add_error(None,ValidationError("Username cannot be blank"))
	# 		return False
			

	# 	if (len(User.objects.filter(username=username)) != 0):
	# 		self.add_error(None,ValidationError("Username already exists"))
	# 		return False

	# 	if (len(User.objects.filter(email=email)) != 0):
	# 		self.add_error(None,ValidationError("Email address already exists"))
	# 		return False
		
	# 	if (p1 != ""):
	# 		if(len(p1)>5):
	# 			if(p1!=p2):
	# 				self.add_error(None,ValidationError("Passwords do not match"))
	# 				return False
	# 		else:
	# 			self.add_error(None,ValidationError("Passwords less than 5 characters"))
	# 			return False
	# 	else:
	# 		self.add_error(None,ValidationError("Password cannot be empty"))
	# 		return False


#class ProfileRegistrationForm(ModelForm):
#   class Meta:
#		model = Profile
#		fields = ()

#	def save(self,user_information,commit=True):
#
#		profile = super(ProfileRegistrationForm,self).save(commit=False)
#
#		profile.user = user_information
#
#		if commit:
#			profile.save()
#		return profile

#class ProfileUpdateForm(ModelForm):
#	class Meta:
#		model = Profile
#		fields = ("About","title","position","profile_picture",)

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
		
class UpdatedCommentForm(ModelForm):
	body = forms.CharField(
		label = '',
		widget = forms.Textarea(
			attrs={
				'rows': 4,
				'placeholder': "Say Something ..."
			}
		)
	)

	class Meta:
		model = Comment
		fields = ("body",)

class CommentReplyForm(ModelForm):
	class Meta:
		model=Comment
		fields = ("body",)

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
	body = forms.CharField(widget=forms.Textarea)

class DateInput(forms.DateInput):
	input_type = 'date'

class ProfileUpdateForm(ModelForm):

	class Meta:
		model = Profile
		fields = ['name','bio','birth_date','location','profile_picture','institute','display_email_opt','tags']
		widgets = {
		  'birth_date': DateInput(),
			'tags': forms.CheckboxSelectMultiple,
		}
		labels ={
			'display_email_opt':"Do you wish to display your email address on your profile?",
		}
