var phraseArray = [
  "3 3 5 5 4 3 5 2 10 4 6 6 11 5 6 6",
  "7 12 16 5 5 7 5 4 11 15",
  "5 2 3 7 6 1 11 2",
  "1 8 8 4 11 5 1 3 4 5 7 5 5 2",
];
var speakers = [
  [15, 47],
  [34, 27],
  [19, 4],
  [13, 10],
];

$(document).ready(function () {
  var currentSound;
  function playSound(sound) {
    const shouldPlay = currentSound !== sound || (currentSound && currentSound.paused);
    stopSound();
    if (shouldPlay) {
      sound.play();
      currentSound = sound;
    }
  }

  function stopSound() {
    if (currentSound) {
      currentSound.pause();
      currentSound.currentTime = 0;
      currentSound = undefined;
    }
  }

  function resetUI() {
    $(".speaker1").removeClass("speaker1");
    $(".speaker2").removeClass("speaker2");
    $("#blank").empty();
  }

  $(".cat").on("click", function () {
    resetUI();

    var getord = this.id.split("_");
    var item = getord[1];

    $("#cat_" + item).addClass("speaker1");

    // finally getting to play some audio
    var sound = $("#meow" + item)[0];
    playSound(sound);
  });

  $(".dialogue").on("click", function () {
    resetUI();

    var getord = this.id.split("_");
    var item = getord[1];
    var sound = $("#conversation" + item)[0];
    playSound(sound);

    var phrase = phraseArray[item - 1];
    var [speaker1, speaker2] = speakers[item - 1];
    $("#blank").text(phrase);
    $('#cat_' + speaker1).addClass('speaker1');
    $('#cat_' + speaker2).addClass('speaker2');
  });

  $(".stop").on("click", stopSound);
});
