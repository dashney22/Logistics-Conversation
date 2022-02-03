from django.urls import path
from . import views
from .views import DeletePostView, AddDislikes,AddLikes, AddCommentDislikes, AddCommentLikes, CommentReplyView

urlpatterns = [
    path("", views.starting_page_view, name="home-page"),
    path('add_post/',views.create_post_view, name="add-post"),
    path("posts", views.posts_view, name="share-thoughts"),
    path("posts/search", views.posts_search_view, name="post-search"),
    path("posts/<slug:slug>", views.post_details_view, name="post-detail-page"),
    path("research-agenda/", views.research_agenda_view, name="research-agenda"),
    path("research-community/", views.research_community_view, name="research-community"),
    path("what-if/", views.what_if_view, name="what-if"),
    path("contact-us/", views.contact_us_view, name="contact-us"),
    path("about-us/", views.about_us_view, name="about-us"),
    path("process/", views.about_us_process_view, name="process"),
    path("posts/<slug:slug>/edit", views.edit_post_view, name="edit-post-page"),
    path("register/", views.register_view, name="register-user"),
    path("login/",views.login_view, name="user-login"),
    path("profile/",views.profile_view, name="user-profile"),
    path("add_tag/",views.add_tag_view, name="add-tag"),
    path("logout/",views.logout_view, name="user-logout"),
    #path("like-post/<slug:slug>", views.like_post_view, name="like-post"),
    #path("like-comment/<slug:slug>", views.like_comment_view, name="like-comment"),
    path("post/<int:pk>/delete", views.delete_comment, name="delete-comment"),
    path("post/<slug:pk>/delete", DeletePostView.as_view(), name="delete-post"),
    path("post/<int:pk>/likes", AddLikes.as_view(), name="likes"),
    path("post/<int:pk>/dislikes", AddDislikes.as_view(), name="dislikes"),
    path("comment/<int:pk>/like", AddCommentLikes.as_view(), name="comment-likes"),
    path("comment/<int:pk>/dislike", AddCommentDislikes.as_view(), name="comment-dislikes"),
    path("post/<int:post_pk>/comment/<int:pk>/reply",CommentReplyView.as_view(),name="comment-reply"),
]