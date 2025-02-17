from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from datetime import datetime

from customer.forms import CommentForm
from customer.forms import CustomerForm
from customer.models import Comment
from customer.models import Customer


#def get_customers(request):
    #customers = Customer.objects.all()
    #paginator = Paginator(customers, 3)
    #page_number = request.GET.get("page")
    #return paginator.get_page(page_number)


#def customers(request):
    #return render(
        #request=request,
        #context={"customer_list": get_customers(request)},
        #template_name="customer/customer_list.html",
    #)


#def customer_create(request):                        # reemplazo de create_customer por customer_create
    #if request.method == "POST":
        #customer_form = CustomerForm(request.POST)
        #if customer_form.is_valid():
            #data = customer_form.cleaned_data
            #actual_objects = Customer.objects.filter(
                #code=data["code"],
                #name=data["name"],
                #email=data["email"],
                #segment=data["segment"],
            #).count()
            #print("actual_objects", actual_objects)
            #if not actual_objects:
                #customer = Customer(
                    #code=data["code"],
                    #name=data["name"],
                    #email=data["email"],
                    #segment=data["segment"],                
                #)
                #customer.save()
                #messages.success(
                    #request,
                    #f"Customer {data['code']} - {data['name']} creado exitosamente!",
                #)
                #return render(
                    #request=request,
                    #context={"customer_list": get_customers(request)},
                    #template_name="customer/customer_list.html",
                #)
            #else:                
                #messages.error(
                    #request,
                    #f"El cliente {data['code']} - {data['name']} ya está creado",
                #)
   
    #customer_form = CustomerForm(request.POST)
    #context_dict = {"form": customer_form}
    #return render(
        #request=request,
        #context=context_dict,
        #template_name="customer/customer_form.html",
    #)

#def customer_detail(request, pk: int):
    #return render(
        #request=request,
        #context={"customer": Customer.objects.get(pk=pk)},
        #template_name="customer/customer_detail.html",
    #)


#def customer_update(request, pk: int):
    #customer = Customer.objects.get(pk=pk)

    #if request.method == "POST":
        #customer_form = CustomerForm(request.POST)
        #if customer_form.is_valid():
            #data = customer_form.cleaned_data
            #customer.code = data["code"]
            #customer.name = data["name"]
            #customer.email = data["email"]
            #customer.segment = data["segment"]
            #customer.save()

            #return render(
                #request=request,
                #context={"customer": customer},
                #template_name="customer/customer_detail.html",
            #)

    #customer_form = CustomerForm(model_to_dict(customer))
    #context_dict = {
        #"customer": customer,
        #"form": customer_form,
    #}
    #return render(
        #request=request,
        #context=context_dict,
        #template_name="customer/customer_form.html",
    #)


#def customer_delete(request, pk: int):
    #customer = Customer.objects.get(pk=pk)
    #if request.method == "POST":
        #customer.delete()

        #customers = Customer.objects.all()
        #context_dict = {"customer_list": customers}
        #return render(
            #request=request,
            #context=context_dict,
            #template_name="customer/customer_list.html",
        #)

    #context_dict = {
        #"customer": customer,
    #}
    #return render(
        #request=request,
        #context=context_dict,
        #template_name="customer/customer_confirm_delete.html",
    #)


#from django.core.exceptions import ValidationError
#from django.urls import reverse_lazy
#from django.views.generic import ListView
#from django.views.generic.detail import DetailView
#from django.views.generic.edit import CreateView, UpdateView, DeleteView

#from customer.models import Customer


class CustomerListView(ListView):
    model = Customer
    paginate_by = 8


class CustomerDetailView(DetailView):
    model = Customer
    template_name = "customer/customer_detail.html"
    fields = ["code", "name", "email", "segment"]

    def get(self, request, pk):
        customer = Customer.objects.get(id=pk)
        comments = Comment.objects.filter(customer=customer).order_by("-updated_at")
        comment_form = CommentForm()
        context = {
            "customer": customer,
            "comments": comments,
            "comment_form": comment_form,
        }
        return render(request, self.template_name, context)    
    


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    success_url = reverse_lazy("customer:customer-list")

    form_class = CustomerForm
    # fields = ["code", "name", "email", "segment", "image"]

    def form_valid(self, form):
        """Filter to avoid duplicate customers"""
        data = form.cleaned_data
        form.instance.owner = self.request.user
        actual_objects = Customer.objects.filter(
            code=data["code"], name=data["name"]
        ).count()
        if actual_objects:
            messages.error(
                self.request,
                f"El cliente {data['code']} - {data['name']} ya está creado",
            )
            form.add_error("name", ValidationError("Acción no válida"))
            return super().form_invalid(form)
        else:
            messages.success(
                self.request,
                f"Cliente {data['code']} - {data['name']} creado exitosamente!",
            )
            return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    fields = ["code", "name", "email", "segment", "image"]

    def get_success_url(self):
        customer_id = self.kwargs["pk"]
        return reverse_lazy("customer:customer-detail", kwargs={"pk": customer_id})

    #def post(self):
        #pass

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy("customer:customer-list")
    
class CommentCreateView(LoginRequiredMixin, CreateView):
    def post(self, request, pk):
        customer = get_object_or_404(Customer, id=pk)
        comment = Comment(
            text=request.POST["comment_text"], owner=request.user, customer=customer
        )
        comment.save()
        return redirect(reverse("customer:customer-detail", kwargs={"pk": pk}))


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment

    def get_success_url(self):
        customer = self.object.customer
        return reverse("customer:customer-detail", kwargs={"pk": customer.id})

    


