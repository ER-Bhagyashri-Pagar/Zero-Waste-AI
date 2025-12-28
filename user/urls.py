# OPTION 1: Remove spline from urls.py (QUICKEST FIX)
# In user/urls.py, simply REMOVE or COMMENT OUT this line:

from django.urls import path
from . import views

urlpatterns = [
    path('base/', views.base, name='base'),
    path('test/', views.test, name='test'),
    path('', views.upload_image_and_voice_input, name='upload_image_and_voice_input'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_food/', views.add_food, name='add_food'),
    path('upload/', views.upload_image_and_voice_input, name='upload'),
    path('fruit_detect/', views.index1, name='fruit_detect'),
    path('video_feed1/', views.video_feed1, name='video_feed1'),
    path('get_detections1/', views.get_detections1, name='get_detections1'),
    path('recipee_slider/', views.recipee_slider, name='recipee_slider'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('rotting_index/', views.rotting_index, name='rotting_index'),
    # path('spline/', views.spline, name='spline'),  # COMMENTED OUT
    path('community/', views.community, name='community'),
    path('chatbot/send/', views.chatbot_send, name='chatbot_send'),
    path('recipe-generator/', views.recipe_generator, name='recipe_generator'),
    path('recipe/generate/', views.generate_recipe_api, name='generate_recipe_api'),
]

# ===================================================================

# OPTION 2: Add spline view to views.py
# Add this function to your views.py:

def spline(request):
    """Shelf Optimize page"""
    return render(request, 'user/spline.html')

# Then keep the URL in urls.py# OPTION 1: Remove spline from urls.py (QUICKEST FIX)
# In user/urls.py, simply REMOVE or COMMENT OUT this line:

from django.urls import path
from . import views

urlpatterns = [
    path('base/', views.base, name='base'),
    path('test/', views.test, name='test'),
    path('', views.upload_image_and_voice_input, name='upload_image_and_voice_input'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_food/', views.add_food, name='add_food'),
    path('upload/', views.upload_image_and_voice_input, name='upload'),
    path('fruit_detect/', views.index1, name='fruit_detect'),
    path('video_feed1/', views.video_feed1, name='video_feed1'),
    path('get_detections1/', views.get_detections1, name='get_detections1'),
    path('recipee_slider/', views.recipee_slider, name='recipee_slider'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('rotting_index/', views.rotting_index, name='rotting_index'),
    # path('spline/', views.spline, name='spline'),  # COMMENTED OUT
    path('community/', views.community, name='community'),
    path('chatbot/send/', views.chatbot_send, name='chatbot_send'),
    path('recipe-generator/', views.recipe_generator, name='recipe_generator'),
    path('recipe/generate/', views.generate_recipe_api, name='generate_recipe_api'),
]

# ===================================================================

# OPTION 2: Add spline view to views.py
# Add this function to your views.py:

def spline(request):
    """Shelf Optimize page"""
    return render(request, 'user/spline.html')

# Then keep the URL in urls.py