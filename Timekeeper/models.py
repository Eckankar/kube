from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from operator import attrgetter
from collections import defaultdict

class Session(models.Model):
    date = models.DateField()
    notes = models.TextField()

    def avgs(self):
        avgs = sorted(Avg5.objects.filter(session=self).all(),
                        key=(lambda avg: (avg.avg().DNF, avg.avg().timestamp)))

        groups = defaultdict(list)
        for avg in avgs:
            groups[avg.puzzle.name].append(avg)

        return groups.items()

    def __unicode__(self):
        return unicode(self.date)

class SessionAdmin(admin.ModelAdmin):
    pass

class CubeTime(models.Model):
    timestamp = models.DecimalField(max_digits=10, decimal_places=2)
    plusTwo = models.BooleanField(default=False)
    DNF = models.BooleanField(default=False)

    def __unicode__(self):
        ts = self.timestamp

        if self.DNF:
            return "DNF"

        secs = ts % 60
        frac = (secs * 100) % 100
        secs._round_floor(0)
        mins = (ts - secs) // 60
        return "%01d:%02d.%02.d" % (mins, secs, frac)

    @staticmethod
    def avg(*times):
        avg = CubeTime()

        avgtimes = [e for e in filter(lambda e: not e.DNF, times)]
        avgtimes.sort(key=attrgetter('timestamp'))
        if len(times) - len(avgtimes) > 1: avg.DNF = True

        if len(avgtimes) == len(times): avgtimes.pop()
        avgtimes.pop(0)

        try:
            avg.timestamp = sum(ct.timestamp for ct in avgtimes) / len(avgtimes)
        except:
            avg.timestamp = 0

        return avg

class CubeTimeAdmin(admin.ModelAdmin):
    pass

class Puzzle(models.Model):
    name = models.TextField()

    def __unicode__(self):
        return self.name

class PuzzleAdmin(admin.ModelAdmin):
    pass

class Avg5(models.Model):
    user = models.ForeignKey(User)
    session = models.ForeignKey(Session)
    puzzle = models.ForeignKey(Puzzle)

    time1 = models.ForeignKey(CubeTime, related_name="avg5_time1")
    time2 = models.ForeignKey(CubeTime, related_name="avg5_time2")
    time3 = models.ForeignKey(CubeTime, related_name="avg5_time3")
    time4 = models.ForeignKey(CubeTime, related_name="avg5_time4")
    time5 = models.ForeignKey(CubeTime, related_name="avg5_time5")

    def avg(self):
        return CubeTime.avg(self.time1, self.time2, self.time3, self.time4, self.time5)

    def improvement(self):
        prev = Avg5.objects.filter(user=self.user, session__date__lt=self.session.date,
                                   puzzle=self.puzzle).order_by('-session__date')

        if len(prev) == 0:
            return "N/A"
        else:
            return "%.2f%%" % (100 * (1 - self.avg().timestamp / prev[0].avg().timestamp))

    def __unicode__(self):
        return "%s (%s, %s, %s, %s, %s)" % (self.avg(), self.time1, self.time2, self.time3, self.time4, self.time5)

class Avg5Admin(admin.ModelAdmin):
    list_display = ['user', 'puzzle', 'session', 'avg', 'time1', 'time2', 'time3', 'time4', 'time5']

admin.site.register(Session, SessionAdmin)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Avg5, Avg5Admin)
admin.site.register(CubeTime, CubeTimeAdmin)