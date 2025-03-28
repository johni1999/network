from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    pass


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)    
    def __str__(self):
        return self.author.username + " - " + self.content[:20] + "..."


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "At: " + self.liked_at + " " + self.user.username + " liked " + self.post.author.username + "'s post"
    class Meta:
        unique_together = ('user', 'post')


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)
    def clean(self):
        if self.follower == self.following:
            raise ValidationError("You can't follow yourself.")
    def __str__(self):
        return "At: "+ self.followed_at + self.follower.username + " followed " + self.following.username

    class Meta:
        unique_together = ('follower', 'following')