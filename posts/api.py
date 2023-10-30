from django.http import JsonResponse
from django.db.models import Q
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from accounts.models import User
from accounts.serializers import UserSerializer
from notification.utils import create_notification
from .models import Post, Like, Comment, Trend
from .serializers import PostSerializer, PostDetailSerializer, CommentSerializer, TrendSerializer
from .forms import PostForm


@api_view(["GET"])
def post_list(request):
    user_ids = [request.user.id]
    for user in request.user.friends.all():
        user_ids.append(user.id)
    posts = Post.objects.filter(created_by__id__in=list(user_ids))
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["POST"])
def post_create(request):
    data = request.data
    form = PostForm(data)
    if form.is_valid():
        post = form.save(commit=False)
        post.created_by = request.user
        post.save()
        serializer = PostSerializer(post)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({"error": "add somehting here later!..."})


@api_view(['DELETE'])
def post_delete(request, pk):
    post = Post.objects.filter(created_by=request.user).get(pk=pk)
    post.delete()

    return JsonResponse({'message': 'post deleted'})


@api_view(['POST'])
def post_report(request, pk):
    post = Post.objects.get(pk=pk)
    post.reported_by_users.add(request.user)
    post.save()

    return JsonResponse({'message': 'post reported'})


@api_view(["GET"])
def post_detail(request, pk):
    user_ids = [request.user.id]

    for user in request.user.friends.all():
        user_ids.append(user.id)

    post = Post.objects.filter(
        Q(created_by_id__in=list(user_ids)) | Q(is_private=False)
    ).get(pk=pk)

    return JsonResponse({"post": PostDetailSerializer(post).data})


@api_view(["GET"])
def post_list_profile(request, id):
    user = User.objects.get(id=id)
    posts = Post.objects.filter(created_by__id=id)
    posts_serializer = PostSerializer(posts, many=True)
    user_serializer = UserSerializer(user)
    return JsonResponse(
        {"posts": posts_serializer.data, "user": user_serializer.data}, safe=False
    )


@api_view(["POST"])
def post_like(request, pk):
    post = Post.objects.get(pk=pk)

    if not post.likes.filter(created_by=request.user):
        like = Like.objects.create(created_by=request.user)

        post = Post.objects.get(pk=pk)
        post.likes_count = post.likes_count + 1
        post.likes.add(like)
        post.save()

        notification = create_notification(request, 'post_like', post_id=post.id)

        return JsonResponse({"message": "like created"})
    else:
        return JsonResponse({"message": "post already liked"})


@api_view(["POST"])
def post_create_comment(request, pk):
    comment = Comment.objects.create(
        body=request.data.get("body"), created_by=request.user
    )

    post = Post.objects.get(pk=pk)
    post.comments.add(comment)
    post.comments_count = post.comments_count + 1
    post.save()

    notification = create_notification(request, 'post_comment', post_id=post.id)

    serializer = CommentSerializer(comment)

    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def get_trends(request):
    serializer = TrendSerializer(Trend.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)
