from django import forms


class CreateServerForm(forms.Form):
    template_name = "form_template.html"

    server_name = forms.CharField(label="Create new Server", max_length=100)


class AddMemberForm(forms.Form):
    user_name = forms.CharField(label="Add Member", max_length=100)