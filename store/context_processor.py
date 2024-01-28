from store.models import Category, Customer


def categories_context(request):
    categories = Category.objects.all()
    return {'categories': categories}


def get_customer(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        return {'customer': customer}
    return {'customer': 'Not logged in'}
