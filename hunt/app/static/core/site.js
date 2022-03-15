(function() {
function assert(value, message) {
  if (!value) {
    throw Error(message);
  }
}

const NOTIFICATION_TIMEOUT_MS = 10 * 1000;
const VOLUME_KEY = 'hunt:volume';
const SOUND_DEBOUNCE_TIME_MS = 7000;
const SOUND_IRRELEVANCE_TIME_MS = 15000;
const LAST_SOUND_TIME_KEY = 'hunt:last_sound_time';

let sharedAudioElement;
const mobileMatcher = window.matchMedia('(max-width: 639.9px)');
const htmlElement = document.querySelector('html');
htmlElement.classList.add('supports-js');

initializeTabbing();
initializeMenu(document.querySelector('.top-menu'));
initializeMobileMenu();
initializePuzzleActionLinks();
initializeNotifications();
initializeVolumeSlider();

window.playSolveSound = playSolveSound;

function initializeTabbing() {
  window.addEventListener('keydown', handleFirstTab);
  function handleFirstTab(e) {
    if (e.key === 'Tab') {
      document.body.classList.add('user-is-tabbing');
      window.removeEventListener('keydown', handleFirstTab);
    }
  }
}

function initializeMenu(menuRoot) {
  if (!menuRoot) return;

  const wrappers = [];
  const triggers = Array.from(menuRoot.querySelectorAll('.dropdown-trigger'));
  const menus = [];
  const isListMenu = {};
  let openIndex = null;

  for (let i = 0; i < triggers.length; i++) {
    const trigger = triggers[i];
    const menu = trigger.parentNode.querySelector('.dropdown-menu');
    assert(
      trigger.getAttribute('aria-controls') === menu.id,
      'Mismatched aria-controls');
    menus.push(menu)
    wrappers.push(trigger.closest('.dropdown-wrapper'));

    if (menu.tagName.toLowerCase() === 'ul') {
      isListMenu[i] = true;
    }

    toggleExpanded(i, false);

    trigger.addEventListener('click', function(event) {
      const isExpanded = trigger.getAttribute('aria-expanded') === 'true';
      toggleExpanded(i, !isExpanded);
    });
    trigger.addEventListener('keydown', function(event) { onTriggerKeydown(i, event); });
    menu.addEventListener('keydown', onMenuKeydown);
  }

  menuRoot.addEventListener('focusout', function(event) {
    const isStillFocused = menuRoot.contains(event.relatedTarget);
    if (!isStillFocused && openIndex !== null) {
      toggleExpanded(openIndex, false);
    }
  });

  function toggleExpanded(index, isExpanded) {
    if (openIndex !== null && index !== openIndex) {
      toggleExpanded(openIndex, false);
    }
    openIndex = isExpanded ? index : null;
    triggers[index].setAttribute('aria-expanded', isExpanded.toString());

    if (isExpanded) {
      const rightSpace = document.body.clientWidth - wrappers[index].offsetLeft;
      const openRight = rightSpace < menus[index].offsetWidth;
      menus[index].classList.toggle('open-right', openRight);
    }
  }

  function onTriggerKeydown(index, event) {
    if (mobileMatcher.matches) return;

    if (event.key === 'Escape') {
      toggleExpanded(index, false)
    } else {
      onArrowKeys(index, event);
    }
  }

  function onMenuKeydown(event) {
    if (mobileMatcher.matches) return;

    assert(openIndex !== null, 'Menu should be open');
    if (event.key === 'Escape') {
      triggers[openIndex].focus();
      toggleExpanded(openIndex, false)
    } else {
      onArrowKeys(openIndex, event);
    }
  }

  function onArrowKeys(index, event) {
    if (mobileMatcher.matches) return;
    if (event.altKey || event.ctrlKey || event.metaKey || event.isComposing) {
      return;
    }

    // Don't steal arrow keys from input elements.
    if (event.target.tagName.toLowerCase() === 'input') {
      return;
    }

    // Handle up/down arrows.
    let newFocus;
    let closeCurrent = false;
    if (isListMenu[index] && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      const menuLinks =
        openIndex === index ? Array.from(menus[openIndex].querySelectorAll('a')) : [];
      if (document.activeElement === triggers[index]) {
        if (event.key === 'ArrowDown' && menuLinks.length) {
          newFocus = menuLinks[0];
        }
      } else {
        const activeLinkIndex = menuLinks.indexOf(document.activeElement);
        if (activeLinkIndex === -1) return;
        if (event.key === 'ArrowUp' && activeLinkIndex === 0) {
          newFocus = triggers[index];
        } else if (event.key === 'ArrowUp') {
          newFocus = menuLinks[activeLinkIndex - 1];
        } else if (event.key === 'ArrowDown' && activeLinkIndex < menuLinks.length) {
          newFocus = menuLinks[activeLinkIndex + 1];
        }
      }
    }
    else if (event.key === 'ArrowLeft' && index > 0) {
      newFocus = triggers[index - 1];
      closeCurrent = true;
    } else if (event.key === 'ArrowRight' && index < triggers.length) {
      newFocus = triggers[index + 1];
      closeCurrent = true;
    }

    if (newFocus) {
      newFocus.focus();
      event.preventDefault();
    }
    if (closeCurrent) {
      toggleExpanded(openIndex, false);
    }
  }
}

function initializeMobileMenu() {
  const toggle = document.querySelector('.mobile-menu-heading button');
  const menu = document.querySelector('.responsive-menu-container');
  const overlay = document.querySelector('.menu-overlay');
  if (!toggle || !menu || !overlay) return;

  mobileMatcher.addEventListener('change', function(e) { onMatcherChanged(e.matches); });
  onMatcherChanged(mobileMatcher.matches);

  function onMatcherChanged(isMobile) {
    if (!isMobile) {
      menu.classList.toggle('menu-open', false);
    }
  }

  toggle.addEventListener('click', function() {
    menu.classList.toggle('menu-open');
  });

  overlay.addEventListener('click', () => {
    menu.classList.toggle('menu-open', false);
  });
}

function initializePuzzleActionLinks() {
  const wrapper = document.querySelector('.puzzle-action-embed-wrapper');
  if (!wrapper) {
    return;
  }
  const iframe = wrapper.querySelector('iframe');
  const close = wrapper.querySelector('button');

  wrapper.classList.toggle('closed', true);

  for (const embeddableLink of document.querySelectorAll('.puzzle-actions a[data-embed-href]')) {
    var actionOnClick = function(event) {
      event.preventDefault();

      // If the iframe is in the DOM, changing the src counts as a navigation in
      // Firefox. Workaround this by removing it first.
      const parent = iframe.parentNode;
      const nextSibling = iframe.nextSibling;
      iframe.remove();

      // Note: Use getAttribute to prevent the DOM normalizing links.
      const targetLink = embeddableLink.dataset.embedHref;;
      if (iframe.getAttribute('src') === targetLink) {
        iframe.src = '';
        wrapper.classList.toggle('closed', true);
      } else {
        iframe.src = targetLink;
        wrapper.classList.toggle('closed', false);
      }

      parent.insertBefore(iframe, nextSibling);
    }
    embeddableLink.addEventListener('click', actionOnClick);
    if(embeddableLink.hasAttribute('data-starts-open')) {
      window.addEventListener('load', actionOnClick);
    }
  }

  close.addEventListener('click', function() {
    iframe.src = '';
    wrapper.classList.toggle('closed', true);
  });
}

function initializeNotifications() {
  if (window.isPublicAccess) {
    return;
  }
  const rewardContainer = document.querySelector('.reward-container');
  const bonusContentContainer = document.querySelector('.bonus-puzzle-container');
  const notifications = document.querySelector('.notifications');
  if (!notifications || !window.puzzleAuthToken) return;
  notifications.setAttribute('aria-live', 'polite');
  notifications.setAttribute('role', 'log');

  // If we enter mobile mode, ensure there's at most one notification.
  mobileMatcher.addEventListener('change', function(e) {
    if (e.matches) {
      while (notifications.firstChild && notifications.firstChild.nextSibling) {
        notifications.firstChild.remove();
      }
    }
  });

  const notificationsUrl =
    (location.protocol === "https:" ? "wss://" : "ws://") +
    `${location.host}/ws/team`;
  const socket = new RobustWebSocket(notificationsUrl);
  socket.addEventListener('open', () => {
    socket.send(JSON.stringify({ type: "AUTH", data: window.puzzleAuthToken }));
  });
  socket.addEventListener('message', (event) => {
    const notificationInfo = JSON.parse(event.data);
    addNotification(notifications, notificationInfo);
    if (notificationInfo.soundUrl) {
      playSolveSound(notificationInfo.soundUrl);
    }
    if (notificationInfo.rewardInfo) {
      if (window.location.pathname.startsWith(notificationInfo.rewardInfo.url)) {
        rewardContainer.innerHTML = notificationInfo.rewardInfo.html;
      }
    }
    if (notificationInfo.bonusContent) {
      if(window.location.pathname.startsWith(notificationInfo.bonusContent.url)) {
        bonusContentContainer.innerHTML = notificationInfo.bonusContent.html;
      }
    } else if (notificationInfo.puzzleUrl) {
      const answersIframe = document.querySelector('.' + notificationInfo.puzzleUrl + '-answers');
      if (answersIframe) {
        answersIframe.src = answersIframe.src;
      }
    }
  });
}

function addNotification(notifications, notificationInfo) {
  const { message, link, special } = notificationInfo;
  if (mobileMatcher.matches) {
    while (notifications.firstChild) {
      notifications.firstChild.remove();
    }
  }

  const notification = document.createElement('div');
  notification.classList.toggle('notification', true);
  notification.classList.toggle(special, true);
  notification.classList.toggle('can-reduce-transition', true);
  notification.classList.toggle('can-reduce-animation', true);
  notifications.appendChild(notification);

  let container;
  if (link) {
    container = document.createElement('a');
    container.href = link;
    container.target = '_blank';
  } else {
    container = document.createElement('span');
  }
  container.innerHTML = message;
  notification.appendChild(container);

  const close = document.createElement('button');
  close.classList.toggle('unstyled', true);
  close.innerText = '×';
  notification.appendChild(close);

  const noDecay = ['sticky', 'story_beat', 'round_released', 'announcement'];
  const timer = noDecay.includes(special) ? null : setTimeout(removeNotification, NOTIFICATION_TIMEOUT_MS);
  notification.addEventListener('click', removeNotification);

  function removeNotification() {
    notification.remove();
    notification.removeEventListener('click', removeNotification);
    if (timer) clearTimeout(timer);
  }
}

function initializeVolumeSlider() {
  const slider = document.querySelector('.volume-menu input[type=range]');
  const label = document.querySelector('.volume-menu label span');
  if (!slider || !label) return;

  if (!sharedAudioElement) {
    sharedAudioElement = new Audio();
  }

  const rawVolume = parseInt(localStorage.getItem(VOLUME_KEY), 10);
  const initialVolume = rawVolume || rawVolume == 0 ? Math.max(Math.min(parseInt(rawVolume, 10), 100), 0) : 30;

  slider.value = initialVolume;
  label.innerText = initialVolume;
  sharedAudioElement.volume = initialVolume / 100;
  slider.addEventListener('input', event => {
    label.innerText = slider.value;
    sharedAudioElement.volume = slider.value / 100;
    localStorage.setItem(VOLUME_KEY, slider.value);
  });
}

function playSolveSound(soundUrl) {
  if (!sharedAudioElement) return;

  const soundEventTime = Date.now();
  sharedAudioElement.src = soundUrl;

  if (sharedAudioElement.readyState === HTMLAudioElement.HAVE_ENOUGH_DATA) {
    maybePlay();
  } else {
    const cb = () => {
      maybePlay();
      sharedAudioElement.removeEventListener('canplaythrough', cb);
    }
    sharedAudioElement.addEventListener('canplaythrough', cb);
  }

  function maybePlay() {
    const now = Date.now();
    const lastSoundTime = localStorage.getItem(LAST_SOUND_TIME_KEY);
    // Avoid playing too many sounds in rapid succession.
    if (lastSoundTime && now - lastSoundTime < SOUND_DEBOUNCE_TIME_MS) return;
    // Don't bother if this callback runs much later than the event it is for.
    if (soundEventTime && now - soundEventTime > SOUND_IRRELEVANCE_TIME_MS) return;

    sharedAudioElement.play();
    localStorage.setItem(LAST_SOUND_TIME_KEY, soundEventTime);
  };
}
})();
