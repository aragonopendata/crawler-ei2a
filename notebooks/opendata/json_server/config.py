NODE_TYPE = [
    {
        "identifier": "http://www.w3.org/ns/locn#Location",
        "name": "http://opendata.aragon.es/def/ei2a#geographicName",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#geographicName"
        ],
        "incomingEdges":[
            "http://opendata.aragon.es/def/ei2a#citationOnEntity"
        ],
        "outgoingEdges":[
        ],
        "image": "img/location.png"
    },
    {
        "identifier": "http://www.w3.org/ns/org#Role",
        "name": "http://opendata.aragon.es/def/ei2a#roleName",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#roleName"
        ],
        "incomingEdges":[
            "http://www.w3.org/ns/org#role",
            "http://opendata.aragon.es/def/ei2a#citationOnEntity"
        ],
        "outgoingEdges":[
        ],
        "image": "img/rol.png"
    },
    {
        "identifier": "http://opendata.aragon.es/def/ei2a#WebPage",
        "name": "http://opendata.aragon.es/def/ei2a#URL",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#summary",
            "http://opendata.aragon.es/def/ei2a#URL"
        ],
        "incomingEdges":[
            "http://opendata.aragon.es/def/ei2a#citationOnWebPage",
            "http://opendata.aragon.es/def/ei2a#similarityOnWebPages",
            "http://opendata.aragon.es/def/ei2a#hasWebPage"
        ],
        "outgoingEdges":[
            "http://opendata.aragon.es/def/ei2a#webPageCategorization"
        ],
        "image": "img/webPage.png"
    },
    {
        "identifier": "http://opendata.aragon.es/def/ei2a/categorization#",
        "name": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        "properties": [
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        ],
        "incomingEdges": [
            "http://opendata.aragon.es/def/ei2a#webPageCategorization",
            "http://opendata.aragon.es/def/ei2a#similarityOnCategory"
        ],
        "outgoingEdges": [
        ],
        "image": "img/category.png"
    },
    {
        "identifier": "http://opendata.aragon.es/def/ei2a#Citation",
        "rawName": "Citación",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#citationPhrase",
            "http://opendata.aragon.es/def/ei2a#citationDate"
        ],
        "incomingEdges": [
        ],
        "outgoingEdges": [
            "http://opendata.aragon.es/def/ei2a#citationOnWebPage",
            "http://opendata.aragon.es/def/ei2a#citationOnEntity"
        ],
        "image": "img/citation.png"
    },
    {
        "identifier": "http://www.w3.org/ns/org#Organization",
        "name": "http://opendata.aragon.es/def/ei2a#organizationName",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#organizationName",
            "http://www.w3.org/ns/org#identifier",
            "http://opendata.aragon.es/def/ei2a#SIUCode"
        ],
        "incomingEdges": [
            "http://www.w3.org/ns/org#organization",
            "http://opendata.aragon.es/def/ei2a#citationOnEntity",
            "http://www.w3.org/ns/org#subOrganizationOf	"
        ],
        "outgoingEdges": [
            "http://www.w3.org/ns/org#subOrganizationOf",
            "http://www.w3.org/ns/org#hasPrimarySite",
            "http://opendata.aragon.es/def/ei2a#hasWebPage"
        ],
        "image": "img/organization.png"
    },
    {
        "identifier": "http://www.w3.org/ns/org#Membership",
        "rawName": "Membresía",
        "properties": [
        ],
        "incomingEdges": [
        ],
        "outgoingEdges": [
            "http://www.w3.org/ns/org#member",
            "http://www.w3.org/ns/org#organization",
            "http://www.w3.org/ns/org#role",
            "http://www.w3.org/ns/org#memberDuring"
        ],
        "image": "img/membresia.svg"
    },
    {
        "identifier": "http://www.w3.org/ns/person#Person",
        "name": "http://opendata.aragon.es/def/ei2a#fullName",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#fullName",
            "http://www.w3.org/ns/org#identifier"
        ],
        "incomingEdges": [
            "http://www.w3.org/ns/org#member",
            "http://opendata.aragon.es/def/ei2a#citationOnEntity"
        ],
        "outgoingEdges": [
        ],
        "image": "img/person.png"
    },
    {
        "identifier": "http://www.w3.org/2006/time#Interval",
        "rawName": "Intervalo de tiempo",
        "properties": [
        ],
        "incomingEdges": [
            "http://www.w3.org/ns/org#memberDuring"
        ],
        "outgoingEdges": [
            "http://www.w3.org/2006/time#hasBeginning",
            "http://www.w3.org/2006/time#hasEnd"
        ],
        "image": "img/time.png"
    },
    {
        "identifier": "http://www.w3.org/2006/time#Instant",
        "name": "http://www.w3.org/2006/time#inXSDDateTimeStamp",
        "properties": [
            "http://www.w3.org/2006/time#inXSDDateTimeStamp"
        ],
        "incomingEdges": [
            "http://www.w3.org/2006/time#hasEnd",
            "http://www.w3.org/2006/time#hasBeginning"
        ],
        "outgoingEdges": [
        ],
        "image": "img/time.png"
    },
    {
        "identifier": "http://www.w3.org/ns/org#Site",
        "rawName": "Sede",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#phone"
        ],
        "incomingEdges": [
            "http://www.w3.org/ns/org#hasPrimarySite"
        ],
        "outgoingEdges": [
            "http://www.w3.org/ns/org#siteAddress"
        ],
        "image": "img/location.png"
    },
    {
        "identifier": "http://www.w3.org/ns/locn#Address",
        "name": "http://www.w3.org/ns/locn#fullAddress",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#adminUnitL3",
            "http://opendata.aragon.es/def/ei2a#adminUnitL6",
            "http://www.w3.org/ns/locn#fullAddress",
            "http://www.w3.org/ns/locn#postCode"
        ],
        "incomingEdges": [
            "http://www.w3.org/ns/org#siteAddress"
        ],
        "outgoingEdges": [
        ],
        "image": "img/location.png"
    },
    {
        "identifier": "http://opendata.aragon.es/def/ei2a#Similarity",
        "rawName": "Similaridad",
        "properties": [
            "http://opendata.aragon.es/def/ei2a#cosineDistance",
            "http://opendata.aragon.es/def/ei2a#pearsonCorrelation"
        ],
        "incomingEdges": [
        ],
        "outgoingEdges": [
            "http://opendata.aragon.es/def/ei2a#similarityOnWebPages",
            "http://opendata.aragon.es/def/ei2a#similarityOnCategory"
        ],
        "image": "img/similarity.png"
    }
]
