from django import forms

class PDFSearchForm(forms.Form):
    palabra = forms.CharField(
        required=False,
        label="Texto a buscar",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: factura, cliente, total..."
        })
    )