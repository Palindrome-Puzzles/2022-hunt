from django import template

register = template.Library()

@register.filter
def romance_costumes(unlocked_puzzles):
    ids = {
        460: { "order": 1, "costume": "Baseball Player"},
        511: { "order": 2, "costume": "Cerberus"},
        480: { "order": 3, "costume": "Hamlet"},
        335: { "order": 4, "costume": "St. Patrick"},
        475: { "order": 5, "costume": "Imhotep"},
        25: { "order": 6, "costume": "Grand High Witch"},
        160: { "order": 7, "costume": "Dogberry"},
        478: { "order": 8, "costume": "Smithers"},
        369: { "order": 9, "costume": "Offred"},
        438: { "order": 10, "costume": "Lando Calrissian"},
        484: { "order": 11, "costume": "Dracula"},
        269: { "order": 12, "costume": "Lara Croft"},
        546: { "order": 13, "costume": "Moana"},
        263: { "order": 14, "costume": "Cleopatra"},
    }
    output = []
    for puzzle in unlocked_puzzles:
        try:
            id = puzzle['puzzle'].external_id
            obj = ids[id]
            order = obj['order']
            output.append(
                {
                    'order': order,
                    'costume_name': obj['costume'],
                    'costume_url': "images/{}.png".format(order),
                    'solved': puzzle['solved'],
                    'puzzle': puzzle['puzzle']
                }
            )
        except KeyError as e:
            continue
    output.sort(key=lambda x: x['order'])
    return output

@register.filter
def romance_notes(unlocked_puzzles, is_public):
    notes = [
        "1. One complete Premium Edition game lasting some number of rounds was played by exactly 5 players, using the required deck (except that one or more cards had been lost). During the game, individual instances of attendees (not all different) were discarded exactly 93 times. From the information you will receive you will be able to determine how many times each particular attendee was discarded during the game. (The specific order of those discards is unrecoverable and irrelevant.)",
        "2. The player who won the game made the final discard of the game, having received no tokens that round until after making that discard. The only other round (call it Round X) in which that player received tokens was one in which that player discarded that same game-ending attendee as the final discard of Round X, similarly having received no tokens in Round X until after that attendee was discarded.",
        "3. In at least 60 percent of the rounds, one attendee (not necessarily the same one each time) was discarded strictly more than — not tied with — any other attendee in that round.",
        "4. For every integer from 1 through N inclusive, where N is the maximum number of times any attendee was discarded over the course of the game, there was at least one attendee discarded that many times. Exactly two of those integers 1 through N are represented by discards of more than one attendee.",
        "5. One particular player was the first player knocked out in every round, each time being knocked out on the turn of the same other particular player, with the player doing the knocking out discarding an attendee and selecting a player, but otherwise neither communicating anything or revealing their hand to anyone. As fate would have it, the player doing all of that knocking out ended the game with no tokens (as did one other player), whereas the always-knocked-out-first player ended up having two tokens at the end of the game.",
        "6. Three particular attendees were discarded the same number of times — call it Y — during the game (with no other attendee being discarded exactly Y times). The total number of these discards (thus, 3Y) was less than the total number of discards of all attendees discarded fewer than Y times, and also less than the total number of discards of all attendees discarded more than Y times.",
        "7. At most 10 different attendees with a strength of 0, 1, 2, 3, 4, 5, or 6 were discarded during the game. The two attendees with strength 2 were discarded a different number of times.",
        "8. Exactly one attendee had a strength of exactly one less than the total number of times it was discarded during the game.",
        "9. At one point, a player held 2 attendees differing in strength by exactly 4 and discarded only the lower-strength one, knowing it would not and could not have any effect on the 2 other players remaining in the round, but recognizing that if they had instead discarded the higher-strength attendee, they would have been forced to immediately discard the lower-strength attendee anyway. This was the only time during that round that this lower-strength attendee was discarded.",
        "10. At least three rounds involved the discard of a particular attendee with a strength less than 5 as a player’s (not necessarily always the same player) first discard of the round and with no other discard of that attendee during the round. These discards did not result in any further action by anyone or the identification of any player.",
        "11. An attendee that never has any effect when or after it is discarded was discarded exactly twice as many times as an attendee with a strength of exactly one more or one less.",
        "12. One attendee, the discarding of which (as the discarder’s turn) always resulted in comparing the discarder’s hand with another, was discarded exactly twice as many times as a different attendee, the discarding of which (as the discarder’s turn) always resulted in comparing the discarder’s hand with another.",
        "13. At least 3 different players discarded an attendee of strength 5 at some point, which each time resulted in an immediate effect on another player.",
        "14. In one round, the very first attendee discarded allowed the discarder to look at two attendees the discarder had not yet seen; that discarded attendee was not discarded again during that round. A particular attendee with a strength of 2 was discarded more times during the game than was a particular attendee with a strength of 5, and coincidentally both of those attendees were discarded exactly the same number of times that they were discarded during a by-the-rules four-handed game that some of the players had played earlier that day, while waiting for the fifth player to arrive.",
    ]
    feeders_solved = len(list(puzzle for puzzle in unlocked_puzzles if not puzzle['puzzle'].is_meta and (puzzle['solved'] or is_public)))
    notes = notes[:feeders_solved]
    return notes
