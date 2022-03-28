function onError(error){
    console.log(error)
    $("#introspection").html("<span style=\"color:red\">Something went wrong. Please refresh. If error persists, contact Hunt Control with steps to reproduce the error.</>");
}

function onExpand(number){
    var row = $(`#task-${number}`)
    row.removeClass("collapsed-description")
    row.css('display', 'block');
    row.css("maxHeight",row[0].scrollHeight)
    var button = $(`#button-${number}`)
    button.html("▲")
    button.unbind("click")
    button.click(function() { onCollapse(number)})
}

function onCollapse(number){
    var row = $(`#task-${number}`)
    row.addClass("collapsed-description")
    row.one('transitionend', () => {
        if (row.hasClass('collapsed-description')) {
            row.css('display', 'none');
        }
    });
    row.css("maxHeight",0)
    var button = $(`#button-${number}`)
    button.html("▼")
    button.unbind("click")
    button.click(function() { onExpand(number)})
}

function renderTask(number, task){
    var status_div = !task.submitted ? "" :
        task.autopilot ? `<div class="task-notice">During the hunt, you would have needed to submit this item.</div>`
            : task.accomplished ? `<div class="task-notice complete">🏆 Complete - your submission was accepted!</div>` :
            `<div class="task-notice">📨 We’ve received your submission.</div>`
    var submission_div = "submission_instruction" in task ? `<div><p>${task.submission_instruction}</p></div>` : ""

    var icon = task.accomplished
            ? `<span title="Task accomplished">🏆</span>`
            : task.submitted ? `<span title="Task submitted">📨</span>` : ""

    var row1 = `<tr class="task-row">
        <td class="task-id no-border">Task #${number}:</td>
        <td class="task-text no-border">${task.text}</td>
        <td class="task-icon no-border">${icon}</td>
        <td class="task-button no-border"><button id="button-${number}" class="expand-button">▼</button></td>
    </tr>`
    var row2 = `<tr class="description-row">
        <td colspan="4">
            <div id="task-${number}" class="collapsible" style="display: none;">
                <div class="description">
                    <div>${task.detailed_description}</div>
                    ${submission_div}
                    ${status_div}
                </div>
            </div>
        </td>
    </tr>`
    return row1 + row2
}

function populate(){
    var url = window.puzzleUrl + "data/"
    var csrftoken = getCookie("csrftoken");
    fetch(url, {
            method: 'POST',
            headers: {"X-CSRFToken": csrftoken},
        })
    .then( response => {
        if (response.ok) {
            response.json().then(data => {
                $("#introspection").html(data.introspection)
                var taskHtml = Object.entries(data.tasks).map(entry => renderTask(entry[0], entry[1])).join()
                $("#tasks").html(taskHtml)
                // Now bind onclicks for all the buttons
                Object.entries(data.tasks).map(entry => {
                    $(`#button-${entry[0]}`).click(function() { onExpand(entry[0])})
                })
            })
            .catch(error =>{
                onError(error);
            })
        }
        else {
            onError("Unexpected response code " + response.status);
        }
    })
    .catch(error =>{
        onError(error);
    })
}

window.addEventListener('load', () => {
    populate()
});
