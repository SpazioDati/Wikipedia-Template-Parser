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

Get key/value data from all templates used in the given page
```python
from wikipedia_template_parser import data_from_templates

data_from_templates("Trento", lang="it")
```

For pages containing the {{coord}} template (it.wiki), data are parsed 
and returned as a dictionary with 'lat' and 'lon' keys:
```python
from wikipedia_template_parser import data_from_templates

data_from_templates("Cattedrale di San Vigilio","it")

[{'data': {'lat': '46.067017', 'lon': '11.121385'}, 'name': u'coord'}, 
(...)]
```

Get all pages in a given category. A maxdepth parameter can
be specified, if omitted it is set to zero (subcategories are not visited)
```python
from wikipedia_template_parser import pages_in_category

pages_in_category("Categoria:Architetture_religiose_d'Italia", "it", maxdepth=20):

pages_in_category("Categoria:Chiese_di_Prato","it")
```
