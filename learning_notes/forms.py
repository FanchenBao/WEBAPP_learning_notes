from django import forms
from .models import Topic, Entry

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text':''}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['title','text']
        labels = {'text':'', 'title':''}
        widgets = {'text':forms.Textarea(attrs = {'cols':80, 'rows':40}),
                    'title':forms.TextInput(attrs={'size': 80})
                    }