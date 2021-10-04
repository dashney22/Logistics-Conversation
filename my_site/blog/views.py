from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Tag, Author
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
all_posts = [
    
    
]

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
    return render(request,"blog/post-detail.html",{
        "post": identified_post,
        "tags" : identified_post.tags.all()
    })

def login_view(request):
    
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username =username,password=password)
		if user is not None:
			login(request, user)
			return redirect('home-page')
		else:
			messages.success(request,("There was an error with your login"))
			return redirect('login')
	else:
		return render(request, 'blog/login.html',{})

