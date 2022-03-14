from django.urls import path
from . import views
from .views import DeletePostView, AddDislikes,AddLikes, AddCommentDislikes, AddCommentLikes, CommentReplyView, PostDetailView, EditPostView, ProfileView,ProfileEditView,PostNotificationView

urlpatterns = [
    path("", views.starting_page_view, name="home-page"),
    path('add_post/',views.create_post_view, name="add-post"),
    path("posts", views.posts_view, name="share-thoughts"),
    path("posts/search", views.posts_search_view, name="post-search"),
    path("posts/<int:pk>", PostDetailView.as_view(), name="post-detail-page"),
    path("research-agenda/", views.research_agenda_view, name="research-agenda"),
    path("research-community/", views.research_community_view, name="research-community"),
    path("what-if/", views.what_if_view, name="what-if"),
    path("contact-us/", views.contact_us_view, name="contact-us"),
    path("about-us/", views.about_us_view, name="about-us"),
    path("process/", views.about_us_process_view, name="process"),
    path("post/<int:pk>/edit", EditPostView.as_view(), name="post-edit"),
    path("register/", views.register_view, name="register-user"),
    path("login/",views.login_view, name="user-login"),
    path("add_tag/",views.add_tag_view, name="add-tag"),
    path("logout/",views.logout_view, name="user-logout"),
    path("post/<int:pk>/delete", views.delete_comment, name="delete-comment"),
    path("post/<int:pk>/delete", DeletePostView.as_view(), name="delete-post"),
    path("post/<int:pk>/likes", AddLikes.as_view(), name="likes"),
    path("post/<int:pk>/dislikes", AddDislikes.as_view(), name="dislikes"),
    path("comment/<int:pk>/like", AddCommentLikes.as_view(), name="comment-likes"),
    path("comment/<int:pk>/dislike", AddCommentDislikes.as_view(), name="comment-dislikes"),
    path("post/<int:post_pk>/comment/<int:pk>/reply",CommentReplyView.as_view(),name="comment-reply"),
    path("profile/<int:pk>", ProfileView.as_view(), name="profile"),
    path("profile/edit/<int:pk>", ProfileEditView.as_view(), name="profile-edit"),
    path("notification/<int:notification_pk>/post<int:post_pk>",PostNotificationView.as_view(),name="post-notification"),
]