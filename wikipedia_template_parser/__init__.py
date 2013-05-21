"""
Wikipedia-Template-Parser
A simple library for extracting data from Wikipedia templates
"""

import re
import requests
from pyquery import PyQuery as pq


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
        'titles': page,
        'rvprop': 'content',
        'rvlimit': '1',
        'format': 'json',
    }
    res = requests.get(url, params=params)
    if not res.ok:
        res.raise_for_status()
    json_pages = res.json()['query']['pages']
    return json_pages.values()[0]['revisions'][0]['*']


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
    match = re.findall(r'\{\{([^}]+)\}\}', content)
    for template_string in match:
        anon_counter = 0
        template_string = clean_wiki_links(template_string)
        template_string = template_string.split("|")
        name, key_values = template_string[0], template_string[1:]
        data = {}
        for key_value in key_values:
            try:
                key, value = key_value.split("=")
            except ValueError:
                anon_counter += 1
                key = 'anon_{}'.format(anon_counter)
                value = key_value
            data[key.strip()] = value.strip()
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


if __name__ == "__main__":
    print pages_with_template("Template:Edificio_religioso", "it")
    print
    print data_from_templates("Volano_(Italia)", "it")
    print
    print data_from_templates("Cattedrale di San Vigilio", "it")
