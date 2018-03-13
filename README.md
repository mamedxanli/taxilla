## Initial configuration ##

* Create group called "operators" and add add/edit/delete permissions on models:
  * Vehicles
  * Carmakes
  * Travels
  * Companies
* Create operator users and add them to "operator" group created above and mark
  "is_staff" tick.
* Create drivers users and mark "is_driver" tick.


## Celery periodic tasks ##

Before running celery jobs you need to ensure that the RabbitMQ is installed
and running, then run the following in a separate terminal unless otherwise
configured:
```
celery -A taxilla worker -l INFO
```


## Template documentation ##

Follow this links to open the template & its documentation:

* http://127.0.0.1:8000/static/unify/index.html
* http://127.0.0.1:8000/static/unify-docs/index.html



## Dev setup ##

Please follow https://gitlab.com/inetreco/taxilla/wikis/Development

## Sphinx documentation ##

* Syntax: http://www.sphinx-doc.org/en/stable/rest.html
* TOC: http://www.sphinx-doc.org/en/stable/markup/toctree.html
* Build: ```make html``` from docs/ folder
