import { findStudents } from './school-db.js';

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

function handleClick(event) {
    const studentName = $("#studentName").val();
    try {
        const rows = findStudents(studentName);
        if(rows.length == 0){
            setErrorMessage(`No students found named '${studentName}'.`, true);
        }else{
            setStudentData(rows);
        }
    }
    catch (error) {
        setErrorMessage(error.message,false);
    }

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