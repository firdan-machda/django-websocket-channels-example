import random
import string
from django import template

register = template.Library()

@register.simple_tag
def random_words(length=5):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))