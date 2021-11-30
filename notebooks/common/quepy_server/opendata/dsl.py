# coding: utf-8

"""
Domain specific language for Opendata quepy.
"""

from quepy.dsl import FixedType, HasKeyword, FixedRelation, FixedDataRelation

# Setup the Keywords for this application
HasKeyword.relation = "rdf:type"

class IsInstance(FixedType):
    fixedtype = "owl:NamedIndividual"

    
class GetEntityFromName(FixedDataRelation):
    relation = "ei2a:organizationName|ei2a:fullName|ei2a:roleName|ei2a:geographicName"

class GetPersonFromName(FixedDataRelation):
    relation = "ei2a:fullName"

class GetOrganizationFromName(FixedDataRelation):
    relation = "ei2a:organizationName"

class GetWebPageFromURL(FixedDataRelation):
    relation = "ei2a:URL"

class GetWebPageFromURLTarget(FixedDataRelation):
    relation = "ei2a:URL"
    addTarget = True


class GetNameFromPerson(FixedRelation):
    relation = "ei2a:fullName"
    reverse = True

class GetCitationFromEntity(FixedRelation):
    relation = "ei2a:citationOnEntity"
    reverse = False

class GetWebPageFromCitationTarget(FixedRelation):
    relation = "ei2a:citationOnWebPage"
    reverse = True
    addTarget = True

class GetURLFromWebPageTarget(FixedRelation):
    relation = "ei2a:URL"
    reverse = True
    addTarget = True

class GetMembershipFromPerson(FixedRelation):
    relation = "org:member"
    reverse = False

class GetOrganizationFromMembershipTarget(FixedRelation):
    relation = "org:organization"
    reverse = True
    addTarget = True

class GetNameFromOrganizationTarget(FixedRelation):
    relation = "ei2a:organizationName"
    reverse = True
    addTarget = True

class GetRoleFromMembershipTarget(FixedRelation):
    relation = "org:role"
    reverse = True
    addTarget = True

class GetNameFromRoleTarget(FixedRelation):
    relation = "ei2a:roleName"
    reverse = True
    addTarget = True

class GetSiteFromOrganization(FixedRelation):
    relation = "org:hasPrimarySite"
    reverse = True

class GetSiteFromOrganizationTarget(FixedRelation):
    relation = "org:hasPrimarySite"
    reverse = True
    addTarget = True

class GetAddressFromSiteTarget(FixedRelation):
    relation = "org:siteAddress"
    reverse = True
    addTarget = True

class GetNameFromAddressTarget(FixedRelation):
    relation = "locn:fullAddress"
    reverse = True
    addTarget = True

class GetPhoneFromSiteTarget(FixedRelation):
    relation = "ei2a:phone"
    reverse = True
    addTarget = True

class GetIntervalFromMembership(FixedRelation):
    relation = "org:memberDuring"
    reverse = True

class GetStartFromIntervalTarget(FixedRelation):
    relation = "time:hasBeginning"
    reverse = True
    addTarget = True

class GetEndFromIntervalTarget(FixedRelation):
    relation = "time:hasEnd"
    reverse = True
    addTarget = True

class GetStampFromTimeTarget(FixedRelation):
    relation = "time:inXSDDateTimeStamp"
    reverse = True
    addTarget = True

class GetSummaryFromWebPageTarget(FixedRelation):
    relation = "ei2a:summary"
    reverse = True
    addTarget = True

class GetCategoryFromWebPageTarget(FixedRelation):
    relation = "ei2a:webPageCategorization"
    reverse = True
    addTarget = True

class GetCategoryNameFromCategoryTarget(FixedRelation):
    relation = "rdf:type"
    reverse = True
    addTarget = True


    