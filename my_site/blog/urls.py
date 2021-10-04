from django.urls import path
from . import views

urlpatterns = [
    path("", views.starting_page, name="home-page"),
    path("",views.user_login, name="login"),
    path("posts", views.posts, name="share-thoughts"),
    path("posts/<slug:slug>", views.post_details, name="post-detail-page"),
    path("posts/", views.post_details, name="research-agenda"),
    path("posts/", views.post_details, name="research-community"),
    path("posts/", views.post_details, name="what-If"),
    path("posts/", views.post_details, name="About-Us"),
    path("posts/", views.post_details, name="registration"),
    
]