from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


def post_list(request):
    posts = Post.objects.select_related("author").all()
    search_query = request.GET.get("q", "").strip()
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(content__icontains=search_query)
        )

    page_obj = Paginator(posts, 5).get_page(request.GET.get("page"))
    return render(
        request,
        "blog/post_list.html",
        {"page_obj": page_obj, "search_query": search_query},
    )


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related("author"), pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


def register(request):
    if request.user.is_authenticated:
        return redirect("post_list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("post_list")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(post)
    else:
        form = PostForm()

    return render(
        request,
        "blog/post_form.html",
        {"form": form, "page_title": "Write a post"},
    )


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(post)
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "blog/post_form.html",
        {"form": form, "page_title": "Edit post"},
    )


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        post.delete()
        return redirect("post_list")

    return render(request, "blog/post_confirm_delete.html", {"post": post})
