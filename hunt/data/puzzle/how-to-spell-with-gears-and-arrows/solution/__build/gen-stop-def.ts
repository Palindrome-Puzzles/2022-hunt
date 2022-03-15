import {TOOTH_HEIGHT} from '../../util';
import {getPegStopPoints} from '../../__build/common';

console.log(`
<svg xmlns="http://www.w3.org/2000/svg" class="hidden">
  <symbol id="stop-symbol" viewbox="${-TOOTH_HEIGHT/2} ${-TOOTH_HEIGHT/2} ${TOOTH_HEIGHT} ${TOOTH_HEIGHT}">
    <polygon points="${getPegStopPoints()}"/>
    <text dominant-baseline="central" text-anchor="middle">STOP</text>
  </symbol>
</svg>`);
