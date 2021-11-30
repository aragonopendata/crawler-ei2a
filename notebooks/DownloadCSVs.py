import requests
import codecs

PREFIX = "/data/VirtuosoData/"
URL_LEGISLATURA = (PREFIX + "ORG_LEGISLATURA.csv","https://opendata.aragon.es/GA_OD_Core/download?view_id=158&formato=csv&name=Organigrama%20del%20Gobierno%20de%20Aragón")
URL_ENTIDAD = (PREFIX + "ORG_ENTIDAD.csv","https://opendata.aragon.es/GA_OD_Core/download?view_id=159&formato=csv&name=Organigrama%20del%20Gobierno%20de%20Aragón")
URL_CARGO = (PREFIX + "ORG_CARGO.csv","https://opendata.aragon.es/GA_OD_Core/download?view_id=160&formato=csv&name=Organigrama%20del%20Gobierno%20de%20Aragón")

PREFIXES = ['Exmo. ', 'Exma. ', 'Dª. ', 'Dña. ', 'Sra. ', 'Sr. ', 'Ilmª. ', 'Ilma. ', 'Ilmo. ', 'Dña. ', 'Excma. ', 'Excmo. ', 'D. ', 'Ilma. ', 'Ilmo. ']
def clean_csv(content):
    i = 1
    while i < len(content) - 1:
        if content[i] is '"' and content[i - 1] is not "\n" \
                and content[i - 1] is not ";" \
                and content[i + 1] is not ";":
            content = content[:i] + content[i + 1:]
        else:
            i += 1
    content = content.replace('"None"', '""')
    return content

def download_clean(url, cargo=False):
    content = requests.get(url[1]).content.decode("utf-8")
    content = clean_csv(content)

    if cargo:
        content = content.replace('"<i>--Actualmente sin titular--</i>"', '""')
        content = content.replace('"<i>--Vacante provisional--</i>"', '""')
        content = content.replace('"Vacante provisional"', '""')
        content = content.replace('"[Sin titular]"', '""')
        content = content.replace('"Sin titular"', '""')
        for pre in PREFIXES:
            content = content.replace(pre, '')

    with codecs.open(url[0],"w","utf-8") as file:
        file.write(content)

download_clean(URL_LEGISLATURA)
download_clean(URL_ENTIDAD)
download_clean(URL_CARGO, True)

