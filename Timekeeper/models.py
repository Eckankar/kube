from django.db import models
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from operator import attrgetter
from collections import defaultdict
from math import isnan

class Session(models.Model):
    date = models.DateField()
    notes = models.TextField()

    def avgs(self):
        avgs = sorted(Avg5.objects.filter(session=self).all(),
                        key=(lambda avg: (avg.avg().DNF, avg.avg().timestamp)))

        groups = defaultdict(list)
        winners = {}
        for avg in avgs:
            groups[avg.puzzle.name].append(avg)

            imp = avg.improvement()
            if not isnan(imp):
                try:
                    if avg.puzzle.name not in winners or winners[avg.puzzle.name][0] < imp:
                        winners[avg.puzzle.name] = [imp, avg]
                except:
                    pass

        for time in winners.values():
            time[1].session_winner = True

        return groups.items()

    def __unicode__(self):
        return "%s (%s)" % (self.notes, unicode(self.date))

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

        plusTwo = "+2" if self.plusTwo else ""

        secs = ts % 60
        frac = (secs * 100) % 100
        secs._round_floor(0)
        mins = (ts - secs) // 60
        return "%01d:%02d.%02.d%s" % (mins, secs, frac, plusTwo)

    def finalTime(self):
        """ Time including any penalties. """
        return self.timestamp + (2 if self.plusTwo else 0)

    @staticmethod
    def avg(*times):
        avg = CubeTime()

        avgtimes = [e for e in filter(lambda e: not e.DNF, times)]
        avgtimes.sort(key=lambda e: e.finalTime())
        if len(times) - len(avgtimes) > 1: avg.DNF = True

        if len(avgtimes) == len(times): avgtimes.pop()
        avgtimes.pop(0)

        try:
            avg.timestamp = sum(ct.finalTime() for ct in avgtimes) / len(avgtimes)
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

    time1 = models.ForeignKey(CubeTime, related_name="avg5_time1", null=True)
    time2 = models.ForeignKey(CubeTime, related_name="avg5_time2", null=True)
    time3 = models.ForeignKey(CubeTime, related_name="avg5_time3", null=True)
    time4 = models.ForeignKey(CubeTime, related_name="avg5_time4", null=True)
    time5 = models.ForeignKey(CubeTime, related_name="avg5_time5", null=True)

    def avg(self):
        return CubeTime.avg(self.time1, self.time2, self.time3, self.time4, self.time5)

    def improvement(self):
        prev = Avg5.objects.filter(user=self.user, session__date__lt=self.session.date,
            puzzle=self.puzzle).order_by('-session__date')

        if len(prev) == 0:
            return float('nan')
        else:
            prevAvg = prev[0].avg()
            if prevAvg.DNF:
                return float('nan')
            return (100 * (1 - self.avg().timestamp / prevAvg.timestamp))

    def improvement_string(self):
        imp = self.improvement()
        if isnan(imp):
            return "N/A"
        return "%.2f%%" % imp

    def __unicode__(self):
        return "%s (%s, %s, %s, %s, %s)" % (self.avg(), self.time1, self.time2, self.time3, self.time4, self.time5)

class Avg5AdminForm(forms.ModelForm):
    time1time = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Time #1")
    time1plus2 = forms.BooleanField(initial=False, required=False, label="+2")
    time1dnf = forms.BooleanField(initial=False, required=False, label="DNF")
    time2time = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Time #2")
    time2plus2 = forms.BooleanField(initial=False, required=False, label="+2")
    time2dnf = forms.BooleanField(initial=False, required=False, label="DNF")
    time3time = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Time #3")
    time3plus2 = forms.BooleanField(initial=False, required=False, label="+2")
    time3dnf = forms.BooleanField(initial=False, required=False, label="DNF")
    time4time = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Time #4")
    time4plus2 = forms.BooleanField(initial=False, required=False, label="+2")
    time4dnf = forms.BooleanField(initial=False, required=False, label="DNF")
    time5time = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Time #5")
    time5plus2 = forms.BooleanField(initial=False, required=False, label="+2")
    time5dnf = forms.BooleanField(initial=False, required=False, label="DNF")

    def save(self, *args, **kwargs):
        for i in range(1,6):
            t = 'time' + str(i)
            if self.cleaned_data[t+'dnf'] and not self.cleaned_data[t+'time']:
                self.cleaned_data[t+'time'] = 0

        (self.instance.time1, created) = CubeTime.objects.get_or_create(timestamp = self.cleaned_data['time1time'], DNF = self.cleaned_data['time1dnf'],
                                                                        plusTwo = self.cleaned_data['time1plus2'])
        (self.instance.time2, created) = CubeTime.objects.get_or_create(timestamp = self.cleaned_data['time2time'], DNF = self.cleaned_data['time2dnf'],
                                                                        plusTwo = self.cleaned_data['time2plus2'])
        (self.instance.time3, created) = CubeTime.objects.get_or_create(timestamp = self.cleaned_data['time3time'], DNF = self.cleaned_data['time3dnf'],
                                                                        plusTwo = self.cleaned_data['time3plus2'])
        (self.instance.time4, created) = CubeTime.objects.get_or_create(timestamp = self.cleaned_data['time4time'], DNF = self.cleaned_data['time4dnf'],
                                                                        plusTwo = self.cleaned_data['time4plus2'])
        (self.instance.time5, created) = CubeTime.objects.get_or_create(timestamp = self.cleaned_data['time5time'], DNF = self.cleaned_data['time5dnf'],
                                                                        plusTwo = self.cleaned_data['time5plus2'])

        return super(Avg5AdminForm, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(Avg5AdminForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            self.fields['time1time'].initial = instance.time1.timestamp
            self.fields['time1plus2'].initial = instance.time1.plusTwo
            self.fields['time1dnf'].initial = instance.time1.DNF
            self.fields['time2time'].initial = instance.time2.timestamp
            self.fields['time2plus2'].initial = instance.time2.plusTwo
            self.fields['time2dnf'].initial = instance.time2.DNF
            self.fields['time3time'].initial = instance.time3.timestamp
            self.fields['time3plus2'].initial = instance.time3.plusTwo
            self.fields['time3dnf'].initial = instance.time3.DNF
            self.fields['time4time'].initial = instance.time4.timestamp
            self.fields['time4plus2'].initial = instance.time4.plusTwo
            self.fields['time4dnf'].initial = instance.time4.DNF
            self.fields['time5time'].initial = instance.time5.timestamp
            self.fields['time5plus2'].initial = instance.time5.plusTwo
            self.fields['time5dnf'].initial = instance.time5.DNF

    class Meta:
        model = Avg5
        fields = ('user', 'session', 'puzzle')
        exclude = ('time1', 'time2', 'time3', 'time4', 'time5')

class Avg5Admin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user', 'session', 'puzzle')
        }),
        ("Times",
            {
             'description': "Times must be entered as seconds. For instance, the time 1:04.45 should be entered as <i>64.45</i>.",
             'fields': (
                 ('time1time', 'time1plus2', 'time1dnf'),
                 ('time2time', 'time2plus2', 'time2dnf'),
                 ('time3time', 'time3plus2', 'time3dnf'),
                 ('time4time', 'time4plus2', 'time4dnf'),
                 ('time5time', 'time5plus2', 'time5dnf'),
             )
         })
    )
    form = Avg5AdminForm
    list_display = ['user', 'puzzle', 'session', 'avg', 'time1', 'time2', 'time3', 'time4', 'time5']
    list_filter = ('puzzle', 'session')

admin.site.register(Session, SessionAdmin)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Avg5, Avg5Admin)
admin.site.register(CubeTime, CubeTimeAdmin)
