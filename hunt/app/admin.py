from django.contrib import admin
from django import forms
from hunt.app.models import TeamData, RoundData, PuzzleData

class TeamDataAdmin(admin.ModelAdmin):
    list_display = ['team']
    search_fields = ['team__name']

admin.site.register(TeamData, TeamDataAdmin)

class PuzzleDataAdmin(admin.ModelAdmin):
    def puzzle_name(data):
        return '%s (%s)' % (data.puzzle.name, data.puzzle.round.name)

    puzzle_name.short_description = 'Puzzle Name'
    list_filter = ['puzzle__round__name']
    list_display = [puzzle_name]
    search_fields = ['puzzle__name']
    ordering = ['puzzle__round__order', 'puzzle__order']

admin.site.register(PuzzleData, PuzzleDataAdmin)

class RoundDataAdmin(admin.ModelAdmin):
    def round_name(data):
        return data.round.name

    list_display = ['round']
    ordering = ['round__order']

admin.site.register(RoundData, RoundDataAdmin)
