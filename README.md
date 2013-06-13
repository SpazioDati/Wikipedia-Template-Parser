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


Get key/vaule data from all templates used in the given page
```python
from wikipedia_template_parser import data_from_templates

data_from_templates("Trento", lang="it")
```

Get all pages in a given category. A maxdepth parameter can
be specified, if omitted it is set to zero (subcategories are not visited)
```python
from wikipedia_template_parser import pages_in_category

pages_in_category("Categoria:Architetture_religiose_d'Italia", "it", maxdepth=20):

pages_in_category("Categoria:Chiese_di_Prato","it")
```
