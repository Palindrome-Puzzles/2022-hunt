//////// DO NOT READ THIS FILE - you will be spoiled /////////





















































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































const hiddenEl = document.querySelector('header dd');
const responses = {
  'POST': 'FOOER TEAD CENTE BAS HAD',
  'HEAD': 'VG MBED AR M AV',
  'PUT': 'FORT DEV MAID MATER',
  'DELETE': 'STRONGO NUL COLE',
};

const search = window.location.search.toUpperCase();
for (const response of Object.keys(responses)) {
  if (search.indexOf(`=${response}&`) > -1 || search.endsWith(`=${response}`)) {
    hiddenEl.innerText = responses[response];
    break;
  }
}