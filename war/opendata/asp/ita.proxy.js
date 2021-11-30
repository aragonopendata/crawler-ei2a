// De https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/keys
if (!Object.keys) {
  Object.keys = (function() {
    'use strict';
    var hasOwnProperty = Object.prototype.hasOwnProperty,
        hasDontEnumBug = !({ toString: null }).propertyIsEnumerable('toString'),
        dontEnums = [
          'toString',
          'toLocaleString',
          'valueOf',
          'hasOwnProperty',
          'isPrototypeOf',
          'propertyIsEnumerable',
          'constructor'
        ],
        dontEnumsLength = dontEnums.length;

    return function(obj) {
      if (typeof obj !== 'object' && (typeof obj !== 'function' || obj === null)) {
        throw new TypeError('Object.keys called on non-object');
      }

      var result = [], prop, i;

      for (prop in obj) {
        if (hasOwnProperty.call(obj, prop)) {
          result.push(prop);
        }
      }

      if (hasDontEnumBug) {
        for (i = 0; i < dontEnumsLength; i++) {
          if (hasOwnProperty.call(obj, dontEnums[i])) {
            result.push(dontEnums[i]);
          }
        }
      }
      return result;
    };
  }());
};

  var ita = {};

  ita.xmlhttp = function () {
      var progIDs = [
          "Msxml2.ServerXMLHTTP.6.0",
          "Msxml2.ServerXMLHTTP.5.0",
          "Msxml2.ServerXMLHTTP.4.0",
          "Msxml2.ServerXMLHTTP.3.0",
          "Msxml2.ServerXMLHTTP",
          "Microsoft.ServerXMLHTTP",
          "Msxml2.XMLHTTP.6.0",
          "Msxml2.XMLHTTP.5.0",
          "Msxml2.XMLHTTP.4.0",
          "Msxml2.XMLHTTP.3.0",
          "Msxml2.XMLHTTP",
          "Microsoft.XMLHTTP"
      ];
      for (var i = 0; i < progIDs.length; i++) {
          try { return new ActiveXObject(progIDs[i]); } // Server.CreateObject
          catch (e) {
              if (i == progIDs.length - 1) throw e;
          }
      }
  };
  /*
   * method: "GET" | "POST"
   * url:
   * data: Request.Form.item || Request.QueryString.item
   * contentType: "application/json" | "text/html"
   */
  ita["ajax"] = function(o){ // url, method, auth, data SIEMPRE DEFINIDOS
    var METHOD = o.method,
        AUTH =   o.auth,
        DATA =   o.data,
        URL =    o.url,
        //_txt = [],
        // _contentType = o.contentType || "application/json"
        XMLHTTP = ita.xmlhttp(),
        RSV_C2S = function( arrRSV ){
          for (var i = 0, RSV; i < arrRSV.length; i++){
            RSV = Request.ServerVariables( arrRSV[i] ).item;
            if ( RSV.length )
              XMLHTTP.setRequestHeader( "_"+ arrRSV[i] +"_", RSV );
          }
        },
        HEADER_C2S = function(){
          COOKIES_C2S();
          // siempre sube al servidor como un FORM sea GET o POST
          XMLHTTP.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
          // custom headers
          RSV_C2S(["AUTH_USER", "AUTH_PASSWORD", "LOGON_USER", "REMOTE_USER", "REMOTE_HOST"]);
          // authorization
          if (AUTH) XMLHTTP.setRequestHeader("Authorization", "Basic "+ AUTH);
        },
        HEADER_S2C = function(){
          COOKIES_S2C();
          // el servidor siempre me devuelve JSON
          Response.ContentType = "application/json;charset=ISO-8859-1";
          // sin proxy
          Response.AddHeader('_sinproxy_', '['+ METHOD +'] '+ URL );
        },
        COOKIES_C2S = function(){
          for (var i = 1; i <= Request.Cookies.Count; i++)
            XMLHTTP.setRequestHeader("Cookie", Request.Cookies.Key(i) +"="+ Request.Cookies.Item(i) );
        },
        COOKIES_S2C = function(){
          // caso de recibir del servidor cookies: SET-COOKIE
          var cookies =  XMLHTTP.getResponseHeader("Set-Cookie"),
              arrCookies = cookies ? cookies.split(";") : [],
              cookie
              ;
          for (var i = 0; i < arrCookies.length; i++){
            cookie = arrCookies[i].split("=");
            Response.Cookies( cookie[0] ) = cookie[1];
          }
        }
        ;
    // -- CAMBIA LOS LIMITES DE TIEMPOS DE ajax (MILISEGUNDOS)
    var lResolve = 24 * 60 * 1000;  // defecto infinito
    var lConnect =  10 * 60 * 1000;  // defecto 60 sg
    var lSend =     10 * 60 * 1000;  // defecto 30 sg
    var lReceive =  10 * 60 * 1000;  // defecto 30vsg
    XMLHTTP.setTimeouts(lResolve, lConnect, lSend, lReceive);
    //--

    if (METHOD === "GET" && !!DATA){
      URL += URL.indexOf("?") === -1 ? "?" + DATA : DATA;
    }
    XMLHTTP.open( METHOD, URL, false);
    HEADER_C2S();
    METHOD === "GET" ?
      XMLHTTP.send() :
      XMLHTTP.send( DATA )
      ;
    HEADER_S2C();
    return XMLHTTP.responseText;

/*
  Response.ContentType = "text/html";
  _txt.push( XMLHTTP.getAllResponseHeaders().split("\n").join("<br>") );
  _txt.push( XMLHTTP.getResponseHeader("Set-Cookie") );
  return  _txt.join("<p>");
*/

  };
