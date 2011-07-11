import os.path
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections, router, transaction, DEFAULT_DB_ALIAS
from django.db.models import get_apps

from fileflatpages.models import FileFlatPage


class Command(BaseCommand):
    help = 'Installs the flatpage fixtures in the database.'
    option_list = BaseCommand.option_list

    comment_re = re.compile(r'^(#|\.\.|<!---?|//)(.*?)(-?-->)?$')
    required_fields = ('url', 'title')
    other_fields = ('enable_comments', 'template_name', 'registration_required')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        fields = '|'.join(self.required_fields + self.other_fields)
        self.keyvalue_re = re.compile(r'^\s*(%s)\s*(?:=|:)(.*)$' % fields)

    def add_fixture(self, app_name, flatpages_path, path):
        file_path = os.path.join(flatpages_path, path)
        fin = file(file_path)
        lines = fin.readlines()
        fin.close()

        # Get the fields from the comments at the top of the file
        fields = {}
        for line in lines:
            match = self.comment_re.match(line)
            if match is None:
                break
            match = self.keyvalue_re.match(match.group(2))
            if match is None:
                continue

            key, value = match.groups()
            if key in fields:
                self.stdout.write("WARNING: Key '%s' is repeated in file %s\n"
                                  % (key, file_path))
            fields[key] = value.strip()

        # Check we have all the required fields
        for field in self.required_fields:
            if field not in fields:
                self.stdout.write("WARNING: Key '%s' is required but missing in %s\n"
                                  % (field, file_path))
                return False

        # Set the fields on the model instance and save
        flatpage, _ = FileFlatPage.objects.get_or_create(app=app_name, path=path)
        for field, value in fields.iteritems():
            setattr(flatpage, field, value)
        flatpage.content = ''.join(lines)
        flatpage.sites = [settings.SITE_ID]
        flatpage.save()

        return True

    def handle(self, *fixture_labels, **options):
        # Do this in a transaction
        using = options.get('database', DEFAULT_DB_ALIAS)
        transaction.commit_unless_managed(using=using)
        transaction.enter_transaction_management(using=using)
        transaction.managed(True, using=using)

        for app_name, app_path in self.app_modules():
            flatpages_path = os.path.join(os.path.dirname(app_path), 'flatpages')

            if not os.path.exists(flatpages_path):
                continue
            if not os.path.isdir(flatpages_path):
                self.stdout.write('WARNING: %s is not a directory\n'
                                  % flatpages_path)
                continue

            self.stdout.write('Processing flatpage fixtures in %s\n'
                              % flatpages_path)
            for path in os.listdir(flatpages_path):
                if self.add_fixture(app_name, flatpages_path, path):
                    self.stdout.write('Added flatpage fixture %s from %s\n'
                                      % (path, app_name))

        # Commit our transaction
        transaction.commit(using=using)
        transaction.leave_transaction_management(using=using)

    @classmethod
    def app_modules(cls):
        for app in get_apps():
            name, _ = app.__name__.rsplit('.', 1)
            if hasattr(app, '__path__'):
                # It's a 'models/' subpackage
                for path in app.__path__:
                    yield (name, path)
            else:
                # It's a models.py module
                yield (name, app.__file__)
