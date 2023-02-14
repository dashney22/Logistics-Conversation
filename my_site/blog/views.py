from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Notification, Post, Tag, Profile, Comment
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView, UpdateView
from .forms import EditPostForm, UserRegistrationForm, CreatePostForm, CreateTagForm, ContactUsForm,UpdatedCommentForm, CommentReplyForm,ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .email_functions import query_notification
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views import View
# Create your views here.
"""
Create post view is used to create a new discussion topic on the share your thoughts page. On a get request, it retrieves the Create post form
and on a post request it retrieves the completed form and checks the data before saving the post to the database.
"""
@login_required(login_url="user-login")
def create_post_view(request):
	author = request.user

	if request.method == "POST":
		formP = CreatePostForm(request.POST)

		if formP.is_valid():
			post = formP.save(author,request.FILES['image'])
			messages.success(request,f"Post was successfully created")
			return redirect('share-thoughts')

		else:
			messages.error(request,("There was an error with your post. Please ensure all information is provided."))
			return render(request,"blog/add_post.html",{"formP":formP})
	formP = CreatePostForm()

	return render(request,"blog/add_post.html",{"formP":formP})


"""
Gets all the posts for the database
"""
def get_all_posts():
	return Post.objects.all()

def starting_page_view(request):
	latest = get_all_posts().order_by("-date")[:3] ## fetches latest 3 posts and order by date from newest to oldest
	return render(request, "blog/index.html",{
		"posts": latest
	})

"""
Displays all of the posts that were retrieved from the database
"""
def posts_view(request):
	all_posts = get_all_posts()
	return render(request,"blog/all-posts.html",{
		"posts" : all_posts
	})

"""
Renders the specific information for a selected post. In a get request the specific post is retrieved based on the PK value that was sent in the request.
The post with the accompanying comments and tags must be retrieved along with a comment form where a person can enter a new comment to the post.
In a post request the information from the comment form is retrieved and a new comment is created in the databaes and then linked to the discussion topic and then the page is rendered with the new comment
"""
class PostDetailView(View):
	# login_url ='/login'
	def get(self, request, pk, *args, **kwargs):
		post = Post.objects.get(pk=pk)
		form  = UpdatedCommentForm()
		comments = Comment.objects.filter(post=post).order_by('date_added')
		author = post.author
		tags = post.tags.all()
		total_comments = Comment.objects.filter(post_id=post).count
		edit_rights = True if author == request.user else False

		context = {
			"post": post,
			"formC": form,
			"edit_rights" : edit_rights,
			"tags": tags,
			"total_comments":total_comments,
			"comments": comments,
		}
		return render(request, "blog/post-detail.html", context)
		

	def post(self, request, pk, *args, **kwargs):
		post = Post.objects.get(pk=pk)
		form  = UpdatedCommentForm(request.POST)
		comments = Comment.objects.filter(post=post).order_by('date_added')

		author = post.author
		tags = post.tags.all()
		total_comments = Comment.objects.filter(post_id=post).count
		edit_rights = True if author == request.user else False

		if form.is_valid():
			new_comment = form.save(commit=False)
			new_comment.commentor = request.user
			new_comment.post = post
			new_comment.save()

		notification = Notification.objects.create(notification_type=2 ,from_user=request.user,to_user=post.author, post=post)

		context = {
			"post": post,
			"formC": form,
			"tags": tags,
			"edit_rights" : edit_rights,
			"total_comments":total_comments,
			"comments": comments,
		}
		return render(request, "blog/post-detail.html", context)
"""
Used to manage the login process for users.
"""	
def login_view(request):
	
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(request, username =username,password=password)
		if user is not None:
			login(request, user)
			return redirect('home-page')
		else:
			messages.error(request,("There was an error with your login"))
			return redirect('user-login')	   
	else:
		return render(request, 'blog/login.html',{})
"""
Registration view used to add a new user to the portal. In the get request the User Registration form is rendered to capture the new user information. The additional profile information is set to the default values that can be changed in the edit profile page.
"""
def register_view(request):

	if request.method == "POST":
		formU = UserRegistrationForm(request.POST)
		#formP = ProfileRegistrationForm(request.POST)

		if formU.is_valid():
		   # if formP.is_valid():
			user = formU.save()
			   # profile = formP.save(user)
			return redirect("home-page")

			#else:
			#	messages.error(request,f"Error with profile creation page. Please ensure that profile information is correct")
		else:
			messages.error(request,f"Error with user information. Please ensure that the user information is correct.")
			return render(request, "blog/register.html", {"formU":formU,}) #"formP":formP})
	formU = UserRegistrationForm()
	#formP = ProfileRegistrationForm()


	return render(request, "blog/register.html", {"formU":formU,}) #"formP":formP})

"""
Add tag view is used to create new research topic tags that can be used in discussion topics or added to a profile. When adding a tag to a profile, it will be added to the network visualization graph.
Get request renders the add tag form.
Post requets takes the entered information and creates new tag.
Autocomplete suggestion method is used on the page to show users which tags have already been created and new tags are compared to old tags to prevent the creation of duplicates.
"""
@login_required(login_url="user-login")
def add_tag_view(request):
	existing_tags = Tag.objects.all()
	tag_names = []
	for tag in existing_tags:
		tag_names.append(tag.caption)
	if request.method == "POST":
		formT = CreateTagForm(request.POST)
		

		if formT.is_valid():
			if (formT.cleaned_data['caption'] in tag_names):
				messages.error(request,f"Tag caption already exists. Please use the existing tag or create a different tag.")
				return redirect("add-tag")
			else:
				tag = formT.save()
				messages.success(request,f"Tag was successfully created")
				return redirect("add-tag")

		else:
			messages.error(request,f"Error with tag creation. Please ensure all tag information is provided")

	formT = CreateTagForm()

	return render(request, "blog/add_tag.html", {"formT":formT,"existing_tags":tag_names})
"""
Similar to the add tag view,but this one is just specific for the creation of tags from a post. When a tag is made from a post the tag is immediately added to the discussion topic.
"""
@login_required(login_url="user-login")
def add_tag_from_post_view(request,post_pk):
	existing_tags = Tag.objects.all()
	tag_names = []
	for tag in existing_tags:
		tag_names.append(tag.caption)
	if request.method == "POST":
		formT = CreateTagForm(request.POST)
		

		if formT.is_valid():
			if (formT.cleaned_data['caption'] in tag_names):
				messages.error(request,f"Tag caption already exists. Please use the existing tag or create a different tag.")
			else:

				tag = formT.save()
				post_information = get_object_or_404(Post,id=post_pk)
				post_information.tags.add(tag) 
			# post_information.save()
				messages.success(request,f"Tag was successfully created")
				return HttpResponseRedirect(reverse('post-detail-page', args=(post_pk,)))
			# return render(request,"blog/post-detail.html",{
			#	 "post": post_information,
			#	 "tags" : post_information.tags.all(),
			#	 "comments": comments,
			#	 "formC" : formC,
			#	 "edit_rights": edit_rights,
			# })

		else:
			messages.error(request,f"Error with tag creation. Please ensure all tag information is provided")

	formT = CreateTagForm(initial={"caption":"", "description":""})

	return render(request, "blog/add_tag.html", {"formT":formT})
"""
Logout view to end the session
"""
def logout_view(request):
	logout(request)
	messages.info(request,f"Logged out successfully!")
	return redirect("home-page")


def what_if_view(request):

	return render(request, "blog/what-if.html",)
"""
Network visualization view. The network that is generated displays the connection between people on the portal and the research topics that they have selected on their profiles.
This allows other users to find people that are working in a specific field of research.
The connections are required to create the edges of the network graph.
All profiles and tags are retrieved from the database and added to the network graph.
"""
def research_community_view(request):

	#Need to get all of the connections from the blog_profile_tags table
	#Need to get the profiles that are linked to them 
	#Need to get the tags that are linked to them

	connections = Profile.tags.through.objects.all()
	profiles = Profile.objects.all()
	tags = Tag.objects.all()
	connection_dict = []
	profiles_tags_nodes = []
	# institutes = []
	# institutes_tags_nodes = []
	# institutes_to_tags_connections = []

	for profile in profiles:
		# if(profile.institute not in institutes):
		# 	print(profile.institute)
		# 	institutes.append(profile.institute.name)
		if (str(profile.profile_picture) != ""):
			profiles_tags_nodes.append({
				'id':"P"+str(profile.id),
				'group':'profiles',
				'label': profile.user.first_name+' '+ profile.user.last_name,
				'image':"../media/{}".format(str(profile.profile_picture)),
				'url': "../profile/{}".format(str(profile.id)),
				'shape':"circularImage",
			})
		else:
			profiles_tags_nodes.append({
				'id':"P"+str(profile.id),
				'group':'profiles',
				'label': profile.user.first_name+' '+ profile.user.last_name,
				'image':"../media/uploads/profile_pictures/default.png",
				'url': "../profile/{}".format(str(profile.id)),
				'shape':"circularImage",
			})

	for tag in tags:
		profiles_tags_nodes.append({
			'id':"T"+str(tag.id),
			'label':tag.caption,
			'title':tag.description,
		})
	# profiles_dict = {'id':[],'profile_picture':[],'full_name':[]}
	# tags_dict = {'id':[],'name':[],'description':[]}



	for connection in connections:
		#use a convention from from nodes are the profile and to is the tag its linked to
		connection_dict.append({"from":("P"+str(connection.profile_id)),"to":("T"+str(connection.tag_id))})
		# institutes_to_tags_connections
	# for profile in profiles:
	# 	profiles_dict["id"].append("P"+str(profile.id))
	# 	profiles_dict["profile_picture"].append(str(profile.profile_picture))
	# 	profiles_dict["full_name"].append(profile.user.first_name+' '+ profile.user.last_name)
	# for tag in tags:
	# 	tags_dict["id"].append("T"+str(tag.id))
	# 	tags_dict["name"].append(tag.caption)
	# 	tags_dict["description"].append(tag.description)

	# context = {"profiles_tags":profiles_tags_nodes,"profile_tags_connections":connection_dict,"institute_tags":institutes_tags_nodes,'institute_tag_connections':institutes_to_tags_connections}
	context = {"profiles_tags":profiles_tags_nodes,"profile_tags_connections":connection_dict}

	return render(request, "blog/research-community.html",context=context)
"""
Contact us page that is linked to a gmail account for sending questions and comments to the CSIR.
"""
def contact_us_view(request):
	
	if request.method == "POST":
		formC = ContactUsForm(request.POST)

		if formC.is_valid():
			email = formC.cleaned_data['email']
			name = formC.cleaned_data['name']
			phone = formC.cleaned_data['phone']
			subject = formC.cleaned_data['subject']
			body = formC.cleaned_data['body']
			query_notification(request,email,name,phone,subject,body)
			messages.success(request,f"Query successfully submitted")
			return redirect("home-page")

	formC = ContactUsForm()
	return render(request, "blog/contact-us.html", {"formC":formC})

def research_agenda_view(request):

	return render(request, "blog/research-agenda.html",)
"""
About us view contains more information regarding the purpose of the logistics conversation portal and other important information.
"""
def about_us_view(request):

	return render(request, "blog/about.html",)

def about_us_process_view(request):

	return render(request, "blog/process.html",)

def what_if_view(request):

	return render(request, "blog/what-if.html",)

"""
Search function that is added to the discussion topics page that allows a user to find a specific discussion based on criteria such as the name of the post, the autor or specific words in the post.
"""
def posts_search_view(request):
	if request.method == 'GET':
		query= request.GET.get('search_bar')
		submitbutton= request.GET.get('"search_submit"')

		if query is not None:
			lookups= Q(title__icontains=query) | Q(excerpt__icontains=query) |Q(content__icontains=query) | Q(author__first_name__icontains=query)| Q(author__last_name__icontains=query) | Q(author__username__icontains=query) |Q(tags__caption__icontains=query)

			results= Post.objects.filter(lookups).distinct()

			context={'posts': results,
					 'submitbutton': submitbutton}

			return render(request, "blog/search-posts.html", context)

		else:
			return render(request, "blog/search-posts.html")

	else:
		return render(request, 'search/search-posts.html')
"""
Function to remove a comment from a post, in the model it is defined what happens to comments that are linked to a specific comment.
"""
@login_required(login_url="user-login")
def delete_comment(request, post_pk, comment_pk):
	comment = Comment.objects.filter(id=comment_pk).last()
	if comment:
		comment.delete()
	return redirect('post-detail-page',pk=post_pk)

"""
Function to remove an entire discussion topic
"""
class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	template_name ='blog/delete_post.html'
	success_url = reverse_lazy('share-thoughts')

	def test_func(self):
		post = self.get_object()
		return self.request.user==post.author

"""
Function to allow the other to modify aspects of topic that they have created.
"""
class EditPostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	template_name = 'blog/update_post.html'
	fields = ['title','excerpt','image','content','tags']

	def get_success_url(self):
		pk = self.kwargs['pk'] 
		return reverse_lazy('post-detail-page', kwargs={'pk': pk})

	def test_func(self):
		post = self.get_object()
		return self.request.user==post.author
"""
Functions to add likes or dislikes to a discussion topic. The function checks to see if a specifc user has already liked a topic and if not, then a like is added. If it is already liked, then the like is removed.
The same logic applies to the dislikes.
"""
class AddLikes(LoginRequiredMixin, View):
	def post(self, request, pk, *args, **kwargs):
		post = Post.objects.get(pk=pk)

		disliked_post = False
		for dislike in post.disliked.all():
			if dislike==request.user:
				disliked_post=True
				break

		if disliked_post:
			post.disliked.remove(request.user)

		is_like = False
		for like in post.liked.all():
			if like==request.user:
				is_like=True
				break
		if not is_like:
			post.liked.add(request.user)
			notification = Notification.objects.create(notification_type=1,from_user=request.user,to_user=post.author,post=post)
		if is_like:
			post.liked.remove(request.user)
		
		next = request.POST.get('next', '/')
		return HttpResponseRedirect(next)

class AddDislikes(LoginRequiredMixin,View):
	def post(self, request, pk, *args, **kwargs):
		post = Post.objects.get(pk=pk)

		is_like = False
		for like in post.liked.all():
			if like==request.user:
				is_like=True
				break

		if is_like:
			post.liked.remove(request.user)

		disliked_post = False

		for dislike in post.disliked.all():
			if dislike==request.user:
				disliked_post=True
				break

		if not disliked_post:
			post.disliked.add(request.user)
			
		if disliked_post:
			post.disliked.remove(request.user)

		next = request.POST.get('next', '/')
		return HttpResponseRedirect(next)
"""
Functions that adds likes or dislikes to a comment. Here the comment must be fetched and then all of the likes on the comment is checked to see if the specific user has already liked a comment and then adds the comment if not already liked or removes it if already liked.
The same logic applies to the dislikes.
"""
class AddCommentLikes(LoginRequiredMixin, View):
	def post(self, request, pk, *args, **kwargs):
		comment = Comment.objects.get(pk=pk)

		disliked_post = False
		for dislike in comment.disliked.all():
			if dislike==request.user:
				disliked_post=True
				break

		if disliked_post:
			comment.disliked.remove(request.user)

		is_like = False
		for like in comment.liked.all():
			if like==request.user:
				is_like=True
				break
		if not is_like:
			comment.liked.add(request.user)
			notification = Notification.objects.create(notification_type=1,from_user=request.user,to_user=comment.commentor,comment=comment)

		if is_like:
			comment.liked.remove(request.user)
		
		next = request.POST.get('next', '/')
		return HttpResponseRedirect(next)

class AddCommentDislikes(LoginRequiredMixin,View):
	def post(self, request, pk, *args, **kwargs):
		comment = Comment.objects.get(pk=pk)

		is_like = False
		for like in comment.liked.all():
			if like==request.user:
				is_like=True
				break

		if is_like:
			comment.liked.remove(request.user)

		disliked_post = False

		for dislike in comment.disliked.all():
			if dislike==request.user:
				disliked_post=True
				break

		if not disliked_post:
			comment.disliked.add(request.user)

		if disliked_post:
			comment.disliked.remove(request.user)

		next = request.POST.get('next', '/')
		return HttpResponseRedirect(next)

"""
Function to allow a user to comment on a previous comment. Comments are linked in a chain to keep track of the parent node of a comment.
"""
class CommentReplyView(LoginRequiredMixin,View):
	def post(self,request,post_pk,pk,*args,**kwargs):
		post = Post.objects.get(pk=post_pk)
		parent_comment = Comment.objects.get(pk=pk)

		form = UpdatedCommentForm(request.POST)

		if form.is_valid():
			new_comment = form.save(commit=False)
			new_comment.commentor = request.user
			new_comment.post = post
			new_comment.parent = parent_comment
			new_comment.save()

		notification = Notification.objects.create(notification_type=2 ,from_user=request.user,to_user=parent_comment.commentor, comment=new_comment)

		return redirect('post-detail-page',pk=post_pk)



"""
Function to view the profile of a specific person. If the person viewing the profile is the owner of the profile, then the profile can be edited.
"""
class ProfileView(View):
	# login_url = "/login/"
	def get(self, request, pk, *args, **kwargs):
		profile = Profile.objects.get(pk=pk)
		researcher_tags_base = list(profile.tags.filter(researcher_tags = profile.id))
		researcher_tags = []
		for tag in researcher_tags_base:
			researcher_tags.append(str(tag))
		user = profile.user
		posts = Post.objects.filter(author=user).order_by('-date')
		context= {
			"user": user,
			"profile": profile,
			"researcher_tags": researcher_tags,
			"posts": posts
		}
		return render(request, "blog/profile.html", context)


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

	model = Profile
	form_class = ProfileUpdateForm
	# fields = ['name','bio','birth_date','location','profile_picture']
	template_name_suffix = "_edit"
	
	def get_success_url(self):
		pk = self.kwargs['pk']
		return reverse_lazy('profile', kwargs={'pk':pk})

	def test_func(self):
		profile = self.get_object()
		return self.request.user == profile.user

"""
Function to add a notification to a persons profile in the case that someone posted a comment or a like on a topic that they created.
"""
class PostNotificationView(View):
	def get(self, request, notification_pk,post_pk,*args, **kwargs):
		notification = Notification.objects.get(pk=notification_pk)
		post = Post.objects.get(pk=post_pk)

		notification.user_has_seen = True
		notification.save()

		return redirect('post-detail-page',pk=post_pk)
