from django import forms
from taggit.forms import TagField
from taggit_labels.widgets import LabelWidget
from django.utils.translation import gettext_lazy as _
from library.models import TagGroup, Instance
from library.utils.taggit import parse_tags, edit_string_for_tags


class TagListWidgetMixin:
    def format_value(self, value):
        if value is not None and not isinstance(value, str):
            value = edit_string_for_tags(value)
        return super().format_value(value)


class TextareaTagWidget(TagListWidgetMixin, forms.Textarea):
    pass


class TagListField(forms.CharField):
    widget = TextareaTagWidget

    def clean(self, value):
        value = super().clean(value)
        try:
            return parse_tags(value)
        except ValueError:
            raise forms.ValidationError(
                _("Please provide a list of tags. One tag per line.")
            )

    def has_changed(self, initial_value, data_value):
        # Always return False if the field is disabled since self.bound_data
        # always uses the initial value in this case.
        if self.disabled:
            return False

        try:
            data_value = self.clean(data_value)
        except forms.ValidationError:
            pass

        # normalize "empty values"
        if not data_value:
            data_value = []
        if not initial_value:
            initial_value = []

        initial_value = [tag.name for tag in initial_value]
        initial_value.sort()

        return initial_value != data_value


class TagGroupForm(forms.ModelForm):
    tags = TagListField(widget=TextareaTagWidget(attrs={'cols': 40}))

    class Meta:
        model = TagGroup
        fields = '__all__'


class TagInstanceForm(forms.ModelForm):
    tags = TagField(widget=LabelWidget(attrs={'style': 'width: 100%;'}))

    class Meta:
        model = Instance
        fields = '__all__'
