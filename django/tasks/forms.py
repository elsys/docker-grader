from django import forms


class TaskForm(forms.Form):
    zip_file = forms.FileField(required=True, allow_empty_file=False,
                               max_length=100, label="File")
