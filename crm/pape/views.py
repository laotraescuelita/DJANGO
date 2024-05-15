import pandas as pd 
from django.contrib.auth.models import User
from django.http import HttpResponse
import json
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .models import Item, OrderItem, Order
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ( 
    ListView, 
    DetailView, 
    CreateView,
    UpdateView,
    DeleteView,
	View
)

def search_product(request):
	item = request.GET.get('search')
	context = {'items' : Item.objects.filter(nombre__icontains=item)}
	return render(request, 'pape/home.html', context)

def delete_products(requets):

    # Obtener los productos del modelo Producto como un queryset
    Item.objects.all().delete()
    
    return HttpResponse('Los productos deben estar eliminados.')

def upload_products(request):
	#Obtenemos el usuario
	user = User.objects.get(id=1)
	
	#Cargamos los datos del archivo de excel.	
	datos_csv = pd.read_csv('C:\\Users\\erick\\OneDrive\\Escritorio\\Erick\\Proyectos_Papeleria\\pape_crm_3\\datos_excel.csv', sep=";")	
	
	for index, item in datos_csv.iterrows():		
		product = Item(
		nombre=item['nombre'],
		precio=item['precio'],
		lugar=item['lugar'],
		categoria=item['categoria'],
		cantidad=item['cantidad'],
		author=user
		)		
		product.save()
	
	
	return HttpResponse('Los productos se han cargado exitosamente en la base de datos.')


def descargar_productos(request):
    
    def decimal_to_float(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    # Obtener los productos del modelo Producto como un queryset
    products = Item.objects.all()

    # Convertir el queryset a una lista de diccionarios
    products_dict = list(products.values('nombre', 'precio', 'lugar', 'categoria', 'created_at', 'author'))

    # Convertir los objetos Decimal a números de punto flotante antes de serializar
    products_json = json.dumps(products_dict, default=decimal_to_float)

    # Escribir los datos de los productos en formato JSON en un archivo
    with open('products.json', 'w') as archivo:
        archivo.write(products_json)
    
    return HttpResponse('Se ha creado el archivo json.')

class ProductListView(ListView):
	model = Item
	template_name = 'pape/home.html'
	context_object_name = 'items'
	paginate_by = 10

class ProductDetailView(DetailView):
    model = Item

class ItemDetailView(DetailView):
	model = Item 
	template_name = 'pape/item.html'

class ProductCreateView(LoginRequiredMixin, CreateView):
	model = Item
	fields = ['nombre', 'precio', 'lugar', 'categoria', 'cantidad_inventario']
	
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)
	
class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Item
	fields = ['nombre', 'precio', 'lugar', 'categoria', 'cantidad']
	
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)
	
	def test_func(self):
		product = self.get_object()
		if self.request.user == product.author:
			return True
		return False

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Item
	success_url = "/"

	def test_func(self):
		product = self.get_object()
		if self.request.user == product.author:
			return True
		return False

class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(author=self.request.user, ordered=False)
			context = {
				'object':order
			}
			return render(self.request, 'pape/order_summary.html', context)
		except ObjectDoesNotExist:
			messages.warning(request, 'No tienes una orden activa.')
			return redirect("/")

@login_required
def add_to_cart(request, pk):
	item = get_object_or_404(Item, pk=pk)
	order_item, created = OrderItem.objects.get_or_create(
		item=item,
		author=request.user,
		ordered=False
	)
	order_qs = Order.objects.filter(author=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		#verificar que el item esta en la order.
		if order.items.filter(item__pk=item.pk).exists():
			order_item.cantidad_ordenada +=1
			order_item.save()
			messages.info(request, "La cantidad de este artículo se actualizo.")
			return redirect('order-summary')
		else:
			order.items.add(order_item)
			messages.info(request, 'Este produco fue agregado al carrito.')
			return redirect('order-summary')
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(
			author=request.user, 
			fecha_orden=ordered_date
		)
		order.items.add(order_item)
		messages.info(request, 'Este produco fue agregado al carrito.')
		return redirect('order-summary')

@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(
        author=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                author=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "Este producto se quito de tu carrito.")
            return redirect("order-summary")
        else:
            messages.info(request, "Este prodcuto no esta en tu carrito.")
            return redirect("pape-detail", pk=pk)
    else:
        messages.info(request, "No tienes una orden activa.")
        return redirect("pape-detail", pk=pk)



@login_required
def remove_single_item_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(
        author=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                author=request.user,
                ordered=False
            )[0]
            if order_item.cantidad_ordenada > 1:
                order_item.cantidad_ordenada -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "La cantidad de este producto se actualizo.")
            return redirect("order-summary")
        else:
            messages.info(request, "Este producto no esta en tu carrito.")
            return redirect("pape-detail", pk=pk)
    else:
        messages.info(request, "No tienes una orden activa.")
        return redirect("pape-detail", pk=pk)
