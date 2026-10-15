from django.core.management.base import BaseCommand

from apps.tenants.models import ApiClient, Tenant


class Command(BaseCommand):
    help = 'Create a tenant and API key for local development.'

    def add_arguments(self, parser):
        parser.add_argument('tenant_slug')
        parser.add_argument('client_name')

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.get_or_create(
            slug=options['tenant_slug'],
            defaults={'name': options['tenant_slug'].replace('-', ' ').title()},
        )
        raw_key, key_hash = ApiClient.generate_key(tenant.name)
        api_client = ApiClient.objects.create(
            tenant=tenant,
            name=options['client_name'],
            key_hash=key_hash,
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Created client: {api_client.name}'))
        self.stdout.write(f'API Key: {raw_key}')
