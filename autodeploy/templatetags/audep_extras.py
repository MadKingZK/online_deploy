#-*- coding: UTF-8 -*-
from django import template
import time 
register = template.Library() 
@register.filter("timestamp") 
def timestamp(value): 
    try: 
        customtime = time.strftime("%Y-%m-%d %X",time.gmtime(value+3600*8))
        return customtime
    except Exception as e:
        return 'N/A'
