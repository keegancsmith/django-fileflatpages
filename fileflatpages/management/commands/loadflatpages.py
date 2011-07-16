import os.path
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections, router, transaction, DEFAULT_DB_ALIAS
from django.db.models import get_apps

from fileflatpages.models import FileFlatPage


class FileFlatPageParser(object):

    comment_re = re.compile(r'^(#|\.\.|<!---?|//)(.*?)(-?-->)?$')
    fieldvalue_re = None

    required_fields = ('url', 'title')
    other_fields = ('enable_comments', 'template_name', 'registration_required')
    special_fields = ('remove_comments',)
    bool_fields = ('enable_comments', 'registration_required', 'remove_comments')
    all_fields = None

    def __init__(self, path):
        self.path = path
        self.warnings = []
        self.fields = {}

        # Remove lines with key = value comments from the content
        self.remove_comments = False

        if FileFlatPageParser.all_fields is None:
            FileFlatPageParser.all_fields = (self.required_fields +
                                             self.other_fields +
                                             self.special_fields)
            fields = '|'.join(self.all_fields)
            fieldvalue_re = re.compile(r'^\s*(%s)\s*(?:=|:)(.*)$' % fields)
            FileFlatPageParser.fieldvalue_re = fieldvalue_re

        self.__calc_fields()

    def __calc_fields(self):
        for line in file(self.path):
            # We only want to process the comments at the top of the file. We
            # also will ignore comments which don't contain an field = value
            match = self.comment_re.match(line)
            if match is None:
                break
            match = self.fieldvalue_re.match(match.group(2))
            if match is None:
                continue

            field, value = match.groups()
            value = value.strip()

            # Warn about potential mistakes
            if field in self.fields:
                self.warnings.append("Field '%s' is repeated" % field)
            if field in self.bool_fields:
                if value not in ('True', 'False'):
                    self.warnings.append(
                        "Field '%s' must be 'True' or 'False'" % field)
                else:
                    value = value == 'True'

            if field in self.special_fields:
                setattr(self, field, value)
            else:
                self.fields[field] = value

    def get_or_create(self, app_name, path):
        # Check we have all the required fields, if not make self.fields empty
        for field in self.required_fields:
            if field not in self.fields:
                self.warnings.append("Field '%s' is required but missing" % field)
                return None

        # Set the fields on the model instance and save
        flatpage, _ = FileFlatPage.objects.get_or_create(app=app_name, path=path)
        for field, value in self.fields.iteritems():
            setattr(flatpage, field, value)
        flatpage.content = self.content
        flatpage.sites = [settings.SITE_ID]

        return flatpage

    @property
    def content(self):
        with file(self.path) as f:
            if self.remove_comments:
                lines = []
                line_iter = iter(f)
                for line in line_iter:
                    match = self.comment_re.match(line)
                    if match is None:
                        lines.append(line)
                        break
                    match = self.fieldvalue_re.match(match.group(2))
                    if match is None:
                        lines.append(line)
                lines.extend(line_iter)
                return ''.join(lines)
            else:
                return f.read()


class Command(BaseCommand):
    help = 'Installs the flatpage fixtures in the database.'
    option_list = BaseCommand.option_list

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
                ffpp = FileFlatPageParser(os.path.join(flatpages_path, path))
                flatpage = ffpp.get_or_create(app_name, path)

                # output warnings
                for warning in ffpp.warnings:
                    self.stdout.write('WARNING: %s in %s\n'
                                      % (warning, ffpp.path))

                if flatpage:
                    flatpage.save()
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
