
var myState = {
    pdf: null,
    currentPage: 1,
    zoom: 1
}



function render() {
    myState.pdf.getPage(myState.currentPage).then((page) => {
        var canvas = document.getElementById("canvas_pdf");
        var ctx = canvas.getContext('2d');
        var viewport = page.getViewport(myState.zoom);
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        page.render({
            canvasContext: ctx,
            viewport: viewport
        });
    });
}