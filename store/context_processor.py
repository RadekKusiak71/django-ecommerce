from store.models import Category, Customer


def categories_context(request):
    categories = Category.objects.all()
    return {'categories': categories}


def get_customer(request):
    customer = Customer.objects.get(user=request.user)
    return {'customer': customer}
