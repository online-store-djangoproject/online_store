"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

admin.site.site_header = 'online store kian'
admin.site.site_title = 'online store Administration'
admin.site.index_title = 'Welcome To online store kian Administration'


urlpatterns = [
    path('admin/', admin.site.urls),

#     API
    path('',include('cors.urls')),
    path('',include('userprofile.urls')),
    path('',include('products.urls')),
    path('',include('orders.urls')),


#     template_name

    path('', TemplateView.as_view(template_name='home/base.html'), name='base'),
    path('req/', TemplateView.as_view(template_name='home/register.html'), name='req'),
    path('choicelog/', TemplateView.as_view(template_name='home/choiceloging.html'), name='choicelog'),
    path('log/', TemplateView.as_view(template_name='home/login.html'), name='log'),
    path('log2/', TemplateView.as_view(template_name='home/login2.html'), name='log2'),
    path('basepro/', TemplateView.as_view(template_name='home/base_profile.html'), name='basepro'),
    path('pro/', TemplateView.as_view(template_name='home/profile.html'), name='pro'),
    path('proaddress/', TemplateView.as_view(template_name='home/profile_address.html'), name='proaddress'),
    path('passreq/', TemplateView.as_view(template_name='home/password_request.html'), name='passreq'),
    path('passcon/', TemplateView.as_view(template_name='home/password_confirm.html'), name='passcon'),
    path('pproductt/', TemplateView.as_view(template_name='home/products.html'), name='pproductt'),
    path('check/', TemplateView.as_view(template_name='home/checkout.html'), name='checkout'),
    path('successs/', TemplateView.as_view(template_name='home/success.html'), name='successs'),
    path('orderss/', TemplateView.as_view(template_name='home/orders.html'), name='orderss'),

]


if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)