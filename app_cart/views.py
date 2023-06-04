from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from app_shops.models.shop import ProductShop
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(ProductShop, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
    return redirect('home')


@require_POST
def cart_change_quantity(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(ProductShop, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=True)
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(ProductShop, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    form = CartAddProductForm()
    return render(request, 'app_cart/detail.html', {'cart': cart, 'form': form})
