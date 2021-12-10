from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import CreateView, ListView

from .forms import RatingForm
from .models import Rating
from products.models import Product
from recommendation import import_data


# class RatingCreateView(LoginRequiredMixin, CreateView):
#     template_name = 'ratings/rating_create.html'
#     form_class = RatingForm
#     queryset = Rating.objects.all()

def rating_create_view(request):
    form = RatingForm(request.POST or None, initial={'user': request.user})
    if form.is_valid():
        form.save()
        data = import_data.ImportData('smoker')
        data.add_rating(form.cleaned_data['user'], form.cleaned_data['product'], form.cleaned_data['score'])
        form = RatingForm(request.POST or None, initial={'user': request.user})

    context = {
        'form': form
    }
    return render(request, 'ratings/rating_create.html', context)


def rating_product_view(request, p_id):
    product = Product.objects.get(id=p_id)
    form = RatingForm(request.POST or None, initial={'user': request.user, 'product': product.name})
    if form.is_valid():
        form.save()
        data = import_data.ImportData('smoker')
        data.add_rating(form.cleaned_data['user'], form.cleaned_data['product'], form.cleaned_data['score'])
        form = RatingForm(request.POST or None, initial={'user': request.user})

    context = {
        'form': form
    }
    return render(request, 'ratings/rating_create.html', context)


class RatingListView(LoginRequiredMixin, ListView):
    template_name = 'ratings/rating_list.html'
    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)



