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

const actualPerformQuery = function(studentName) {
    var url = window.puzzleUrl + "findstudents/?name=" + studentName;
    var csrftoken = getCookie("csrftoken");
    return fetch(url, {
            method: 'POST',
            headers: {"X-CSRFToken": csrftoken},
        })
        .then(response => {
            if (response.ok) {
                return response.json().catch(error => {
                    throw Error("Something went very wrong! Please contact Hunt Control with steps to reproduce this error.");
                });
            } else {
                return response.text().then(message => {
                    throw Error(message);
                });
            }
        })
}

function handleClick(event) {
    var studentName = $("#studentName").val();
    const performQuery = window.stubPerformQuery || actualPerformQuery;
    performQuery(studentName)
        .then(data => {
            if(data.rows.length == 0){
                setErrorMessage(`No students found named '${studentName}'.`, true);
            }else{
                setStudentData(data.rows);
            }
        })
        .catch(error => {
            setErrorMessage(error.message, false);
        });
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
