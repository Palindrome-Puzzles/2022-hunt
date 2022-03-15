from django.contrib import admin

from .models import Handler, HqLog, Task

admin.site.register(Handler)
admin.site.register(HqLog)
admin.site.register(Task)
