from __future__ import absolute_import
from __future__ import unicode_literals

from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div

from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from bazaar.goods.models import Product, ProductSet, CompositeProduct
from bazaar.helpers import FormHelperMixin


class EanValidationMixin(forms.ModelForm):
    ean = forms.CharField(max_length=20, required=False)

    def clean_ean(self):
        form_ean = self.cleaned_data['ean']
        saved_ean = self.instance.ean
        inserting = self.instance.pk is None

        if not form_ean:
            return form_ean

        if inserting or (form_ean != saved_ean):
            if Product.objects.filter(ean=form_ean).exists():
                raise ValidationError(u'A product with this ean already exists')

        return form_ean


class ProductForm(EanValidationMixin, FormHelperMixin, forms.ModelForm):
    code = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                '',
                'name',
                'description',
                'ean',
                'code',
                'photo',
                'price'
            ),
            FormActions(
                Div(
                    HTML("""<a class="btn btn-default" href="{% url 'bazaar:product-list' %}">"""
                         """<i class="glyphicon glyphicon-chevron-left"></i>&nbsp;Back</a>&nbsp;"""),
                    Submit('save', 'Submit'),
                    css_class="col-md-8 col-md-offset-3"
                ),
                css_class="form-group"
            )
        )

    class Meta:
        model = Product
        exclude = ("price_lists", )


class CompositeProductForm(EanValidationMixin, FormHelperMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CompositeProductForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                '',
                'name',
                'description',
                'photo',
                'price'
            )
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    class Meta:
        model = CompositeProduct
        exclude = ("products", )


class ProductSetForm(forms.ModelForm):
    class Meta:
        model = ProductSet
        exclude = ("composite",)

    def __init__(self, *args, **kwargs):
        super(ProductSetForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset(
                '',
                'product',
                'quantity',
                css_class='formset'
            )
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

ProductSetFormSet = modelformset_factory(ProductSet, form=ProductSetForm, min_num=1, validate_min=True, extra=0)
