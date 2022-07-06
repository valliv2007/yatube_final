from core.models import CreateModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             unique=True,
                             verbose_name="name of group")
    slug = models.SlugField(unique=True, verbose_name="url name of group")
    description = models.TextField(verbose_name="description of group")

    def __str__(self):
        return self.title


class Post(CreateModel):
    text = models.TextField(verbose_name="Текст поста",
                            help_text="Текст нового поста")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор поста")
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              verbose_name="Группа",
                              related_name="posts",
                              help_text="Группа, к которой будет"
                                        " относиться пост")
    image = models.ImageField(verbose_name="Изображение",
                              upload_to="posts/",
                              blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.text[:15]


class Comment(CreateModel):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name="comments",
                             verbose_name="post comment")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="author of comment")
    text = models.TextField(verbose_name="comment text")

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name="follower",
                             on_delete=models.CASCADE,
                             verbose_name="follower")
    author = models.ForeignKey(User,
                               related_name="following",
                               on_delete=models.CASCADE,
                               verbose_name="following")
