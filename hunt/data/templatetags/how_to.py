from django import template

register = template.Library()

@register.filter
def how_to_component_sections(puzzles, is_public):
    sections = [
        "1-b1pO8lJA3v",
        "2-38RHrgNz1w",
        "3-0bLyL5TApz",
        "4-CMkxSykzBd",
        "5-ebXMASshOg",
        "6-uSLttyOgPH",
        "7-pKX442vlXU",
        "8-7u5XNYxJjP",
        "9-SHHVwI9kBS",
    ]
    feeders_solved = len(list(puzzle for puzzle in puzzles if puzzle['solved'] or is_public))
    sections = sections[:feeders_solved]
    return sections
