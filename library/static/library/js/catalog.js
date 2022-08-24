

function wait(bool) {
    let el = $("#wait");
    if (bool) {
        el.show();
    }
    else {
        el.hide();;
    }
}

function send(msg, addr, action) {
    $.ajax({
        type: 'POST',
        url: addr,
        data: msg,
        success: action,
        error: function(xhr, str){
            console.log(str);
        }
    });
}

function library_post(options) {
    let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let msg = {csrfmiddlewaretoken: token};
    let addr, action;
    switch (options['action'])
    {
        case "pdf":
            addr = "/load_url";
            msg = Object.assign({}, msg, {'document': options['document']});
            action = function(data) {
                $('#content')[0].src = '/viewer/?file='+data["url"];
            };
            send(msg, addr, action);
            break;
        case "menu":
            addr = "/load_menu";
            msg = Object.assign({}, msg, {'periodic': options['periodic'], "search-string": options['search-string']});
            action = function(data) {
                if (!options['search-string'])  {
                    show_menu(data, true);
                }
                else {
                    show_menu(data, false);
                }
            };
            send(msg, addr, action);
            break;
        case "autocomplete":
            addr = "/load_autocomplete";
            msg = Object.assign({}, msg, {'periodic': options['periodic']});
            action = function(data) {
                init_autocomplete(data);
            };
            send(msg, addr, action);
            break;
        default:
            alert('Error');
            break;
    }
}

function menuItemClick(selectedId, selectedLi, $clickedLi) {
    if (selectedLi.hasClass("parent_li")) {
        selectedLi.find(' > span i').click();
    }
    else {
        $('#cover').hide();
        $('#content').show();
        library_post({
            'action': 'pdf',
            'document': selectedId
        });
    }
}

function show_menu(json, subload) {
    let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let config = {
        mandatorySelect: false,
        selectedIdElementName: 'nav-list',
        selectedItemId: 'nav-list',
        onSelect: menuItemClick,
    }

    if (subload) {
        let lazyconf = {
            lazyLoad: true,
            lazyRequestUrl: '/load_menu',
            lazyLoadMethod: 'POST',
            lazySendParameterName: 'value',
            additionalParams: {
            csrfmiddlewaretoken: token,
            periodic: $('#periodic').val()
            }
        }

        Object.assign(config, lazyconf);
    }

    $('#nav-list').jsonTree(json, config);
    wait(false);
}

function init_autocomplete(menuitems) {
    var availableTags = menuitems;

    function split( val ) {
        return val.split( /,\s*/ );
    }
    function extractLast( term ) {
        return split( term ).pop();
    }

    $( "#search-string" ).on( "keydown", function( event ) {
        if ( event.keyCode === $.ui.keyCode.TAB &&
        $( this ).autocomplete( "instance" ).menu.active ) {
            event.preventDefault();
        }
    })
    .autocomplete({
        minLength: 0,
        source: function( request, response ) {
            response( $.ui.autocomplete.filter(
            availableTags, extractLast( request.term ) ) );
        },
        focus: function() {
            return false;
        },
        select: function( event, ui ) {
            var terms = split( this.value );
            terms.pop();
            terms.push( ui.item.value );
            terms.push( "" );
            this.value = terms.join( ", " );
            return false;
        }
    });
}

$( document ).ready(function() {
    $('#search-string').val('');
    wait(true);
    $('form').submit(function(e) {
        $("#nav-list").empty();
        $("#nav-list").removeData();
        wait(true);
        library_post({
            'action': 'menu',
            'periodic': $('#periodic').val(),
            'search-string': $('#search-string').val()
        });
        $('#search-string').val('');
        return false;
    });
    library_post({
        'action': 'menu',
        'periodic': $('#periodic').val(),
        'str': $('#search-string').val()
    });
    library_post({
        'action': 'autocomplete',
        'periodic': $('#periodic').val()
    });
    $('#content').hide();
});



