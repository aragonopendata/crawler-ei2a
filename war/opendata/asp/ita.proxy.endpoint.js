// obtener _endpoint...
var _projectsNames =  Object.keys(ITA.config.projects),
    _cookieProjectName = Request.Cookies("vmp.project").item,
    _projectName = _projectsNames.length === 1
      ? _projectsNames[0]  // caso de 1 solo proyecto en "ita.configuration.js"
      : _cookieProjectName !== ""
      ? _cookieProjectName // caso de cookie "vmp.project"
      : false,
    RQS = Request.QueryString.item,
    _endpoint,
    _endpoints,
    o = {}
    ;
if ( _projectName ){
    _endpoint =  ITA.config.projects[ _projectName ].endpoint;
    _endpoints = ITA.config.projects[ _projectName ].endpoints;
} else {
  Response.Write( "ni se envia cookie: vmp.project, ni ita.configuration.js tiene un unico ");
  Response.End();
}
;
if (!!_endpoints) {
    // caso "": url TOTAL
    // caso "xxx": url TOTAL
    // caso "*": url + RQS
    if (RQS in _endpoints) {
        _endpoint = _endpoints[RQS];
        RQS = "";
    } else {
        _endpoint = _endpoints["*"];
        // caso "~": contiene .... [ ""]: url + RQS
        // comprobar que existe CONTIENE
        if ("~" in _endpoints) {
            for (var key in _endpoints["~"])
                if (RQS.indexOf(key) !== -1)
                    _endpoint = _endpoints["~"][key];
        }
        // caso "^": empieza por .... [ ""]: url + RQS
        // comprobar que existe EMPIEZA por
        if ("^" in _endpoints) {
            for (var key in _endpoints["^"])
                if (RQS.indexOf(key) === 0)
                    _endpoint = _endpoints["^"][key];
        }
    }
}
if (!_endpoint) {
    Response.Write( "no existe 'endpoint' definido en 'ita.configuration.js'");
    Response.End();
}
o = {
    url:    _endpoint.url + (RQS || _endpoint.altQueryString || ""),
    method: _endpoint.method || "POST",
    auth:   _endpoint.auth || false,
    data:   Request.Form.item ,
    jsonp:  !!_endpoint.jsonp
};
try{
      Response.Write( ita.ajax(o) );
  } catch(e){
      Response.AddHeader("Content-Type","text/html;charset=ISO-8859-1") ;
      for (var i in e) Response.Write( i+" = "+ e[i] + "<br>");
      Response.Write('<p>');
      for (var j in o) Response.Write( j+" = "+ o[j] + "<br>");
      Response.Write( Request.Form.item );
  };

//caso particular bien hecho...
