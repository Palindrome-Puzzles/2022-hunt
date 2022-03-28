const QUESTIONS = [
    {
        'q': 'Hoe noem je een onverwacht einde van een film of een garneri[n]g die op veel cocktails wordt gebruikt?',
        'options': ['highball', 'quarrel', 'ending', 'everclear', 'lemon'],
        'score': 10,
        'image': 'q1-z4dlyoAiky.png',
        'correct': 1,
    },
    {
        'q': 'In welke hoeveelheid zitten volgens een bakker dertien ding[e]n?',
        'options': ['granola', 'oil', 'boxes', 'elephant', 'dough'],
        'score': 10,
        'image': 'q2-39n0JPLfyP.png',
        'correct': 2,
    },
    {
        'q': 'Wat voor soort arts geeft een opzette[l]ijk bevooroordeelde kijk op een politieke situatie?',
        'options': ['web', 'executive', 'spider', 'rotate', 'kindergarten'],
        'score': 8,
        'image': 'q3-lYAhAInp2S.png',
        'correct': 2,
    },
    {
        'q': 'Welk woord beschrijft een donkere bierstij[l] en ook een theepot in een lied?',
        'options': ['naughty', 'rinse', 'empty', 'ornery', 'rye'],
        'score': 1,
        'image': 'q4-00gVebMGNF.png',
        'correct': 0,
    },
    {
        'q': 'Wat is het woord [v]oor een gepubliceerde verklaring die de reputatie van een persoon schaadt?',
        'options': ['dirty', 'dragonfly', 'epigram', 'ruin', 'tick'],
        'score': 10,
        'image': 'q5-U8Fuxu9lCC.png',
        'correct': 1,
    },
    {
        'q': 'Welk dier is een v[o]lwassen mannelijke kip met een felrode kam op zijn kop?',
        'options': ['horse', 'schedule', 'elevator', 'quinoa', 'unicorn'],
        'score': 5,
        'image': 'q6-kGWIhFuGli.png',
        'correct': 1,
    },
    {
        'q': 'Over wat voor soort romance zingt Lady Gaga in ee[n] single uit 2009?',
        'options': ['evening', 'shallow', 'telephone', 'bathtub', 'independent'],
        'score': 12,
        'image': 'q7-uk4wNNqwCn.png',
        'correct': 3,
    },
    {
        'q': 'Welk type kopje wordt vaak gebruikt om hete vloeistoffen zoals koffie of warme chocola[d]emelk in te bewaren?',
        'options': ['orange', 'nip', 'mosquito', 'stein', 'ant'],
        'score': 7,
        'image': 'q8-FnGxF0273p.png',
        'correct': 2,
    },
    {
        'q': 'Welk[e] boekwinkel in New York City heeft de slogan &lsquo;achttien mijl aan boeken&rsquo;?',
        'options': ['beach', 'lion', 'paperback', 'hardcover', 'appendix'],
        'score': 3,
        'image': 'q9-tpGWveRhuf.png',
        'correct': 0,
    },
    {
        'q': 'Welk woord volgt [n]agel, computer, of zaak?',
        'options': ['traffic jam', 'bite', 'electric', 'toe', 'individual'],
        'score': 5,
        'image': 'q10-RqAd5vqS6j.png',
        'correct': 0,
    },
    {
        'q': 'Welke n[a]am werd in de klassieke mythologie gebruikt voor een planeet en is ook de naam van een gevallen engel in de Bijbel?',
        'options': ['comet', 'apostle', 'lunar', 'lollipop', 'match'],
        'score': 15,
        'image': 'q11-3xqQIoZaKS.png',
        'correct': 4,
    },
    {
        'q': 'Als je een [M]cKroket bestelt, wat voor soort broodje krijg je dan?',
        'options': ['yogurt', 'bun', 'yellow', 'toast', 'citizen'],
        'score': 12,
        'image': 'q12-FgEio9lzqR.png',
        'correct': 4,
    },
    {
        'q': 'Welk schaakstuk wordt soms aangeduid [m]et hetzelfde woord dat wordt gebruikt voor een gebouw waar een koningin of koning woont?',
        'options': ['hill', 'estate', 'smoke', 'checkmate', 'outhouse'],
        'score': 4,
        'image': 'q13-txJ6brLJTH.png',
        'correct': 2,
    },
    {
        'q': 'Welk ijshockeyte[a]m speelt zijn thuiswedstrijden in de stad waar een beroemd theekransje werd gehouden?',
        'options': ['Rangers', 'Red Wings', 'Eagles', 'Browns', 'Cardinals'],
        'score': 6,
        'image': 'q14-bSEC62C0k7.png',
        'correct': 3,
    },
    {
        'q': 'Welk lid van de lookfamilie staat ook bek[e]nd als wilde prei?',
        'options': ['turnip', 'disaster', 'avalanche', 'niece', 'shallot'],
        'score': 7,
        'image': 'q15-rU6obRWXAV.png',
        'correct': 1,
    },
    {
        'q': 'Welk woord wordt gebruikt voor een grotesk of a[n]gstaanjagend wezen, zoals één die zogenaamd in een Schots meer leeft?',
        'options': ['whiskey', 'elevator', 'rhinoceros', 'sample', 'submarine'],
        'score': 8,
        'image': 'q16-BrwyUQprab.png',
        'correct': 3,
    }
];

let state = null;
let winHandler = () => {};

window.stubSend = async (body) => {
  if (body.__seq === 0) {
    state = initialState();
    return {...projectState(state), __sid: 'abc', __status: 'success'};
  } else {
    transformState(state, body);
    return {
      ...projectState(state),
      __sid: 'abc',
      __status: state.completed ? 'complete' : 'success',
    };
  }
};

window.onWin = (handler) => {
  winHandler = handler;
}

function initialState() {
  return {
    'question': 1,
  };
}

function projectState(state) {
  const num = state.question;
  const question = QUESTIONS[num - 1];
  const prev_question_score = num > 1 ? QUESTIONS[num - 2]['score'] : 0;
  return {
      'num': question ? num : null,
      'q': question ? question['q'] : undefined,
      'options': question ? question['options'] : undefined,
      'image': question ? get_image_path(question['image']) : undefined,
      'score': prev_question_score
  }
}

function transformState(state, body) {
  if (body.answer === QUESTIONS[state.question - 1].correct) {
    state.question += 1;
  } else {
    state.question = 1;
  }

  if (state.question > QUESTIONS.length) {
    winHandler(QUESTIONS.map(q => ({...q, 'image': get_image_path(q['image'])})));
  }
}

function get_image_path(filename) {
  return window.puzzleStaticDirectory + 'images/' + filename;
}
