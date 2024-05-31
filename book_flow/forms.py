from django import forms


class IssueBookForm(forms.Form):
    book_id = forms.IntegerField(widget=forms.HiddenInput())
