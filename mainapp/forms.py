from django import forms

class MyMedicalRecordsForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 20 megabytes'
    )

class GPMedicalRecordsForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 20 megabytes'
    )