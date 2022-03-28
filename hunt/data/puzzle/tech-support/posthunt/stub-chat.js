window.stubChat = ({q}) => {
  const WORDS = new Set([
    "understandings", "understanding", "conversations", "disappearing", "informations", "grandmothers", "grandfathers", "questionings", "conversation", "information", "approaching", "understands", "immediately", "positioning", "questioning", "grandmother", "travellings", "questioners", "recognizing", "recognizers", "televisions", "remembering", "rememberers", "expressions", "discovering", "disappeared", "interesting", "grandfather", "straightest", "controllers", "controlling", "considering", "remembered", "cigarettes", "companying", "completely", "spreadings", "considered", "continuing", "controlled", "stationing", "controller", "straighter", "stretching", "businesses", "somebodies", "soldiering", "countering", "darknesses", "situations", "directions", "disappears", "younglings", "suggesting", "afternoons", "breathings", "distancing", "screenings", "schoolings", "especially", "everything", "everywhere", "explaining", "explainers", "expression", "branchings", "revealings", "repeatings", "surprising", "rememberer", "somewheres", "television", "themselves", "recognizer", "recognizes", "recognized", "belongings", "finishings", "travelling", "questioner", "beginnings", "travelings", "questioned", "followings", "pretending", "forgetting", "forgetters", "forwarding", "positioned", "travellers", "gatherings", "perfecting", "understand", "understood", "weightings", "approaches", "officering", "numberings", "happenings", "mentioning", "letterings", "husbanding", "imaginings", "approached", "apartments", "whispering", "interested", "discovered", "spinnings", "clearings", "climbings", "spendings", "clothings", "colorings", "soundings", "truckings", "somewhere", "troubling", "companies", "companied", "beautiful", "computers", "confusing", "considers", "travelers", "youngling", "continues", "continued", "traveller", "traveling", "yellowing", "apartment", "beginning", "wheelings", "travelled", "sometimes", "something", "appearing", "cornering", "believing", "countered", "believers", "countries", "soldiered", "coverings", "creatures", "crossings", "accepting", "daughters", "belonging", "situation", "silvering", "different", "silencing", "touchings", "bettering", "tomorrows", "disappear", "thinkings", "boardings", "discovers", "admitting", "wrappings", "distances", "distanced", "sightings", "shrugging", "doctoring", "showering", "shoulders", "shoppings", "shootings", "dressings", "sheetings", "shadowing", "settlings", "servicing", "seriously", "seconding", "searching", "weighting", "screening", "screaming", "schooling", "teachings", "bothering", "everybody", "botherers", "bottoming", "excepting", "expecting", "explained", "direction", "explainer", "surprised", "surprises", "waterings", "branching", "revealing", "returning", "surfacing", "familiars", "repeating", "fathering", "reminding", "supposing", "breasting", "attacking", "remembers", "breathing", "remaining", "breathers", "brightest", "brownings", "suggested", "recognize", "fightings", "attention", "figurings", "receiving", "reasoning", "realizing", "fingering", "buildings", "finishing", "stupidest", "stuffings", "questions", "watchings", "flashings", "strongest", "strikings", "flighting", "flowering", "promisers", "promising", "following", "bathrooms", "prettiest", "pretended", "stretched", "foreheads", "foresting", "stretches", "forgotten", "pressings", "forgetter", "strangest", "preparing", "forwarded", "strangers", "possibles", "positions", "afternoon", "straights", "pocketing", "gardening", "pleasings", "wondering", "gathering", "picturing", "personals", "perfected", "stomaches", "stomached", "carefully", "stationed", "catchings", "parenting", "paintings", "orderings", "groupings", "wintering", "officered", "offerings", "centering", "numbering", "neighbors", "certainly", "happening", "narrowing", "narrowest", "mountains", "mothering", "mirroring", "middlings", "messaging", "standings", "mentioned", "mattering", "marriages", "histories", "machining", "hospitals", "listening", "lightings", "springing", "lettering", "husbanded", "spreaders", "whispered", "imagining", "imaginers", "spreading", "important", "languages", "answering", "cigarette", "interests", "spiriting", "cleanings", "knockings", "soundest", "coatings", "sounders", "sounding", "colleges", "coloring", "colorful", "wouldn't", "training", "colorers", "sorriest", "worrying", "belonged", "approach", "tracking", "touchers", "touching", "computer", "whatever", "toppings", "confused", "confuses", "workings", "consider", "bettered", "teething", "tonights", "tonguers", "tonguing", "continue", "arriving", "tomorrow", "controls", "together", "blacking", "blackest", "throwers", "blocking", "throwing", "coolings", "someones", "blockers", "somebody", "thirties", "soldiers", "cornered", "weighted", "counting", "thoughts", "counters", "thinking", "thinners", "thinning", "coursing", "covering", "thinnest", "craziest", "snapping", "creating", "creature", "thickest", "boarding", "crossing", "smokings", "crowding", "smelling", "smallest", "cuttings", "slipping", "slightly", "dancings", "sleepers", "sleeping", "slamming", "wordings", "darkness", "daughter", "boatings", "skinning", "weddings", "thanking", "sittings", "deciding", "deciders", "singling", "singings", "despites", "simplest", "terrible", "silvered", "tellings", "wearings", "youngest", "watering", "silences", "teachers", "bookings", "agreeing", "teaching", "discover", "attacked", "bothered", "botherer", "watching", "swingers", "bottling", "distance", "silenced", "signings", "bottomed", "sighting", "shutting", "shrugged", "wondered", "swinging", "doctored", "sweetest", "showered", "showings", "doorways", "shouting", "shoulder", "wronging", "shortest", "surprise", "dragging", "shopping", "shooters", "drawings", "actually", "shooting", "dreaming", "dressing", "avoiding", "shitting", "shirting", "shipping", "drinking", "drinkers", "braining", "sheeting", "sharpest", "drivings", "sharpers", "dropping", "droppers", "shadowed", "surfaced", "settling", "washings", "settings", "services", "serviced", "earliest", "backings", "earthing", "servings", "branches", "branched", "seconded", "seatings", "surfaces", "searched", "searches", "walkings", "screened", "waitings", "screamed", "supposed", "emptiest", "emptying", "breaking", "breakers", "schooled", "enjoying", "enjoyers", "entering", "runnings", "breasted", "rounders", "rounding", "supposes", "everyone", "visitors", "visiting", "breathed", "excepted", "roofings", "exciting", "breathes", "expected", "rollings", "bankings", "breather", "explains", "villages", "bridging", "viewings", "brighter", "ringings", "righting", "suitings", "bringing", "revealed", "bringers", "returned", "failings", "repliers", "replying", "repeated", "brothers", "familiar", "wintered", "families", "suggests", "farthest", "furthest", "browning", "fathered", "removing", "building", "reminded", "bathroom", "allowing", "suddenly", "remember", "allowers", "feedings", "builders", "burnings", "feelings", "remained", "refusing", "stupider", "windings", "although", "stuffing", "studying", "business", "angriest", "fighting", "fighters", "students", "figuring", "received", "twenties", "receives", "fillings", "reasoned", "findings", "stronger", "turnings", "realizes", "realized", "readiest", "fingered", "readying", "striking", "trusters", "finishes", "trusting", "finished", "readings", "reachers", "reaching", "quieters", "quietest", "quieting", "fittings", "quickest", "writings", "beaching", "question", "trucking", "callings", "stranger", "flashing", "beatings", "answered", "flattest", "flatting", "flighted", "straight", "troubled", "flowered", "pullings", "storming", "promiser", "couldn't", "promised", "promises", "couldn’t", "followed", "stoppers", "problems", "probably", "prettier", "stopping", "pretends", "stomachs", "troubles", "pressers", "tripping", "forehead", "stickers", "forested", "pressing", "whispers", "carrying", "sticking", "carriers", "stepping", "stealers", "forwards", "stealing", "becoming", "prepares", "prepared", "powering", "freeings", "stations", "possible", "position", "freshest", "beddings", "wrapping", "fronting", "catching", "fuckings", "policing", "funniest", "pointers", "pointing", "catchers", "pocketed", "gardened", "starters", "ceilings", "pleasing", "gathered", "starting", "centered", "platings", "plastics", "planning", "pictured", "pictures", "traveler", "pickings", "personal", "glancing", "yourself", "chancing", "perfects", "changing", "peopling", "partying", "partings", "parented", "grabbing", "grabbers", "changers", "checking", "starring", "bedrooms", "checkers", "pairings", "standing", "painting", "outsides", "greatest", "cheeking", "greening", "greenest", "grouping", "ordering", "anything", "openings", "guarding", "wheeling", "officers", "guessing", "spreader", "offering", "children", "anywhere", "numbered", "choicest", "noticers", "noticing", "hallways", "nothings", "hangings", "nobodies", "admitted", "neighbor", "choosing", "choosers", "happened", "neckings", "happiest", "narrowed", "narrower", "spotting", "churches", "mouthing", "traveled", "mountain", "mothered", "accepted", "mornings", "mirrored", "headings", "spirited", "hearings", "heatings", "circling", "middling", "messaged", "messages", "heaviest", "wouldn’t", "spinners", "mentions", "helpings", "cleanest", "memories", "meetings", "meanings", "appeared", "mattered", "marrieds", "marrying", "marriage", "yellowed", "markings", "cleaning", "managing", "cleaners", "holdings", "machined", "machines", "lunching", "luckiest", "lowering", "longings", "clearest", "hospital", "lockings", "littlest", "clearing", "listened", "housings", "lightest", "lighting", "lighters", "spinning", "hundreds", "hurrying", "believes", "spenders", "believed", "climbing", "husbands", "lettered", "lettings", "learning", "leadings", "ignoring", "laughing", "ignorers", "imagines", "yellower", "imagined", "climbers", "imaginer", "spending", "closings", "specials", "speakers", "language", "believer", "clothing", "clouding", "speaking", "interest", "spacings", "landings", "knowings", "southest", "jacketed", "knocking", "kitchens", "kissings", "killings", "keepings", "dresses", "biggest", "sticker", "careful", "shirted", "warmers", "shipped", "birding", "drinker", "carries", "sheeted", "warming", "carried", "carrier", "driving", "sharper", "tonight", "drivers", "casings", "sharers", "sharing", "stepped", "dropped", "dropper", "whisper", "shapers", "shaping", "shakers", "shaking", "tonguer", "shadows", "stealer", "several", "tongued", "staying", "settles", "settled", "dusting", "setting", "tongues", "catting", "backing", "catches", "earlier", "warmest", "earthed", "service", "serving", "warring", "wanters", "catcher", "serious", "eastest", "sensing", "senders", "easiest", "sending", "sellers", "selling", "seeming", "seeings", "tiniest", "seconds", "station", "causing", "seating", "edgings", "stating", "timings", "efforts", "starter", "causers", "screens", "blacker", "ceiling", "screams", "centers", "wanting", "walling", "walkers", "certain", "emptied", "empties", "emptier", "thrower", "endings", "started", "schools", "scarers", "scaring", "sayings", "engines", "savings", "sanding", "enjoyed", "starers", "saddest", "enjoyer", "staring", "enoughs", "rushing", "bagging", "runners", "entered", "running", "chances", "entires", "chancer", "rubbing", "rowings", "rounder", "chanced", "rounded", "starred", "rooming", "changed", "changes", "blocked", "angrier", "exactly", "changer", "blocker", "excepts", "checked", "excited", "walking", "excites", "roofing", "through", "expects", "blooded", "checker", "cheeked", "throats", "explain", "wakings", "springs", "thought", "waiting", "blowing", "rolling", "rocking", "risings", "ringing", "baggers", "animals", "righter", "righted", "ridings", "richest", "facings", "reveals", "blowers", "choicer", "choices", "returns", "voicing", "worries", "resting", "chooses", "failing", "spreads", "replier", "failers", "falling", "spotted", "replies", "replied", "chooser", "thinned", "fallers", "thinner", "balling", "boarded", "repeats", "visitor", "farther", "further", "circles", "another", "removed", "fastest", "removes", "fathers", "thicker", "circled", "visited", "reminds", "fearing", "spirits", "classes", "answers", "banking", "boating", "cleaned", "feeding", "spinner", "thanked", "village", "worried", "feeling", "cleaner", "remains", "cleared", "refuses", "refused", "workers", "reddest", "telling", "yellows", "spender", "working", "clearer", "clearly", "climbed", "tearing", "fighter", "teaming", "figured", "figures", "booking", "viewing", "climber", "usually", "closest", "receive", "filling", "teacher", "reasons", "closing", "finally", "closers", "anybody", "finding", "anymore", "realize", "special", "finders", "booting", "realest", "clothed", "readier", "readies", "readied", "fingers", "teaches", "tallest", "clothes", "speaker", "readers", "talkers", "clouded", "talking", "reading", "firings", "spacing", "takings", "reacher", "reached", "coating", "reaches", "raising", "raining", "fishing", "quietly", "fittest", "fitting", "systems", "whether", "bothers", "wrapped", "fitters", "quieted", "quieter", "quickly", "coffees", "quicker", "fixings", "coldest", "sounded", "sounder", "actings", "anyways", "college", "flashed", "flashes", "bottles", "flatter", "flatted", "colored", "bottled", "wording", "turning", "sorting", "flights", "colorer", "putting", "pushers", "pushing", "flowers", "pullers", "swinger", "wonders", "sorrier", "pulling", "proving", "comings", "bottoms", "promise", "truster", "boxings", "company", "follows", "younger", "trusted", "sweeter", "yelling", "problem", "without", "beached", "footing", "confuse", "beaches", "brained", "bearing", "pretend", "trucked", "forcing", "presser", "wishing", "trouble", "forests", "appears", "beating", "airings", "forever", "surface", "control", "forgets", "accepts", "pressed", "wronged", "winters", "forming", "presses", "prepare", "beaters", "breaker", "wheeled", "because", "forward", "coolers", "cooling", "allowed", "powered", "pourers", "freeing", "pouring", "tripped", "coolest", "breasts", "someone", "fresher", "suppose", "somehow", "friends", "breaths", "copping", "fronted", "becomes", "porches", "poppers", "popping", "poorest", "treeing", "fucking", "fullest", "pooling", "breathe", "polices", "funnier", "funnies", "policed", "bedding", "corners", "futures", "pointer", "pointed", "gamings", "counted", "soldier", "pockets", "wetting", "pleased", "gardens", "wetters", "wettest", "pleases", "counter", "sunning", "players", "westest", "country", "gathers", "bridges", "playing", "plating", "bridged", "plastic", "couples", "softest", "getting", "planned", "getters", "placing", "gifting", "pinking", "pilings", "piecing", "picture", "coursed", "courses", "summers", "picking", "snowing", "phoning", "bedroom", "glances", "glanced", "winging", "snapped", "glassed", "glasses", "perhaps", "covered", "crazies", "crazier", "perfect", "peopled", "persons", "peoples", "suiting", "pausing", "passing", "goldest", "partied", "windows", "parties", "parting", "creates", "grabbed", "smokers", "created", "grabber", "brought", "weights", "bringer", "arrives", "crosser", "crosses", "grasses", "parents", "palming", "graying", "pairing", "crossed", "painted", "arrived", "greying", "smoking", "paining", "outside", "brother", "greater", "smilers", "outings", "greened", "greener", "crowded", "travels", "smiling", "ordered", "grounds", "offings", "smelled", "openers", "browner", "grouped", "opening", "smaller", "growing", "okaying", "officer", "guarded", "slowest", "slowing", "cupping", "slipped", "guessed", "guesses", "cutting", "offices", "gunning", "offered", "browned", "allower", "nursing", "numbing", "suggest", "cutters", "numbers", "sliders", "halving", "sliding", "noticer", "wedding", "notices", "noticed", "nothing", "writers", "hallway", "handing", "sleeper", "normals", "noising", "hanging", "nodding", "dancing", "wearing", "writing", "slammed", "hangers", "darkest", "skinned", "happens", "trained", "needing", "builder", "beliefs", "happier", "necking", "nearest", "hardest", "nearing", "burning", "believe", "winding", "hatting", "narrows", "stupids", "sitting", "mouthed", "deadest", "watered", "sisters", "mothers", "singled", "winning", "morning", "mooning", "moments", "heading", "missing", "decides", "decided", "decider", "mirrors", "minutes", "hearing", "minings", "already", "minding", "middled", "heating", "burners", "singles", "middles", "deepest", "stuffed", "heaters", "singing", "simpler", "heavier", "heavies", "belongs", "message", "despite", "mention", "simples", "studies", "studied", "silvers", "helping", "helpers", "members", "meeting", "willing", "meanest", "attacks", "herself", "meaning", "dinners", "student", "hidings", "matters", "marries", "married", "busying", "busiest", "silence", "against", "highest", "wildest", "hilling", "marking", "mapping", "manages", "managed", "himself", "history", "tracked", "strikes", "manning", "hitting", "makings", "hitters", "whiting", "towards", "watched", "holding", "toucher", "machine", "holders", "lunches", "lunched", "watches", "luckier", "stretch", "streets", "lowered", "loudest", "lookers", "looking", "longing", "calling", "longest", "locking", "bending", "washing", "signing", "hottest", "littler", "benders", "strange", "sighted", "listens", "linings", "likings", "housing", "beneath", "sighing", "sicking", "however", "lighted", "sickest", "lighter", "calming", "lifters", "hundred", "calmest", "hurried", "hurries", "lifting", "touched", "doesn't", "doesn’t", "hurting", "touches", "showers", "husband", "doctors", "letters", "cameras", "letting", "tossing", "leaving", "learned", "dogging", "leaning", "leafing", "leaders", "leading", "whitest", "layered", "ignored", "showing", "ignores", "stories", "ignorer", "shoving", "laughed", "lasting", "largest", "imaging", "doorway", "besting", "imagine", "shouted", "stormed", "downing", "storing", "topping", "avoided", "dragged", "shorter", "betters", "stopper", "landers", "insides", "instead", "written", "drawing", "shopped", "stopped", "between", "landing", "shooter", "knowing", "jackets", "dreamed", "carding", "toothed", "knocked", "knifing", "kitchen", "joining", "teethed", "stomach", "joiners", "kissing", "kindest", "killers", "killing", "shoeing", "kidding", "jumping", "kickers", "kicking", "jumpers", "keepers", "dressed", "keeping", "enough", "checks", "kicked", "jumper", "kicker", "kidded", "jumped", "killed", "joking", "killer", "kinder", "joiner", "kisses", "kissed", "joined", "knives", "knifes", "knifed", "jacket", "knocks", "itself", "ladies", "landed", "lander", "inside", "larger", "images", "lasted", "imaged", "laughs", "ignore", "aboves", "laying", "accept", "layers", "across", "yellow", "leaded", "leader", "leaved", "leaned", "learns", "leaves", "yelled", "lesser", "letter", "living", "lifted", "lifter", "humans", "hugest", "lights", "wrongs", "houses", "liking", "likers", "lining", "housed", "acting", "listen", "hotels", "little", "hotter", "locals", "locked", "horses", "longer", "longed", "looked", "hoping", "looker", "losing", "adding", "louder", "loving", "lovers", "lowing", "lowest", "writer", "lowers", "homing", "holing", "holder", "making", "hitter", "makers", "manned", "manage", "writes", "admits", "mapped", "marked", "hilled", "higher", "afraid", "hiding", "hidden", "matter", "ageing", "helper", "member", "helped", "memory", "hellos", "heater", "metals", "middle", "heated", "mights", "minded", "hearts", "mining", "minute", "headed", "mirror", "misses", "missed", "moment", "moneys", "monies", "months", "mooned", "mostly", "having", "mother", "worlds", "hating", "mouths", "moving", "movers", "movies", "musics", "worker", "myself", "naming", "namers", "narrow", "hatted", "hardly", "nearer", "neared", "nearly", "harder", "necked", "needed", "happen", "hanger", "newest", "nicest", "nights", "worked", "nobody", "nodded", "handed", "noises", "noised", "worded", "normal", "norths", "nosing", "agrees", "noting", "notice", "halves", "halved", "number", "guying", "numbed", "nurses", "nursed", "agreed", "wooden", "offing", "gunned", "offers", "office", "guards", "wonder", "okayed", "okay'd", "okay’d", "ok'ing", "ok’ing", "oldest", "womens", "opened", "opener", "groups", "womans", "within", "ground", "orders", "others", "outing", "wished", "greens", "greats", "owning", "wishes", "owners", "paging", "pained", "paints", "greyed", "greyer", "paired", "palest", "grayed", "palmed", "papers", "grayer", "parent", "parted", "passed", "golder", "passes", "pauses", "paused", "paying", "person", "people", "wipers", "goings", "glance", "phones", "phoned", "photos", "picked", "giving", "givens", "pieces", "pieced", "piling", "gifted", "pinked", "pinker", "places", "placed", "getter", "gotten", "plated", "plates", "gently", "played", "gather", "player", "please", "gating", "garden", "pocket", "gamers", "points", "pointy", "gaming", "future", "wiping", "fuller", "police", "pooled", "poorer", "fucked", "popped", "popper", "fronts", "friend", "freers", "poured", "pourer", "freest", "powers", "formed", "forget", "forgot", "forest", "forces", "forced", "footed", "pretty", "follow", "fliers", "flyers", "proven", "airing", "proves", "proved", "prover", "pulled", "flying", "puller", "flower", "pushes", "pushed", "floors", "pusher", "flight", "fixers", "fixing", "quicks", "winter", "fitted", "quiets", "fitter", "winged", "radios", "rained", "raises", "raised", "fishes", "rather", "fished", "firsts", "firing", "reader", "finish", "finger", "fining", "finest", "realer", "finder", "really", "finals", "reason", "filled", "figure", "fought", "fights", "fields", "fewest", "redder", "refuse", "remain", "feeing", "remind", "feared", "father", "faster", "remove", "repeat", "family", "faller", "fallen", "failer", "failed", "rested", "fading", "return", "reveal", "riches", "richer", "riding", "ridden", "window", "riders", "rights", "facing", "allows", "ringed", "rising", "rivers", "extras", "rocked", "rolled", "expect", "roofed", "excite", "except", "rooves", "roomed", "events", "rounds", "rowing", "evened", "rubbed", "almost", "entire", "runner", "enters", "keying", "rushed", "rushes", "sadder", "safest", "sanded", "enjoys", "saving", "engine", "savers", "winded", "saying", "enders", "scared", "scares", "scarer", "scenes", "ending", "school", "scream", "either", "eights", "screen", "egging", "effort", "search", "edging", "seated", "second", "eaters", "seeing", "seemed", "eating", "seller", "sender", "senses", "sensed", "easier", "easily", "earths", "serves", "served", "willed", "dusted", "settle", "during", "driers", "sevens", "sexing", "shadow", "shakes", "shaken", "dryers", "shaker", "always", "shaped", "driest", "shapes", "shaper", "drying", "shares", "shared", "sharer", "sharps", "driver", "drives", "driven", "sheets", "droves", "drinks", "shirts", "drunks", "shoots", "dreams", "shorts", "dozens", "should", "downed", "shouts", "shoved", "shoves", "showed", "wilder", "shower", "dogged", "doctor", "shrugs", "didn’t", "sicker", "sicked", "didn't", "siding", "sighed", "doings", "sights", "signed", "dinner", "silent", "silver", "dyings", "widest", "simple", "simply", "deeper", "single", "decide", "deaths", "sister", "deader", "sizing", "darker", "wholes", "sleeps", "dances", "danced", "slides", "slider", "cutter", "slower", "slowed", "slowly", "smalls", "cupped", "smells", "smelly", "crying", "smiles", "smiled", "smiler", "crowds", "smokes", "smoked", "smoker", "create", "covers", "snowed", "whited", "softer", "course", "softly", "couple", "counts", "corner", "whiter", "copped", "cooled", "cooler", "coming", "whites", "sorted", "colors", "colder", "sounds", "coffee", "coated", "spaces", "clouds", "spaced", "spoken", "speaks", "clothe", "closed", "closes", "closer", "spends", "climbs", "clears", "cleans", "spirit", "cities", "circle", "church", "choose", "spread", "chosen", "choice", "chests", "sprung", "spring", "sprang", "stages", "stairs", "cheeks", "stands", "keeper", "change", "chance", "stared", "stares", "starer", "chairs", "starts", "center", "causer", "caused", "states", "stated", "causes", "caught", "catted", "stayed", "steals", "stolen", "casing", "sticks", "caring", "carded", "stones", "animal", "cannot", "stored", "stores", "storms", "answer", "camera", "calmer", "calmed", "called", "street", "buyers", "bought", "strike", "struck", "buying", "anyone", "strong", "busier", "busied", "busing", "burner", "stuffs", "burned", "stupid", "builds", "browns", "suites", "suited", "brings", "summer", "bright", "sunned", "bridge", "breath", "breast", "breaks", "broken", "surest", "branch", "brains", "anyway", "boxing", "wheels", "sweets", "swings", "bottom", "bottle", "system", "bother", "tables", "taking", "takers", "talked", "talker", "boring", "taller", "booted", "taught", "booked", "teamed", "teared", "boning", "appear", "bodies", "thanks", "boated", "thicks", "boards", "bluest", "things", "thinks", "blower", "thirds", "thirty", "though", "threes", "throat", "bloods", "thrown", "throws", "blocks", "timing", "blacks", "timers", "tinier", "biters", "tiring", "todays", "biting", "toning", "tongue", "arming", "birded", "bigger", "wetter", "toothy", "beyond", "better", "topped", "tossed", "bested", "tosses", "beside", "bender", "toward", "bended", "tracks", "belong", "trains", "belief", "travel", "behind", "begins", "before", "bedded", "became", "become", "beater", "beaten", "trucks", "truest", "aren’t", "aren't", "trusts", "truths", "trying", "turned", "twenty", "around", "uncles", "weight", "wasn’t", "wasn't", "arrive", "unless", "upping", "wedded", "viewed", "barely", "visits", "banked", "balled", "voices", "voiced", "waited", "bagger", "waking", "walked", "bagged", "walker", "walled", "asking", "wanted", "wanter", "warred", "waring", "backed", "warmed", "warmer", "babies", "washed", "washes", "avoids", "attack", "waters", "asleep", "watery", "waving", "wavers", "seems", "party", "minds", "eaten", "sells", "sends", "known", "sense", "hours", "pasts", "paths", "easts", "pause", "mined", "layer", "payed", "serve", "earth", "early", "wills", "aired", "heard", "hears", "dusts", "kills", "goers", "hotel", "seven", "dried", "ideas", "sexed", "sexes", "going", "drier", "dries", "dryer", "glass", "heads", "shake", "leads", "shook", "aging", "gives", "phone", "local", "photo", "shape", "picks", "above", "locks", "money", "drops", "share", "given", "wrong", "girls", "month", "sharp", "piece", "wilds", "sheet", "drove", "drive", "moons", "lands", "piles", "ships", "drink", "piled", "drank", "drunk", "shirt", "pinks", "shits", "dress", "shoes", "mores", "shoot", "longs", "shots", "dream", "drawn", "draws", "drags", "shops", "haves", "horse", "short", "gifts", "dozen", "place", "downs", "shout", "hopes", "shove", "hoped", "plans", "wiper", "doors", "shown", "shows", "wiped", "plate", "world", "mouth", "doers", "joins", "shrug", "shuts", "leafs", "moved", "plays", "moves", "sicks", "don’t", "pleas", "sided", "sides", "sighs", "don't", "gated", "sight", "looks", "gates", "wives", "mover", "signs", "doing", "dirts", "knees", "movie", "learn", "gamer", "games", "gamed", "dying", "music", "since", "desks", "sings", "singe", "deeps", "point", "acted", "musts", "yells", "funny", "death", "wider", "loses", "sixes", "whose", "names", "sizes", "sized", "skins", "keyed", "skies", "pools", "slams", "darks", "named", "slept", "namer", "sleep", "leave", "dance", "slide", "hated", "young", "whole", "fucks", "who’s", "slips", "who's", "slows", "front", "porch", "loved", "hates", "small", "fresh", "cries", "cried", "smell", "white", "nears", "loves", "smile", "freer", "pours", "lover", "freed", "power", "smoke", "frees", "yeses", "crowd", "cross", "jokes", "fours", "snaps", "crazy", "forms", "cover", "homed", "snows", "among", "necks", "happy", "least", "press", "force", "homes", "count", "needs", "wipes", "years", "cools", "foots", "joked", "foods", "never", "songs", "comes", "sorry", "flier", "color", "sorts", "souls", "lower", "newer", "flyer", "colds", "sound", "flown", "south", "works", "coats", "space", "nicer", "prove", "lucky", "spoke", "night", "speak", "cloud", "hurts", "yards", "pulls", "holed", "flies", "close", "climb", "spent", "spend", "words", "holes", "hangs", "clear", "lunch", "spins", "clean", "class", "liars", "floor", "holds", "spots", "alive", "noise", "flats", "chose", "flash", "nones", "child", "fixer", "fixed", "fixes", "chest", "cheek", "mains", "stage", "hands", "makes", "stair", "quick", "stood", "check", "fiver", "stand", "stars", "fives", "north", "wrote", "stare", "lying", "quiet", "noses", "quite", "start", "chair", "nosed", "radio", "lived", "rains", "notes", "state", "large", "cause", "raise", "catch", "noted", "maker", "stays", "halls", "angry", "stole", "steal", "reach", "first", "cased", "cases", "steps", "lives", "fires", "stuck", "carry", "stick", "cares", "still", "cared", "fired", "cards", "added", "stone", "reads", "halve", "stops", "write", "can’t", "ready", "hairy", "store", "hairs", "can't", "storm", "numbs", "story", "could", "finer", "knife", "fines", "calms", "fined", "calls", "hurry", "while", "buyer", "finds", "nurse", "found", "which", "lifts", "admit", "final", "fills", "lasts", "keeps", "where", "buses", "bused", "study", "offed", "stuff", "fight", "woods", "burnt", "burns", "field", "human", "build", "built", "wings", "offer", "brown", "allow", "guyed", "suite", "suits", "bring", "marks", "fewer", "feels", "hills", "wines", "later", "feeds", "agree", "guess", "surer", "fears", "broke", "break", "guard", "brain", "highs", "often", "marry", "ahead", "knock", "boxes", "sweet", "boxed", "okays", "swing", "swung", "falls", "reply", "hides", "fails", "huger", "table", "takes", "taken", "laugh", "taker", "rests", "house", "talks", "bored", "women", "faded", "fades", "wheel", "facts", "wraps", "boots", "teach", "faces", "teams", "older", "books", "tears", "bones", "maybe", "woman", "faced", "areas", "boned", "opens", "tells", "rides", "grows", "thank", "their", "boats", "thens", "there", "these", "thick", "rider", "after", "board", "right", "bluer", "thins", "blues", "blued", "grown", "thing", "again", "rings", "think", "blows", "blown", "third", "would", "means", "those", "risen", "three", "rises", "blood", "eying", "heres", "throw", "block", "threw", "roses", "group", "river", "black", "tying", "times", "timed", "roads", "rocks", "order", "timer", "meant", "green", "tired", "tires", "extra", "meets", "today", "rolls", "biter", "bitey", "other", "toned", "tones", "light", "bites", "worry", "birds", "roofs", "armed", "outer", "rooms", "outed", "every", "tooth", "teeth", "round", "image", "bests", "event", "liked", "evens", "rowed", "likes", "touch", "bends", "windy", "bents", "towns", "winds", "great", "below", "track", "overs", "owned", "liker", "train", "enter", "wound", "begun", "helps", "began", "begin", "owner", "beers", "kinds", "wests", "paged", "trees", "treed", "tripe", "trips", "pages", "alone", "hello", "beats", "enjoy", "bears", "truck", "beach", "safer", "trues", "truer", "trued", "safes", "hells", "sames", "trust", "truth", "pains", "wells", "sands", "tried", "tries", "greys", "turns", "isn’t", "isn't", "heavy", "twice", "saves", "uncle", "saved", "under", "kicks", "saver", "paint", "lines", "grays", "until", "weeks", "upped", "pairs", "using", "asked", "usual", "scare", "being", "ender", "metal", "views", "paled", "banks", "visit", "pales", "paler", "voice", "scene", "heats", "waits", "balls", "ended", "empty", "woken", "palms", "wakes", "waked", "walks", "lined", "knows", "pants", "worse", "paper", "walls", "worst", "wants", "eight", "heart", "along", "backs", "egged", "jumps", "warms", "grass", "might", "edges", "grabs", "seats", "avoid", "parts", "edged", "aunts", "watch", "about", "eater", "won’t", "water", "won't", "waved", "waves", "goods", "waver", "golds", "wears", "ears", "grab", "fits", "each", "sets", "knee", "lots", "part", "dust", "noes", "fish", "stay", "good", "rain", "cats", "work", "wild", "laid", "hang", "gold", "pass", "step", "loud", "case", "help", "your", "past", "nods", "home", "care", "path", "hell", "read", "love", "fire", "gods", "lift", "card", "stop", "pays", "keys", "cars", "paid", "idea", "fine", "none", "real", "into", "drop", "heat", "wish", "cans", "kids", "find", "goer", "goes", "went", "calm", "just", "lead", "gone", "call", "fill", "nose", "ship", "huge", "acts", "lows", "buys", "some", "note", "kind", "shit", "shat", "mind", "ices", "busy", "pick", "hand", "shod", "shoe", "gave", "reds", "shot", "hall", "fews", "ours", "feel", "burn", "drew", "such", "draw", "shop", "give", "felt", "wing", "suit", "drag", "hear", "feed", "mine", "girl", "feds", "iced", "down", "when", "fees", "half", "suns", "able", "word", "fear", "nows", "door", "fast", "sure", "leaf", "pile", "jobs", "show", "wine", "boys", "dogs", "yell", "hair", "guys", "kept", "doer", "fall", "fell", "head", "shut", "gift", "hole", "rest", "numb", "kick", "lean", "take", "both", "sick", "fail", "fade", "took", "miss", "side", "sigh", "held", "talk", "last", "plan", "bore", "hold", "done", "tall", "teas", "fact", "boot", "like", "wife", "rich", "sign", "book", "wood", "team", "does", "main", "offs", "tear", "tore", "torn", "rode", "dirt", "gets", "bone", "joke", "ride", "make", "told", "play", "died", "tell", "dies", "tens", "area", "body", "than", "boat", "line", "guns", "desk", "that", "what", "kiss", "them", "they", "gate", "sang", "then", "plea", "kill", "face", "sing", "sung", "eyes", "thin", "blue", "deep", "made", "rung", "ring", "sirs", "wide", "he’s", "rang", "moon", "blow", "eyed", "sits", "more", "whys", "dead", "blew", "days", "this", "left", "grew", "he's", "size", "rise", "rose", "whom", "have", "skin", "most", "late", "grow", "slam", "road", "game", "tied", "ties", "arms", "time", "dark", "rock", "okay", "ages", "mens", "roll", "mans", "tiny", "slid", "dads", "airs", "ok'd", "tire", "wets", "ok’d", "i’ll", "roof", "slip", "full", "cuts", "pool", "slow", "tone", "bite", "lips", "cups", "bits", "room", "olds", "poor", "bird", "adds", "ever", "knew", "hate", "fuck", "pops", "even", "tops", "wipe", "hits", "once", "west", "hour", "rows", "rubs", "toss", "best", "ones", "only", "from", "runs", "bend", "bent", "onto", "open", "move", "town", "free", "pour", "legs", "rush", "jump", "snap", "many", "hill", "less", "maps", "snow", "keep", "safe", "much", "soft", "join", "beer", "i'll", "beds", "four", "tree", "same", "sand", "form", "cops", "must", "year", "cool", "trip", "lets", "beat", "mark", "born", "bear", "with", "come", "save", "know", "true", "sons", "lock", "song", "soon", "laws", "came", "outs", "name", "well", "been", "says", "said", "sort", "feet", "soul", "high", "yeah", "were", "hide", "foot", "turn", "cold", "wind", "yard", "twos", "coat", "food", "over", "hats", "owns", "ends", "lady", "aged", "arts", "else", "long", "flew", "hurt", "page", "week", "upon", "lays", "used", "uses", "hard", "eggs", "wins", "very", "mays", "seas", "pain", "near", "view", "bars", "weds", "pull", "edge", "wrap", "lies", "bank", "spin", "ball", "grey", "seat", "spun", "lied", "neck", "push", "wait", "hope", "bags", "city", "look", "wake", "spot", "saws", "woke", "wear", "pink", "liar", "eats", "walk", "need", "sees", "seen", "puts", "seem", "wall", "want", "pair", "gray", "sell", "will", "flat", "back", "pale", "sold", "asks", "wars", "land", "send", "mean", "warm", "baby", "sent", "also", "wash", "away", "here", "easy", "hung", "sens", "star", "hers", "aunt", "palm", "worn", "life", "meet", "wore", "east", "live", "news", "five", "wave", "next", "lost", "lose", "nice", "ways", "far", "few", "war", "bad", "bag", "bar", "wed", "use", "ups", "art", "was", "two", "try", "are", "bed", "top", "arm", "wet", "big", "too", "bit", "tie", "the", "ten", "tvs", "tea", "box", "boy", "sun", "bus", "but", "buy", "any", "can", "car", "cat", "and", "son", "cop", "sos", "cry", "cup", "cut", "who", "dad", "sky", "day", "six", "why", "sit", "sat", "sir", "die", "did", "dog", "she", "dry", "sex", "set", "ear", "ate", "eat", "see", "saw", "win", "won", "sea", "egg", "end", "say", "sad", "ran", "run", "rub", "row", "eye", "rid", "ask", "fed", "fee", "red", "way", "fit", "fix", "all", "put", "fly", "for", "pop", "fun", "get", "got", "god", "pay", "own", "out", "our", "air", "ors", "one", "old", "ohs", "gun", "key", "off", "guy", "now", "not", "nor", "nod", "nos", "ago", "new", "hat", "age", "had", "has", "her", "met", "hey", "may", "hid", "map", "him", "add", "his", "man", "men", "hit", "mad", "low", "lot", "hot", "lip", "how", "lit", "lie", "kid", "i'm", "let", "i’m", "leg", "i'd", "i’d", "ice", "led", "act", "lay", "law", "ins", "yes", "yet", "you", "its", "job", "no", "at", "by", "my", "on", "ha", "do", "ok", "he", "oh", "is", "tv", "me", "us", "as", "hi", "go", "if", "of", "am", "up", "to", "we", "so", "in", "or", "it", "be", "an", "i", "a"
  ]);
  const random_responses = [
      "Can you try something else?", // 5
      "Head in another direction with this.", // 6
      "Ah, I don’t know the right reply...", // 7
      "There’s something that I don’t know how to reply to.", // 10
      "At first glance, that doesn’t look like what I want.", // 12
      "Please try something else - that’s something that’s out of my understanding for now.", // 14
      "Perhaps try a different idea - my replies are very few at this time, sorry." // 15
  ];
  const input = q.trim().toLowerCase();
  const target_string = 'mtproto';
  const error_response = "Sorry, I’m still learning and only know the ten hundred most used words!";
  const success_response = "Way to follow chat protocols! What’s the app for that, again?"
  const alpha_only = /([^a-z'’])/;
  const internal_strip = / +/;
  let clean_string = input.replace(alpha_only, " ").replace(internal_strip, ' ');

  if (clean_string == "telegram")
      return {'a':"Ooh, that’s what you need! I can’t help you any more, but have you checked out our email support and web page?"}

  const words = clean_string.split(' ');
  if (!words.every(w => WORDS.has(w)))
      return {'a':error_response};

  const test_string = words.map(w => w[0]);
  const target = target_string.split(' ');
  const incorrect = "❌"
  const place = "🌚"
  const letter = "🌝"
  const shorter = Math.min(target.length, test_string.length);
  const longer = Math.max(target.length, test_string.length);
  const output = new Array(longer).fill(incorrect);

  for (let i = 0; i < shorter; i++) { // we only need to check the length of the string for exact messages
    // check for place matches
    if (test_string[i] == target[i]) {
        target[i] = place
        test_string[i] = place
        output[i] = place
    }
  }

  for (let i = 0; i < test_string.length; i++) {
      // check for other matches
      if ("abcdefghijklmnopqrstuvwxyz".includes(test_string[i])) {
          if (target.includes(test_string[i])) {
              target[target.index(test_string[i])] = letter;
              test_string[i] = letter;
              output[i] = letter;
          }
      }
  }

  for (let i = 0; i < test_string.length; i++) {
    if ("abcdefghijklmnopqrstuvwxyz".includes(test_string[i])) {
      if (!target.includes(test_string[i])) {
        output[i] = incorrect
      }
    }
  }

  const joinedOutput = output.join("")

  let response_text = joinedOutput + ' ' + randomChoice(random_responses);
  if (joinedOutput == new Array(target.length).fill(place))
      response_text = success_response

  return {'a': response_text};
};

function randomInt(a, b) {
  return a + Math.floor(Math.random() * (b - a + 1));
}

function randomChoice(arr) {
  return arr[randomInt(0, arr.length-1)];
}
