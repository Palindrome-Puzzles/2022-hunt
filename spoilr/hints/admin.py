from django.contrib import admin

from spoilr.core.admin import PuzzleAccessRoundFilter
from spoilr.core.models import Puzzle

from .models import HintSubmission

class HintSubmissionAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['puzzle'].queryset = Puzzle.objects.all()
        return super(HintSubmissionAdmin, self).render_change_form(request, context, *args, **kwargs)

    list_display = ('__str__', 'create_time', 'team', 'puzzle', 'resolved_time')
    list_filter = (PuzzleAccessRoundFilter, 'team__name')
    search_fields = ['team__name', 'puzzle__name', 'puzzle__round__name']
    ordering = ['create_time']

admin.site.register(HintSubmission, HintSubmissionAdmin)
