let canvas = document.getElementById("myCanvas");
let ctx = canvas.getContext("2d");
window.puzzleOnLoad = puzzleOnLoad;
let canvasNext = document.getElementById("myCanvasNext");
let ctxNext = canvasNext.getContext("2d");

const numCols = 12;
const numRows = 25;
const wallThickness = 20;
const wellWidth = 240;
const wellHeight = 500;
const cellWidth = 20;
const cellHeight = 20;

let wordlist = [];

let curLevel = 1;
let turnNum = 0;
let isGameOver = 0;
let curPiece = {};
let blockInput = false;
let fixed = [];
let whenFixed = [];

function puzzleOnLoad() {
    document.addEventListener("keydown", keyDownHandler, false);
    $(".dpad").click(buttonHandler);

    $("#btn-1").click(function() { startNewLevel(1) });
    $("#btn-2").click(function() { startNewLevel(2) });
    $("#btn-3").click(function() { startNewLevel(3) });
    $("#btn-4").click(function() { startNewLevel(4) });
    $("#btn-5").click(function() { startNewLevel(5) });
    $("#btn-6").click(function() { startNewLevel(6) });

    startNewLevel(1);
    draw();
}

function getState(payload, handler){
    blockInput = true;
    (window.stubGetState || actualGetState)(payload, handler);
}

function actualGetState(payload, handler) {
    const PUZZLE_ENDPOINT = window.puzzleUrl + "state";
    const CSRF_TOKEN = window.getCookie('csrftoken');
    $.post(
        {
            'url': PUZZLE_ENDPOINT,
            'dataType': 'json',
            'cache': false,
            'headers': {
                "X-CSRFToken": CSRF_TOKEN
            },
            data: payload,
            success: handler,
        }
    );
}

function setupNewLevel ( data ){
    wordlist = data['wordlist'];
    isGameOver = 0;
    blockInput = false;
    startNewPiece();
}

function updateLevelIndicator( lnum ) {
    $("#level-title").html("Level "+lnum);
    $(".level-indicator").html("");
    $("#lev" + lnum).html(">");
}

function setStatus(msg){
    $("#msg").html(msg);
}

function showAnswerChecker( lnum ){
    for (let i = 0; i <=6; i++) {
        var answerCheckerDiv = $("#answer-" + i);
        if(i == lnum){
            answerCheckerDiv.show()

            // Force reload of iframe
            var answerChecker = answerCheckerDiv.find("iframe")[0]
            answerChecker.src = answerChecker.src
        } else {
            answerCheckerDiv.hide()
        }
    }
}

function startNewLevel( lnum ){
    setStatus("");
    curLevel = lnum;
    updateLevelIndicator( curLevel );
    showAnswerChecker( curLevel )
    turnNum = 0;
    for(var r=0; r<numRows; r++) {
        fixed[r] = [];
        for(var c=0; c<numCols; c++) {
            fixed[r][c] = " ";
        }
    }
    for(var r=0; r<numRows; r++) {
        whenFixed[r] = [];
        for(var c=0; c<numCols; c++) {
            whenFixed[r][c] = -1;
        }
    }
    return getState({
        level: lnum,
        last_word: '',
        grid: JSON.stringify(fixed)
    }, setupNewLevel);
}

function gameWinOrLoss( data ) {
    blockInput = false;
    if( !data['success'] ){
        endGameLoss();
        return;
    }

    if( turnNum >= wordlist.length ){
        endGameWin();
        return;
    }
    startNewPiece();
}

function verifyWell(){
    return getState({
        level: curLevel,
        last_word: curPiece.glyphs,
        grid: JSON.stringify(fixed)
    }, gameWinOrLoss);
}


function drawWell(){
    ctx.beginPath();
    ctx.rect(wallThickness, 0, wellWidth, wellHeight);
    ctx.fillStyle = "#ffcc99";
    ctx.fill();
    ctx.closePath();
}

function drawFixed(){
    for(var r=0; r<numRows; r++){
        for(var c=0; c<numCols; c++){
            ctx.beginPath();
            ctx.rect(wallThickness+c*cellWidth, r*cellHeight, cellWidth, cellHeight);
            ctx.strokeStyle = "#aaaaaa";
            if(fixed[r][c] != " "){
                ctx.fillStyle = "#bb0055";
                ctx.fill();
            }
            ctx.stroke();
            ctx.closePath();
            if(fixed[r][c] != " "){
                ctx.font = "20px Courier";
                ctx.fillStyle = "#ffffff";
                ctx.fillText(fixed[r][c], wallThickness+c*cellWidth+4, (r+1)*cellHeight-4);
            }

        }
    }
}

function drawCurrent(){
    for(var t=curPiece.tmin; t<=curPiece.tmax; t++){
        var x = curPiece.x + t*curPiece.dx;
        var y = curPiece.y + t*curPiece.dy;

        ctx.beginPath();
        ctx.rect(wallThickness+x*cellWidth, y*cellHeight, cellWidth, cellHeight);
        ctx.strokeStyle = "#aaaaaa";
        ctx.fillStyle = "#2222dd";
        ctx.fill();
        ctx.stroke();
        ctx.closePath();

        ctx.font = "20px Courier";
        ctx.fillStyle = "#ffffff";
        ctx.fillText(curPiece.glyphs[t-curPiece.tmin], wallThickness+x*cellWidth+4, (y+1)*cellHeight-4);

    }
}

function drawNext(){
    ctxNext.beginPath();
    ctxNext.rect(0, 0, canvasNext.width, canvasNext.height);
    ctxNext.fillStyle = "#ffcc99";
    ctxNext.fill();
    ctxNext.closePath();

    ctxNext.font = "16px Arial";
    ctxNext.fillStyle = "#000000";
    ctxNext.fillText("Next Piece:", 8, 16);

    if( turnNum+1 >= wordlist.length ){
        return;
    }
    var nextWord = wordlist[turnNum+1];
    var l = nextWord.length;
    var p = (canvasNext.width - l*cellWidth)/2;
    for(var i=0; i<l; i++){
        ctxNext.beginPath();
        ctxNext.rect(p+i*cellWidth, 1.5*cellHeight, cellWidth, cellHeight);
        ctxNext.strokeStyle = "#aaaaaa";
        ctxNext.fillStyle = "#2222dd";
        ctxNext.fill();
        ctxNext.stroke();
        ctxNext.closePath();

        ctxNext.font = "20px Courier";
        ctxNext.fillStyle = "#ffffff";
        ctxNext.fillText(nextWord[i], p+i*cellWidth+4, 2.5*cellHeight-4);
    }

}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawWell();
    drawFixed();
    drawCurrent();
    drawNext();
}



function endGameLoss(){
    isGameOver = 1;
    setStatus("Illegal placement. Game Over.")
    // ctx.font = "16px Arial";
    // ctx.fillStyle = "#ffffff";
    // ctx.fillText("Illegal placement. Game Over.", 8, canvas.height-4);
}

function endGameWin(){
    isGameOver = 1;
    setStatus("Level completed!")
    // ctx.font = "16px Arial";
    // ctx.fillStyle = "#ffffff";
    // ctx.fillText("Level completed!", 8, canvas.height-4);
}



function finalizePiece(){

    // fix piece
    for(let t=curPiece.tmin; t<=curPiece.tmax; t++){
        let x = curPiece.x + t*curPiece.dx;
        let y = curPiece.y + t*curPiece.dy;
        fixed[y][x] = curPiece.glyphs[t-curPiece.tmin];
        whenFixed[y][x] = turnNum;
    }

    // if this is not the first piece, check if it's adjacent to another piece
    let ok = 0;
    let t = curPiece.tmin - 1
    let x = curPiece.x + t*curPiece.dx;
    let y = curPiece.y + t*curPiece.dy;
    if( x>=0 && x<numCols && y>=0 && y<numRows ){
        if( fixed[y][x] != " " ){
            ok = 1;
        }
    }
    t = curPiece.tmax + 1
    x = curPiece.x + t*curPiece.dx;
    y = curPiece.y + t*curPiece.dy;
    if( x>=0 && x<numCols && y>=0 && y<numRows ){
        if( fixed[y][x] != " " ){
            ok = 1;
        }
    }
    for(t=curPiece.tmin; t<=curPiece.tmax; t++){
        x = curPiece.x + t*curPiece.dx + curPiece.dy;
        y = curPiece.y + t*curPiece.dy + curPiece.dx;
        if( x>=0 && x<numCols && y>=0 && y<numRows ){
            if( fixed[y][x] != " " ){
                ok = 1;
            }
        }
        x = curPiece.x + t*curPiece.dx - curPiece.dy;
        y = curPiece.y + t*curPiece.dy - curPiece.dx;
        if( x>=0 && x<numCols && y>=0 && y<numRows ){
            if( fixed[y][x] != " " ){
                ok = 1;
            }
        }
    }
    if( turnNum>0 && !ok ){
        endGameLoss();
        return;
    }
    turnNum++;
    verifyWell();
}


function startNewPiece(){

    var l = wordlist[turnNum].length;
    curPiece.x = Math.floor(numCols/2);
    curPiece.y = Math.floor(1+l/2);
    curPiece.dx = 1;
    curPiece.dy = 0;
    curPiece.tmin = -Math.floor(l/2);
    curPiece.tmax = curPiece.tmin + l - 1;
    curPiece.glyphs = wordlist[turnNum];

    draw();

    // check if piece overlaps existing pieces
    for(var t=curPiece.tmin; t<=curPiece.tmax; t++){
        var x = curPiece.x + t*curPiece.dx;
        var y = curPiece.y + t*curPiece.dy;
        if( fixed[y][x] != " " ){
            endGameLoss();
            return;
        }
    }
}

function undoMove() {
    if( turnNum == 0 ){
        return;
    }
    turnNum--;
    isGameOver = 0;
    setStatus("");
    // remove the previous piece from the board
    for(let r=0; r<numRows; r++){
        for(let c=0; c<numCols; c++){
            if( whenFixed[r][c] >= turnNum ){
                whenFixed[r][c] = -1;
                fixed[r][c] = " ";
            }
        }
    }

    startNewPiece();

}


function moveLeft() {
    // check if piece can be moved left
    let ok = 1;
    for(let t=curPiece.tmin; t<=curPiece.tmax; t++){
        let x = curPiece.x + t*curPiece.dx - 1;
        let y = curPiece.y + t*curPiece.dy;
        if( x < 0  || fixed[y][x] != " " ){
            ok = 0;
        }
    }
    if(ok){
        curPiece.x--;
        draw();
    }
}

function moveRight() {
    // check if piece can be moved right
    let ok = 1;
    for(let t=curPiece.tmin; t<=curPiece.tmax; t++){
        let x = curPiece.x + t*curPiece.dx + 1;
        let y = curPiece.y + t*curPiece.dy;
        if( x >= numCols || fixed[y][x] != " " ){
            ok = 0;
        }
    }
    if(ok){
        curPiece.x++;
        draw();
    }
}

function rotate() {
    // check if piece can be rotated clockwise    new (dx,dy) = (-dy, dx)
    let ok = 1;
    for(let t=curPiece.tmin; t<=curPiece.tmax; t++){
        let y = curPiece.y + t*curPiece.dx;
        let x = curPiece.x - t*curPiece.dy;
        if( x < 0 || x >= numCols || y < 0 || y >= numRows || fixed[y][x] != " " ){
            ok = 0;
        }
    }
    if(ok){
        let tmp = curPiece.dx;
        curPiece.dx = -curPiece.dy;
        curPiece.dy = tmp;
        draw();
    }

}

function descend() {
    // check if piece can be moved down
    let ok = 1;
    for(let t=curPiece.tmin; t<=curPiece.tmax; t++){
        let x = curPiece.x + t*curPiece.dx;
        let y = curPiece.y + t*curPiece.dy + 1;
        if( y >= numRows || fixed[y][x] != " " ){
            ok = 0;
        }
    }
    if(ok){
        curPiece.y++;
        draw();
    }
    else{
        finalizePiece();
    }
}

function drop() {
    let ok = 1;
    while(ok){
        // check if piece can be moved down
        for(let t=curPiece.tmin; t<=curPiece.tmax; t++){
            let x = curPiece.x + t*curPiece.dx;
            let y = curPiece.y + t*curPiece.dy + 1;
            if( y >= numRows || fixed[y][x] != " " ){
                ok = 0;
            }
        }
        if(ok){
            curPiece.y++;
        }
    }
    draw();
    finalizePiece();
}

function buttonHandler(e) {
    if (blockInput){
        return;
    }
    e.preventDefault();
    switch ($(e.target).data().keypad) {
        case "Z":
            undoMove();
            break;
        case "R":
            startNewLevel(curLevel);
            break;
    }
    if ( isGameOver ) {
        return;
    }
    switch ($(e.target).data().keypad) {
        case "Up":
            rotate();
            break;
        case "Down":
            descend();
            break;
        case "Left":
            moveLeft();
            break;
        case "Right":
            moveRight()
            break;
        case "V":
            drop();
            break;
    }
}

function keyDownHandler(e) {
    if (blockInput || e.ctrlKey || e.altKey || e.metaKey || e.shiftKey ){
        return;
    }
    console.debug(e);
    if(e.key == "r" || e.key == "R") {
        startNewLevel(curLevel);
        return;
    }
    if(e.key == "z" || e.key == "Z") {
        undoMove();
        return;
    }
    if( isGameOver ){
        return;
    }
    if(e.key == "Right" || e.key == "ArrowRight") {
        moveRight();
        e.preventDefault();
    }
    else if(e.key == "Left" || e.key == "ArrowLeft") {
        moveLeft();
        e.preventDefault();
    }
    else if(e.key == "Up" || e.key == "ArrowUp") {
        rotate();
        e.preventDefault();
    }
    else if(e.key == "Down" || e.key == "ArrowDown") {
        descend();
        e.preventDefault();
    }
    else if(e.key == "v" || e.key == "V") {
        drop();
    }

}
