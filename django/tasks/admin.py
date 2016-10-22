from django import forms
from django.contrib import admin
from codemirror import CodeMirrorTextarea

from .models import Task
from .models import TaskStep
from .models import TaskSubmission


class TaskStepForm(forms.ModelForm):
    class Meta:
        model = TaskStep
        widgets = {
            'input_source': CodeMirrorTextarea,
            'output_source': CodeMirrorTextarea,
        }
        fields = '__all__'


class TaskStepAdmin(admin.ModelAdmin):
    form = TaskStepForm


admin.site.register(Task)
admin.site.register(TaskStep, TaskStepAdmin)
admin.site.register(TaskSubmission)
