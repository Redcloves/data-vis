from django.shortcuts import render
from django import forms
from bokeh.embed import components
from . import coviddata

choices = [(state['State'], state['Name']) for index,state in coviddata.restrictions.iterrows()]
choices.insert(0, ('', '- - - -'))

class choice(forms.Form):
    field = forms.ChoiceField(choices = choices, label= 'Breakdown of surgeries by state',widget=forms.Select(attrs={'onchange': 'submit();'}))

def index(request):
    map = coviddata.plot_states()
    if request.GET and request.GET['field'] != '':
        chosen_state = request.GET['field']
        plot = coviddata.plot_weekly(chosen_state)
        script, (map_div, plot_div) = components((map, plot))

        for state_name in choices:
            if state_name[0]==chosen_state:
                name = state_name[1]
                break
        context = dict(script=script, map_div=map_div, plot_div = plot_div, form=choice(), name = name)
    else:
        script, map_div = components(map)
        context = dict(script=script, map_div=map_div, form=choice())
    return render(request, 'home.html', context)

