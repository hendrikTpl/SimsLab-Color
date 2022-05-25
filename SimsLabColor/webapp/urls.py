from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('add/', views.add_img, name='add_img'),
    path('process_img/', views.process_img, name='process_img'),
    path('search/', views.search, name='search'),
    path('show/', views.show_img, name='show_img'),
    path('show_real/<int:id>', views.show_real, name='show_real'),
    path('show_ori/<int:id>', views.show_ori, name='show_ori'),
    path('showlist/', views.showlist, name='showlist'),
    path('guide/', views.guide, name='guide'),
    path('edit/<int:pk>', views.edit_img, name='edit_img'),
    path('remove/<int:pk>', views.remove_img, name='remove_img'),
    path('tambah/', views.tambah, name='tambah'),
    path('tambah/tambah_proc/', views.tambah_proc, name='tambah_proc'),
    path('hapus/<int:id>', views.hapus, name='hapus'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
