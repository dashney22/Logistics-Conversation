from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Post, Tag, Profile, Comment
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView, UpdateView
from .forms import EditPostForm, UserRegistrationForm, ProfileRegistrationForm, ProfileUpdateForm, CreatePostForm, CreateTagForm, CreateCommentForm, ContactUsForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from .email_functions import query_notification

from django.urls import reverse_lazy, reverse
# Create your views here.

@login_required(login_url="user-login")
def create_post_view(request):
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


def user_login_view(request):
    return render(request, "blog/login.html", {})

# get all posts function
def get_all_posts():
    return Post.objects.all()

def starting_page_view(request):
    latest = get_all_posts().order_by("-date")[:3] ## fetches latest 3 posts and order by date from newest to oldest
    return render(request, "blog/index.html",{
        "posts": latest
    })


def posts_view(request):
    all_posts = get_all_posts()
    return render(request,"blog/all-posts.html",{
        "posts" : all_posts
    })

def like_post_view(request,slug):
    post = get_object_or_404(Post,id=request.POST.get('post_id'))
    
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return HttpResponseRedirect(reverse('post-detail-page', args=[str(slug)]))


def like_comment_view(request, slug ):
    comment = get_object_or_404(Comment,id=request.POST.get('comment_id'))
    
    liked = False
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True

    return HttpResponseRedirect(reverse('post-detail-page', args=[str(slug)]))


def post_details_view(request, slug):
    identified_post = get_object_or_404(Post, slug=slug)
    #identified_post = next(post for post in crack_post if post["slug"]== slug)
    author = identified_post.author
    comments = Comment.objects.filter(post_id=identified_post)

    if request.method == "POST":
        formC = CreateCommentForm(request.POST)

        if formC.is_valid():
            print(request.FILES)
            if (request.FILES):
                comment = formC.save(request.user,request.FILES['image'],identified_post)
            else:
                comment = formC.save(request.user,None,identified_post)


            query = formC.instance
            return redirect("post-detail-page",slug = slug)
        else: 
            messages.error(request,("There was an issue with the comment"))

    formC = CreateCommentForm(initial={"body":"", "image":None})
    edit_rights = True if author == request.user else False
    return render(request,"blog/post-detail.html",{
        "post": identified_post,
        "tags" : identified_post.tags.all(),
        "comments": comments,
        "formC" : formC,
        "edit_rights": edit_rights,
    })
@login_required(login_url="user-login")
def edit_post_view(request,slug):
    post_information = get_object_or_404(Post,slug=slug)
    author = post_information.author
    if (author == request.user):
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
@login_required(login_url="user-login")
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

@login_required(login_url="user-login")
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


@login_required(login_url="user-login")
def add_tag_from_post_view(request,slug):

    if request.method == "POST":
        formT = CreateTagForm(request.POST)
        

        if formT.is_valid():
            tag = formT.save()
            post_information = get_object_or_404(Post,slug=slug)
            post_information.tags.add(tag) 
            # post_information.save()
            author = post_information.author
            comments = Comment.objects.filter(post_id=post_information)
            formC = CreateCommentForm(initial={"body":"", "image":None})
            edit_rights = True if author == request.user else False
            return HttpResponseRedirect(reverse('post-detail-page', args=(post_information.slug,)))
            # return render(request,"blog/post-detail.html",{
            #     "post": post_information,
            #     "tags" : post_information.tags.all(),
            #     "comments": comments,
            #     "formC" : formC,
            #     "edit_rights": edit_rights,
            # })

        else:
            messages.error(request,f"Error with tag creation. Please ensure all tag information is provided")

    formT = CreateTagForm(initial={"caption":"", "description":""})

    return render(request, "blog/add_tag.html", {"formT":formT})

def logout_view(request):
	logout(request)
	messages.info(request,f"Logged out successfully!")
	return redirect("home-page")


def what_if_view(request):

    return render(request, "blog/what-if.html",)

def research_community_view(request):

    return render(request, "blog/research-community.html",)

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

def about_us_view(request):

    return render(request, "blog/about.html",)

def about_us_process_view(request):

    return render(request, "blog/process.html",)

def what_if_view(request):

    return render(request, "blog/what-if.html",)


def get_queryset(request):
        query = request.GET.get('search_bar')
        print(request.GET)
        object_list = Post.objects.filter(
            Q(title__icontains=query) | Q(excerpt__icontains=query) |Q(content__icontains=query) | Q(author__icontains=query) |Q(tags__icontains=query)
        )
        return object_list




def posts_search_view(request):
    if request.method == 'GET':
        query= request.GET.get('search_bar')
        submitbutton= request.GET.get('"search_submit"')

        if query is not None:
            lookups= Q(title__icontains=query) | Q(excerpt__icontains=query) |Q(content__icontains=query) | Q(author__first_name__icontains=query)| Q(author__last_name__icontains=query) | Q(author__username__icontains=query) |Q(tags__caption__icontains=query)

            results= Post.objects.filter(lookups).distinct()
            print(results)
            context={'posts': results,
                     'submitbutton': submitbutton}

            return render(request, "blog/search-posts.html", context)

        else:
            return render(request, "blog/search-posts.html")

    else:
        return render(request, 'search/search-posts.html')


def delete_comment(request, pk):
     comment = Comment.objects.filter(post=pk).last()
     if comment:
         comment.delete()
     return redirect('share-thoughts')

class DeletePostView(DeleteView):
    model = Post
    template_name ="blog/delete_post.html"
    success_url = reverse_lazy("share-thoughts")

@login_required(login_url="user-login")
class EditPostView(UpdateView):
    model = Post
    template_name = 'update_post.html'
    fields = ['title','excerpt','image','content','tags']
