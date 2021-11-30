    //
	// precargar la plantilla SELECT as�ncronamente
	//
var ITA = (function(){
	/*****************************/
	// el servidor web de avempacejs
	// y el servidor java  est�n en el mismo
	// servidor/dominio/ip
	//
	var isSAMEDOMAIN = true;
	/*****************************/
	var getPath = function(){
		if (typeof window !== "undefined"){
			var PATH = document.location;
			// NAVEGADOR - CLIENTE
			return PATH.href.substr(0, PATH.href.length - PATH.hash.length);
		} else {
			// ASP - SERVIDOR
			return Request.ServerVariables("HTTP_REFERER");
		}
	};
	var isSERVER = typeof document === "undefined" && typeof Request !== "undefined";
	var ORIGIN =      isSERVER ? "": document.location.origin;
	var PATH =        isSERVER ? "": document.location.pathname;
	var ORIGIN_PATH = isSERVER ? Request.ServerVariables("HTTP_REFERER") : (ORIGIN + PATH);
	var getORIGIN = function( origin){
    		return isSAMEDOMAIN ? ORIGIN : (origin || ORIGIN);
    	};

	var URL_SOLR = URL = ""; //"http://193.146.117.220:8880";

    // -------------------------------------------------------------------------
    // depende del valor de la COOKIE...fijado por un SELECT
    var getCookie = function(name){
            var cookies = document.cookie.split(';');
            for (let i = 0, c; i < cookies.length; i++) {
                c = cookies[i].replace(/^\s+/, '');
                if (c.startsWith(name + '='))
                    return decodeURIComponent(c.substring(name.length + 1).split('+').join(' '));
            }
            return null;
        };
    var WORKFLOW = getCookie('ita.ontologies') === "2" ? "documentsWebAragon" : "documents"
    // -------------------------------------------------------------------------

	var ___project = {
        "moriartysearch_opendata": {
            "id": "moriartysearch_opendata",
            "ajax":"asp/ita.proxy.asp",
            "solrUrl": URL_SOLR +"/web-server/rest/"+ WORKFLOW +"/",
            //"fq": ["anyo:["+ ((new Date()).getFullYear() - 3) +" TO "+ (new Date()).getFullYear() +"]"],
            endpoints: {
                "": {
                    url: getORIGIN() + PATH + "json/opendata.json",
                    method: "GET",
                    auth: "dHVyaXNtb2RlYXJhZ29uOkFyYWdvbjIwMTY=" // "turismodearagon:Aragon2016"
                },
                "*": {
                    url: getORIGIN(URL) + "/web-server/rest/search/",
                    auth: "dHVyaXNtb2RlYXJhZ29uOkFyYWdvbjIwMTY=" // "turismodearagon:Aragon2016"
                }
            },
            "urljson": "json/",
            "home": "opendata",
            "label": "Aragón Open Data Buscador"
        }
	};

	var obj = {
		config: {
			origin: ORIGIN,
			path: ORIGIN_PATH,
			projects: ___project
		}
	};
	return obj;
})();
