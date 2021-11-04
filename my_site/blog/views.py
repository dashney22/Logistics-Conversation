from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Tag, Profile, Comment
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import CreateView
from .forms import EditPostForm, UserRegistrationForm, ProfileRegistrationForm, ProfileUpdateForm, CreatePostForm, CreateTagForm, CreateCommentForm
from django.contrib.auth.decorators import login_required



# Create your views here.
all_posts = [
    
    
]

def create_post(request):
    author = request.user

    if request.method == "POST":
        formP = CreatePostForm(request.POST)

        if formP.is_valid():
            post = formP.save(author,request.FILES['image'])
            return redirect('share-thoughts')

        else:
            messages.error(request,("There was an error with your post. Please ensure all information is provided."))
            return render(request,"blog/add_post.html",{"formP":formP})
    formP = CreatePostForm()

    return render(request,"blog/add_post.html",{"formP":formP})


def user_login(request):
    return render(request, "blog/login.html", {})

# get all posts function
def get_all_posts():
    return Post.objects.all()

def starting_page(request):
    latest = get_all_posts().order_by("-date")[:3] ## fetches latest 3 posts and order by date from newest to oldest
    return render(request, "blog/index.html",{
        "posts": latest
    })


def posts(request):
    all_posts = get_all_posts()
    return render(request,"blog/all-posts.html",{
        "posts" : all_posts
    })

def post_details(request, slug):
    identified_post = get_object_or_404(Post, slug=slug)
    #identified_post = next(post for post in crack_post if post["slug"]== slug)
    author = request.user
    comments = Comment.objects.filter(post_id=identified_post)

    if request.method == "POST":
        formC = CreateCommentForm(request.POST)

        if formC.is_valid():
            print(request.FILES)
            if (request.FILES):
                comment = formC.save(author,request.FILES['image'],identified_post)
            else:
                comment = formC.save(author,None,identified_post)


            query = formC.instance
            return redirect("post-detail-page",slug = slug)
        else: 
            messages.error(request,("There was an issue with the comment"))

    formC = CreateCommentForm(initial={"body":"", "image":None})
    return render(request,"blog/post-detail.html",{
        "post": identified_post,
        "tags" : identified_post.tags.all(),
        "comments": comments,
        "formC" : formC,
    })

def edit_post(request,slug):
    post_information = get_object_or_404(Post,slug=slug)
    if request.method == "GET":
        form = EditPostForm(initial={"title":post_information.title,
                                     "excerpt":post_information.excerpt,
                                     "image":post_information.image,
                                     "content":post_information.content,
                                     "tags":post_information.tags.all()})
        return render(request,"blog/update_post.html",{'form':form,'post':post_information})
    else:
        form = EditPostForm(request.POST,instance=post_information)
        edited_post = form.save()
        return redirect("share-thoughts")

    
def login_view(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username)
        print(password)
        user = authenticate(request, username =username,password=password)
        if user is not None:
            login(request, user)
            return redirect('home-page')
        else:
            messages.error(request,("There was an error with your login"))
            return redirect('user-login')       
    else:
        return render(request, 'blog/login.html',{})

def register_view(request):

    if request.method == "POST":
        formU = UserRegistrationForm(request.POST)
        formP = ProfileRegistrationForm(request.POST)

        if formU.is_valid():
            if formP.is_valid():
                user = formU.save()
                profile = formP.save(user)
                return redirect("home-page")

            else:
                messages.error(request,f"Error with profile creation page. Please ensure that profile information is correct")
        else:
            messages.error(request,f"Error with user information. Please ensure that the user information is correct.")

    formU = UserRegistrationForm()
    formP = ProfileRegistrationForm()


    return render(request, "blog/register.html", {"formU":formU,"formP":formP})

def profile_view(request):
    profile_information = get_object_or_404(Profile,user=request.user)
    if request.method  == 'GET':
        form = ProfileUpdateForm(initial={"About":profile_information.About,
                                            "title":profile_information.title,
                                            "position":profile_information.position,
                                            "profile_picture": profile_information.profile_picture,
                                            }) 
        return render(request,"blog/update_profile.html",{'form':form})
    else:
        form = ProfileUpdateForm(request.POST,instance=profile_information) 
        profile_update = form.save()
        return redirect('home-page')

def add_tag_view(request):

    if request.method == "POST":
        formT = CreateTagForm(request.POST)
        

        if formT.is_valid():
            tag = formT.save()

            return redirect("home-page")

        else:
            messages.error(request,f"Error with tag creation. Please ensure all tag information is provided")

    formT = CreateTagForm()

    return render(request, "blog/add_tag.html", {"formT":formT})

def logout_view(request):
	logout(request)
	messages.info(request,f"Logged out successfully!")
	return redirect("home-page")


def what_if_view(request):

    return render(request, "blog/what-if.html",)

def research_community(request):

    return render(request, "blog/research-community.html",)

def about_us(request):
    return render(request,'blog/about_us.html',{})

def contact_us(request):
    return render(request,'blog/contact.html',{})
