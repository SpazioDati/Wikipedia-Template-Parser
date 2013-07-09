"""
Wikipedia-Template-Parser
A simple library for extracting data from Wikipedia templates
"""

import re
import requests
import urllib
from pyquery import PyQuery as pq
import mwparserfromhell


def clean_wiki_links(s):
    """
    Given a wiki text removes links syntax
    Examples: [[Page]] -> Page
              [[Page|displayed text]] -> displayed text
    """
    # clean links without renaming
    s = re.sub(r'\[\[([^\|\]]+)\]\]', r'\1', s)
    # clean links with renaming
    s = re.sub(r'\[\[[^\|\]]+\|([^\]]+)\]\]', r'\1', s)
    return s


def clean_ref(s):
    """
    Cleans <ref> tags
    """
    text = pq(s)
    res = []
    for el in text.contents():
        if isinstance(el, basestring):
            res.append(el.strip())
        elif el.tag != "ref":
            res.append(clean_ref(el))
    return " ".join(res)


def get_wikitext_from_api(page, lang='en'):
    """
    Given a page title and the language returns the wiki text of the latest
    revision of the page
    """
    url = 'http://{}.wikipedia.org/w/api.php'.format(lang)
    params = {
        'action': 'query',
        'prop': 'revisions',
        'titles': urllib.unquote(page.replace(' ', '_')),
        'rvprop': 'content',
        'rvlimit': '1',
        'format': 'json',
        'redirects': True
    }
    res = requests.get(url, params=params)
    if not res.ok:
        res.raise_for_status()
    json_pages = res.json()['query']['pages']
    return json_pages.values()[0]['revisions'][0]['*']


def extract_data_from_coord(template):

    coord = {'lat': '', 'lon': ''}
    optionalpars = ['dim', 'globe', 'region', 'scale', 'source', 'type', 'display']

    todel = set()
    for k, v in template.iteritems():
        for op in optionalpars:
            if (op in v) or (op in k):
                todel.add(k)
                break

    for k in todel:
        del template[k]

    anonpars = [tpar for tpar in template.keys() if 'anon_' in tpar]
    for ap in anonpars:
        template[int(ap.strip('anon_'))] = template[ap]
        del template[ap]

    parsnums = [int(p.strip('anon_')) for p in anonpars]
    parcount = len(anonpars)
    startpar = min(parsnums)

    gglat = float(template[startpar])
    mmlat = 0
    sslat = 0
    gglong = 0
    mmlong = 0
    sslong = 0
    dirlat = ''
    dirlong = ''
    if parcount == 2:
        gglong = float(template[startpar+1])
    elif parcount == 4:
        dirlat = str(template[startpar+1])
        gglong = float(template[startpar+2])
        dirlong = str(template[startpar+3])
    elif parcount == 6:
        mmlat = float(template[startpar+1])
        dirlat = str(template[startpar+2])
        gglong = float(template[startpar+3])
        mmlong = float(template[startpar+4])
        dirlong = str(template[startpar+5])
    elif parcount == 8:
        mmlat = float(template[startpar+1])
        sslat = float(template[startpar+2])
        dirlat = str(template[startpar+3])
        gglong = float(template[startpar+4])
        mmlong = float(template[startpar+5])
        sslong = float(template[startpar+6])
        dirlong = str(template[startpar+7])

    deglat = float(gglat)+float(mmlat)/60.0+float(sslat)/3600.0
    deglong = float(gglong)+float(mmlong)/60.0+float(sslong)/3600.0

    if dirlat == "S":
        deglat = - deglat
    if dirlong == "W":
        deglong = - deglong

    coord['lat'] = str(deglat)
    coord['lon'] = str(deglong)
    return coord


def data_from_templates(page, lang='en'):
    """
    Given a page title and the language returns a list with the data of every
    template included in the page.
    Every list item is a dictionary with 2 keys: name and data. name is the
    name of the template while data is a dictionary with key/value attributes
    of the template.
    """
    store = []
    content = ' '.join(get_wikitext_from_api(page, lang).split())
    content = clean_ref(content)
    #match = re.findall(r'\{\{([^}]+)\}\}', content)
    match = mwparserfromhell.parse(content).filter_templates()
    for template_string in match:
        template_string = template_string[2:-2]
        anon_counter = 0
        template_string = clean_wiki_links(template_string)
        template_string = template_string.split("|")
        name, key_values = template_string[0].strip(), template_string[1:]
        data = {}
        for key_value in key_values:
            try:
                key, value = key_value.split("=", 1)
            except ValueError:
                anon_counter += 1
                key = 'anon_{}'.format(anon_counter)
                value = key_value
            data[key.strip()] = value.strip()
        if name.lower() == 'coord':
            data = extract_data_from_coord(data)
        store.append({'name': name, 'data': data})
    return store


def pages_with_template(template, lang='en', eicontinue=None):
    """
    Returns a list of pages that use the given template
    """
    url = 'http://{}.wikipedia.org/w/api.php'.format(lang)
    params = {
        'action': 'query',
        'list': 'embeddedin',
        'eititle': template,
        'eilimit': 500,
        'format': 'json',
    }
    if eicontinue:
        params['eicontinue'] = eicontinue
    res = requests.get(url, params=params)
    if not res.ok:
        res.raise_for_status()
    result = [x['title'] for x in res.json()['query']['embeddedin']]
    try:
        eicontinue = res.json()['query-continue']['embeddedin']['eicontinue']
    except KeyError:
        eicontinue = None
    if eicontinue:
        result += pages_with_template(template, lang, eicontinue)
    return result


def pages_in_category(catname, lang='en', maxdepth=0,
                      cmcontinue=None, subcats=None, visitedcats=None):
    """
    Returns a list of pages in a given category and its subcategories
    parameters:
    catname: category name with prefix (e.g. "Categoria:Chiese_di_Prato")
    lang: Wikipedia language code (e.g. "it"), optional (default is "en")
    maxdepth: specifies the number (a non-negative integer) of levels
              to descend at most in the category tree starting from catname.
    """
    url = 'http://{}.wikipedia.org/w/api.php'.format(lang)
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': catname,
        'cmlimit': '500',
        'format': 'json'
    }
    if visitedcats is None:
        visitedcats = list()
    if cmcontinue:
        params['cmcontinue'] = cmcontinue
    res = requests.get(url, params=params)
    if not res.ok:
        res.raise_for_status()
    result = [x['title'].encode('utf-8') for x in res.json()['query']['categorymembers']
              if x['ns'] == 0]
    subcats = [x['title'].replace(' ', '_')
               for x in res.json()['query']['categorymembers']
               if x['ns'] == 14 and x['title'] not in visitedcats]
    try:
        cmcontinue = res.json()['query-continue']['categorymembers']['cmcontinue']
    except KeyError:
        cmcontinue = None
    if cmcontinue:
        result += pages_in_category(catname,
                                    lang=lang,
                                    maxdepth=maxdepth,
                                    cmcontinue=cmcontinue,
                                    subcats=subcats,
                                    visitedcats=visitedcats)
    maxdepth -= 1
    if maxdepth >= 0:
        if subcats:
            for cat in subcats:
                result += pages_in_category(cat,
                                            lang=lang,
                                            maxdepth=maxdepth,
                                            cmcontinue=cmcontinue,
                                            subcats=subcats,
                                            visitedcats=visitedcats)
                visitedcats.append(cat)
    return result

if __name__ == "__main__":
    print pages_with_template("Template:Edificio_religioso", "it")
    print
    print data_from_templates("Volano_(Italia)", "it")
    print
    print data_from_templates("Cattedrale di San Vigilio", "it")
    print
    print pages_in_category("Categoria:Architetture_religiose_d'Italia", "it", maxdepth=20)
    print
    print pages_in_category("Categoria:Chiese_di_Prato", "it")
    print
    print data_from_templates("Chiesa di San Pantaleo (Zoagli)", "it")
    print
    print data_from_templates(urllib.quote("Chiesa di San Pantaleo (Zoagli)"), "it")
    print
    print get_wikitext_from_api("Chiesa di San Petronio", "it")
