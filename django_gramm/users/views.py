from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from blog.models import Post
from .tokens import account_activation_token
from .models import Profile, Subscription
from .forms import LoginForm, UserEditForm, ProfileEditForm, SignupForm

User = get_user_model()


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
            else:
                return HttpResponse('Disabled account')
        else:
            return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('users:profile', username=request.user.username)

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'users/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            Profile.objects.create(user=user)

            current_site = get_current_site(request)
            subject = 'Activate your blog account.'
            message = render_to_string('users/acc_active_email.html', {
                'user': user, 'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            toemail = form.cleaned_data.get('email')
            email = EmailMessage(subject, message, to=[toemail])
            email.send()
            return render(request, 'users/signup_done.html', {'email': toemail})
        else:
            print(form.errors)
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('users:edit')
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def profile_view(request, username):
    user_profile = get_object_or_404(User, username=username)

    posts = Post.objects.filter(author=user_profile, status=Post.Status.PUBLISHED)
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    followers_count = Subscription.subscriptions.count_followers(user_profile)
    following_count = Subscription.subscriptions.count_following(user_profile)

    is_following = Subscription.objects.filter(
        follower=request.user,
        following=user_profile
    ).exists()

    return render(request, "users/profile.html", {
        "user_profile": user_profile,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
    })


@login_required
def follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    Subscription.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )

    return redirect("users:profile", username=username)


@login_required
def unfollow(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)

    Subscription.objects.filter(
        follower=request.user,
        following=user_to_unfollow
    ).delete()

    return redirect("users:profile", username=username)


@login_required
def followers_list(request, username):
    user_profile = get_object_or_404(User, username=username)
    followers = Subscription.subscriptions.followers_of(user_profile)
    return render(request, 'users/followers_list.html', {
        'user_profile': user_profile,
        'followers': followers,
    })

@login_required
def following_list(request, username):
    user_profile = get_object_or_404(User, username=username)
    following = Subscription.subscriptions.following_of(user_profile)
    return render(request, 'users/following_list.html', {
        'user_profile': user_profile,
        'following': following,
    })


@login_required
@require_POST
def follow_ajax(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    sub, created = Subscription.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    return JsonResponse({
        "status": "followed" if created else "already_following",
        "unfollow_url": reverse('users:unfollow_ajax', args=[username]),
    })

@login_required
@require_POST
def unfollow_ajax(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    deleted, _ = Subscription.objects.filter(
        follower=request.user,
        following=user_to_unfollow
    ).delete()
    return JsonResponse({
        "status": "unfollowed" if deleted else "not_following",
        "follow_url": reverse('users:follow_ajax', args=[username]),
    })
