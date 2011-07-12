========================
 Django File Flat Pages
========================

This is a Django App which makes FlatPage fixtures nicer to edit and
store. This is accomplished through the Django command *loadflatpages*.


Example Site
============

An example project is stored under `example_project` directory. See the
directory `example_project/app/flatpages` for the flatpages that get added to
the database. To get the example site up and running under a virtual
environment follow these steps::

 $ virtualenv --no-site-packages env
 $ . env/bin/activate
 $ pip install -r example_project/requirements.txt
 $ python setup.py install
 $ python example_project/manage.py syncdb
 $ python example_project/manage.py loadflatpages # What django-fileflatpages adds
 $ python example_project/manage.py runserver

You should now be able to browse the example site at http://localhost:8000/
