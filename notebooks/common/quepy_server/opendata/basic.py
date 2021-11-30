# coding: utf-8

from refo import Group, Plus, Question
from quepy.parsing import Lemma, Pos, QuestionTemplate, Token, Particle, \
                          Lemmas, Literal
from quepy.dsl import HasKeyword, IsRelatedTo, HasType
from dsl import *

det = Pos("DT") | Lemma("del") | Pos("IN") # de del el la...
entity = Group(Plus((Pos("NNP") | Pos("NN") | Pos("NNS")) + Question(Plus(Pos("JJ") | Pos("CC") | det))), "target")  # Entidades con determinantes intercalados
donde = (Lemma("donde") | Lemma("dónde"))
que = (Lemma("que") | Lemma("qué"))
cuando = (Lemma("cuando") | Lemma("cuándo"))
cual = (Lemma("cual") | Lemma("cuál"))

# Citaciones de una entidad
# Ejemplo: ¿Dónde se ha citado Sanidad?
class Citations(QuestionTemplate):
    target = Question(Pos("DT")) + entity
    verbs = Lemma("citar")
    regex = Question(Pos(".")) + donde + Question(Pos("PRP")) + Question(Pos("MD")) + Question(Lemma("ser")) + verbs + target + Question(Pos("."))

    def interpret(self, match):
        target = match.target.tokens
        entity = GetEntityFromName(target) + IsInstance()
        citation = GetCitationFromEntity(entity)
        webPage = GetWebPageFromCitationTarget(citation)
        url = GetURLFromWebPageTarget(webPage)
        return url, (target, "{0} ha sido citado/a en:")

# Organización donde trabaja una persona
# Ejemplo: ¿Dónde trabaja Ángel Fernández?
class GetOrganization(QuestionTemplate):
    target = entity
    regex = Question(Pos(".")) + donde + Lemma("trabajar") + target + Question(Pos("."))

    def interpret(self, match):
        target = match.target.tokens
        person = GetPersonFromName(target) + IsInstance()
        membership = GetMembershipFromPerson(person)
        organization = GetOrganizationFromMembershipTarget(membership)
        organizationName = GetNameFromOrganizationTarget(organization)
        return organizationName, (target, "{0} trabaja en:")


# Rol que ocupa una persona
# Ejemplo: ¿Qué puesto ocupa Ángel Fernández?
class GetRole(QuestionTemplate):
    target = entity
    nouns = Lemma("puesto") | Lemma("cargo") | Lemma("empleo") | Lemma("oficio") | Lemma("ministerio")
    verbs = Lemma("ocupar")
    regex = Question(Pos(".")) + que + nouns + verbs + target + Question(Pos("."))

    def interpret(self, match):
        target = match.target.tokens
        person = GetPersonFromName(target) + IsInstance()
        membership = GetMembershipFromPerson(person)
        role = GetRoleFromMembershipTarget(membership)
        roleName = GetNameFromRoleTarget(role)
        return roleName, (target, "{0} trabaja como:")


# Momento en el que empezó a trabajar una persona
# Ejemplo: ¿Cuándo empezó a trabajar Manuel Muniesa Alfonso?
class GetTimeStart(QuestionTemplate):
    target = entity
    verbs = Lemma("empezar") + Question(Pos("IN")) + Lemma("trabajar")
    regex = Question(Pos(".")) + cuando + verbs + target + Question(Pos("."))

    def interpret(self, match):
        target = match.target.tokens
        person = GetPersonFromName(target) + IsInstance()
        membership = GetMembershipFromPerson(person)
        interval = GetIntervalFromMembership(membership)
        start = GetStartFromIntervalTarget(interval)
        stampStart = GetStampFromTimeTarget(start)
        return stampStart, (target, "{0} empezó:".decode("utf-8"))

# Momento en el que terminó de trabajar una persona
# Ejemplo: ¿Cuándo terminó de trabajar Manuel Muniesa Alfonso?
class GetTimeEnd(QuestionTemplate):
    target = entity
    verbs = Lemma("terminar") + Question(Pos("IN")) + Lemma("trabajar")
    regex = Question(Pos(".")) + cuando + verbs + target + Question(Pos("."))

    def interpret(self, match):
        target = match.target.tokens
        person = GetPersonFromName(target) + IsInstance()
        membership = GetMembershipFromPerson(person)
        interval = GetIntervalFromMembership(membership)
        end = GetEndFromIntervalTarget(interval)
        stampEnd = GetStampFromTimeTarget(end)
        return stampEnd, (target, "{0} terminó:".decode("utf-8"))


# Dirección de una organización
# Ejemplo: ¿Dónde está el Instituto Tecnológico de Aragón?
class GetAddress(QuestionTemplate):
    target = Question(Pos("DT")) + entity
    regex = Question(Pos(".")) + donde + Lemma("estar") + target + Question(Pos("."))

    def interpret(self, match):
        target = match.target.tokens
        organization = GetOrganizationFromName(target) + IsInstance()
        site = GetSiteFromOrganization(organization)
        address = GetAddressFromSiteTarget(site)
        addressName = GetNameFromAddressTarget(address)
        return addressName, (target, "{0} se encuentra en:")


# Teléfono de una organización
# Ejmplo: ¿Cuál es el teléfono del Instituto Tecnológico de Aragón?
class GetPhone(QuestionTemplate):
    target = Question(det) + entity
    phonePrefixes = (det + (Lemma("número") | Lemma("numero")))
    phoneName = Question(det) + (Lemma("teléfono") | Lemma("móvil") | Lemma("telefono") | Lemma("movil"))
    phone = Question(phonePrefixes) + phoneName
    regex = Question(Pos(".")) + cual + Lemma("ser") + phone + target + Question(Pos("."))

    def interpret(self, match):
        target = match.target.tokens
        organization = GetOrganizationFromName(target) + IsInstance()
        site = GetSiteFromOrganizationTarget(organization)
        phone = GetPhoneFromSiteTarget(site)
        return phone, (target, "Su número de teléfono es:".decode("utf-8"))


# Resumen de una página web
# Ejemplo: Resumen de http://transparencia.aragon.es/node/5528
class Summary(QuestionTemplate):
    target = Group(Token("URL_MATCH"), "target")
    regex = (Lemma("resumer") | Lemma("resumen")) + Question(Pos("IN")) + target

    def interpret(self, match):
        target = match.target.tokens
        WebPage = GetWebPageFromURLTarget(target) + IsInstance()
        summary = GetSummaryFromWebPageTarget(WebPage)
        return summary, (target, "El resumen es:")


# Categorías de una página web
# Ejemplo: Categorías de http://transparencia.aragon.es/node/5528
class Categories(QuestionTemplate):
    target = Group(Token("URL_MATCH"), "target")
    regex = (Lemma("categorías") | Lemma("categoría") | Lemma("categoria")) + Question(Pos("IN")) + target

    def interpret(self, match):
        target = match.target.tokens
        WebPage = GetWebPageFromURL(target) + IsInstance()
        category = GetCategoryFromWebPageTarget(WebPage)
        categoryName = GetCategoryNameFromCategoryTarget(category)
        return categoryName, (target, "La lista de categorías es:")
