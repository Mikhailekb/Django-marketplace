from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from app_shops.models.shop import ProductShop
from .cart import Cart


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(ProductShop, id=product_id)
    cart.add(product=product)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart_change_quantity(request, product_id, type):
    cart = Cart(request)
    product = get_object_or_404(ProductShop, id=product_id)
    if type == 'plus':
        cart.add(product=product)
    elif type == 'minus':
        cart.minus(product=product)
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(ProductShop, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)

    return render(request, 'pages/cart.html', {'cart': cart})
