from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import User, Post, Like, Follow


def index(request):
    if request.method == "POST":
        # Get the content and post it.
        content = request.POST.get("post")
        if content:
            post = Post(author=request.user, content=content)
            post.save()
        return redirect("index")
    
    # Get all the posts and annotate them with the likes count.
    posts = Post.objects.annotate(likes_count=Count('like')).order_by("-created_at")
    
    # Paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    return render(request, "network/index.html", {'page_obj': page_obj})

def landing(request):
    return render(request, "network/landing.html")

@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user).annotate(likes_count=Count('like')).order_by('-created_at')
    is_following = request.user.following.filter(following=profile_user).exists()
    
    # Paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'network/profile.html', {
        'profile_user': profile_user,
        'is_following': is_following,
        'page_obj': page_obj
    })


def follow(request, username):
    # Get the user to follow.
    user = get_object_or_404(User, username=username)
    
    # Check if the user is already followed.
    if request.user.following.filter(following=user).exists():
        request.user.following.filter(following=user).delete()
    else:
        request.user.following.create(following=user)
    return redirect('profile', username=username)


def following(request):
    # Get the users the logged-in user is following
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    # Get posts from those users
    posts = Post.objects.filter(author__id__in=following_users).order_by('-created_at')
    # Paginate the posts
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/following.html', {
        'page_obj': page_obj,
        'user': request.user
    })
    
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if Like.objects.filter(user=user, post=post).exists():
        Like.objects.filter(user=user, post=post).delete()
        liked = False
    else:
        Like.objects.create(user=user, post=post)
        liked = True

    like_count = post.like_set.count()
    return JsonResponse({'liked': liked, 'like_count': like_count})

@csrf_exempt
def edit_post(request, post_id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return JsonResponse({"error": "You are not authorized to edit this post."}, status=403)

            data = json.loads(request.body)
            post.content = data.get("content", post.content)
            post.save()
            return JsonResponse({"success": True})
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
    return JsonResponse({"error": "Invalid request method."}, status=400)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("landing"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.like_set.all():
            post.like_set.remove(request.user)
        else:
            post.like_set.add(request.user)
        return JsonResponse({"likes_count": post.like_set.count()})
