$(document).ready(function(){

    console.log('editor.js loaded.');

    var projectEditor = new SimpleMDE({
        autofocus: true,
        element: $("#editor")[0]
    });

//    // Check if editor needs text inserted
//    var contentToggle = document.getElementsByClassName('needs-content')[0];
//    if (contentToggle) {
//        projectEditor.value(contentToggle.value);
//    }


});