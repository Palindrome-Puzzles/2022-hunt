import urllib.parse

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction, models
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, reverse

from spoilr.core.api.decorators import inject_team, inject_interaction, require_safe_referrer
from spoilr.core.api.events import dispatch, HuntEvent
from spoilr.core.api.hunt import release_interaction, release_round, release_puzzles
from spoilr.core.models import Puzzle, PuzzleAccess, Round, Team

from hunt.app.core.constants import ROUND_RD1_URL, ROUND_RD2_URL, ROUND_RD3_META_URL, ROUND_RD3_URLS
from hunt.app.core.interactions import on_interaction_email_received
from hunt.app.core.puzzles import unlock_available_puzzles
from hunt.deploy.util import require_hunt_launch
from .common import get_shared_context, verify_team_accessible

@require_hunt_launch()
@inject_team(require_admin=True)
@verify_team_accessible()
@inject_interaction(error_if_inaccessible=False)
@require_safe_referrer
def release_interaction_view(request):
    if not request.interaction.interactiondata.email_key_trigger:
        return HttpResponseForbidden('Can only be used for email-triggered interactions')

    if on_interaction_email_received(request.interaction, request.team):
        next_url = request.META.get('HTTP_REFERER')
        return redirect(next_url or reverse('index'))
    else:
        return HttpResponseForbidden('Interaction not yet available to unlock')

RELEASE_ACT1_INCREASE = 2
INCREASE_RADIUS_AMOUNT_1 = 3

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
def release_act1_view(request):
    context = get_shared_context(request.team)
    act2_unlocked = any(round_info['round'].url == ROUND_RD2_URL for round_info in context['rounds'])
    if act2_unlocked:
        return redirect(reverse('index'))

    with transaction.atomic():
        refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)
        if not refetched_team.teamdata.act2_puzzle_radius_increased:
            refetched_team.teamdata.extra_puzzle_radius += RELEASE_ACT1_INCREASE
            refetched_team.teamdata.act2_puzzle_radius_increased = True
            refetched_team.teamdata.save()

    refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)

    # This is idempotent - no need for a transaction.
    rd2 = Round.objects.get(url=ROUND_RD2_URL)
    rd2_initial_puzzles = Puzzle.objects.select_related('puzzledata').filter(round__url=ROUND_RD2_URL, puzzledata__unlock_order=0)
    release_round(refetched_team, rd2)
    release_puzzles(refetched_team, rd2_initial_puzzles)

    # NB: rd2 increases the radius too by the same amount as the initial released puzzles.
    extra_unlocks = RELEASE_ACT1_INCREASE
    if extra_unlocks:
        unlocked_rd1_puzzles = set(
            pa.puzzle.id for pa in PuzzleAccess.objects.filter(puzzle__round__url=ROUND_RD1_URL, team=refetched_team)
        )
        rd1_puzzles_to_unlock = (Puzzle.objects
            .select_related('puzzledata')
            .filter(round__url=ROUND_RD1_URL, puzzledata__unlock_order__isnull=False)
            .exclude(id__in=unlocked_rd1_puzzles)
            .order_by('puzzledata__unlock_order'))[:extra_unlocks]
        release_puzzles(refetched_team, rd1_puzzles_to_unlock)
        extra_unlocks -= len(rd1_puzzles_to_unlock)

    if extra_unlocks:
        unlocked_rd2_puzzles = set(
            pa.puzzle.id for pa in PuzzleAccess.objects.filter(puzzle__round__url=ROUND_RD2_URL, team=refetched_team)
        )
        rd2_puzzles_to_unlock = (Puzzle.objects
            .select_related('puzzledata')
            .filter(round__url=ROUND_RD2_URL, puzzledata__unlock_order__isnull=False)
            .exclude(id__in=unlocked_rd2_puzzles)
            .order_by('puzzledata__unlock_order'))[:extra_unlocks]
        release_puzzles(refetched_team, rd2_puzzles_to_unlock)
        extra_unlocks -= len(rd2_puzzles_to_unlock)

    unlock_available_puzzles(refetched_team)

    return redirect(reverse('index'))

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
def increase_radius_view(request):
    context = get_shared_context(request.team)
    rd2 = next((round_info for round_info in context['rounds'] if round_info['round'].url == ROUND_RD2_URL), None)
    rd2_meta_solved = any(puzzle_info['solved'] for puzzle_info in rd2['puzzles'] if puzzle_info['puzzle'].is_meta) if rd2 else None
    if not rd2 or rd2_meta_solved:
        return redirect(reverse('index'))

    already_used_act2_release = request.team.teamdata.act2_puzzle_radius_increased
    if already_used_act2_release:
        return redirect(reverse('index'))

    with transaction.atomic():
        refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)
        if not refetched_team.teamdata.radius_increased_1:
            refetched_team.teamdata.extra_puzzle_radius += INCREASE_RADIUS_AMOUNT_1
            refetched_team.teamdata.radius_increased_1 = True
            refetched_team.teamdata.save()

    refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)
    unlock_available_puzzles(refetched_team)

    return redirect(reverse('index'))

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
def unlock_pen_station_view(request):
    context = get_shared_context(request.team)
    rd2 = next((round_info for round_info in context['rounds'] if round_info['round'].url == ROUND_RD2_URL), None)
    rd3_1 = next((round_info for round_info in context['rounds'] if round_info['round'].url == ROUND_RD3_URLS[0]), None)
    if not rd2 or rd3_1 or request.team.teamdata.act3_release:
        return redirect(reverse('index'))

    rd3_1 = Round.objects.get(url=ROUND_RD3_URLS[0])
    rd3_1_initial_puzzles = Puzzle.objects.select_related('puzzledata').filter(round__url=ROUND_RD3_URLS[0], puzzledata__unlock_order=0)
    release_round(request.team, rd3_1)
    release_puzzles(request.team, rd3_1_initial_puzzles)

    rd3_2 = Round.objects.get(url=ROUND_RD3_URLS[1])
    rd3_2_initial_puzzles = Puzzle.objects.select_related('puzzledata').filter(round__url=ROUND_RD3_URLS[1], puzzledata__unlock_order=0)
    release_round(request.team, rd3_2)
    release_puzzles(request.team, rd3_2_initial_puzzles)

    request.team.teamdata.act3_release = True
    request.team.teamdata.save()

    return redirect(reverse('index'))

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
def unlock_more_1_view(request):
    if request.team.teamdata.act3_release_1:
        return redirect(reverse('index'))

    context = get_shared_context(request.team)
    rd3_1 = next((round_info for round_info in context['rounds'] if round_info['round'].url == ROUND_RD3_URLS[0]), None)
    rd3_3 = next((round_info for round_info in context['rounds'] if round_info['round'].url == ROUND_RD3_URLS[2]), None)

    if rd3_1 and not rd3_3:
        rd3 = Round.objects.get(url=ROUND_RD3_URLS[2])
        rd3_initial_puzzles = (Puzzle.objects
            .filter(round__url=ROUND_RD3_URLS[2], puzzledata__unlock_order=0))
        release_round(request.team, rd3)
        release_puzzles(request.team, rd3_initial_puzzles)

        with transaction.atomic():
            refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)
            refetched_team.teamdata.extra_puzzle_radius += 1
            refetched_team.teamdata.act3_release_1 = True
            refetched_team.teamdata.save()

    return redirect(reverse('index'))

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
def unlock_more_2_view(request):
    if request.team.teamdata.act3_release_2:
        return redirect(reverse('index'))

    context = get_shared_context(request.team)
    rd3_3 = next((round_info for round_info in context['rounds'] if round_info['round'].url == ROUND_RD3_URLS[2]), None)
    rd3_6 = next((round_info for round_info in context['rounds'] if round_info['round'].url == ROUND_RD3_URLS[5]), None)

    if rd3_3 and not rd3_6:
        available_rounds = set(round_info['round'].url for round_info in context['rounds'])
        next_unavailable_round = next(round_url for round_url in ROUND_RD3_URLS if round_url not in available_rounds)

        rd = Round.objects.get(url=next_unavailable_round)
        rd_initial_puzzles = (Puzzle.objects
            .filter(round__url=next_unavailable_round, puzzledata__unlock_order=0))
        release_round(request.team, rd)
        release_puzzles(request.team, rd_initial_puzzles)

        with transaction.atomic():
            refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)
            refetched_team.teamdata.extra_puzzle_radius += 1
            refetched_team.teamdata.act3_release_2 = True
            refetched_team.teamdata.save()

    return redirect(reverse('index'))

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
def unlock_more_3_view(request):
    context = get_shared_context(request.team)
    rd3_10 = next((round_info for round_info in context['rounds'] if round_info['round'].url == ROUND_RD3_URLS[9]), None)

    if not rd3_10:
        available_rounds = set(round_info['round'].url for round_info in context['rounds'])
        next_unavailable_round = next(round_url for round_url in ROUND_RD3_URLS if round_url not in available_rounds)
        dispatch(
            HuntEvent.EXTRA_PUZZLES_RELEASED,
            message=f"Released round {next_unavailable_round} via magic link",
            team=request.team,
            object_id=next_unavailable_round,
        )
        rd = Round.objects.get(url=next_unavailable_round)
        rd_initial_puzzles = (Puzzle.objects
            .filter(round__url=next_unavailable_round, puzzledata__unlock_order=0))
        release_round(request.team, rd)
        release_puzzles(request.team, rd_initial_puzzles)

        with transaction.atomic():
            refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)
            refetched_team.teamdata.extra_puzzle_radius += 1
            refetched_team.teamdata.save()
    else:
        dispatch(
            HuntEvent.EXTRA_PUZZLES_RELEASED,
            message=f"Boosted puzzle radius by 8 via magic link",
            team=request.team,
        )
        with transaction.atomic():
            refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)
            refetched_team.teamdata.extra_puzzle_radius = min(
                refetched_team.teamdata.extra_puzzle_radius + 8, 200)
            refetched_team.teamdata.save()

    refetched_team = Team.objects.select_related('teamdata').get(id=request.team.id)
    unlock_available_puzzles(refetched_team)

    return redirect(reverse('index'))

HQ_FROM = 'HQ <hq@mitmh2022.com>'
MORE_ROUNDS_1_SUBJECT = 'Unlocking More Areas'
MORE_ROUNDS_2_SUBJECT = 'Unlocking Even More Areas'
MORE_ROUNDS_3_SUBJECT = 'Unlocking The Next Area'
MORE_ROUNDS_TEXT_TEMPLATE = '''Hello [team name].

We are emailing you to offer to unlock the next region of Pen Station. We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.

This will unlock the following things:
- The next region in the Hunt.
- A number of feeder (non-meta) puzzles.
- Some non-zero number of meta puzzles.

There are some reasons why you may or may not want to click the link.
- Reasons Why:
    - You're not planning on solving the metas you have open anytime soon, and you want to continue to see the rest of the Hunt.
    - You just don't have enough feeder puzzles unlocked to satisfy the size of your team.
- Reasons Why Not:
    - You don't want to overwhelm your team with more puzzles.
    - You want your team to focus on the puzzles and metas that you've got.

If you wish to unlock the next region now, you can do so with the following link: [link]. If you choose not to do so now, you may click the link at any time this weekend up until you open the round normally. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.

–
Team Palindrome
'''
MORE_ROUNDS_HTML_TEMPLATE = '''Hello [team name].

<p>We are emailing you to offer to unlock the next region of Pen Station. We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.</p>

<p>This will unlock the following things:</p>
<ul>
<li>The next region in the Hunt.</li>
<li>A number of feeder (non-meta) puzzles.</li>
<li>Some non-zero number of meta puzzles.</li>
</ul>

<p>There are some reasons why you may or may not want to click the link.</p>
<ul>
<li>Reasons Why:
<ul>
<li>You’re not planning on solving the metas you have open anytime soon, and you want to continue to see the rest of the Hunt.</li>
<li>You just don’t have enough feeder puzzles unlocked to satisfy the size of your team.</li>
</ul>
</li>
<li>Reasons Why Not:
<ul>
<li>You don’t want to overwhelm your team with more puzzles.</li>
<li>You want your team to focus on the puzzles and metas that you’ve got.</li>
</ul>
</li>
</ul>

<p>If you wish to unlock the next region now, you can do so with the following link: <a href="[link]">[link]</a>. If you choose not to do so now, you may click the link at any time this weekend up until you open the round normally. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.</p>

<p>–<br>
Team Palindrome</p>
'''
NEXT_ROUNDS_TEXT_TEMPLATE = '''Hello [team name].

We are emailing you to offer to unlock as many of the next regions of Pen Station as you'd like. We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.

Everytime you click this link, it will unlock the following things:
- The next region in the Hunt.
- A number of feeder (non-meta) puzzles.
- Some non-zero number of meta puzzles.

There are some reasons why you may or may not want to click the link.
- Reasons Why:
    - You're not planning on solving the metas you have open anytime soon, and you want to continue to see the rest of the Hunt.
    - You just don't have enough feeder puzzles unlocked to satisfy the size of your team.
- Reasons Why Not:
    - You don't want to overwhelm your team with more puzzles.
    - You want your team to focus on the puzzles and metas that you've got.

If you wish to unlock the next region now, you can do so with the following link: [link]. You can click this link multiple times to unlock even more rounds. If you choose not to do so now, you may click the link at any time this weekend up until you open the round normally. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.

–
Team Palindrome
'''
NEXT_ROUNDS_HTML_TEMPLATE = '''Hello [team name].

<p>We are emailing you to offer to unlock as many of the next regions of Pen Station as you'd like. We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.</p>

<p>Everytime you click this link, it will unlock the following things:</p>
<ul>
<li>The next region in the Hunt.</li>
<li>A number of feeder (non-meta) puzzles.</li>
<li>Some non-zero number of meta puzzles.</li>
<ul>

<p>There are some reasons why you may or may not want to click the link.</p>
<ul>
<li>Reasons Why:
<ul>
<li>You’re not planning on solving the metas you have open anytime soon, and you want to continue to see the rest of the Hunt.</li>
<li>You just don’t have enough feeder puzzles unlocked to satisfy the size of your team.</li>
</ul>
</li>
<li>Reasons Why Not:
<ul>
<li>You don’t want to overwhelm your team with more puzzles.</li>
<li>You want your team to focus on the puzzles and metas that you’ve got.</li>
</ul>
</li>
</ul>

<p>If you wish to unlock the next region now, you can do so with the following link: <a href="[link]">[link]</a>. You can click this link multiple times to unlock even more rounds. If you choose not to do so now, you may click the link at any time this weekend up until you open the round normally. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.</p>

<p>–<br>
Team Palindrome</p>
'''

PEN_STATION_SUBJECT = 'Unlocking Pen Station'
PEN_STATION_TEXT_TEMPLATE = '''Hello [team name].

We are emailing you to offer to unlock the next act. We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.

This will unlock the following things:
- The next act of the Hunt.
- Enough feeder (non-meta) puzzles to get you up to 10 feeders unlocked.
- Some non-zero number of meta puzzles in the next act.

There are some reasons why you may or may not want to click the link.
- Reasons Why:
    - You're not planning on solving the Ministry anytime soon, and you want to continue to see the rest of the Hunt.
    - You just don’t have enough feeder puzzles unlocked to satisfy the size of your team.
- Reasons Why Not:
    - You don't want to overwhelm your team with more puzzles.
    - You want your team to focus on solving the Ministry before unlocking other things.
    - There is a beautiful mid-hunt interaction and reward, and your team wants to reach that special point.

If you wish to unlock the next Act now, you can do so with the following link: https://bookspace.world/release/pen-station/. If you choose not to do so now, you may click the link at any time this weekend up until you open Act 3 normally. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.

–
Team Palindrome
'''
PEN_STATION_HTML_TEMPLATE = '''<p>Hello [team name].</p>

<p>We are emailing you to offer to unlock the next act. We know that some teams prefer to focus on accomplishing specific goals throughout the Hunt, while others just want to solve as many puzzles as possible. Because teams have vastly different goals and vastly different capabilities, we wanted to provide you with the option of the free unlock without forcing you into it.</p>

<p>This will unlock the following things:</p>
<ul>
<li>The next act of the Hunt.</li>
<li>Enough feeder (non-meta) puzzles to get you up to 10 feeders unlocked.</li>
<li>Some non-zero number of meta puzzles in the next act.</li>
</ul>

<p>There are some reasons why you may or may not want to click the link.</p>
<ul>
<li>Reasons Why:
<ul>
<li>You're not planning on solving the Ministry anytime soon, and you want to continue to see the rest of the Hunt.</li>
<li>You just don’t have enough feeder puzzles unlocked to satisfy the size of your team.</li>
</ul>
</li>
<li>Reasons Why Not:
<ul>
<li>You don't want to overwhelm your team with more puzzles.</li>
<li>You want your team to focus on solving the Ministry before unlocking other things.</li>
<li>There is a beautiful mid-hunt interaction and reward, and your team wants to reach that special point.</li>
</ul>
</li>
</ul>

<p>If you wish to unlock the next Act now, you can do so with the following link: <a href="https://bookspace.world/release/pen-station/">https://bookspace.world/release/pen-station/</a>. If you choose not to do so now, you may click the link at any time this weekend up until you open Act 3 normally. If you have any questions about how this works, do not hesitate to use the Contact HQ form to ask us.</p>

<p>–<br>
Team Palindrome</p>
'''

# TODO(sahil): To run this with a cron job, we need to disable authentication. Or just
# visit the URL periodically. Or of course, build another form of authentication. Investigate!
@require_hunt_launch()
@inject_team(require_admin=True)
def email_to_unlock_more_view(request):
    emailed = []
    for team in Team.objects.all():
        context = get_shared_context(team)
        unlocked_round_urls = set(round_info['round'].url for round_info in context['rounds'])

        if ROUND_RD2_URL not in unlocked_round_urls: continue

        subject = None
        body_text = None
        body_html = None
        if ROUND_RD3_URLS[0] not in unlocked_round_urls and not team.teamdata.act3_release_emailed:
            subject = PEN_STATION_SUBJECT
            body_text = PEN_STATION_TEXT_TEMPLATE.replace('[team name]', team.name)
            body_html = PEN_STATION_HTML_TEMPLATE.replace('[team name]', team.name)

            team.teamdata.act3_release_emailed = True

        elif ROUND_RD3_URLS[0] in unlocked_round_urls and ROUND_RD3_URLS[2] not in unlocked_round_urls and not team.teamdata.act3_release_1_emailed:
            subject = MORE_ROUNDS_1_SUBJECT
            body_text = MORE_ROUNDS_TEXT_TEMPLATE.replace('[team name]', team.name).replace('[link]', 'https://bookspace.world/release/pen-station/1')
            body_html = MORE_ROUNDS_HTML_TEMPLATE.replace('[team name]', team.name).replace('[link]', 'https://bookspace.world/release/pen-station/1')

            team.teamdata.act3_release_1_emailed = True

        elif ROUND_RD3_URLS[2] in unlocked_round_urls and ROUND_RD3_URLS[5] not in unlocked_round_urls and not team.teamdata.act3_release_2_emailed:
            subject = MORE_ROUNDS_2_SUBJECT
            body_text = MORE_ROUNDS_TEXT_TEMPLATE.replace('[team name]', team.name).replace('[link]', 'https://bookspace.world/release/pen-station/2')
            body_html = MORE_ROUNDS_HTML_TEMPLATE.replace('[team name]', team.name).replace('[link]', 'https://bookspace.world/release/pen-station/2')

            team.teamdata.act3_release_2_emailed = True

        elif ROUND_RD3_URLS[9] not in unlocked_round_urls and not team.teamdata.act3_release_3_emailed:
            subject = MORE_ROUNDS_3_SUBJECT
            body_text = NEXT_ROUNDS_TEXT_TEMPLATE.replace('[team name]', team.name).replace('[link]', 'https://bookspace.world/release/pen-station/next')
            body_html = NEXT_ROUNDS_HTML_TEMPLATE.replace('[team name]', team.name).replace('[link]', 'https://bookspace.world/release/pen-station/next')
            team.teamdata.act3_release_3_emailed = True

        if body_text:
            mail = EmailMultiAlternatives(
                subject, body_text,
                HQ_FROM, [team.shared_account.email])
            mail.attach_alternative(body_html, 'text/html')
            mail.send()
            emailed.append(team.name)

            team.teamdata.save()

    return HttpResponse(
        ('Emailed ' + ', '.join(emailed))
        if emailed else
        'No team emailed')
