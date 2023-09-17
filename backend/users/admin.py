from django.contrib import admin

from backend.settings import EMPTY_FIELD_VALUE
from users.models import User, Follow


class UserAdmin(admin.ModelAdmin):
    """Настройки админ. панели для модели пользователей. """
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )
    search_fields = ('email', 'username')
    empty_value_display = EMPTY_FIELD_VALUE


class FollowAdmin(admin.ModelAdmin):
    """Настройки админ. панели для модели подписок на авторов."""
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user__username', 'user__email')
    empty_value_display = EMPTY_FIELD_VALUE


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
