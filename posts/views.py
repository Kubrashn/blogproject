from django.shortcuts import render , redirect
from.models import *
from.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
#anasayfa
def index(request):
    posts = Post.objects.filter(isPublish = True).order_by('-created_at')[:5]
    if request.method == 'POST':
        if request.user.is_authenticated:
            postId = request.POST['postId']
            post = Post.objects.get(id = postId)
            if 'like' in request.POST:
                if request.user.profile in post.like.all():
                    post.like.remove(request.user.profile)
                    post.save()
                    return redirect('index')
                else:
                    post.like.add(request.user.profile)
                    post.dislike.remove(request.user.profile)
                    post.save()
                    return redirect('index')
            if 'dislike' in request.POST :
                if request.user.profile in post.dislike.all():
                    post.dislike.remove()
                    post.save()
                    return redirect('index')
                else:
                    post.dislike.add(request.user.profile)
                    post.like.remove(request.user.profile)
                    post.save()
                    return redirect('index')

    context = {
        'posts':posts
    }
    return render(request , 'index.html' , context)

@login_required(login_url='login')
def create(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user.profile
            post.save()
            messages.success(request , 'Postunuz olusturulmustur denetlendikten sonra yayinlanacak')
            return redirect('index')
    context = {
        'form' : form
    }    
    return render(request, 'create.html', context)

def detay(request , postId , slug):
    post = Post.objects.get(id = postId , slug = slug)
    context = {
        'post':post
    }
    return render(request, 'post.html' , context)




