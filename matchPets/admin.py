from django.contrib import admin

from .models import FriendshipRequest, Message, Notification, Pet, User

admin.site.register(User)
admin.site.register(Pet)  # para poder ver las mascotas desde admin


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'user', 'tipo', 'leida', 'created_at')
    list_filter = ('tipo', 'leida')


@admin.register(FriendshipRequest)
class FriendshipRequestAdmin(admin.ModelAdmin):
    list_display = ('from_pet', 'to_pet', 'from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'read', 'created_at')
    list_filter = ('read',)
