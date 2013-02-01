pngypacky.py
============

Packs javascript and assets into a single self extracting file using the techinque described in http://daeken.com/superpacking-js-demos  

Usage
-----

```
superpack.py directory-or-file directory-or-file...
```

Any .js files explicitly listed on the command line will be eval()ed on load, in the order in which they are mentioned on the command line, in global scope.  

All files will be provided as base64 encoded data: URIs in the PackedFiles global array, indexed by their path.  

A global function is also provided for decoding data: URIs:

```
DecodeFile(base64_encoded_data_uri)
```

e.g.

```
superpack.py jquery.js code.js style.css image_directory > result.html
```

Now when result.html is opened in a browser, code.js can do things like

```
$('head').append( $('<link rel="stylesheet" type="text/css" />').attr('href',PackedFiles["style.css"]) );
$('#myimage').attr('src',PackedFiles["image_directory/my_image.png"]) );
```
