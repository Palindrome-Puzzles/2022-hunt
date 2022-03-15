function setErrorMessage(message, noStudentsFound){
    $("#studentData").html("");
    if(noStudentsFound){
        $("#errorMessage").removeClass("error");
    } else {
        $("#errorMessage").addClass("error");
    }
    $("#errorMessage").html("<p>"+message+"</p>");
}

function setStudentData(dataRows){
    $("#errorMessage").html("");
    var tableRows = dataRows.map(row => `<tr><td>${row[0]}</td> <td>${row[1]}</td></tr>`).join()
    $("#studentData").html(tableRows);
}

function onRealError(){
    setErrorMessage("Something went very wrong! Please contact Hunt Control with steps to reproduce this error.", false);
}

function handleClick(event) {
    var studentName = $("#studentName").val();
    var url = window.puzzleUrl + "findstudents/?name=" + studentName;
    var csrftoken = getCookie("csrftoken");
    fetch(url, {
            method: 'POST',
            headers: {"X-CSRFToken": csrftoken},
        })
    .then( response => {
        if (response.ok) {
            response.json().then(data => {
                if(data.rows.length == 0){
                    setErrorMessage(`No students found named '${studentName}'.`, true);
                }else{
                    setStudentData(data.rows);
                }
            })
            .catch(error =>{
                onRealError();
            })
        }
        else {
            response.text().then(text => { setErrorMessage(text,false);});
        }
    })
    .catch(error =>{
        onRealError(error);
    })

    event.preventDefault();
}

function handleKeyUp(event) {
    if(event.key === 'Enter'){
        handleClick(event)
    }
}

$("#searchButton").keypress(handleKeyUp);
$("#searchButton").click(handleClick);
$("#studentName").keypress(handleKeyUp);