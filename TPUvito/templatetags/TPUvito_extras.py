from django import template
from django.utils.safestring import mark_safe
import os

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)
@register.filter
def get_photo(obj):
        return obj.get_photo(True)
@register.filter
def get_photos(obj):
      photos = obj.get_photo(False)
      return photos
@register.filter
def get_photo_for_profile(obj):
      photos = obj.get_photo_redact(True)
      if not photos:
            return False
      return True
@register.filter
def get_photos_for_profile(obj):
      photos = obj.get_photo_redact(False)
      return photos
@register.filter
def get_primary_name(obj):
      return os.listdir(obj.media)[-1]
@register.filter
def is_num(arg1):
      return str.isnumeric(arg1)
@register.filter
def day_month_year_format(date):
      return date.strftime('%d %B %Y')
@register.filter
def set_stars(rating):
        if not rating:
              rating = 0
        if rating>4.5:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'  alt=''><img src='/static/star.svg' alt=''>")
        elif rating>4:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'  alt=''><img src='/static/half_star.svg' alt=''>")
        elif rating>3.5:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
        elif rating>3:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/half_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
        elif rating>2.5:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
        elif rating>2:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/half_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
        elif rating>1.5:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
        elif rating>1:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/half_star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
        elif rating>0.5:return mark_safe("<img src='/static/star.svg'  alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
        elif rating>0: return mark_safe("<img src='/static/half_star.svg'  alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
        else:return mark_safe("<img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>")
@register.filter(mark_safe=True)
def get_heart(arr,obj):
      if obj in arr:return 'checked_also'
      else: return ''
