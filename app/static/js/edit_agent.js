async function swapButton(button) {
  row = $(button.parentElement.parentElement);
  elements = $(row)
    .find("input, select")
    .toArray();
  if (
    $(row)
      .find("button.edit-btn i")
      .hasClass("fa-save")
  ) {
    if ($(button).hasClass("edit-btn")) {
      if ($(row).attr("changed") !== undefined) {
        $(row).removeAttr("changed");
        var elementJSON = new Object();
        for (i = 0; i < elements.length; i++) {
          $.extend(
            elementJSON,
            JSON.parse(
              '{ "' +
                $(elements[i]).attr("name") +
                '" : "' +
                $(elements[i]).val() +
                '"}'
            )
          );
        }
        console.log(elementJSON);
        $.ajax({
          type: "POST",
          url: location.href,
          data: JSON.stringify(elementJSON),
          contentType: "application/json; charset=utf-8",
          dataType: "json",
          success: function(data) {
            console.log(data);
          },
          error: function(errMsg) {
            console.log(errMsg.responseText);
            for (i = 0; i < elements.length; i++) {
              $(elements[i]).val(
                $(elements[i].parentElement).attr("cache_value")
              );
            }
            alertMsg = JSON.parse(errMsg.responseText);
            alert(alertMsg.response.replace("$$", "\n"));
          }
        });
      }
    } else {
      if ($(row).attr("changed") !== undefined) {
        ret = await showPrompt("There are unsaved changes", "Discard", "Keep");
        if (ret) {
          for (i = 0; i < elements.length; i++) {
            $(elements[i]).val(
              $(elements[i].parentElement).attr("cache_value")
            );
          }
          $(row).removeAttr("changed");
        } else return;
      }
    }
    $(row)
      .find("button.exit-btn")
      .addClass("invisible");
  } else {
    for (i = 0; i < elements.length; i++) {
      $(elements[i].parentElement).attr("cache_value", elements[i].value);
    }
    $(row)
      .find("button.exit-btn")
      .removeClass("invisible");
  }
  $(row)
    .find("input.inline-edit")
    .attr("readonly", function(_, attr) {
      return !attr;
    })
    .toggleClass("form-control")
    .toggleClass("form-control-plaintext");
  $(row)
    .find("select.inline-edit")
    .attr("disabled", function(_, attr) {
      return !attr;
    })
    .toggleClass("form-control")
    .toggleClass("form-control-plaintext");
  $(row)
    .find("button.edit-btn")
    .toggleClass("btn-success")
    .toggleClass("btn-primary");
  $(row)
    .find("button.edit-btn i")
    .toggleClass("fa-edit")
    .toggleClass("fa-save");
}

function createButton(button) {
  row = $(button.parentElement.parentElement);
  elements = $(row)
    .find("input, select")
    .toArray();
  var elementJSON = new Object();
  for (i = 0; i < elements.length; i++) {
    $.extend(
      elementJSON,
      JSON.parse(
        '{ "' +
          $(elements[i]).attr("name") +
          '" : "' +
          $(elements[i]).val() +
          '"}'
      )
    );
  }
  console.log(elementJSON);
  $.ajax({
    type: "PUT",
    url: location.href,
    data: JSON.stringify(elementJSON),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(data) {
      console.log(data);
      document.location.reload();
    },
    error: function(errMsg) {
      console.log(errMsg.responseText);
      for (i = 0; i < elements.length; i++) {
        $(elements[i]).val($(elements[i].parentElement).attr("cache_value"));
      }
      alertMsg = JSON.parse(errMsg.responseText);
      alert(alertMsg.response.replace("$$", "\n"));
    }
  });
}

async function deleteButton(button) {
  if (
    await showPrompt(
      "Are you sure you want to delete this job?",
      "Delete",
      "Cancel"
    )
  ) {
    row = $(button.parentElement.parentElement);
    elements = $(row)
      .find("input, select")
      .toArray();
    var elementJSON = new Object();
    for (i = 0; i < elements.length; i++) {
      $.extend(
        elementJSON,
        JSON.parse(
          '{ "' +
            $(elements[i]).attr("name") +
            '" : "' +
            $(elements[i]).val() +
            '"}'
        )
      );
    }
    console.log(elementJSON);
    $.ajax({
      type: "DELETE",
      url: location.href,
      data: JSON.stringify(elementJSON),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data) {
        console.log(data);
        document.location.reload();
      },
      error: function(errMsg) {
        console.log(errMsg.responseText);
      }
    });
  }
}

function showPrompt(msg, success, fail) {
  var p = new Promise(function(resolve, reject) {
    var dialog = $("<div/>", { class: "popup" })
      .append($("<p/>").html(msg))
      .append(
        $("<div/>", { class: "text-right" })
          .append(
            $("<button/>", { class: "btn btn-danger discard-btn" })
              .html(success)
              .on("click", function() {
                $(".overlay").remove();
                resolve(true);
              })
          )
          .append(
            $("<button/>", { class: "btn btn-success keep-btn" })
              .html(fail)
              .on("click", function() {
                $(".overlay").remove();
                resolve(false);
              })
          )
      );
    var overlay = $("<div/>", { class: "overlay" }).append(dialog);

    $("body").append(overlay);
  });
  return p;
}

$(document).ready(function() {
  $("input, select").on("change keyup keydown", function(e) {
    $(e.currentTarget.parentElement.parentElement).attr("changed", "");
  });
});

async function manualRequestButton(button, requestType) {
  if (
    await showPrompt("Send manual request to end point?", "Confirm", "Cancel")
  ) {
    row = $(button.parentElement.parentElement);
    elements = $(row)
      .find("input, select")
      .toArray();
    var elementJSON = new Object();
    for (i = 0; i < elements.length; i++) {
      $.extend(
        elementJSON,
        JSON.parse(
          '{ "' +
            $(elements[i]).attr("name") +
            '" : "' +
            $(elements[i]).val() +
            '"}'
        )
      );
    }
    $.extend(
      elementJSON,
      JSON.parse('{ "requestType" : "' + requestType + '"}')
    );
    console.log(elementJSON);
    $.ajax({
      type: "POST",
      url: location.href,
      data: JSON.stringify(elementJSON),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data) {
        console.log(data);
        document.location.reload();
      },
      error: function(errMsg) {
        console.log(errMsg.responseText);
      }
    });
  }
}
