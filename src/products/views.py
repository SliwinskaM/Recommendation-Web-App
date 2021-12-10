from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View, ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Product
from .forms import ProductForm, RawProductForm



class ProductListView(LoginRequiredMixin, ListView):
    queryset = Product.objects.all() # przefiltruj tu po sklepie


class ProductDetailView(LoginRequiredMixin, DetailView):
    #queryset = Product.objects.all() # przefiltruj tu po sklepie

    def get_object(self): #niepotrzebne to xd, chyba że bd rozbudowywać przechwytywanie błędów?
        id_ = self.kwargs.get("id")
        return get_object_or_404(Product, id=id_)


class ProductCreateView(LoginRequiredMixin, CreateView):
    template_name = 'products/product_create.html'
    form_class = ProductForm
    queryset = Product.objects.all()


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'products/product_delete.html'

    def get_object(self): #niepotrzebne to xd, chyba że bd rozbudowywać przechwytywanie błędów?
        id_ = self.kwargs.get("id")
        return get_object_or_404(Product, id=id_)

    def get_success_url(self):
        return reverse('product_list')



# def product_create_view(request):
#     form = RawProductForm()
#     if request.method == "POST":
#         form = RawProductForm(request.POST)
#         if form.is_valid():
#             print(form.cleaned_data)
#             Product.objects.create(**form.cleaned_data)
#         else:
#             print(form.errors)
#
#     context = {
#         'form': form
#     }
#     return render(request, "products/product_create.html", context)


# def product_list_view(request):
#     queryset = Product.objects.all()
#     context = {
#         'object_list': queryset
#     }
#     return render(request, "products/product_list.html", context)


# def product_detail_view(request, pk):
#     obj = Product.objects.get(id=pk)
#     context = {
#         'object': obj
#     }
#     return render(request, "products/product_detail.html", context)

# def product_add_view(request):
#     form = ProductForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#         form = ProductForm(request.POST or None)
#
#     context = {
#         'form': form
#     }
#     return render(request, "products/product_create.html", context)