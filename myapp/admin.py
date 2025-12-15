from django.contrib import admin
from myapp.models import *
# Register your models here.
admin.site.register(student_reg)
admin.site.register(course)
admin.site.register(lesson)
admin.site.register(MCQQuestion)