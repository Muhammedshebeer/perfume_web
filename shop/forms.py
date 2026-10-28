from django import forms
from .models import Product, Inquiry, Order, Brand, Category
from .validators import validate_product_image

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','slug','sku','brand','category','description','price','compare_at_price','size_ml',
                'concentration','top_notes','heart_notes','base_notes','stock','is_featured','is_active','image','image_alt']
        widgets={'description':forms.Textarea(attrs={'rows':4}),
                 'image':forms.FileInput(attrs={'accept':'image/jpeg,image/png,image/webp','id':'main-image-input'})}
    def clean_image(self):
        image=self.cleaned_data.get('image')
        if image:
            validate_product_image(image)
        elif not self.instance.pk:
            raise forms.ValidationError('A main product image is required.')
        return image
    def clean(self):
        data=super().clean()
        compare=data.get('compare_at_price')
        price=data.get('price')
        if compare is not None and price is not None and compare <= price:
            self.add_error('compare_at_price','Compare-at price must exceed the selling price.')
        return data

class InquiryForm(forms.ModelForm):
    class Meta: model=Inquiry; fields=['name','email','phone','message']; widgets={'message':forms.Textarea(attrs={'rows':4})}

class CheckoutForm(forms.ModelForm):
    class Meta: model=Order; fields=['name','email','phone','address','city','notes']; widgets={'address':forms.Textarea(attrs={'rows':3}),'notes':forms.Textarea(attrs={'rows':2})}
