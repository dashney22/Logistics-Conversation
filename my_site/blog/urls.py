from django.urls import path
from . import views
# from .views import CreatePost

urlpatterns = [
    path("", views.starting_page, name="home-page"),
    path('add_post/',views.create_post, name="add-post"),
    path("posts", views.posts, name="share-thoughts"),
    path("posts/<slug:slug>", views.post_details, name="post-detail-page"),
    path("posts/", views.post_details, name="research-agenda"),
    path("research-community/", views.research_community, name="research-community"),
    path("what-if/", views.what_if_view, name="what-if"),
    path("posts/", views.post_details, name="about-us"),
    path("posts/<slug:slug>/edit", views.edit_post, name="edit-post-page"),
    path("register/", views.register_view, name="register-user"),
    path("login/",views.login_view, name="user-login"),
    path("profile/",views.profile_view, name="user-profile"),
    path("add_tag/",views.add_tag_view, name="add-tag"),
    path("logout/",views.logout_view, name="user-logout"),
]