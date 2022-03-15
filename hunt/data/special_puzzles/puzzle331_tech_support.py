"""
Puzzle backends for the puzzle: "Tech Support".
"""
import logging, random, re

from django.http import HttpResponseBadRequest, JsonResponse, HttpRequest
from django.http.response import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Template, Context
from django.template.loader import render_to_string
from django.shortcuts import render
from django.conf import settings

from hunt.app.views.common import require_puzzle_access, get_puzzle_context, get_round_summary
from hunt.app.core.assets.resolvers import create_puzzle_url_resolver, create_round_url_resolver
from hunt.app.core.assets.rewriter import rewrite_relative_paths
from hunt.app.core.assets.refs import get_round_static_path
from hunt.data_loader.puzzle import get_puzzle_data_text
from hunt.data_loader.round import get_round_data_text
from hunt.deploy.util import require_hunt_launch

from spoilr.core.api.decorators import inject_team, inject_puzzle

# Rough outline of how this works:
# 1. We receive a payload from the puzzle with the opcode, current state hash. and (optionally) the selected images
# 2. If the session hash matches a non-starting round, then we use that round, otherwise we assume it's the starting round
# 3. If there's a payload, we check whether all of the images selected were in the round, and none of the unselected images were
# 4. We also check that we receive exactly nine unique image hashes
# 5. If either 3 or 4 fail then we return a generic error, otherwise we return the next hash

logger = logging.getLogger(__name__)

@require_puzzle_access(allow_rd0_access=False)
@inject_team(redirect_if_missing=True)
def chat(request: HttpRequest, **kwargs) -> HttpResponse:
    common_style = get_round_data_text(request.puzzle.round.url or 'new-you-city', 'round_common.css')
    round_url_resolver = create_round_url_resolver(request.puzzle.round.url or 'new-you-city', 'round')

    context = get_puzzle_context(request.team, request.puzzle)

    context['round_info'] = get_round_summary(request.team, request.puzzle.round, None)
    context['rd_root'] = get_round_static_path(request.puzzle.round.url or 'new-you-city', variant='round')
    context['is_breakglass_access'] = False

    context_obj= Context(context)

    context['round_common_style'] = rewrite_relative_paths(
        Template(common_style).render(context_obj), round_url_resolver) if common_style else None

    page = render(request, 'puzzle_files/tech-support/chat.tmpl', context)
    return page

@require_http_methods(['GET','POST','PUT','HEAD','DELETE'])
@require_hunt_launch()
@csrf_exempt
@inject_team(redirect_if_missing=False)
@inject_puzzle(error_if_inaccessible=False)
def website_page(request: HttpRequest, **kwargs) -> HttpResponse:
    common_style = get_round_data_text(request.puzzle.round.url or 'new-you-city', 'round_common.css')
    round_url_resolver = create_round_url_resolver(request.puzzle.round.url or 'new-you-city', 'round')

    context = get_puzzle_context(request.team, request.puzzle)

    context['round_info'] = get_round_summary(request.team, request.puzzle.round, None)
    context['rd_root'] = get_round_static_path(request.puzzle.round.url or 'new-you-city', variant='round')
    context['is_breakglass_access'] = False

    context_obj= Context(context)

    context['round_common_style'] = rewrite_relative_paths(
        Template(common_style).render(context_obj), round_url_resolver) if common_style else None

    page = render(request, 'puzzle_files/tech-support/info.tmpl', context)
    responses = {
            'POST': 'FOOER TEAD CENTE BAS HAD',
            'HEAD': 'VG MBED AR M AV',
            'PUT': 'FORT DEV MAID MATER',
            'DELETE': 'STRONGO NUL COLE',
        }

    if request.method in ["POST", "HEAD", "PUT", "DELETE"]:
        page.status_code = 202
        page.headers['x-elements'] = responses[request.method]

    elif request.method == "GET":
        page.headers['x-elements'] = "You got this message! How about you post, put, head and delete some elements to get the Really Full Convention document (DOC)?"
    else:
        page.headers['']

    return page


@require_POST
@require_puzzle_access(allow_rd0_access=False)
def password_reset(request: HttpRequest) -> JsonResponse:
    reset_email = settings.PUZZLE_TECH_SUPPORT_EMAIL
    recipient = request.POST['email']
    at_part = re.match("^.+?\+(.+?)@.+$", recipient)
    replace = True
    answers = [
        "AND",
        "ARM",
        "AZE",
        "BEL",
        "BRB",
        "FRA",
        "ITA", '840', 'UNITEDSTATESOFAMERICA', "USA", "US"
    ]
    start_headers = {"x-message-query": "I'm a logical conjunction"}
    email_headers = {}
    subject = "Your Tech Support request"
    if at_part and at_part.groups() and any([ at_part.group(1).upper()== (x) for x in answers ]):
        if at_part.group(1).upper()== ("AND"):#I
            email_headers = {
                'x-message-query': "Some alternative to x86/x64"
            }
        elif at_part.group(1).upper()== ("ARM"):#S
            email_headers = {
                'x-message-query': "Often what you might see on a vehicle from Anhalt-Zerbst"
            }
        elif at_part.group(1).upper()== ("AZE"):#O
            email_headers = {
                'x-message-query': "Say waist in Istanbul"
            }
        elif at_part.group(1).upper()== ("BEL"):#S
            email_headers = {
                'x-message-query': "U no I'll return soon"
            }
        elif at_part.group(1).upper()== ("BRB"):#U
            email_headers = {
                'x-message-query': "Major airport you might fly into if you want to see the Geographer in person"
            }
        elif at_part.group(1).upper()== ("FRA"):#M
            email_headers = {
                'x-message-query': "She's the chair of the ABC, down under"
            }
        elif at_part.group(1).upper()== ("ITA"):#S
            email_headers['x-message'] = "Please request again with your email alias + ans"
        elif at_part.group(1).upper()== ("840"):
            subject = "🤏 " + subject
            email_headers['x-message'] = "This is a clue for the answer you want, in short."
            replace = False
        elif at_part.group(1).upper()== ("UNITEDSTATESOFAMERICA"):
            subject = "🤏 " + subject
            email_headers['x-message'] = "This is the country you want, briefly."
            replace = False
        elif at_part.group(1).upper()== ("US"):
            subject = "🤏 " + subject
            email_headers['x-message'] = "This is not the ans we are looking for."
            replace = False
        elif at_part.group(1).upper()== ("USA"):
            subject = "🇺🇸 " + subject
            email_headers['x-message'] = "Thank you. For further assistance, please seek support via chat or webpage."
            replace = False
        else:
            email_headers = start_headers
    else:
            if '+' in recipient:
                subject = "⛔ " + subject
            email_headers = start_headers
    if replace:
        email_headers['x-message'] = "Please request again with your email alias + ans"

    if reset_email:
        mail = EmailMultiAlternatives(
            subject=subject,
            body=render_to_string("puzzle_files/tech-support/emails/txt.txt.tmpl", {}),
            from_email=reset_email,
            to=[recipient],
            alternatives=[(render_to_string("puzzle_files/tech-support/emails/html.html.tmpl", {}), "text/html")],
            reply_to=[reset_email],
            headers=email_headers
        )
        mail.send(fail_silently=True)
        return JsonResponse({'success':True})


@require_POST
@require_puzzle_access(allow_rd0_access=False)
def chat_bot(request: HttpRequest) -> JsonResponse:
    WORDS = [
        "understandings", "understanding", "conversations", "disappearing", "informations", "grandmothers", "grandfathers", "questionings", "conversation", "information", "approaching", "understands", "immediately", "positioning", "questioning", "grandmother", "travellings", "questioners", "recognizing", "recognizers", "televisions", "remembering", "rememberers", "expressions", "discovering", "disappeared", "interesting", "grandfather", "straightest", "controllers", "controlling", "considering", "remembered", "cigarettes", "companying", "completely", "spreadings", "considered", "continuing", "controlled", "stationing", "controller", "straighter", "stretching", "businesses", "somebodies", "soldiering", "countering", "darknesses", "situations", "directions", "disappears", "younglings", "suggesting", "afternoons", "breathings", "distancing", "screenings", "schoolings", "especially", "everything", "everywhere", "explaining", "explainers", "expression", "branchings", "revealings", "repeatings", "surprising", "rememberer", "somewheres", "television", "themselves", "recognizer", "recognizes", "recognized", "belongings", "finishings", "travelling", "questioner", "beginnings", "travelings", "questioned", "followings", "pretending", "forgetting", "forgetters", "forwarding", "positioned", "travellers", "gatherings", "perfecting", "understand", "understood", "weightings", "approaches", "officering", "numberings", "happenings", "mentioning", "letterings", "husbanding", "imaginings", "approached", "apartments", "whispering", "interested", "discovered", "spinnings", "clearings", "climbings", "spendings", "clothings", "colorings", "soundings", "truckings", "somewhere", "troubling", "companies", "companied", "beautiful", "computers", "confusing", "considers", "travelers", "youngling", "continues", "continued", "traveller", "traveling", "yellowing", "apartment", "beginning", "wheelings", "travelled", "sometimes", "something", "appearing", "cornering", "believing", "countered", "believers", "countries", "soldiered", "coverings", "creatures", "crossings", "accepting", "daughters", "belonging", "situation", "silvering", "different", "silencing", "touchings", "bettering", "tomorrows", "disappear", "thinkings", "boardings", "discovers", "admitting", "wrappings", "distances", "distanced", "sightings", "shrugging", "doctoring", "showering", "shoulders", "shoppings", "shootings", "dressings", "sheetings", "shadowing", "settlings", "servicing", "seriously", "seconding", "searching", "weighting", "screening", "screaming", "schooling", "teachings", "bothering", "everybody", "botherers", "bottoming", "excepting", "expecting", "explained", "direction", "explainer", "surprised", "surprises", "waterings", "branching", "revealing", "returning", "surfacing", "familiars", "repeating", "fathering", "reminding", "supposing", "breasting", "attacking", "remembers", "breathing", "remaining", "breathers", "brightest", "brownings", "suggested", "recognize", "fightings", "attention", "figurings", "receiving", "reasoning", "realizing", "fingering", "buildings", "finishing", "stupidest", "stuffings", "questions", "watchings", "flashings", "strongest", "strikings", "flighting", "flowering", "promisers", "promising", "following", "bathrooms", "prettiest", "pretended", "stretched", "foreheads", "foresting", "stretches", "forgotten", "pressings", "forgetter", "strangest", "preparing", "forwarded", "strangers", "possibles", "positions", "afternoon", "straights", "pocketing", "gardening", "pleasings", "wondering", "gathering", "picturing", "personals", "perfected", "stomaches", "stomached", "carefully", "stationed", "catchings", "parenting", "paintings", "orderings", "groupings", "wintering", "officered", "offerings", "centering", "numbering", "neighbors", "certainly", "happening", "narrowing", "narrowest", "mountains", "mothering", "mirroring", "middlings", "messaging", "standings", "mentioned", "mattering", "marriages", "histories", "machining", "hospitals", "listening", "lightings", "springing", "lettering", "husbanded", "spreaders", "whispered", "imagining", "imaginers", "spreading", "important", "languages", "answering", "cigarette", "interests", "spiriting", "cleanings", "knockings", "soundest", "coatings", "sounders", "sounding", "colleges", "coloring", "colorful", "wouldn't", "training", "colorers", "sorriest", "worrying", "belonged", "approach", "tracking", "touchers", "touching", "computer", "whatever", "toppings", "confused", "confuses", "workings", "consider", "bettered", "teething", "tonights", "tonguers", "tonguing", "continue", "arriving", "tomorrow", "controls", "together", "blacking", "blackest", "throwers", "blocking", "throwing", "coolings", "someones", "blockers", "somebody", "thirties", "soldiers", "cornered", "weighted", "counting", "thoughts", "counters", "thinking", "thinners", "thinning", "coursing", "covering", "thinnest", "craziest", "snapping", "creating", "creature", "thickest", "boarding", "crossing", "smokings", "crowding", "smelling", "smallest", "cuttings", "slipping", "slightly", "dancings", "sleepers", "sleeping", "slamming", "wordings", "darkness", "daughter", "boatings", "skinning", "weddings", "thanking", "sittings", "deciding", "deciders", "singling", "singings", "despites", "simplest", "terrible", "silvered", "tellings", "wearings", "youngest", "watering", "silences", "teachers", "bookings", "agreeing", "teaching", "discover", "attacked", "bothered", "botherer", "watching", "swingers", "bottling", "distance", "silenced", "signings", "bottomed", "sighting", "shutting", "shrugged", "wondered", "swinging", "doctored", "sweetest", "showered", "showings", "doorways", "shouting", "shoulder", "wronging", "shortest", "surprise", "dragging", "shopping", "shooters", "drawings", "actually", "shooting", "dreaming", "dressing", "avoiding", "shitting", "shirting", "shipping", "drinking", "drinkers", "braining", "sheeting", "sharpest", "drivings", "sharpers", "dropping", "droppers", "shadowed", "surfaced", "settling", "washings", "settings", "services", "serviced", "earliest", "backings", "earthing", "servings", "branches", "branched", "seconded", "seatings", "surfaces", "searched", "searches", "walkings", "screened", "waitings", "screamed", "supposed", "emptiest", "emptying", "breaking", "breakers", "schooled", "enjoying", "enjoyers", "entering", "runnings", "breasted", "rounders", "rounding", "supposes", "everyone", "visitors", "visiting", "breathed", "excepted", "roofings", "exciting", "breathes", "expected", "rollings", "bankings", "breather", "explains", "villages", "bridging", "viewings", "brighter", "ringings", "righting", "suitings", "bringing", "revealed", "bringers", "returned", "failings", "repliers", "replying", "repeated", "brothers", "familiar", "wintered", "families", "suggests", "farthest", "furthest", "browning", "fathered", "removing", "building", "reminded", "bathroom", "allowing", "suddenly", "remember", "allowers", "feedings", "builders", "burnings", "feelings", "remained", "refusing", "stupider", "windings", "although", "stuffing", "studying", "business", "angriest", "fighting", "fighters", "students", "figuring", "received", "twenties", "receives", "fillings", "reasoned", "findings", "stronger", "turnings", "realizes", "realized", "readiest", "fingered", "readying", "striking", "trusters", "finishes", "trusting", "finished", "readings", "reachers", "reaching", "quieters", "quietest", "quieting", "fittings", "quickest", "writings", "beaching", "question", "trucking", "callings", "stranger", "flashing", "beatings", "answered", "flattest", "flatting", "flighted", "straight", "troubled", "flowered", "pullings", "storming", "promiser", "couldn't", "promised", "promises", "couldn’t", "followed", "stoppers", "problems", "probably", "prettier", "stopping", "pretends", "stomachs", "troubles", "pressers", "tripping", "forehead", "stickers", "forested", "pressing", "whispers", "carrying", "sticking", "carriers", "stepping", "stealers", "forwards", "stealing", "becoming", "prepares", "prepared", "powering", "freeings", "stations", "possible", "position", "freshest", "beddings", "wrapping", "fronting", "catching", "fuckings", "policing", "funniest", "pointers", "pointing", "catchers", "pocketed", "gardened", "starters", "ceilings", "pleasing", "gathered", "starting", "centered", "platings", "plastics", "planning", "pictured", "pictures", "traveler", "pickings", "personal", "glancing", "yourself", "chancing", "perfects", "changing", "peopling", "partying", "partings", "parented", "grabbing", "grabbers", "changers", "checking", "starring", "bedrooms", "checkers", "pairings", "standing", "painting", "outsides", "greatest", "cheeking", "greening", "greenest", "grouping", "ordering", "anything", "openings", "guarding", "wheeling", "officers", "guessing", "spreader", "offering", "children", "anywhere", "numbered", "choicest", "noticers", "noticing", "hallways", "nothings", "hangings", "nobodies", "admitted", "neighbor", "choosing", "choosers", "happened", "neckings", "happiest", "narrowed", "narrower", "spotting", "churches", "mouthing", "traveled", "mountain", "mothered", "accepted", "mornings", "mirrored", "headings", "spirited", "hearings", "heatings", "circling", "middling", "messaged", "messages", "heaviest", "wouldn’t", "spinners", "mentions", "helpings", "cleanest", "memories", "meetings", "meanings", "appeared", "mattered", "marrieds", "marrying", "marriage", "yellowed", "markings", "cleaning", "managing", "cleaners", "holdings", "machined", "machines", "lunching", "luckiest", "lowering", "longings", "clearest", "hospital", "lockings", "littlest", "clearing", "listened", "housings", "lightest", "lighting", "lighters", "spinning", "hundreds", "hurrying", "believes", "spenders", "believed", "climbing", "husbands", "lettered", "lettings", "learning", "leadings", "ignoring", "laughing", "ignorers", "imagines", "yellower", "imagined", "climbers", "imaginer", "spending", "closings", "specials", "speakers", "language", "believer", "clothing", "clouding", "speaking", "interest", "spacings", "landings", "knowings", "southest", "jacketed", "knocking", "kitchens", "kissings", "killings", "keepings", "dresses", "biggest", "sticker", "careful", "shirted", "warmers", "shipped", "birding", "drinker", "carries", "sheeted", "warming", "carried", "carrier", "driving", "sharper", "tonight", "drivers", "casings", "sharers", "sharing", "stepped", "dropped", "dropper", "whisper", "shapers", "shaping", "shakers", "shaking", "tonguer", "shadows", "stealer", "several", "tongued", "staying", "settles", "settled", "dusting", "setting", "tongues", "catting", "backing", "catches", "earlier", "warmest", "earthed", "service", "serving", "warring", "wanters", "catcher", "serious", "eastest", "sensing", "senders", "easiest", "sending", "sellers", "selling", "seeming", "seeings", "tiniest", "seconds", "station", "causing", "seating", "edgings", "stating", "timings", "efforts", "starter", "causers", "screens", "blacker", "ceiling", "screams", "centers", "wanting", "walling", "walkers", "certain", "emptied", "empties", "emptier", "thrower", "endings", "started", "schools", "scarers", "scaring", "sayings", "engines", "savings", "sanding", "enjoyed", "starers", "saddest", "enjoyer", "staring", "enoughs", "rushing", "bagging", "runners", "entered", "running", "chances", "entires", "chancer", "rubbing", "rowings", "rounder", "chanced", "rounded", "starred", "rooming", "changed", "changes", "blocked", "angrier", "exactly", "changer", "blocker", "excepts", "checked", "excited", "walking", "excites", "roofing", "through", "expects", "blooded", "checker", "cheeked", "throats", "explain", "wakings", "springs", "thought", "waiting", "blowing", "rolling", "rocking", "risings", "ringing", "baggers", "animals", "righter", "righted", "ridings", "richest", "facings", "reveals", "blowers", "choicer", "choices", "returns", "voicing", "worries", "resting", "chooses", "failing", "spreads", "replier", "failers", "falling", "spotted", "replies", "replied", "chooser", "thinned", "fallers", "thinner", "balling", "boarded", "repeats", "visitor", "farther", "further", "circles", "another", "removed", "fastest", "removes", "fathers", "thicker", "circled", "visited", "reminds", "fearing", "spirits", "classes", "answers", "banking", "boating", "cleaned", "feeding", "spinner", "thanked", "village", "worried", "feeling", "cleaner", "remains", "cleared", "refuses", "refused", "workers", "reddest", "telling", "yellows", "spender", "working", "clearer", "clearly", "climbed", "tearing", "fighter", "teaming", "figured", "figures", "booking", "viewing", "climber", "usually", "closest", "receive", "filling", "teacher", "reasons", "closing", "finally", "closers", "anybody", "finding", "anymore", "realize", "special", "finders", "booting", "realest", "clothed", "readier", "readies", "readied", "fingers", "teaches", "tallest", "clothes", "speaker", "readers", "talkers", "clouded", "talking", "reading", "firings", "spacing", "takings", "reacher", "reached", "coating", "reaches", "raising", "raining", "fishing", "quietly", "fittest", "fitting", "systems", "whether", "bothers", "wrapped", "fitters", "quieted", "quieter", "quickly", "coffees", "quicker", "fixings", "coldest", "sounded", "sounder", "actings", "anyways", "college", "flashed", "flashes", "bottles", "flatter", "flatted", "colored", "bottled", "wording", "turning", "sorting", "flights", "colorer", "putting", "pushers", "pushing", "flowers", "pullers", "swinger", "wonders", "sorrier", "pulling", "proving", "comings", "bottoms", "promise", "truster", "boxings", "company", "follows", "younger", "trusted", "sweeter", "yelling", "problem", "without", "beached", "footing", "confuse", "beaches", "brained", "bearing", "pretend", "trucked", "forcing", "presser", "wishing", "trouble", "forests", "appears", "beating", "airings", "forever", "surface", "control", "forgets", "accepts", "pressed", "wronged", "winters", "forming", "presses", "prepare", "beaters", "breaker", "wheeled", "because", "forward", "coolers", "cooling", "allowed", "powered", "pourers", "freeing", "pouring", "tripped", "coolest", "breasts", "someone", "fresher", "suppose", "somehow", "friends", "breaths", "copping", "fronted", "becomes", "porches", "poppers", "popping", "poorest", "treeing", "fucking", "fullest", "pooling", "breathe", "polices", "funnier", "funnies", "policed", "bedding", "corners", "futures", "pointer", "pointed", "gamings", "counted", "soldier", "pockets", "wetting", "pleased", "gardens", "wetters", "wettest", "pleases", "counter", "sunning", "players", "westest", "country", "gathers", "bridges", "playing", "plating", "bridged", "plastic", "couples", "softest", "getting", "planned", "getters", "placing", "gifting", "pinking", "pilings", "piecing", "picture", "coursed", "courses", "summers", "picking", "snowing", "phoning", "bedroom", "glances", "glanced", "winging", "snapped", "glassed", "glasses", "perhaps", "covered", "crazies", "crazier", "perfect", "peopled", "persons", "peoples", "suiting", "pausing", "passing", "goldest", "partied", "windows", "parties", "parting", "creates", "grabbed", "smokers", "created", "grabber", "brought", "weights", "bringer", "arrives", "crosser", "crosses", "grasses", "parents", "palming", "graying", "pairing", "crossed", "painted", "arrived", "greying", "smoking", "paining", "outside", "brother", "greater", "smilers", "outings", "greened", "greener", "crowded", "travels", "smiling", "ordered", "grounds", "offings", "smelled", "openers", "browner", "grouped", "opening", "smaller", "growing", "okaying", "officer", "guarded", "slowest", "slowing", "cupping", "slipped", "guessed", "guesses", "cutting", "offices", "gunning", "offered", "browned", "allower", "nursing", "numbing", "suggest", "cutters", "numbers", "sliders", "halving", "sliding", "noticer", "wedding", "notices", "noticed", "nothing", "writers", "hallway", "handing", "sleeper", "normals", "noising", "hanging", "nodding", "dancing", "wearing", "writing", "slammed", "hangers", "darkest", "skinned", "happens", "trained", "needing", "builder", "beliefs", "happier", "necking", "nearest", "hardest", "nearing", "burning", "believe", "winding", "hatting", "narrows", "stupids", "sitting", "mouthed", "deadest", "watered", "sisters", "mothers", "singled", "winning", "morning", "mooning", "moments", "heading", "missing", "decides", "decided", "decider", "mirrors", "minutes", "hearing", "minings", "already", "minding", "middled", "heating", "burners", "singles", "middles", "deepest", "stuffed", "heaters", "singing", "simpler", "heavier", "heavies", "belongs", "message", "despite", "mention", "simples", "studies", "studied", "silvers", "helping", "helpers", "members", "meeting", "willing", "meanest", "attacks", "herself", "meaning", "dinners", "student", "hidings", "matters", "marries", "married", "busying", "busiest", "silence", "against", "highest", "wildest", "hilling", "marking", "mapping", "manages", "managed", "himself", "history", "tracked", "strikes", "manning", "hitting", "makings", "hitters", "whiting", "towards", "watched", "holding", "toucher", "machine", "holders", "lunches", "lunched", "watches", "luckier", "stretch", "streets", "lowered", "loudest", "lookers", "looking", "longing", "calling", "longest", "locking", "bending", "washing", "signing", "hottest", "littler", "benders", "strange", "sighted", "listens", "linings", "likings", "housing", "beneath", "sighing", "sicking", "however", "lighted", "sickest", "lighter", "calming", "lifters", "hundred", "calmest", "hurried", "hurries", "lifting", "touched", "doesn't", "doesn’t", "hurting", "touches", "showers", "husband", "doctors", "letters", "cameras", "letting", "tossing", "leaving", "learned", "dogging", "leaning", "leafing", "leaders", "leading", "whitest", "layered", "ignored", "showing", "ignores", "stories", "ignorer", "shoving", "laughed", "lasting", "largest", "imaging", "doorway", "besting", "imagine", "shouted", "stormed", "downing", "storing", "topping", "avoided", "dragged", "shorter", "betters", "stopper", "landers", "insides", "instead", "written", "drawing", "shopped", "stopped", "between", "landing", "shooter", "knowing", "jackets", "dreamed", "carding", "toothed", "knocked", "knifing", "kitchen", "joining", "teethed", "stomach", "joiners", "kissing", "kindest", "killers", "killing", "shoeing", "kidding", "jumping", "kickers", "kicking", "jumpers", "keepers", "dressed", "keeping", "enough", "checks", "kicked", "jumper", "kicker", "kidded", "jumped", "killed", "joking", "killer", "kinder", "joiner", "kisses", "kissed", "joined", "knives", "knifes", "knifed", "jacket", "knocks", "itself", "ladies", "landed", "lander", "inside", "larger", "images", "lasted", "imaged", "laughs", "ignore", "aboves", "laying", "accept", "layers", "across", "yellow", "leaded", "leader", "leaved", "leaned", "learns", "leaves", "yelled", "lesser", "letter", "living", "lifted", "lifter", "humans", "hugest", "lights", "wrongs", "houses", "liking", "likers", "lining", "housed", "acting", "listen", "hotels", "little", "hotter", "locals", "locked", "horses", "longer", "longed", "looked", "hoping", "looker", "losing", "adding", "louder", "loving", "lovers", "lowing", "lowest", "writer", "lowers", "homing", "holing", "holder", "making", "hitter", "makers", "manned", "manage", "writes", "admits", "mapped", "marked", "hilled", "higher", "afraid", "hiding", "hidden", "matter", "ageing", "helper", "member", "helped", "memory", "hellos", "heater", "metals", "middle", "heated", "mights", "minded", "hearts", "mining", "minute", "headed", "mirror", "misses", "missed", "moment", "moneys", "monies", "months", "mooned", "mostly", "having", "mother", "worlds", "hating", "mouths", "moving", "movers", "movies", "musics", "worker", "myself", "naming", "namers", "narrow", "hatted", "hardly", "nearer", "neared", "nearly", "harder", "necked", "needed", "happen", "hanger", "newest", "nicest", "nights", "worked", "nobody", "nodded", "handed", "noises", "noised", "worded", "normal", "norths", "nosing", "agrees", "noting", "notice", "halves", "halved", "number", "guying", "numbed", "nurses", "nursed", "agreed", "wooden", "offing", "gunned", "offers", "office", "guards", "wonder", "okayed", "okay'd", "okay’d", "ok'ing", "ok’ing", "oldest", "womens", "opened", "opener", "groups", "womans", "within", "ground", "orders", "others", "outing", "wished", "greens", "greats", "owning", "wishes", "owners", "paging", "pained", "paints", "greyed", "greyer", "paired", "palest", "grayed", "palmed", "papers", "grayer", "parent", "parted", "passed", "golder", "passes", "pauses", "paused", "paying", "person", "people", "wipers", "goings", "glance", "phones", "phoned", "photos", "picked", "giving", "givens", "pieces", "pieced", "piling", "gifted", "pinked", "pinker", "places", "placed", "getter", "gotten", "plated", "plates", "gently", "played", "gather", "player", "please", "gating", "garden", "pocket", "gamers", "points", "pointy", "gaming", "future", "wiping", "fuller", "police", "pooled", "poorer", "fucked", "popped", "popper", "fronts", "friend", "freers", "poured", "pourer", "freest", "powers", "formed", "forget", "forgot", "forest", "forces", "forced", "footed", "pretty", "follow", "fliers", "flyers", "proven", "airing", "proves", "proved", "prover", "pulled", "flying", "puller", "flower", "pushes", "pushed", "floors", "pusher", "flight", "fixers", "fixing", "quicks", "winter", "fitted", "quiets", "fitter", "winged", "radios", "rained", "raises", "raised", "fishes", "rather", "fished", "firsts", "firing", "reader", "finish", "finger", "fining", "finest", "realer", "finder", "really", "finals", "reason", "filled", "figure", "fought", "fights", "fields", "fewest", "redder", "refuse", "remain", "feeing", "remind", "feared", "father", "faster", "remove", "repeat", "family", "faller", "fallen", "failer", "failed", "rested", "fading", "return", "reveal", "riches", "richer", "riding", "ridden", "window", "riders", "rights", "facing", "allows", "ringed", "rising", "rivers", "extras", "rocked", "rolled", "expect", "roofed", "excite", "except", "rooves", "roomed", "events", "rounds", "rowing", "evened", "rubbed", "almost", "entire", "runner", "enters", "keying", "rushed", "rushes", "sadder", "safest", "sanded", "enjoys", "saving", "engine", "savers", "winded", "saying", "enders", "scared", "scares", "scarer", "scenes", "ending", "school", "scream", "either", "eights", "screen", "egging", "effort", "search", "edging", "seated", "second", "eaters", "seeing", "seemed", "eating", "seller", "sender", "senses", "sensed", "easier", "easily", "earths", "serves", "served", "willed", "dusted", "settle", "during", "driers", "sevens", "sexing", "shadow", "shakes", "shaken", "dryers", "shaker", "always", "shaped", "driest", "shapes", "shaper", "drying", "shares", "shared", "sharer", "sharps", "driver", "drives", "driven", "sheets", "droves", "drinks", "shirts", "drunks", "shoots", "dreams", "shorts", "dozens", "should", "downed", "shouts", "shoved", "shoves", "showed", "wilder", "shower", "dogged", "doctor", "shrugs", "didn’t", "sicker", "sicked", "didn't", "siding", "sighed", "doings", "sights", "signed", "dinner", "silent", "silver", "dyings", "widest", "simple", "simply", "deeper", "single", "decide", "deaths", "sister", "deader", "sizing", "darker", "wholes", "sleeps", "dances", "danced", "slides", "slider", "cutter", "slower", "slowed", "slowly", "smalls", "cupped", "smells", "smelly", "crying", "smiles", "smiled", "smiler", "crowds", "smokes", "smoked", "smoker", "create", "covers", "snowed", "whited", "softer", "course", "softly", "couple", "counts", "corner", "whiter", "copped", "cooled", "cooler", "coming", "whites", "sorted", "colors", "colder", "sounds", "coffee", "coated", "spaces", "clouds", "spaced", "spoken", "speaks", "clothe", "closed", "closes", "closer", "spends", "climbs", "clears", "cleans", "spirit", "cities", "circle", "church", "choose", "spread", "chosen", "choice", "chests", "sprung", "spring", "sprang", "stages", "stairs", "cheeks", "stands", "keeper", "change", "chance", "stared", "stares", "starer", "chairs", "starts", "center", "causer", "caused", "states", "stated", "causes", "caught", "catted", "stayed", "steals", "stolen", "casing", "sticks", "caring", "carded", "stones", "animal", "cannot", "stored", "stores", "storms", "answer", "camera", "calmer", "calmed", "called", "street", "buyers", "bought", "strike", "struck", "buying", "anyone", "strong", "busier", "busied", "busing", "burner", "stuffs", "burned", "stupid", "builds", "browns", "suites", "suited", "brings", "summer", "bright", "sunned", "bridge", "breath", "breast", "breaks", "broken", "surest", "branch", "brains", "anyway", "boxing", "wheels", "sweets", "swings", "bottom", "bottle", "system", "bother", "tables", "taking", "takers", "talked", "talker", "boring", "taller", "booted", "taught", "booked", "teamed", "teared", "boning", "appear", "bodies", "thanks", "boated", "thicks", "boards", "bluest", "things", "thinks", "blower", "thirds", "thirty", "though", "threes", "throat", "bloods", "thrown", "throws", "blocks", "timing", "blacks", "timers", "tinier", "biters", "tiring", "todays", "biting", "toning", "tongue", "arming", "birded", "bigger", "wetter", "toothy", "beyond", "better", "topped", "tossed", "bested", "tosses", "beside", "bender", "toward", "bended", "tracks", "belong", "trains", "belief", "travel", "behind", "begins", "before", "bedded", "became", "become", "beater", "beaten", "trucks", "truest", "aren’t", "aren't", "trusts", "truths", "trying", "turned", "twenty", "around", "uncles", "weight", "wasn’t", "wasn't", "arrive", "unless", "upping", "wedded", "viewed", "barely", "visits", "banked", "balled", "voices", "voiced", "waited", "bagger", "waking", "walked", "bagged", "walker", "walled", "asking", "wanted", "wanter", "warred", "waring", "backed", "warmed", "warmer", "babies", "washed", "washes", "avoids", "attack", "waters", "asleep", "watery", "waving", "wavers", "seems", "party", "minds", "eaten", "sells", "sends", "known", "sense", "hours", "pasts", "paths", "easts", "pause", "mined", "layer", "payed", "serve", "earth", "early", "wills", "aired", "heard", "hears", "dusts", "kills", "goers", "hotel", "seven", "dried", "ideas", "sexed", "sexes", "going", "drier", "dries", "dryer", "glass", "heads", "shake", "leads", "shook", "aging", "gives", "phone", "local", "photo", "shape", "picks", "above", "locks", "money", "drops", "share", "given", "wrong", "girls", "month", "sharp", "piece", "wilds", "sheet", "drove", "drive", "moons", "lands", "piles", "ships", "drink", "piled", "drank", "drunk", "shirt", "pinks", "shits", "dress", "shoes", "mores", "shoot", "longs", "shots", "dream", "drawn", "draws", "drags", "shops", "haves", "horse", "short", "gifts", "dozen", "place", "downs", "shout", "hopes", "shove", "hoped", "plans", "wiper", "doors", "shown", "shows", "wiped", "plate", "world", "mouth", "doers", "joins", "shrug", "shuts", "leafs", "moved", "plays", "moves", "sicks", "don’t", "pleas", "sided", "sides", "sighs", "don't", "gated", "sight", "looks", "gates", "wives", "mover", "signs", "doing", "dirts", "knees", "movie", "learn", "gamer", "games", "gamed", "dying", "music", "since", "desks", "sings", "singe", "deeps", "point", "acted", "musts", "yells", "funny", "death", "wider", "loses", "sixes", "whose", "names", "sizes", "sized", "skins", "keyed", "skies", "pools", "slams", "darks", "named", "slept", "namer", "sleep", "leave", "dance", "slide", "hated", "young", "whole", "fucks", "who’s", "slips", "who's", "slows", "front", "porch", "loved", "hates", "small", "fresh", "cries", "cried", "smell", "white", "nears", "loves", "smile", "freer", "pours", "lover", "freed", "power", "smoke", "frees", "yeses", "crowd", "cross", "jokes", "fours", "snaps", "crazy", "forms", "cover", "homed", "snows", "among", "necks", "happy", "least", "press", "force", "homes", "count", "needs", "wipes", "years", "cools", "foots", "joked", "foods", "never", "songs", "comes", "sorry", "flier", "color", "sorts", "souls", "lower", "newer", "flyer", "colds", "sound", "flown", "south", "works", "coats", "space", "nicer", "prove", "lucky", "spoke", "night", "speak", "cloud", "hurts", "yards", "pulls", "holed", "flies", "close", "climb", "spent", "spend", "words", "holes", "hangs", "clear", "lunch", "spins", "clean", "class", "liars", "floor", "holds", "spots", "alive", "noise", "flats", "chose", "flash", "nones", "child", "fixer", "fixed", "fixes", "chest", "cheek", "mains", "stage", "hands", "makes", "stair", "quick", "stood", "check", "fiver", "stand", "stars", "fives", "north", "wrote", "stare", "lying", "quiet", "noses", "quite", "start", "chair", "nosed", "radio", "lived", "rains", "notes", "state", "large", "cause", "raise", "catch", "noted", "maker", "stays", "halls", "angry", "stole", "steal", "reach", "first", "cased", "cases", "steps", "lives", "fires", "stuck", "carry", "stick", "cares", "still", "cared", "fired", "cards", "added", "stone", "reads", "halve", "stops", "write", "can’t", "ready", "hairy", "store", "hairs", "can't", "storm", "numbs", "story", "could", "finer", "knife", "fines", "calms", "fined", "calls", "hurry", "while", "buyer", "finds", "nurse", "found", "which", "lifts", "admit", "final", "fills", "lasts", "keeps", "where", "buses", "bused", "study", "offed", "stuff", "fight", "woods", "burnt", "burns", "field", "human", "build", "built", "wings", "offer", "brown", "allow", "guyed", "suite", "suits", "bring", "marks", "fewer", "feels", "hills", "wines", "later", "feeds", "agree", "guess", "surer", "fears", "broke", "break", "guard", "brain", "highs", "often", "marry", "ahead", "knock", "boxes", "sweet", "boxed", "okays", "swing", "swung", "falls", "reply", "hides", "fails", "huger", "table", "takes", "taken", "laugh", "taker", "rests", "house", "talks", "bored", "women", "faded", "fades", "wheel", "facts", "wraps", "boots", "teach", "faces", "teams", "older", "books", "tears", "bones", "maybe", "woman", "faced", "areas", "boned", "opens", "tells", "rides", "grows", "thank", "their", "boats", "thens", "there", "these", "thick", "rider", "after", "board", "right", "bluer", "thins", "blues", "blued", "grown", "thing", "again", "rings", "think", "blows", "blown", "third", "would", "means", "those", "risen", "three", "rises", "blood", "eying", "heres", "throw", "block", "threw", "roses", "group", "river", "black", "tying", "times", "timed", "roads", "rocks", "order", "timer", "meant", "green", "tired", "tires", "extra", "meets", "today", "rolls", "biter", "bitey", "other", "toned", "tones", "light", "bites", "worry", "birds", "roofs", "armed", "outer", "rooms", "outed", "every", "tooth", "teeth", "round", "image", "bests", "event", "liked", "evens", "rowed", "likes", "touch", "bends", "windy", "bents", "towns", "winds", "great", "below", "track", "overs", "owned", "liker", "train", "enter", "wound", "begun", "helps", "began", "begin", "owner", "beers", "kinds", "wests", "paged", "trees", "treed", "tripe", "trips", "pages", "alone", "hello", "beats", "enjoy", "bears", "truck", "beach", "safer", "trues", "truer", "trued", "safes", "hells", "sames", "trust", "truth", "pains", "wells", "sands", "tried", "tries", "greys", "turns", "isn’t", "isn't", "heavy", "twice", "saves", "uncle", "saved", "under", "kicks", "saver", "paint", "lines", "grays", "until", "weeks", "upped", "pairs", "using", "asked", "usual", "scare", "being", "ender", "metal", "views", "paled", "banks", "visit", "pales", "paler", "voice", "scene", "heats", "waits", "balls", "ended", "empty", "woken", "palms", "wakes", "waked", "walks", "lined", "knows", "pants", "worse", "paper", "walls", "worst", "wants", "eight", "heart", "along", "backs", "egged", "jumps", "warms", "grass", "might", "edges", "grabs", "seats", "avoid", "parts", "edged", "aunts", "watch", "about", "eater", "won’t", "water", "won't", "waved", "waves", "goods", "waver", "golds", "wears", "ears", "grab", "fits", "each", "sets", "knee", "lots", "part", "dust", "noes", "fish", "stay", "good", "rain", "cats", "work", "wild", "laid", "hang", "gold", "pass", "step", "loud", "case", "help", "your", "past", "nods", "home", "care", "path", "hell", "read", "love", "fire", "gods", "lift", "card", "stop", "pays", "keys", "cars", "paid", "idea", "fine", "none", "real", "into", "drop", "heat", "wish", "cans", "kids", "find", "goer", "goes", "went", "calm", "just", "lead", "gone", "call", "fill", "nose", "ship", "huge", "acts", "lows", "buys", "some", "note", "kind", "shit", "shat", "mind", "ices", "busy", "pick", "hand", "shod", "shoe", "gave", "reds", "shot", "hall", "fews", "ours", "feel", "burn", "drew", "such", "draw", "shop", "give", "felt", "wing", "suit", "drag", "hear", "feed", "mine", "girl", "feds", "iced", "down", "when", "fees", "half", "suns", "able", "word", "fear", "nows", "door", "fast", "sure", "leaf", "pile", "jobs", "show", "wine", "boys", "dogs", "yell", "hair", "guys", "kept", "doer", "fall", "fell", "head", "shut", "gift", "hole", "rest", "numb", "kick", "lean", "take", "both", "sick", "fail", "fade", "took", "miss", "side", "sigh", "held", "talk", "last", "plan", "bore", "hold", "done", "tall", "teas", "fact", "boot", "like", "wife", "rich", "sign", "book", "wood", "team", "does", "main", "offs", "tear", "tore", "torn", "rode", "dirt", "gets", "bone", "joke", "ride", "make", "told", "play", "died", "tell", "dies", "tens", "area", "body", "than", "boat", "line", "guns", "desk", "that", "what", "kiss", "them", "they", "gate", "sang", "then", "plea", "kill", "face", "sing", "sung", "eyes", "thin", "blue", "deep", "made", "rung", "ring", "sirs", "wide", "he’s", "rang", "moon", "blow", "eyed", "sits", "more", "whys", "dead", "blew", "days", "this", "left", "grew", "he's", "size", "rise", "rose", "whom", "have", "skin", "most", "late", "grow", "slam", "road", "game", "tied", "ties", "arms", "time", "dark", "rock", "okay", "ages", "mens", "roll", "mans", "tiny", "slid", "dads", "airs", "ok'd", "tire", "wets", "ok’d", "i’ll", "roof", "slip", "full", "cuts", "pool", "slow", "tone", "bite", "lips", "cups", "bits", "room", "olds", "poor", "bird", "adds", "ever", "knew", "hate", "fuck", "pops", "even", "tops", "wipe", "hits", "once", "west", "hour", "rows", "rubs", "toss", "best", "ones", "only", "from", "runs", "bend", "bent", "onto", "open", "move", "town", "free", "pour", "legs", "rush", "jump", "snap", "many", "hill", "less", "maps", "snow", "keep", "safe", "much", "soft", "join", "beer", "i'll", "beds", "four", "tree", "same", "sand", "form", "cops", "must", "year", "cool", "trip", "lets", "beat", "mark", "born", "bear", "with", "come", "save", "know", "true", "sons", "lock", "song", "soon", "laws", "came", "outs", "name", "well", "been", "says", "said", "sort", "feet", "soul", "high", "yeah", "were", "hide", "foot", "turn", "cold", "wind", "yard", "twos", "coat", "food", "over", "hats", "owns", "ends", "lady", "aged", "arts", "else", "long", "flew", "hurt", "page", "week", "upon", "lays", "used", "uses", "hard", "eggs", "wins", "very", "mays", "seas", "pain", "near", "view", "bars", "weds", "pull", "edge", "wrap", "lies", "bank", "spin", "ball", "grey", "seat", "spun", "lied", "neck", "push", "wait", "hope", "bags", "city", "look", "wake", "spot", "saws", "woke", "wear", "pink", "liar", "eats", "walk", "need", "sees", "seen", "puts", "seem", "wall", "want", "pair", "gray", "sell", "will", "flat", "back", "pale", "sold", "asks", "wars", "land", "send", "mean", "warm", "baby", "sent", "also", "wash", "away", "here", "easy", "hung", "sens", "star", "hers", "aunt", "palm", "worn", "life", "meet", "wore", "east", "live", "news", "five", "wave", "next", "lost", "lose", "nice", "ways", "far", "few", "war", "bad", "bag", "bar", "wed", "use", "ups", "art", "was", "two", "try", "are", "bed", "top", "arm", "wet", "big", "too", "bit", "tie", "the", "ten", "tvs", "tea", "box", "boy", "sun", "bus", "but", "buy", "any", "can", "car", "cat", "and", "son", "cop", "sos", "cry", "cup", "cut", "who", "dad", "sky", "day", "six", "why", "sit", "sat", "sir", "die", "did", "dog", "she", "dry", "sex", "set", "ear", "ate", "eat", "see", "saw", "win", "won", "sea", "egg", "end", "say", "sad", "ran", "run", "rub", "row", "eye", "rid", "ask", "fed", "fee", "red", "way", "fit", "fix", "all", "put", "fly", "for", "pop", "fun", "get", "got", "god", "pay", "own", "out", "our", "air", "ors", "one", "old", "ohs", "gun", "key", "off", "guy", "now", "not", "nor", "nod", "nos", "ago", "new", "hat", "age", "had", "has", "her", "met", "hey", "may", "hid", "map", "him", "add", "his", "man", "men", "hit", "mad", "low", "lot", "hot", "lip", "how", "lit", "lie", "kid", "i'm", "let", "i’m", "leg", "i'd", "i’d", "ice", "led", "act", "lay", "law", "ins", "yes", "yet", "you", "its", "job", "no", "at", "by", "my", "on", "ha", "do", "ok", "he", "oh", "is", "tv", "me", "us", "as", "hi", "go", "if", "of", "am", "up", "to", "we", "so", "in", "or", "it", "be", "an", "i", "a"]
    random_responses = [
        "Can you try something else?", #5
        "Head in another direction with this.", #6
        "Ah, I don’t know the right reply...", #7
        "There’s something that I don’t know how to reply to.", #10
        "At first glance, that doesn’t look like what I want.", #12
        "Please try something else - that’s something that’s out of my understanding for now.", #14
        "Perhaps try a different idea - my replies are very few at this time, sorry." #15
    ]
    input = request.POST['q'].strip()
    target = 'mtproto'
    error_response = "Sorry, I’m still learning and only know the ten hundred most used words!"
    success_response = "Way to follow chat protocols! What’s the app for that, again?"
    alpha_only = re.compile("([^a-z'’])")
    internal_strip = re.compile(" +")
    clean_string = alpha_only.sub(" ", input.lower().strip())
    clean_string = internal_strip.sub(" ", clean_string)

    if clean_string == "telegram":
        return JsonResponse({'a':"Ooh, that’s what you need! I can’t help you any more, but have you checked out our email support and web page?"})

    if not all([c in WORDS for c in clean_string.split(" ")]):
        return JsonResponse({'a':error_response})

    test_string = [w[0] for w in clean_string.strip().split(" ")]
    target = [c for c in target.lower().strip()]
    incorrect = "❌"
    place = "🌚"
    letter = "🌝"
    shorter = len(target) if len(target) < len(test_string) else len(test_string)
    longer = len(target) if len(target) > len(test_string) else len(test_string)
    output = [incorrect]*longer

    for i in range(shorter): # we only need to check the length of the string for exact messages
        # check for place matches
        if test_string[i] == target[i]:
            target[i] = place
            test_string[i] = place
            output[i] = place

    for i in range(len(test_string)):
        # check for other matches
        if test_string[i] in "abcdefghijklmnopqrstuvwxyz":
            if test_string[i] in target:
                target[target.index(test_string[i])] = letter
                test_string[i] = letter
                output[i] = letter

    for i in range(len(test_string)):
        if test_string[i] in "abcdefghijklmnopqrstuvwxyz":
            if test_string[i] not in target:
                output[i] = incorrect

    # if len(target) > len([ o for o in output if o.strip() ]):
    #     output.append(padding*(len(target) - len([ o for o in output if o.strip() ])))

    output = "".join(output)

    response_text = " ".join([output, random.choice(random_responses)])
    if output == place * len(target):
        response_text = success_response

    return JsonResponse({'a': response_text})
