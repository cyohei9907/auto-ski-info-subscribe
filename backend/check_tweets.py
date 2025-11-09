import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.models import Tweet

ids = ['1986991969659424873', '1986992711598285205', '1986992831509242163', '1986963184801202303']

print("Checking tweet IDs in database:")
for tid in ids:
    exists = Tweet.objects.filter(tweet_id=tid).exists()
    status = "EXISTS" if exists else "NOT FOUND"
    print(f'Tweet {tid}: {status}')

print(f"\nTotal tweets in database: {Tweet.objects.count()}")
