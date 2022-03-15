from django import template

from hunt.app.core.assets.refs import get_round_static_path

register = template.Library()

FANTASY_GLYPHS = {
    373: "anumberofgames-2wyJSLC8iP", #a number of games
    110: "curiouscustoms-LxZroIvVo5", #curious customs
    452: "garden-zaWMFk0MiY", #enchanted garden
    474: "delicious-btyXLNjuYV", #magically delicious
    276: "potions-As79KGQbHF", #potions
    492: "royalsteeds-nOUbnKjHjV", #royal steeds
    163: "somethingcommand-goAxrdrXvu", #something command
    477: "sorcery-zXNjJA52qV", #sorcery
}

@register.simple_tag()
def fantasy_submission(puzzle, team):
    id = puzzle.external_id
    glyph = FANTASY_GLYPHS.get(id, None)

    if (puzzle.is_meta):
        return {
            'glyph_filename': None
        }

    return {
        'puzzle_url': puzzle.url,
        'glyph_filename': "{}.jpg".format(glyph),
        'rd_root': get_round_static_path(puzzle.round.url, variant='round'),
    }

@register.filter
def fantasy_feeders(puzzles, is_public):
    stub_solve_time = now() if is_public else None
    solved_fantasy_feeders = list(
        puzzle_info for puzzle_info in puzzles if (puzzle_info['solved'] or is_public) and not puzzle_info['puzzle'].is_meta)
    solved_fantasy_feeders.sort(key=lambda puzzle_info: puzzle_info['solved_time'] or stub_solve_time)
    for feeder in solved_fantasy_feeders:
        feeder['glyph'] = FANTASY_GLYPHS.get(feeder['puzzle'].external_id, None)
    return solved_fantasy_feeders
