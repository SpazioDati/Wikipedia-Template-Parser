Wikipedia-Template-Parser
=========================

A simple library for extracting data from Wikipedia templates



Examples
--------


Get all pages that contain the given template
```python
from wikipedia_template_parser import pages_with_template

pages_with_template("Template:Infobox_Italian_comune", lang="en")
```

By default the script doesn't return user and template pages; if you want them to be returned, you can set the `skip_users_and_templates` param:
```python
pages_with_template("Template:Infobox_Italian_comune", lang="en", skip_users_and_templates=False)
```

Get key/value data from all templates used in the given page
```python
from wikipedia_template_parser import data_from_templates

data_from_templates("Trento", lang="it")
```

Instead of requesting the page on the fly, you can pass the wikitext to
`data_from_templates` and have it parsed:
```python

# get just the text
pisa_text = get_wikitext_from_api("Torre pendente di Pisa", "it")

# an alternative could be be:
#   with open('some_file_with_wikitext.txt', 'r') as in_:
#        pisa_text = in_.read().decode('utf-8')

# manipulate the text as you wish
# ... do stuff ...

data_from_templates("Torre pendente di Pisa",
                    lang="it",
                    wikitext=pisa_text
                    )
```

For pages containing the {{coord}} template (it.wiki), data are parsed 
and returned as a dictionary with 'lat' and 'lon' keys:
```python
from wikipedia_template_parser import data_from_templates

data_from_templates("Cattedrale di San Vigilio", "it")

[{'data': {'lat': '46.067017', 'lon': '11.121385'}, 'name': u'coord'}, 
(...)]
```

If the coordinates are embedded in another template, like for [Template:Infobox_struttura_militare/man](http://it.wikipedia.org/wiki/Template:Infobox_struttura_militare/man) 
you can:
```python
from wikipedia_template_parser import data_from_templates

data_from_templates("Forte Campo Luserna", "it", extra_coords={
                    'infobox struttura militare': [  # lowercase and with no underscores
                        ['LatGradi', 'LatPrimi', 'LatSecondi', 'LatNS'],  # the latitude attributes in the template data
                        ['LongGradi', 'LongPrimi', 'LongSecondi', 'LongEW'],  # the longitude ones
                    ]
                })

[{'data': {'lat': '45.926814', 'lon': '11.3366', (...)}, 'name': u'Infobox_struttura_militare'}, 
(...)]
```


Get all pages in a given category. A maxdepth parameter can
be specified, if omitted it is set to zero (subcategories are not visited)
```python
from wikipedia_template_parser import pages_in_category

pages_in_category("Categoria:Architetture_religiose_d'Italia", "it", maxdepth=20):

pages_in_category("Categoria:Chiese_di_Prato","it")
```
