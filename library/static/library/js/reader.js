$( document ).ready(function() {
    var elements = document.querySelectorAll(".menu-item");
    for (var i = 0; i < elements.length; i++) {
        elements[i].onclick = function(e){
            load_pdf(this.id);
        };
    }
});

function load_pdf(doc){
    let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let msg = { csrfmiddlewaretoken: token, document: doc };
    $.ajax({
        type: 'POST',
        url: "/load",
        data: msg,
        success: function(data) {
            $('#content')[0].src = '/viewer?file='+data["url"];
        },
        error:  function(xhr, str){
            alert(str);
        }
    });
}