from django.core import validators
from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models.deletion import CASCADE
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

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
    likes = models.ManyToManyField(User, related_name="comment_likes")
    parent = models.ForeignKey('self', on_delete=models.CASCADE,blank=True,null=True, related_name='+')

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

class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE)
    About = models.TextField(blank= True)
    title = models.CharField(max_length=6,choices =titles,default="mr")
    position = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="posts/profile_pictures",blank= True)


