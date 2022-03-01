from django.core import validators
from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models.deletion import CASCADE
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

########################
# AUTHOR MODEL
########################

# class Author(models.Model):
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     email_address = models.EmailField(max_length=50)
    
#     def full_name(self):
#         return f"{self.first_name} {self.last_name}"

#     def __str__(self):
#         return self.full_name()

titles = (("mr","Mr."),
          ("mrs","Mrs."),
          ("ms","Ms."),
          ("dr", "Dr."),
          ("prof","Prof."),)

class User(AbstractUser):
    email = models.EmailField( null = False, blank = False)
    checked = models.BooleanField(default= False)
    
    def __str__(self):
        return self.first_name +" " + self.last_name


class Tag(models.Model):
    caption = models.CharField(max_length=50)
    description = models.TextField(default="")

    def __str__(self):
        return self.caption

    def get_absolute_url(self):
        return reverse('share-thoughts')

class Post(models.Model):
    title = models.CharField(max_length=100)
    excerpt = models.CharField(max_length=200)
    image = models.ImageField(upload_to="posts/", blank=True, null = True)
    date = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True, db_index=True)
    content = models.TextField(validators=[MinLengthValidator(10)])
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="posts")
    tags = models.ManyToManyField(Tag)
    likes = models.ManyToManyField(User, related_name="blog_likes")
    liked = models.ManyToManyField(User, blank=True, related_name="liked")
    disliked = models.ManyToManyField(User, blank=True, related_name="disliked")
    
    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title + ' ' + str(self.author)

    def get_absolute_url(self):
        return reverse("share-thoughts", args=(str(self.id)))
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    commentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="commentors")
    date_added = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    image = models.ImageField(upload_to="posts/", blank=True, null = True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,blank=True,null=True, related_name='+')
    liked = models.ManyToManyField(User, blank=True, related_name="comment_liked")
    disliked = models.ManyToManyField(User, blank=True, related_name="comment_disliked")
    

    def total_likes(self):
        return self.likes.count()
        
    def __str__(self):
        return '%s - %s' %(self.post.title, self.name)

    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by('-date_added').all()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, verbose_name="user",related_name="profile")
    name = models.CharField(max_length=30,blank=True,null=True)
    bio =models.TextField(max_length=500, blank=True,null=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="uploads/profile_pictures",default='uploads/profile_pictures/default.png',blank= True)

class Notification(models.Model):
    notofication_type = models.IntegerField()
    to_user = models.ForeignKey(User,related_name ="notification_to", on_delete=models.CASCADE,null=True)
    from_user = models.ForeignKey(User,related_name ="notification_from", on_delete=models.CASCADE,null=True)
    post = models.ForeignKey('Post',on_delete=models.CASCADE,related_name="+",null=True, blank=True)
    comment = models.ForeignKey('Comment',on_delete=models.CASCADE,related_name="+",null=True, blank=True)
    date = models.DateTimeField(default= timezone.now)
    user_has_seen = models.BooleanField(default= False)