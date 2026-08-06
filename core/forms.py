from django import forms
from .models import PatientComment

class PatientCommentForm(forms.ModelForm):
    class Meta:
        model = PatientComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Escribe un comentario...',
                'class': 'form-control',
            })
        }