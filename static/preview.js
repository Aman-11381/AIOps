$(document).ready( function () {
    $('.preview-table').DataTable({
        "scrollX": true
    } );
} );

$('div.table-wrapper table').addClass('table table-striped table-bordered preview-table');