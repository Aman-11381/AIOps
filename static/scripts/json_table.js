$(document).ready(function() {
    $('#train-preview').DataTable( {
        "scrollX": true,
        "ajax": '../static/files/train.json',
        "columns": [
            { "data": "Level" },
            { "data": "Date and Time" },
            { "data": "Source" },
            { "data": "Event ID" },
            { "data": "Task Category" },
            { "data": "Description" }
        ]
    } );

    $('#test-preview').DataTable( {
        "scrollX": true,
        "ajax": '../static/files/test.json',
        "columns": [
            { "data": "Date and Time" },
            { "data": "Source" },
            { "data": "Event ID" },
            { "data": "Task Category" },
            { "data": "Description" }
        ]
    } );

    $('#result-preview').DataTable( {
        "scrollX": true,
        "ajax": '../static/files/result.json',
        "columns": [
            { "data": "Level"},
            { "data": "Date and Time" },
            { "data": "Source" },
            { "data": "Event ID" },
            { "data": "Task Category" },
            { "data": "Description" }
        ]
    } );
} );