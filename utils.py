from django.shortcuts import render_to_response
from django.template.context_processors import csrf

def mp_render(request, template, context={}):
    context.update(csrf(request))
    context['nick'] = request.COOKIES.get('nick')
    return render_to_response(template, context)
