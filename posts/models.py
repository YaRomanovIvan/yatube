from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
    )
    slug = models.SlugField(
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание",
    )

    class Meta:
        verbose_name_plural = "Группы"
        verbose_name = "Группа"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        blank=True,
        null=True,
    )
    image = models.ImageField(
        upload_to="posts/", blank=True, null=True, verbose_name="Изображение"
    )

    class Meta:
        verbose_name_plural = "Посты"
        verbose_name = "Пост"
        ordering = ["-pub_date"]

    def __str__(self):
        return (
            f"Пользователь: {self.author.username}, "
            f"Группа: {self.group}, "
            f'Дата и время: {self.pub_date.strftime("%d.%m.%Y %H:%M:%S")}, '
            f"Текст: {self.text[:15]}, "
            f"Картинка: {self.image}"
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments", verbose_name="Автор"
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время публикации"
    )

    class Meta:
        verbose_name_plural = "Комментарии"
        verbose_name = "Комментарий"
        ordering = ["-created"]

    def __str__(self):
        return (
            f"Пост: {self.post}, "
            f"Автор: {self.author}, "
            f"Текст: {self.text[:15]}, "
            f'Дата: {self.created}.strftime("%d.%m.%Y %H:%M:%S")'
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", verbose_name="Автор"
    )

    class Meta:
        verbose_name = "Система подписки"

    def __str__(self):
        return f"Автор: {self.author}, Пользователь: {self.user}"
