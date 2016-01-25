from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from .models import Post
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm



# Create your views here.
def post_list(request):
    if request.user.is_authenticated():
        posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    else:
        posts = Post.objects.filter(draft=False).filter(published_date__lte=timezone.now()).order_by('-published_date')
    
    query = request.GET.get("q")
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(text__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) 
            ).distinct()

    paginator = Paginator(posts, 5) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post_list.html', {'posts':posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.draft:
        if not request.user.is_authenticated():
            raise Http404
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if not request.user.is_authenticated():
        raise Http404
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.published_date = timezone.now()
            post.save()
            messages.success(request, "Awesome! Your new post was successfully created!")
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})
    

def post_edit(request, pk):
    if not request.user.is_authenticated():
        raise Http404
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.published_date = timezone.now()
            post.save()
            messages.success(request, "Awesome! Your new post was successfully edited!")
            return redirect('post_detail', pk=post.pk)
    else:
        
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
    
def post_delete(request, pk):
    if not request.user.is_authenticated():
        raise Http404
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, "That post was successfully deleted!")
    return redirect("post_list")