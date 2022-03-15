from django.contrib import admin

from .special_puzzles.puzzle555_completing_the_story.progress import P555CTSBookModel

class P555CTSBookModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'book', 'found_time')

admin.site.register(P555CTSBookModel, P555CTSBookModelAdmin)
