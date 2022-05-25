from django import forms 
from .models import add_img_table, img_helper_table, img_processed_table

class add_img_form(forms.ModelForm):
    class Meta:
        model = add_img_table
        fields = ('img_category','img_id',  'n_color', 'img_label', 'img_file')
        labels = { 
            'img_category': 'Image Category', 
            'img_id': 'Image ID',
            'n_color': 'Number of Colors',
            'img_label': 'Image Label', 
            'img_file': 'Image File'

        }
    def __init__(self, *args, **kwargs):
        super(add_img_form, self).__init__(*args, **kwargs)
        self.fields['img_category'].empty_label = 'Select a Category'

# class search_img_form(forms.ModelForm):
#     class Meta:
#         model = img_processed_table
#         fields = ('id','img_id', 'img_category' 'n_color','img_h','img_w','img_type','isRGB', 'img_label', 'img_file')
#         labels = { 
#             'img_category': 'Category', 
#             'img_id': 'Image ID',
#             'n_color': 'Colors',
#             'img_label': 'Image Label', 
#             'img_file': 'Image File',
#             'img_h': 'Image Height',
#             'img_w': 'Image Width',
#             'img_type': 'Image Type',
#             'isRGB': 'Is RGB'

#         }
#     def __init__(self, *args, **kwargs):
#         super(search_img_form, self).__init__(*args, **kwargs)
        

