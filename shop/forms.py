from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer_name', 
            'customer_email', 
            'customer_phone', 
            'customer_address', 
            'customer_comment'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите ваше имя'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@example.com'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'customer_address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Введите адрес доставки',
                'rows': 3
            }),
            'customer_comment': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Дополнительные пожелания (необязательно)',
                'rows': 2
            }),
        }
        labels = {
            'customer_name': 'Ваше имя',
            'customer_email': 'Email',
            'customer_phone': 'Телефон',
            'customer_address': 'Адрес доставки',
            'customer_comment': 'Комментарий к заказу',
        }