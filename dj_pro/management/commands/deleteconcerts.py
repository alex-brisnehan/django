from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = """Deletes concerts that have already taken place. Good thing to 
    run daily in cron."""
    
    def handle_noargs(self, **kwargs):
        import datetime
        from on_air import models
        
        old_concerts = models.dj.Concert.objects.filter(date__lt=datetime.date.today())
        print "%d concerts deleted" % old_concerts.count()
        old_concerts.delete()
        
