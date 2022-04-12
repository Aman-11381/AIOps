$(document).ready( function () {
    $('.preview-table').DataTable({
        "scrollX": true
    } );
} );

$('div.table-wrapper table').addClass('table table-bordered cell-border hover preview-table');

