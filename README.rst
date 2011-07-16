====================
django-fileflatpages
====================

This is a Django app that makes fixtures for FlatPages more convenient.

One of the main drawbacks with ``django.contrib.flatpages`` is that the only
way to store your flat pages with your source files is as a
fixture. ``django-fileflatpages`` solves this problem by inserting files as
FlatPages from your apps.

What django-fileflatpages gives you is the Django management command
*loadflatpages*. For each app in your projects INSTALLED_APPS, *loadflatpages*
will look for the directory ``flatpages``. If it finds a flatpages directory,
it adds each file in the flatpages directory as a flatpage.

The ``FlatPage`` attributes are specified using comments at the top of each
file. ``django-fileflatpages`` starts at the first line, and for each line it
looks for ``attribute = value`` comments. As soon as ``django-fileflatpages``
encounters a non-comment line, it stops looking for further comments.

For example::

  .. -*- mode: rst -*-
  .. url = /about/
  .. title = About
  .. template_name = flatpages/rst.html
  .. enable_comments = False

  Hello World

creates::

  FlatPage(url='/about', title='About', template_name='flatpages/rst.html',
           enable_comments=False, sites=[settings.SITE_ID],
           content=file(fixture_path).read())

There is one special field you can specify, ``remove_comments = True``. This
will remove comment lines with field = value directives from the content that
is stored in the database.

The main website for django-fileflatpages is
https://bitbucket.org/keegan_csmith/django-fileflatpages but there is also a
git mirror at https://github.com/keegancsmith/django-fileflatpages


Installation
============

* Install ``django-fileflatpages`` with your favourite python package manager::

    pip install django-fileflatpages

* Add ``"fileflatpages"`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = [
        # ...
        "fileflatpages",
    ]

* Make sure you have also enabled flatpages for your
  project. https://docs.djangoproject.com/en/dev/ref/contrib/flatpages/

Now when you run ``django-admin.py loadflatpages`` all installed apps will
have there flatpages added.


Example Site
============

An example project is stored under ``example_project`` directory. See the
directory ``example_project/app/flatpages`` for the flatpages that get added to
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
