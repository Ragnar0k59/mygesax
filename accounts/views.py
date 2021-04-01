from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponse, JsonResponse
import csv
import json
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from base.models import UserProfile


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

def csv_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'
    
    writer = csv.writer(response)
    
    for index,user in enumerate(User.objects.values()):
        if index == 0:
            writer.writerow([k for k in user])

        writer.writerow([v for k,v in user.items()])        
    return response

def csv_import(request):
    try:
        if request.method == 'POST':
            body_unicode = request.body.decode('utf-8')
            data = body_unicode.split('\n')[4:]
            data_tmp = '\r'.join(data).split('\r')
            data_tmp = [value for value in data_tmp if not value == '']
            data = data_tmp[:-1]
            user_keys = data[0].split(',')

            for user in data[1:]:
                typed_user = []
                for value in user.split(','):
                    if value == 'True':
                        value = True
                    elif value == 'False':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    else:
                        value = value
                    typed_user.append(value)
                userToCreate = list(zip(user_keys, typed_user))
                u = User(**{k: v for k, v in userToCreate})
                u.save()
            
            return JsonResponse({'message': 'Users imported successfully.', 'error': False})
    except:
        return JsonResponse({'message': 'An error occurred.', 'error': True})

def save_user_profile(sender, instance, signal, *args, **kwargs):
    if sender is User:
        UserProfile.objects.create(user=instance, avatar="")
        
post_save.connect(save_user_profile, sender=User)