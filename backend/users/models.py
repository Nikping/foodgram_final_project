from django.db import models
from django.db.models import UniqueConstraint
from django.forms import ValidationError

from django.contrib.auth import get_user_model

User = get_user_model()


class Follow(models.Model):
    """Модель подписки на автора."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('-id', )
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'{self.user.get_username} оформил подписку на: '
            f'{self.author.get_username}'
        )

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Подписку на самого себя оформить нельзя!'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
