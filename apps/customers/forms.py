from django import forms

class ImportExcelForm(forms.Form):

    file = forms.FileField(
        label="Archivo Excel",
    )

    def clean_file(self):

        file = self.cleaned_data["file"]

        if not file.name.lower().endswith(
            (".xlsx", ".xls")
        ):
            raise forms.ValidationError(
                "El archivo debe ser un Excel (.xlsx o .xls)."
            )

        return file