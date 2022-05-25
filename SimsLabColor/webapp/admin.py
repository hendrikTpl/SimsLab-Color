from django.contrib import admin
from .models import add_img_table, img_helper_table, img_processed_table, img_categories

# Register your models here.
admin.site.register(add_img_table)
admin.site.register(img_helper_table)
admin.site.register(img_processed_table)
admin.site.register(img_categories)



