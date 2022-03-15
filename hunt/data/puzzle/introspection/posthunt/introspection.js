// NOTE TO SOLVERS: Inspecting this code is not needed to solve the puzzle and it may contain spoilers.
function onExpand(number){
    var row = $(`#description-${number}`)
    row.removeClass("collapsed-description")
    row.addClass("expanded-description")
    row.css("maxHeight",row[0].scrollHeight)
    var button = $(`#button-${number}`)
    button.html("▲")
    button.unbind("click")
    button.click(function() { onCollapse(number)})
}

function onCollapse(number){
    var row = $(`#description-${number}`)
    row.removeClass("expanded-description")
    row.addClass("collapsed-description")
    row.css("maxHeight",0)
    var button = $(`#button-${number}`)
    button.html("▼")
    button.unbind("click")
    button.click(function() { onExpand(number)})
}

const INTROSPECTION_VALUES = [
    "?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>,<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>J<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>,<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>J<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>,<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>J<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>B<wbr>?<wbr>B<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>,<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>B<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>J<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>B<wbr>?<wbr>?<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>B<wbr>Y<wbr>B<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>,<wbr>W<wbr>?<wbr>?<wbr>?<wbr>Y<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>B<wbr>Y<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>J<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>W<wbr>?<wbr>?<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>B<wbr>Y<wbr>?<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>W<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>W<wbr>V<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>?<wbr>?<wbr>?<wbr>U<wbr>?<wbr>?<wbr>?<wbr>D<wbr>B<wbr>Y<wbr>B<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>U<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>U<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>,<wbr>W<wbr>?<wbr>?<wbr>?<wbr>Y<wbr>?<wbr>U<wbr>?<wbr>F<wbr>?<wbr>?<wbr>?<wbr>B<wbr>Y<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>M<wbr>U<wbr>?<wbr>J<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>?<wbr>?<wbr>G<wbr>F<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>W<wbr>?<wbr>?<wbr>?<wbr>G<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>B<wbr>Y<wbr>?<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>P<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>W<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>?<wbr>M<wbr>?<wbr>D<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>W<wbr>V<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>S<wbr>S<wbr>?<wbr>U<wbr>?<wbr>?<wbr>?<wbr>D<wbr>B<wbr>Y<wbr>B<wbr>?<wbr>?<wbr>?<wbr>S<wbr>C<wbr>?<wbr>?<wbr>?<wbr>?<wbr>C<wbr>?<wbr>?<wbr>C<wbr>U<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>U<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>,<wbr>W<wbr>?<wbr>S<wbr>H<wbr>Y<wbr>?<wbr>U<wbr>?<wbr>F<wbr>?<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>?<wbr>?<wbr>C<wbr>H<wbr>?<wbr>?<wbr>H<wbr>?<wbr>?<wbr>?<wbr>?<wbr>S<wbr>?<wbr>?<wbr>?<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>C<wbr>?<wbr>?<wbr>S<wbr>S<wbr>?<wbr>S<wbr>?<wbr>H<wbr>S<wbr>P<wbr>?<wbr>?<wbr>M<wbr>U<wbr>?<wbr>J<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>?<wbr>C<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>D<wbr>?<wbr>H<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>?<wbr>?<wbr>G<wbr>F<wbr>?<wbr>?<wbr>D<wbr>?<wbr>H<wbr>?<wbr>S<wbr>?<wbr>C<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>H<wbr>?<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>?<wbr>?<wbr>C<wbr>?<wbr>H<wbr>?<wbr>W<wbr>?<wbr>?<wbr>?<wbr>G<wbr>P<wbr>?<wbr>?<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>H<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>P<wbr>H<wbr>?<wbr>?<wbr>?<wbr>C<wbr>W<wbr>H<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>S<wbr>M<wbr>?<wbr>D<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>W<wbr>V<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>S<wbr>S<wbr>?<wbr>U<wbr>L<wbr>?<wbr>?<wbr>D<wbr>B<wbr>Y<wbr>B<wbr>?<wbr>?<wbr>?<wbr>S<wbr>C<wbr>?<wbr>?<wbr>?<wbr>?<wbr>C<wbr>?<wbr>I<wbr>C<wbr>U<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>U<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>G<wbr>I<wbr>?<wbr>L<wbr>,<wbr>W<wbr>?<wbr>S<wbr>H<wbr>Y<wbr>?<wbr>U<wbr>?<wbr>F<wbr>?<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>?<wbr>?<wbr>C<wbr>H<wbr>?<wbr>L<wbr>H<wbr>?<wbr>L<wbr>L<wbr>I<wbr>S<wbr>I<wbr>?<wbr>?<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>C<wbr>?<wbr>?<wbr>S<wbr>S<wbr>I<wbr>S<wbr>?<wbr>H<wbr>S<wbr>P<wbr>?<wbr>?<wbr>M<wbr>U<wbr>?<wbr>J<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>I<wbr>C<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>M<wbr>?<wbr>I<wbr>?<wbr>?<wbr>?<wbr>L<wbr>L<wbr>?<wbr>?<wbr>D<wbr>?<wbr>H<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>I<wbr>?<wbr>G<wbr>F<wbr>?<wbr>L<wbr>D<wbr>?<wbr>H<wbr>?<wbr>S<wbr>?<wbr>C<wbr>?<wbr>?<wbr>?<wbr>I<wbr>?<wbr>?<wbr>H<wbr>?<wbr>?<wbr>L<wbr>D<wbr>?<wbr>?<wbr>?<wbr>I<wbr>C<wbr>?<wbr>H<wbr>?<wbr>W<wbr>?<wbr>?<wbr>?<wbr>G<wbr>P<wbr>L<wbr>?<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>H<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>P<wbr>H<wbr>?<wbr>?<wbr>I<wbr>C<wbr>W<wbr>H<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>L<wbr>I<wbr>?<wbr>?<wbr>L<wbr>?<wbr>G<wbr>I<wbr>?<wbr>L<wbr>S<wbr>M<wbr>?<wbr>D<wbr>?<wbr>?<wbr>F<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>W<wbr>V<wbr>I<wbr>G<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>S<wbr>S<wbr>?<wbr>U<wbr>L<wbr>?<wbr>?<wbr>D<wbr>B<wbr>Y<wbr>B<wbr>?<wbr>?<wbr>?<wbr>S<wbr>C<wbr>?<wbr>N<wbr>N<wbr>?<wbr>C<wbr>?<wbr>I<wbr>C<wbr>U<wbr>?<wbr>?<wbr>V<wbr>?<wbr>N<wbr>U<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>D<wbr>?<wbr>?<wbr>G<wbr>I<wbr>?<wbr>L<wbr>,<wbr>W<wbr>?<wbr>S<wbr>H<wbr>Y<wbr>?<wbr>U<wbr>?<wbr>F<wbr>?<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>?<wbr>?<wbr>C<wbr>H<wbr>?<wbr>L<wbr>H<wbr>?<wbr>L<wbr>L<wbr>I<wbr>S<wbr>I<wbr>?<wbr>?<wbr>N<wbr>M<wbr>?<wbr>N<wbr>?<wbr>N<wbr>?<wbr>?<wbr>C<wbr>?<wbr>?<wbr>S<wbr>S<wbr>I<wbr>S<wbr>?<wbr>H<wbr>S<wbr>P<wbr>?<wbr>N<wbr>M<wbr>U<wbr>N<wbr>J<wbr>?<wbr>M<wbr>?<wbr>?<wbr>?<wbr>I<wbr>C<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>M<wbr>?<wbr>I<wbr>N<wbr>?<wbr>?<wbr>L<wbr>L<wbr>?<wbr>N<wbr>D<wbr>?<wbr>H<wbr>?<wbr>G<wbr>?<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>I<wbr>?<wbr>G<wbr>F<wbr>?<wbr>L<wbr>D<wbr>?<wbr>H<wbr>?<wbr>S<wbr>?<wbr>C<wbr>?<wbr>?<wbr>?<wbr>I<wbr>N<wbr>?<wbr>H<wbr>?<wbr>?<wbr>L<wbr>D<wbr>?<wbr>?<wbr>?<wbr>I<wbr>C<wbr>?<wbr>H<wbr>?<wbr>W<wbr>?<wbr>?<wbr>N<wbr>G<wbr>P<wbr>L<wbr>?<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>H<wbr>?<wbr>?<wbr>V<wbr>?<wbr>?<wbr>P<wbr>H<wbr>?<wbr>N<wbr>I<wbr>C<wbr>W<wbr>H<wbr>?<wbr>?<wbr>?<wbr>?<wbr>?<wbr>L<wbr>I<wbr>?<wbr>?<wbr>L<wbr>?<wbr>G<wbr>I<wbr>?<wbr>L<wbr>S<wbr>M<wbr>?<wbr>D<wbr>?<wbr>?<wbr>F<wbr>?<wbr>N<wbr>D<wbr>N<wbr>?<wbr>W<wbr>V<wbr>I<wbr>G<wbr>?<wbr>N<wbr>?<wbr>?<wbr>?<wbr>",
    "?<wbr>S<wbr>S<wbr>?<wbr>U<wbr>L<wbr>?<wbr>?<wbr>D<wbr>B<wbr>Y<wbr>B<wbr>?<wbr>?<wbr>R<wbr>S<wbr>C<wbr>O<wbr>N<wbr>N<wbr>?<wbr>C<wbr>?<wbr>I<wbr>C<wbr>U<wbr>?<wbr>?<wbr>V<wbr>?<wbr>N<wbr>U<wbr>?<wbr>D<wbr>O<wbr>?<wbr>D<wbr>O<wbr>?<wbr>D<wbr>O<wbr>?<wbr>D<wbr>O<wbr>?<wbr>G<wbr>I<wbr>R<wbr>L<wbr>,<wbr>W<wbr>?<wbr>S<wbr>H<wbr>Y<wbr>O<wbr>U<wbr>R<wbr>F<wbr>?<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>R<wbr>?<wbr>C<wbr>H<wbr>?<wbr>L<wbr>H<wbr>O<wbr>L<wbr>L<wbr>I<wbr>S<wbr>I<wbr>R<wbr>O<wbr>N<wbr>M<wbr>?<wbr>N<wbr>O<wbr>N<wbr>?<wbr>?<wbr>C<wbr>R<wbr>O<wbr>S<wbr>S<wbr>I<wbr>S<wbr>?<wbr>H<wbr>S<wbr>P<wbr>?<wbr>N<wbr>M<wbr>U<wbr>N<wbr>J<wbr>O<wbr>M<wbr>R<wbr>?<wbr>?<wbr>I<wbr>C<wbr>?<wbr>?<wbr>?<wbr>R<wbr>O<wbr>M<wbr>?<wbr>I<wbr>N<wbr>R<wbr>O<wbr>L<wbr>L<wbr>?<wbr>N<wbr>D<wbr>?<wbr>H<wbr>?<wbr>G<wbr>R<wbr>?<wbr>?<wbr>?<wbr>Z<wbr>I<wbr>?<wbr>G<wbr>F<wbr>?<wbr>L<wbr>D<wbr>?<wbr>H<wbr>?<wbr>S<wbr>?<wbr>C<wbr>R<wbr>?<wbr>?<wbr>I<wbr>N<wbr>?<wbr>H<wbr>?<wbr>O<wbr>L<wbr>D<wbr>?<wbr>?<wbr>?<wbr>I<wbr>C<wbr>?<wbr>H<wbr>?<wbr>W<wbr>R<wbr>O<wbr>N<wbr>G<wbr>P<wbr>L<wbr>?<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>H<wbr>O<wbr>O<wbr>V<wbr>?<wbr>R<wbr>P<wbr>H<wbr>O<wbr>N<wbr>I<wbr>C<wbr>W<wbr>H<wbr>?<wbr>?<wbr>?<wbr>R<wbr>?<wbr>L<wbr>I<wbr>?<wbr>?<wbr>L<wbr>?<wbr>G<wbr>I<wbr>R<wbr>L<wbr>S<wbr>M<wbr>?<wbr>D<wbr>?<wbr>O<wbr>F<wbr>?<wbr>N<wbr>D<wbr>N<wbr>O<wbr>W<wbr>V<wbr>I<wbr>G<wbr>?<wbr>N<wbr>?<wbr>R<wbr>?<wbr>",
    "A<wbr>S<wbr>S<wbr>A<wbr>U<wbr>L<wbr>T<wbr>?<wbr>D<wbr>B<wbr>Y<wbr>B<wbr>?<wbr>A<wbr>R<wbr>S<wbr>C<wbr>O<wbr>N<wbr>N<wbr>?<wbr>C<wbr>T<wbr>I<wbr>C<wbr>U<wbr>T<wbr>A<wbr>V<wbr>?<wbr>N<wbr>U<wbr>?<wbr>D<wbr>O<wbr>T<wbr>D<wbr>O<wbr>T<wbr>D<wbr>O<wbr>T<wbr>D<wbr>O<wbr>T<wbr>G<wbr>I<wbr>R<wbr>L<wbr>,<wbr>W<wbr>A<wbr>S<wbr>H<wbr>Y<wbr>O<wbr>U<wbr>R<wbr>F<wbr>A<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>R<wbr>A<wbr>C<wbr>H<wbr>?<wbr>L<wbr>H<wbr>O<wbr>L<wbr>L<wbr>I<wbr>S<wbr>I<wbr>R<wbr>O<wbr>N<wbr>M<wbr>A<wbr>N<wbr>O<wbr>N<wbr>?<wbr>A<wbr>C<wbr>R<wbr>O<wbr>S<wbr>S<wbr>I<wbr>S<wbr>A<wbr>H<wbr>S<wbr>P<wbr>A<wbr>N<wbr>M<wbr>U<wbr>N<wbr>J<wbr>O<wbr>M<wbr>R<wbr>A<wbr>T<wbr>I<wbr>C<wbr>A<wbr>T<wbr>?<wbr>R<wbr>O<wbr>M<wbr>A<wbr>I<wbr>N<wbr>R<wbr>O<wbr>L<wbr>L<wbr>A<wbr>N<wbr>D<wbr>T<wbr>H<wbr>?<wbr>G<wbr>R<wbr>?<wbr>A<wbr>T<wbr>Z<wbr>I<wbr>?<wbr>G<wbr>F<wbr>?<wbr>L<wbr>D<wbr>T<wbr>H<wbr>?<wbr>S<wbr>?<wbr>C<wbr>R<wbr>?<wbr>T<wbr>I<wbr>N<wbr>T<wbr>H<wbr>?<wbr>O<wbr>L<wbr>D<wbr>A<wbr>T<wbr>T<wbr>I<wbr>C<wbr>T<wbr>H<wbr>?<wbr>W<wbr>R<wbr>O<wbr>N<wbr>G<wbr>P<wbr>L<wbr>A<wbr>C<wbr>?<wbr>B<wbr>Y<wbr>H<wbr>O<wbr>O<wbr>V<wbr>?<wbr>R<wbr>P<wbr>H<wbr>O<wbr>N<wbr>I<wbr>C<wbr>W<wbr>H<wbr>A<wbr>T<wbr>A<wbr>R<wbr>?<wbr>L<wbr>I<wbr>T<wbr>T<wbr>L<wbr>?<wbr>G<wbr>I<wbr>R<wbr>L<wbr>S<wbr>M<wbr>A<wbr>D<wbr>?<wbr>O<wbr>F<wbr>A<wbr>N<wbr>D<wbr>N<wbr>O<wbr>W<wbr>V<wbr>I<wbr>G<wbr>?<wbr>N<wbr>?<wbr>R<wbr>?<wbr>",
    "ASSAULTED BY BEARS CONNECTICUT AVENUE DOT DOT DOT DOT GIRL, WASH YOUR FACE BY RACHEL HOLLIS IRON MAN ONE ACROSS IS AHS PANMUNJOM RATICATE ROMAIN ROLLAND THE GREAT ZIEGFELD THE SECRET IN THE OLD ATTIC THE WRONG PLACE BY HOOVERPHONIC WHAT ARE LITTLE GIRLS MADE OF AND NOW VIGENERE",
]

function recomputeIntrospection(){

    var completedTaskCount = 0;
    for(let i = 1; i<= 13; i++){
        let iconSpan = $(`#icon-${i}`);
        if(iconSpan.attr("data-state") == '2'){
            completedTaskCount++;
        }
    }

    $("#introspection").html(INTROSPECTION_VALUES[completedTaskCount]);
}

const INTROSPECTION_TASKS = {
    "1":{
       "text":"WRITE STORY OF A GASHLYCRUMB TINY",
       "puzzle": "Bad Beginnings",
       "detailed_description":"<p>Write a Bulwer-Lytton-worthy first sentence of the worst possible novel of a Gashlycrumb Tiny.</p>\n",
    },
    "2":{
       "text":"MAKE A BEST PICTURE-WINNING MOVIE",
       "puzzle": "My Dinner With Big Boi",
       "detailed_description":"<p><a href=\"/puzzle/my-dinner-with-big-boi/task\">See this page for the full set of instructions.</a></p>"
    },
    "3":{
       "text":"PERFORM A EUROVISION SONG PASTICHE",
       "puzzle": "❤️ & ☮️",
       "detailed_description":"<p>Provide us with a video of your original Eurovision pastiche. It must follow these rules:</p>\n<ol type=\"1\">\n  <li>You must perform an original song</li>\n  <li>We need to see the person who is singing</li>\n  <li>No more than 6 people in the video</li>\n  <li>The song is between 1 and 3 minutes in length</li>\n  <li>You are free to choose what language you sing in</li>\n</ol>\n<p>The following videos should help spark your imagination: \n<a href=\"https://www.youtube.com/watch?v=Cv6tgnx6jTQ\" target=\"_blank\">Video 1</a>, \n<a href=\"https://www.youtube.com/watch?v=hfjHJneVonE\" target=\"_blank\">Video 2</a>, \n<a href=\"https://youtu.be/CTP17rWuUMo?t=195\" target=\"_blank\">Video 3</a></p>\n",
    },
    "4":{
       "text":"COME UP WITH ANOTHER ITEM FOR THIS YEAR\u2019S SCAVENGER HUNT LIST",
       "puzzle": "Book Reports",
       "detailed_description":"<p>Come up with another task. Your task should be based on a self-help book not included in the scavenger hunt, and should have two different options - one easier and one harder.</p>\n",
    },
    "5":{
       "text":"CATCH ONE OF YOUR TEAM MEMBERS IN A POKEBALL",
       "puzzle": "Lentalgram",
       "detailed_description":"<p>Provide a picture of one of your team members inside of a Pok\u00e9 Ball.</p>\n"
    },
    "6":{
       "text":"MAKE A STAR TREK EPISODE ABOUT HUNT",
       "puzzle": "Does Any Kid Still Do This Anymore?",
       "detailed_description":"<p>Provide us with the video of this episode. Your episode should be between 1 minute and 5 minutes long.</p>\n",
    },
    "7":{
       "text":"CREATE THE 2021 VERSE FOR \u201cWE DIDN\u2019T START THE FIRE\u201d",
       "puzzle": "Proof by Induction",
       "detailed_description":"<p>Create the 2021 verse for the song \u201cWe Didn\u2019t Start the Fire\u201d by Billy Joel. Your verse should be as long as those in the song (for example, \u201cHarry Truman\u201d to \u201cgoodbye\u201d is one verse). Provide both the lyrics to your verse and also a video of at least one of your members singing it. <a href=\"https://www.youtube.com/watch?v=j9HF26bUaf0\" target=\"_blank\">This karaoke version of WDSTF</a> may help.</p> \n"
    },
    "8":{
       "text":"CREATE YOUR TEAM\u2019S MONOPOLY BOARD",
       "puzzle": "First You GO",
       "detailed_description":"<p>Provide both a picture of the board and a text list of what all the spaces are. <b>Optional:</b> Share the history behind why your team chose the spaces you did.</p>\n",
    },
    "9":{
       "text":"DECLINE A NOBEL PRIZE FOR LITERATURE",
       "puzzle": "Everybody Must Get Rosetta Stoned",
       "detailed_description":"<p>Provide sufficient evidence that a member of your team has declined the Nobel Prize in Literature. If that evidence is convincing enough, we will not research further.</p>\n"
    },
    "10":{
       "text":"CAMEO IN AN MCU MOVIE",
       "puzzle": "This or That",
       "detailed_description":"<p>Provide sufficient evidence that at least one member of your team has cameoed in a Marvel Cinematic Universe movie. If that evidence is convincing enough, we will not research further.</p>\n",
    },
    "11":{
       "text":"MAKE A NEW 7X WITH MIT AT ONE ACROSS",
       "puzzle": "49ers",
       "detailed_description":"<p>Create your own 7x7 crossword following the standard rules for crossword grids (as listed <a href=\"https://www.7xwords.com/why.html\" target=\"_blank\">here</a>). The answer to 1-Across should be MIT, but you don't need to put 1-Across in the very far left of the top row. Find a working fill for your grid and write clues, and save your crossword in .puz format. If you want your puzzle to be a cryptic, or a vowelless, or something else funky like that, be our guest! Creativity is definitely encouraged.</p>\n<p>You can use any crossword construction software you might already have access to, or use a free web app like <a href=\"https://crosshare.org/construct\" target=\"_blank\">Crosshare</a> or <a href=\"https://viresh-ratnakar.github.io/exet.html\" target=\"_blank\">Exet</a> (which both allow export to .puz), or just make the crossword in a spreadsheet and turn it into a .puz file by creating a text file in <a href=\"https://www.litsoft.com/across/docs/AcrossTextFormat.pdf\" target=\"_blank\">Across Lite text format</a> and then converting it into a .puz file from there. Test your .puz file by opening it in a solving app (you can use <a href=\"https://www.crosswordnexus.com/solve/\" target=\"_blank\">Crossword Nexus</a> on the web if you don't have a solving app on your computer).</p>\n"
    },
    "12":{
       "text":"WRITE \u201cNANCY DREW SOLVES A PUZZLE\u201d",
       "puzzle": "Word Search of Babel",
       "detailed_description":"<p>Write this Nancy Drew fanfic in the form of a drabble (that is, exactly 100 words). You may use Google Docs or your favorite word processor to count the words.</p>\n",
    },
    "13":{
       "text":"SEND US A TELEGRAM",
       "puzzle": "Tech Support",
       "detailed_description":"<p>Interpret this any way you like. If you need information from us to send the telegram appropriately, please use the \u201cContact HQ\u201d link in the hunt menu. When you have sent the telegram, also use the submission link to let us know how you sent it so we can give you the appropriate credit.</p>\n"
    }
}

// data-state values for the tasks:
// 0: hidden, 1: revealed but not completed, 2: completed
function switchTaskStatus(taskNumber){
    var iconSpan = $(`#icon-${taskNumber}`);
    var state = iconSpan.attr("data-state");
    switch(state){
        case '0':
            iconSpan.attr("data-state","1");
            iconSpan.html("📨");
            iconSpan.attr("title","Click to accomplish the task.");
            $(`#task-${taskNumber}`).html(INTROSPECTION_TASKS[taskNumber].text);
            $(`#button-${taskNumber}`).prop('disabled', false);
            $(`#button-${taskNumber}`);
            break;
        case '1':
            iconSpan.attr("data-state","2");
            iconSpan.html("🏆");
            iconSpan.attr("title","Click to reset the task.");
            $(`#task-${taskNumber}`).html(INTROSPECTION_TASKS[taskNumber].text);
            $(`#button-${taskNumber}`).prop('disabled', false);
            recomputeIntrospection();
            break;
        case '2':
        default:
            iconSpan.attr("data-state","0");
            iconSpan.html("👁️");
            iconSpan.attr("title","Click to reveal the task.");
            $(`#task-${taskNumber}`).html(answerWillAppear(INTROSPECTION_TASKS[taskNumber].puzzle));
            $(`#button-${taskNumber}`).prop('disabled', true);
            onCollapse(taskNumber);
            recomputeIntrospection();
    }
}

function answerWillAppear(puzzleName){
    return `Answer for ${puzzleName} will appear here.`;
}

function renderTask(number, task){
    var icon = `<span id="icon-${number}" data-state="-1"></span>`;

    var row1 = `<tr class="task-row">
        <td class="task-id no-border">Task #${number}:</td>
        <td id="task-${number}" class="task-text no-border" height="41px"></td>
        <td class="task-icon no-border">${icon}</td>
        <td class="task-button no-border"><button id="button-${number}" class="expand-button" title="See task description">▼</button></td>
    </tr>`
    var row2 = `<tr class="description-row">
        <td colspan="4">
            <div id="description-${number}" class="collapsible">
                <div class="description">
                    <div>${task.detailed_description}</div>
                </div>
            </div>
        </td>
    </tr>`
    return row1 + row2
}

function populate(){
    var taskHtml = Object.entries(INTROSPECTION_TASKS).map(entry => renderTask(entry[0], entry[1])).join()
                $("#tasks").html(taskHtml);
    // Now bind onclicks for all the buttons and icons
    Object.entries(INTROSPECTION_TASKS).map(entry => {
        $(`#button-${entry[0]}`).click(function() {onExpand(entry[0])});
        $(`#icon-${entry[0]}`).click(function() {switchTaskStatus(entry[0])});
        switchTaskStatus(entry[0]);
    })
}

window.addEventListener('load', () => {
    populate();
});