const URLdomain = ''; //'http://193.146.117.220:8880/';
console.warn(document.location.origin);

(function(){
    $('.btn_popbar').on('click', e =>{
        e.target.nextElementSibling.classList.toggle('width0');
    })
})();
// Función para comprobar si un string es una URL
const isURL = str => (new RegExp('^https?://.+')).test(str) && !str.includes("ei2a/categorization");

/*
    Fill <panel> with <header> as top message and <list> as information,
    if <printKey> prints the keys of <list>
*/
const printPanel = (header, list, printKey) =>
        `<div class="list-group">
            ${ header ? `<div class="list-group-item active">${header}</div>`: ``}
            ${ Object.entries(list).map(([key, url]) =>
                Array.isArray(url) ?
                    `<div class='list-group-item'>
                        <strong>${key}</strong>
                        <div class='list-group'>
                            ${ url.map(item => `<div class='list-group-item'>${item}</div>`).join('') }
                        </div>
                    </div>`
                    :
                    `<div class='list-group-item'>
                        ${ printKey ? `<strong>${key}</strong><br/>` : ''}
                        ${
                            isURL(url) ?
                                (url.length > 55 ?  url.slice(0, 52) + "..." : url).link(url) :
                                url
                        }
                    </div>`
                ).join('')
            }
        </div>`
        ;

const data = {
    info: {},
    solrInfo: {},
    alertMaxNodes: false,
    numNodes: 20,
    question: '',
    urlQuestionWorkflow: `${URLdomain}web-server/rest/executeWorkFlowGet/5afbf8699194be00015eb2ee?save=false&wait=true&question=`,
    //---------------------------
    content: {
        answer: false,
        message: "",
        results: {}
    },
    warning: '',
    lang: 'es',
    translate: {
        "actualDate": {
            "es": "Última actualización"
        }
    }
};
const vue_numNodes = new Vue({
    el: document.getElementById('nodesSlider'),
    template: `
        <form class="form-horizontal">
            <div class="form-group form-group-sm">
                <label class="col-sm-4 control-label" for="numNodes">{{numNodes}} nodos máximo</label>
                <div class="col-sm-8">
                    <input id="numNodes" class="form-control input-sm" type="range" min="10" max="100"
                        v-model="numNodes"  />
                </div>
            </div>
        </form>
    `,
    data
});
const vue_info = new Vue({
    el: document.getElementById('info'),
    template:   `<div class="flex">
                    <div class="flex-fill" v-html="html" v-show="noHaySolrInfo"></div>
                </div>`,
    data,
    computed:{
        html(){ return Object.keys(this.info).length > 0 ?
                    printPanel(null, this.info, true) :
                    `<strong>No hay información que mostrar</strong>`
        },
        noHaySolrInfo(){ return !(this.solrInfo && Object.keys(this.solrInfo).length > 0) }
    }
});
const vue_solrInfo = new Vue({
    el: document.getElementById('solrInfo'),
    template: //`<div v-html="html"></div>`,
        `<div class="flex" v-show="haySolrInfo">
            <div class="flex-fill">
                <div class="clearfix" style="margin-bottom:1em">
                    <a :href="url" target="_blank" :title="url" v-show="url">
                        <i class="fa-2x" :class="url | extIcon"></i> ver {{url | extType}}
                    </a>
                    <div class="pull-right" style="margin:.5em 3.5em .5em 1em">
                        <small>{{"actualDate" | translate}}:</small> <i class="fa fa-calendar"></i> {{actualDate | date}}
                    </div>
                </div>
                <div class="clearfix" style="margin-bottom:1em">
                    <button class="btn btn-default btn-xs"
                        data-trigger="focus"
                        data-placement="bottom"
                        data-toggle="popover"
                        data-container="body"
                        data-html="true"
                        :data-content="personas | list"
                        :disabled="noHay(personas)">
                            <i class="fa fa-users"></i> {{personas | length}} {{"personas" | translate}}
                    </button>
                    &nbsp;
                    <button class="btn btn-default btn-xs"
                        data-trigger="focus"
                        data-placement="bottom"
                        data-toggle="popover"
                        data-container="body"
                        data-html="true"
                        :data-content="organizaciones | list"
                        :disabled="noHay(organizaciones)">
                            <i class="fa fa-university"></i> {{organizaciones | length}} {{"organizaciones" | translate}}
                    </button>
                    &nbsp;
                    <button class="btn btn-default btn-xs"
                        data-trigger="focus"
                        data-placement="bottom"
                        data-toggle="popover"
                        data-container="body"
                        data-html="true"
                        :data-content="localizaciones | list"
                        :disabled="noHay(localizaciones)">
                            <i class="fa fa-location-arrow"></i> {{localizaciones | length}} {{"localizaciones" | translate}}
                    </button>
                    &nbsp;
                    <button class="btn btn-default btn-xs"
                        data-trigger="focus"
                        data-placement="bottom"
                        data-toggle="popover"
                        data-container="body"
                        data-html="true"
                        :data-content="categorias | list"
                        :disabled="noHay(categorias)">
                            <i class="fa fa-location-arrow"></i> {{categorias | length}} {{"categorias" | translate}}
                    </button>
                </div>
                <div>
                    <p v-html="texto"></p>
                </div>
            </div>
        </div>`,
    data,
    computed:{
        html(){           return printPanel(null, this.solrInfo, true); },
        url(){            return this.info["Ruta o dirección que sirve para ubicar de manera precisa una web, subdominio o portal"] || "" },
        actualDate(){     return this.solrInfo.actualDate },
        personas(){       return this.solrInfo.personas },
        organizaciones(){ return this.solrInfo.organizaciones },
        localizaciones(){ return this.solrInfo.localizaciones},
        categorias(){     return this.solrInfo.categorias},
        texto(){          return this.info["Resumen  de la web, subdominio o portal del Gobierno de Aragón analizada y procesada"] || this.solrInfo.texto },
        haySolrInfo(){    return this.solrInfo && Object.keys(this.solrInfo).length > 0}
    },
    methods: {
        initPopover: function(){
            // ojo, no sé dónde ponerlo...
            // al acabar activar bootstrap popover...¿aunque no exista?
            const POPOVERS = this.$el.querySelectorAll('[data-toggle="popover"]');
            $(POPOVERS).popover();
        },
        noHay: function(value){  return Array.isArray(value) ? value.length === 0 : true}
    },
    filters: {
        date: function(value){ return value ? new Date(value).toLocaleString(data.lang).split(" ")[0] : '' },
        translate(txt){
            return  txt in data.translate ? data.translate[txt][data.lang] : txt
        },
        extType: function(value){
            const URL = value.toLowerCase();
            return URL.includes('.pdf') ? "PDF" :
                   URL.includes('.doc') ? "Ms WORD" :
                   "URL"
                   ;
        },
        extIcon: function(value){
            const URL = value.toLowerCase();
            return 'fa fa-'+
                   (URL.includes('.pdf') ? "file-pdf-o" :
                    URL.includes('.doc') ? "doc" :
                   "external-link")
                   ;
        },
        list:   function(value){ return Array.isArray(value) ? `<ol><li>${value.join('</li><li>')}</li><ol>` : '' },
        length: function(value){ return Array.isArray(value) ? value.length : 0 }
    },
    mounted(){ this.initPopover(); },
    updated(){ this.initPopover(); }
});
const vue_alertMaxNodes = new Vue({
    el: document.getElementById('alertMaximumNodes'),
    template: `<div v-html="mssg"></div>`,
    data,
    computed: {
        mssg(){
            return this.alertMaxNodes ?
                `<div class='alert alert-danger'>
                    <strong>Atención:</strong> Mostrando el máximo número de nodos
                </div>` :
                ''
        }
    }
});
const vue_question = new Vue({
    el: document.getElementById('question'),
    template: `<input type="text" class="question form-control" placeholder="Pregunte..."
                    v-model="question"
                    @keyup.enter="quepyRequest">`,
    data,
    computed: {
        url(){
            return this.urlQuestionWorkflow + encodeURIComponent(this.question);
        }
    },
    methods: {
        quepyRequest(){
            $.getJSON(this.url, ({results:{content}}) => {
                this.content = content;
            });
        }
    }
});
const vue_answer = new Vue({
    el: document.getElementById('answer'),
    data,
    template: `<div class="answer flex-fill transparent-to-events" v-html="html" @click.prevent="makeQuestion($event)"></div>`,
    computed:{
        html(){   return this.answer ? this.preguntaValida() : this.preguntaNoValida() },
        answer(){ return this.content.answer },
        message(){return this.content.message},
        results(){return this.content.results}
    },
    methods: {
        makeQuestion(e){
            if(e.target.matches('.question-sample')){
                // asignar pregunta
                this.question = e.target.textContent;
                // FOCUS en INPUT
                vue_question.$el.focus();
                // como si pulsara ENTER para buscar PREGUNTA
                vue_question.quepyRequest();
            }
        },
        preguntaNoValida(){
            const results = this.results || [];
            return Array.isArray(results) ?
                `<div class="list-group">
                    <div class="list-group-item">
                        <p><strong>${this.message}</strong></p>
                        <ul>
                            ${results.map(question => `
                             <li class="ellipsis">
                                <a class="question-sample">${question}</a>
                             </li>`).join('')}
                        </ul>
                    </div>
                </div>` :
                '';
        },
        preguntaValida(){
            return `<div class="list-group">
                        ${Object.keys(this.results).map(key =>
                            `<div class="list-group-item">
                                <p>${this.message.replace("{0}", `<strong>${key}</strong>`)}</p>
                                <ul>
                                    ${ Object.entries(this.results[key]).map(([key, [ url, node]]) => `
                                         <li class="ellipsis">
                                            <a onclick="changeGraph('${node}',0,0); return false;" title="${url}">
                                             ${url}
                                            </a>
                                         </li>`
                                     ).join('')}
                                </ul>
                            </div>`).join('')}
                    </div>`;
        }

    }
});
// INICIALIZACIÓN DE VARIABLES
var s = new sigma({
    settings: {
        autoRescale: true,
        sideMargin:50,
        rescaleIgnoreSize: true,
        //----------------------------
        minArrowSize: 6,
        animationsTime: 1000,
        font: 'monospace',
        defaultEdgeColor: "#5ea2ba",
        edgeColor: 'default', // source|target|default
        defaultNodeColor: "#ffffff",
        defaultEdgeType: "arrow",
        borderSize: 8, //0 px default
        defaultNodeBorderColor: 'rgba(255,200,0,0.8)',
        nodeHoverColor: 'default', // node|default

        minNodeSize: 0,
        maxNodeSize: 0,
    },
    renderer: {
        container: document.getElementById('graph-container'),
        type: 'canvas'
    }
});

// Activa las formas personalizadas, usada para poner iconos en los nodos
CustomShapes.init(s);
s.refresh();

// Para poder mover los nodos
// var dragListener = sigma.plugins.dragNodes(s, s.renderers[0]);
//
// // Al hacer click llamar a <changeGraph>
// dragListener.bind('drag', e => {
//     dragListener.unbind('dragend');
// });
//
// dragListener.bind('startdrag', ({data:{node}}) => {
//     if (node.fin_x !== 0 || node.fin_y !== 0) { // Si no es el nodo central
//         dragListener.bind('dragend', e =>{
//             console.warn('click');
//             changeGraph(node.nodeName, node["read_cam0:x"], node["read_cam0:y"]);
//         });
//         setTimeout(() =>{
//             dragListener.unbind('dragend');
//         }, 500);
//     }
// });
    s.bind('clickNode', ({data:{node}}) =>{
        changeGraph(node.nodeName, node["read_cam0:x"], node["read_cam0:y"]);
    })
    .bind('overNode', ({data:{node}}) =>{
        node.label = node.over_label;
        s.refresh();
    })
    .bind('outNode', ({data:{node}}) =>{
        node.label = node.ini_label;
        s.refresh();
    })
    ;




/*	Función principal, cambia el grafo dependiendo de <concept>
    <xAnimation> y <yAnimation> se usan para las animaciones
*/
const changeGraph = (concept, xAnimation, yAnimation) =>{
    // Petición para obtener el JSON
    const urlWorkflow = `${URLdomain}web-server/rest/executeWorkFlowGet/5afe7a599194be0001f5b21c?save=false&wait=true&concept=`;

    const $_json = $.getJSON(urlWorkflow + encodeURIComponent(concept) + "&nodes=" + encodeURIComponent(data.numNodes));

    const ANIMATE_COLLAPSE = true;
    const ANIMATE_EXPAND = true;

    const nowExpand = () =>
        $_json
            .then(({results:{content}}) => content)
            .then(graphExpand)
            ;

    const graphExpand = json =>{
        // me aseguro que la ventana con INFO está abierta Sí o Sí...
        const infoHidden = document.querySelector('.width0');
        if (infoHidden){
            infoHidden.classList.remove('width0');
        }

        // console.warn(json.graph.nodes, json);
        // Posiciones iniciales
        const nodeDefault  = {

        };
        // Valores por defecto de los nodos !TODO averiguar como moverlos al constructor
        json.graph.nodes.forEach(node =>{
            const label = node.label;
            Object.assign(node, nodeDefault, {
                    over_label: label,
                    ini_label: label,
                    label: label.length > 33 ? `${label.slice(0,30)}...` : label,

                    size: 20,
                    borderColor: "#5ea2ba",
                    type: "circle",

                    x: ANIMATE_EXPAND ? xAnimation : node.fin_x,
                    y: ANIMATE_EXPAND ? yAnimation : node.fin_y
                }
            );
        });

        data.info = json.info || {};
        // Rellenar info de solr
        data.solrInfo  = json.solrInfo || {};
        // Alerta de máximo de nodos alcanzados
        data.alertMaxNodes = json.alertMaximumNodes;

        // Reiniciar el grafo y volverlo a llenar
        s.graph.clear();
        s.graph.read(json.graph); // addNode(s) y addEdge(s)
        //CustomShapes.init(s);
        s.refresh();

        if (ANIMATE_EXPAND){
            sigma.plugins.animate(
                s,
                {
                    x: 'fin_x',
                    y: 'fin_y'
                },
                {
                    easing: 'cubicInOut',
                    duration: 1000,
                    onComplete: function() {
                        // do stuff here after animation is complete
                    }
                }
            );
        }
    };
    // data.info = `<strong>Cargando datos...</strong>`;
    // data.solrInfo  = {};
    // data.alertMaxNodes = false;
    Object.assign( data, {
        info: {},
        warning: `<strong>Cargando datos...</strong>`,
        solrInfo: {},
        alertMaxNodes: false
    });


    if (ANIMATE_COLLAPSE){
        s.graph.nodes().forEach(node => {
            node.collapse_x = xAnimation;
            node.collapse_y = yAnimation;
            // node.collapse_size = 10;
        });
        sigma.plugins.animate(
            s,
            {
                x:    'collapse_x',
                y:    'collapse_y',
                // size: 'collapse_size'
            },
            {
                easing: 'cubicInOut',
                duration: 250,
                onComplete: nowExpand
            }
        );
    } else {
        nowExpand();
    }
}

//changeGraph("http://opendata.aragon.es/def/ei2a#Entidad2241",0,0);
//changeGraph("http://opendata.aragon.es/def/ei2a#ORG11198",0,0);
changeGraph("http://opendata.aragon.es/def/ei2a#Entidad420", 0, 0);
//changeGraph("http://opendata.aragon.es/def/ei2a#WebPage22",0,0);
