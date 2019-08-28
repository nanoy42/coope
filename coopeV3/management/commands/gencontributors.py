from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import subprocess

class Command(BaseCommand):
    help = 'Generate the git contributors file'

    def handle(self, *args, **options):
        try:
            subprocess.call("rm " + settings.BASE_DIR + "/contributors.txt", shell=True)
        except:
            pass
        subprocess.call("git -C " + settings.BASE_DIR + " shortlog -n $@ | grep \"):\" | sed 's|:||' >> " + settings.BASE_DIR + "/contributors.txt", shell=True)
        subprocess.call("cat " + settings.BASE_DIR + "/contributors.txt", shell=True)