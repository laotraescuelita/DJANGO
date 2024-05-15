from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

#las categorias nos ayudaran a saber a que departamento pertenecen.
CATEGORIAS_SELECCIONADAS = (
    ('escolar', 'escolar'),
    ('papel', 'papel'),
    ('regalos_fiestas','regalos_fiestas'),
    ('monografias','monografias'),
    ('biografias', 'biografias'),
    ('animales', 'animales'),
    ('animales_marinos', 'animales_Marinos'),
    ('microorganismos', 'microorganismos'),
    ('aves', 'aves'),
    ('flores', 'flores'),
    ('comestibles', 'comestibles'),
    ('arboles', 'arboles'),
    ('dinosaurios', 'dinosaurios'),
    ('acontecimientos', 'acontecimientos'),
    ('mapas', 'mapas'),
    ('esquemas', 'esquemas'),
    ('hule', 'hule'),
    ('unicel', 'unicel'),
    ('madera', 'madera'),
)


class Item(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.FloatField()
    lugar = models.CharField(max_length=10, blank=True)
    categoria = models.CharField(choices=CATEGORIAS_SELECCIONADAS, max_length=20, default="escolar", blank="")
    cantidad_inventario = models.IntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE) #Este campo ligas las tablas Record y User.
    
    def __str__(self):
        return(f"{self.nombre} {self.cantidad_inventario}")

    def get_absolute_url(self):
        return reverse('pape-detail', kwargs={'pk':self.pk})
    
    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={'pk':self.pk})
    
    def get_remove_to_cart(self):
        return reverse('remove-from-cart', kwargs={'pk':self.pk})



class OrderItem(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cantidad_ordenada = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.cantidad_ordenada} de {self.item.nombre}'

    def get_total_item_price(self):
        return self.cantidad_ordenada * self.item.precio

class Order(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)    
    items = models.ManyToManyField(OrderItem)
    fecha_orden = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.author.username
    
    def get_total(self):
        total = 0 
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total

