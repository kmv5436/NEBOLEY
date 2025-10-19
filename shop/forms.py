from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    agree_to_terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'Вы должны согласиться с условиями перед оформлением заказа'},
        label='Я согласен с условиями обработки персональных данных и политикой возврата'
    )
    
    class Meta:
        model = Order
        fields = [
            'customer_name', 
            'customer_email', 
            'customer_phone', 
            'customer_address', 
            'customer_comment',
            'agreed_to_terms'  # добавляем новое поле
        ]
        widgets = {
            'customer_comment': forms.Textarea(attrs={'rows': 4}),
            'agreed_to_terms': forms.HiddenInput()  # скрытое поле для сохранения в модель
        }