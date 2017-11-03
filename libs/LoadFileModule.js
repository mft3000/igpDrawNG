// ver 0.1

// NextUI igpDrawNGv2.py reader 
// Francesco Marangione (fmarangi@cisco.com) 

(function addButtonsToLoad() {
	
	// show input forms to select and load .js file
	
	if (typeof topologyData == 'undefined') {

		var fileref = document.createElement('input');
		fileref.setAttribute("type", "file");
		fileref.setAttribute("id", "thefile");
		fileref.setAttribute("accept", ".js");
		fileref.setAttribute("onchange", "alertFilename()");
		document.getElementsByTagName('form')[0].appendChild(fileref);

	}
})();

function loadjsfile(filename, filetype, where){
	
	
	if (filetype == "js"){
		var fileref = document.createElement('script');
		fileref.setAttribute("src", filename);
		fileref.setAttribute("type", "text/javascript");
	}
	if (typeof fileref != 'undefined')
		document.getElementsByTagName(where)[0].appendChild(fileref);
}

function alertFilename() {
	
	var thefile = document.getElementById('thefile');
	var pieces = thefile.value.split('\\');
	var db_file_name = pieces[pieces.length-1];
		
	loadjsfile(db_file_name, "js", "body");	
	
	loadjsfile("app/base/base.js", "js", "body");
	
}