from django.db import models

#upload to the folder
def img_path(instance, filename):
    return '{0}/{1}/{2}/{3}'.format(instance.img_category,instance.n_color, instance.img_id, filename)

# Create your models here.
class img_categories(models.Model): # I used to create media structured folder image helper information
    img_categ = models.CharField(max_length=150)    

    def __str__(self):
        return self.img_categ
    class Meta:
        db_table="webapp_img_categories"

class add_img_table(models.Model):
    img_category = models.ForeignKey(img_categories, on_delete=models.CASCADE)
    img_id =models.CharField(max_length=150)
    n_color = models.IntegerField(default=1)
    img_label = models.TextField(blank=True, null=True)
    img_file = models.ImageField(upload_to= img_path) #upload to the folder
    img_thumbs = models.ImageField(upload_to= img_path, blank=True, null=True)     
    
    def __str__(self):
        return self.img_id
    class Meta:
        db_table="webapp_add_img_table"

class img_processed_table(models.Model):
    img_category = models.ForeignKey(img_categories, on_delete=models.CASCADE)
    img_id =models.CharField(max_length=150)    
    n_color = models.IntegerField(default=1)
    img_file = models.ImageField(upload_to= img_path)
    img_thumbs = models.ImageField(upload_to= img_path, blank=True, null=True) 
    img_h = models.IntegerField(default=1920)
    img_w = models.IntegerField(default=1080)
    img_type = models.CharField(max_length=150)
    isRGB =models.BooleanField()
    img_label = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.img_id
    class Meta:
        db_table="webapp_img_processed_table"

class img_helper_table(models.Model): # used to create media structured folder image helper information
    img_category = models.CharField(max_length=150)
    n_color = models.IntegerField(default=1)
    img_id =models.CharField(max_length=150)    
   

    def __str__(self):
        return self.img_id

    class Meta:
        db_table="webapp_img_helper_table"





