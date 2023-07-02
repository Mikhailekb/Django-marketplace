from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from app_shops.models.shop import ProductShop
from .cart import Cart


def cart_add(request, product_shop_id):
    quantity = request.POST.get('quantity')
    if isinstance(quantity, str) and quantity.isdigit():
        quantity = min(int(quantity), 10000)
    else:
        quantity = 1
    cart = Cart(request)
    product_shop = get_object_or_404(ProductShop.objects.with_discount_price(), id=product_shop_id)
    cart.add(product_shop=product_shop, quantity=quantity)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart_change_quantity(request, product_shop_id, type):
    cart = Cart(request)
    product_shop = get_object_or_404(ProductShop, id=product_shop_id)
    if type == 'plus':
        cart.add(product_shop=product_shop)
    elif type == 'minus':
        cart.minus(product_shop=product_shop)
    return redirect('cart_detail')


def cart_remove(request, product_shop_id):
    cart = Cart(request)
    cart.remove(product_shop_id)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    cart.validate_goods()

    return render(request, 'pages/cart.html', {'cart': cart})
