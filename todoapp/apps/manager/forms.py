from django import forms
from django.forms import widgets
from todoapp.apps.manager.models import *
from django.forms.models import BaseModelFormSet
from django.utils.functional import curry


class DateSelectorWidget(widgets.MultiWidget):
    def __init__(self, attrs=None,years=None,days=None):
        MONTHS = {
            1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr',
            5:'May', 6:'Jun', 7:'Jul', 8:'Aug',
            9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'
            }

        
        try :
            years = [(year, year) for year in years]
            days = [(d, dd) for d,dd in days]
            months = [(month, MONTHS[month]) for month in range(1,13)]
        except ValueError:
            return ''

        _widgets = (
            widgets.Select(attrs=None, choices=years),
            widgets.Select(attrs=None, choices=months),
            widgets.Select(attrs=None,choices=days),
        )
        super(DateSelectorWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        try:
            if value:
                return [value.year,value.month,value.day]
            return [None, None, None]
        except AttributeError:
            dt = [int(x) for x in value.split("-")]
            return [dt[0],dt[1],dt[2]]


    def format_output(self, rendered_widgets):
        widget_context={'year':rendered_widgets[0],'month':rendered_widgets[1],'week':rendered_widgets[2]}
        return u''.join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        try:
            D = date(day=int(datelist[2]), month=int(datelist[1]),
                    year=int(datelist[0]))
        except ValueError:
            return ''
        else:
            return str(D)

class MyModelFormsetBase(BaseModelFormSet):
    extra_args=None
    def __init__(self,*args,**kwargs):
        self.extra_args=kwargs.pop('extra_args',None)
        subFormClass = self.form
        self.form = curry(subFormClass,extra_args=self.extra_args)
        super(MyModelFormsetBase,self).__init__(*args,**kwargs)


class TaskCheckForm(forms.ModelForm):
    class Meta:
        model = Task
        fields=('completed','canceled')

    def __init__(self,*args,**kwargs):
        self.task = kwargs.get('instance', None)
        self.extra_args=kwargs.pop('extra_args',None)

        super(TaskCheckForm,self).__init__(*args,**kwargs)
        self.fields['completed'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['canceled'].widget.attrs['onchange'] = 'this.form.submit();'


class DateChangeForm(forms.ModelForm):
    recurring=forms.BooleanField(required=False)
    class Meta:
        model=Task
        fields=('start_date','end_date','freq',)
    def __init__(self, *args, **kwargs):
        self.extra_args=kwargs.pop('extra_args',{})
        super(DateChangeForm,self).__init__(*args,**kwargs)
        self.fields['start_date'].required=False
        self.fields['end_date'].required=False




    def clean(self):
        cleaned_data=self.cleaned_data
        sd=cleaned_data.get('start_date')
        ed=cleaned_data.get('end_date')
        r=cleaned_data.get('recurring')
        if r and sd and ed and (ed-sd).days<0:
            raise forms.ValidationError('Dates must be in chronological order.')
        if sd==None or (r and ed==None):
            raise forms.ValidationError('Dates must be given.')
        return cleaned_data

    def save(self):
        task=super(DateChangeForm,self).save(commit=False)
        r=self.cleaned_data['recurring']
        task.completed=False
        task.canceled=False
        if r:
            task.start_date=self.cleaned_data['start_date']
            task.end_date=self.cleaned_data['end_date']

        else:
            task.start_date=self.cleaned_data['start_date']
            task.end_date=self.cleaned_data['start_date']
        task.save()
        return task




