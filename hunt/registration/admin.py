from django.contrib import admin

from .models import TeamRegistrationInfo, UserAuth, UnattachedSolverRegistrationInfo

admin.site.register(TeamRegistrationInfo)
admin.site.register(UnattachedSolverRegistrationInfo)
admin.site.register(UserAuth)
