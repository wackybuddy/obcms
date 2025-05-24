from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Update the site domain for admin "View site" link'

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(pk=1)
            site.domain = '127.0.0.1:8000'
            site.name = 'OBC Management System'
            site.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated site: {site.domain} - {site.name}'
                )
            )
        except Site.DoesNotExist:
            site = Site.objects.create(
                pk=1,
                domain='127.0.0.1:8000',
                name='OBC Management System'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created site: {site.domain} - {site.name}'
                )
            )