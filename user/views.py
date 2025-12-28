from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from PIL import Image
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from twilio.rest import Client
from ultralytics import YOLO
import google.generativeai as genai
import cv2
import numpy as np
import json
import os
import logging
import threading
from django.views.decorators.csrf import csrf_exempt

from .models import FoodItem

load_dotenv()
logger = logging.getLogger(__name__)

# ============ CONFIGURATION ============
API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

if account_sid and auth_token:
    client = Client(account_sid, auth_token)
else:
    client = None
    logger.warning("Twilio credentials not found. Notifications disabled.")

def send_twilio_notification():
    if not client:
        logger.warning("Twilio client not configured. Skipping notification.")
        return
    
    try:
        # Send notification to BOTH your numbers
        numbers = ['+17814731752', '+917499752800']  # Your two numbers
        
        for number in numbers:
            # Send text alert
            client.messages.create(
                from_='whatsapp:+14155238886',
                body="🍌 Alert! Your banana has started rotting! 🍌 Consider making a recipe today! 😋",
                to=f'whatsapp:{number}'
            )
            
            # Send recipe suggestion with image
            client.messages.create(
                from_='whatsapp:+14155238886',
                media_url=['https://static.toiimg.com/thumb/msid-67569905,width-400,resizemode-4/67569905.jpg'],
                body="Here's a recipe suggestion! 🍌🥛",
                to=f'whatsapp:{number}'
            )
        
        logger.info(f"Notifications sent successfully to {len(numbers)} numbers")
        
    except Exception as e:
        logger.error(f"Error sending Twilio notification: {e}")

# Global variables
detected_objects = []
expiry_notifications_sent = {}
model = None
cap = None

# ============ FRUITS AND VEGETABLES FILTER ============
FRUITS_VEGETABLES = {
    "apple": 7,
    "banana": 5,
    "orange": 10,
    "carrot": 14,
    "broccoli": 5,
    "tomato": 7,
    "potato": 21,
    "onion": 30,
    "grapes": 7,
    "strawberry": 3,
    "lettuce": 5,
    "cucumber": 7,
    "avocado": 4,
    "mango": 5,
    "watermelon": 7,
    "pineapple": 5,
    "lemon": 14,
    "peach": 4,
    "pear": 7,
}

# ============ RECIPE DATABASE ============
RECIPE_DATA = {
    'banana': {
        'name': 'Banana Shake',
        'image_url': 'https://static.toiimg.com/thumb/msid-67569905,width-400,resizemode-4/67569905.jpg',
        'emoji': '🍌'
    },
    'apple': {
        'name': 'Apple Smoothie',
        'image_url': 'https://www.vegrecipesofindia.com/wp-content/uploads/2021/04/apple-smoothie-1.jpg',
        'emoji': '🍎'
    },
    'orange': {
        'name': 'Orange Juice',
        'image_url': 'https://www.alphafoodie.com/wp-content/uploads/2022/02/Orange-Juice-Square.jpeg',
        'emoji': '🍊'
    },
    'default': {
        'name': 'Quick Recipe',
        'image_url': 'https://static.toiimg.com/thumb/msid-67569905,width-400,resizemode-4/67569905.jpg',
        'emoji': '🥗'
    }
}

def get_recipe_info(fruit_name):
    """Get recipe information for a fruit"""
    fruit_lower = fruit_name.lower()
    return RECIPE_DATA.get(fruit_lower, RECIPE_DATA['default'])

# ============ NOTIFICATION FUNCTION ============
def check_and_notify_expiry(label, days_left, confidence):
    """Send notification if confidence >= 60% and days_left <= 5"""
    global expiry_notifications_sent
    
    print(f"\n{'='*60}")
    print(f"📱 NOTIFICATION CHECK:")
    print(f"   Item: {label}")
    print(f"   Days Left: {days_left}")
    print(f"   Confidence: {confidence*100:.1f}%")
    print(f"{'='*60}")
    
    # Check if Twilio is configured
    if not client:
        print("❌ Twilio client not configured!")
        return
    
    # Check confidence threshold (60%)
    if confidence < 0.60:
        print(f"⏭️ Confidence {confidence*100:.1f}% is below 60% threshold")
        return
    
    print(f"✅ Confidence {confidence*100:.1f}% meets 60% threshold")
    
    # Check days left threshold (5 days)
    if days_left is None or days_left > 5:
        print(f"⏭️ Days left ({days_left}) is above 5 days threshold")
        return
    
    print(f"✅ Days left ({days_left}) is within 5 days threshold")
    
    # Duplicate check
    notification_key = f"{label}_{days_left}_{date.today().strftime('%Y%m%d')}"
    if notification_key in expiry_notifications_sent:
        print(f"⏭️ Notification already sent today for {label}")
        return
    
    print(f"✅ Ready to send notification")
    
    try:
        number = '+17814731752'
        recipe_info = get_recipe_info(label)
        emoji = recipe_info['emoji']
        recipe_name = recipe_info['name']
        
        # Create message based on days left
        if days_left == 0:
            urgency = "🚨 CRITICAL"
            message = f"{urgency}! Your {label} expires TODAY! {emoji}\n\n"
        elif days_left == 1:
            urgency = "⚠️ URGENT"
            message = f"{urgency}! Your {label} expires TOMORROW! {emoji}\n\n"
        elif days_left == 2:
            urgency = "⚠️ Alert"
            message = f"{urgency}! Your {label} expires in {days_left} days! {emoji}\n\n"
        elif days_left <= 5:
            urgency = "ℹ️ Reminder"
            message = f"{urgency}: Your {label} expires in {days_left} days. {emoji}\n\n"
        
        message += f"⏰ Days Left: {days_left} day{'s' if days_left != 1 else ''}\n"
        message += f"📊 Detection Confidence: {confidence*100:.1f}%\n\n"
        message += f"🍳 Try making: {recipe_name}!\n"
        message += f"Use it before it goes bad! 🌟"
        
        print(f"📤 Sending notification to {number}...")
        
        # Send main alert
        msg1 = client.messages.create(
            from_='whatsapp:+14155238886',
            body=message,
            to=f'whatsapp:{number}'
        )
        print(f"✅ Alert sent (SID: {msg1.sid}, Status: {msg1.status})")
        
        # Send recipe image
        recipe_msg = f"{emoji} {recipe_name.upper()} RECIPE {emoji}\n\n"
        recipe_msg += f"Perfect for your {label}!\n"
        recipe_msg += f"Quick & Easy • Delicious 🎉"
        
        msg2 = client.messages.create(
            from_='whatsapp:+14155238886',
            media_url=[recipe_info['image_url']],
            body=recipe_msg,
            to=f'whatsapp:{number}'
        )
        print(f"✅ Recipe image sent (SID: {msg2.sid}, Status: {msg2.status})")
        
        expiry_notifications_sent[notification_key] = True
        print(f"\n🎉 SUCCESS! Notification sent to {number}")
        print(f"{'='*60}\n")
        logger.info(f"📱 Notification sent: {label} - {days_left} days - {confidence*100:.1f}%")
        
    except Exception as e:
        print(f"\n❌ NOTIFICATION FAILED!")
        print(f"Error: {str(e)}")
        print(f"{'='*60}\n")
        logger.error(f"Error sending notification: {e}")
        import traceback
        traceback.print_exc()

def calculate_days_left(expiry_date):
    """Calculate days left until expiry"""
    try:
        if isinstance(expiry_date, str):
            for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%d %b %Y']:
                try:
                    expiry_date = datetime.strptime(expiry_date, fmt).date()
                    break
                except ValueError:
                    continue
        
        if isinstance(expiry_date, date):
            days_left = (expiry_date - date.today()).days
            return days_left
    except Exception as e:
        logger.error(f"Error calculating days left: {e}")
    return None

def is_fruit_or_vegetable(label):
    """Check if detected object is a fruit or vegetable"""
    return label.lower() in FRUITS_VEGETABLES

# ============ BASIC VIEWS ============
def base(request):
    return render(request, 'base.html')

def test(request):
    return render(request, 'test.html')

def add_food(request):
    return render(request, 'add_food.html')

def upload_image_and_voice_input(request):
    image_url = None
    expiry_date = None
    image_processed = False

    if request.method == 'POST':
        food_name = request.POST.get('food_name', '')
        expiry_date = request.POST.get('expiry_date', '')
        
        if food_name and expiry_date:
            food_item = FoodItem(name=food_name, expiry_date=expiry_date)
            food_item.save()
            
            days_left = calculate_days_left(expiry_date)
            if days_left is not None and days_left <= 5:
                check_and_notify_expiry(food_name, days_left, 1.0)

        if 'image' in request.FILES:
            uploaded_image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(uploaded_image.name, uploaded_image)
            image_url = fs.url(filename)
            request.session['uploaded_image'] = filename

            try:
                img = Image.open(uploaded_image)
                model = genai.GenerativeModel('gemini-2.0-flash')
                caption_response = model.generate_content(
                    ["Extract the expiry date from this image. Only return the date, e.g., '12th Jan 2024'", img]
                )
                extracted_expiry_date = caption_response.text.strip()
                image_processed = True
                expiry_date = extracted_expiry_date

                if food_name and expiry_date and expiry_date != "Error parsing expiry date":
                    food_item = FoodItem(name=food_name, expiry_date=expiry_date, image=uploaded_image)
                    food_item.save()
                    
                    days_left = calculate_days_left(expiry_date)
                    if days_left is not None and days_left <= 5:
                        check_and_notify_expiry(food_name, days_left, 1.0)

            except Exception as e:
                logger.error(f"Error while processing the image: {e}")
                expiry_date = "Error generating expiry date"
                image_processed = True

            return JsonResponse({
                'expiry_date': str(expiry_date),
                'redirect_url': '/dashboard'
            })
                
    return render(request, 'user/voice_input_form.html', {
        'expiry_date': expiry_date,
        'image_url': image_url,
        'image_processed': image_processed
    })

def dashboard(request):
    food_items = FoodItem.objects.all()

    for item in food_items:
        if isinstance(item.expiry_date, str):
            try:
                item.expiry_date = datetime.strptime(item.expiry_date, '%d %b %Y').date()
            except ValueError:
                item.expiry_date = None
        
        if item.expiry_date:
            days_left = (item.expiry_date - date.today()).days
            
            if item.expiry_date < date.today():
                item.status = 'expired'
            elif days_left <= 5:
                item.status = 'expiring soon'
                check_and_notify_expiry(item.name, days_left, 1.0)
            elif item.expiry_date < (date.today() + timedelta(days=7)):
                item.status = 'expiring this week'
            else:
                item.status = 'good'
        else:
            item.status = 'invalid date'

    return render(request, 'user/dashboard.html', {'food_items': food_items})

def recipee_slider(request):
    return render(request, 'user/recipee_slider.html')

def send_twilio_notification():
    if not client:
        return
    
    try:
        number = '+17814731752'
        recipe_info = get_recipe_info('banana')
        
        client.messages.create(
            from_='whatsapp:+14155238886',
            body=f"🍌 Alert! Your banana has started rotting!\n\nMake a {recipe_info['name']} today! 😋",
            to=f'whatsapp:{number}'
        )
        
        client.messages.create(
            from_='whatsapp:+14155238886',
            media_url=[recipe_info['image_url']],
            body=f"🍌 {recipe_info['name'].upper()} RECIPE\n\nPerfect for ripe bananas! 🥤",
            to=f'whatsapp:{number}'
        )
        
        logger.info("Rotting notification sent")
    except Exception as e:
        logger.error(f"Error sending Twilio notification: {e}")

def gen_frames():
    model = YOLO("yolov8n.pt")
    model.to('cpu')
    
    cap = cv2.VideoCapture("banana2.mp4")
    start_rotting_threshold = 0.1
    fully_rotted_threshold = 0.2
    notification_sent = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detected_area = frame[y1:y2, x1:x2]

                gray = cv2.cvtColor(detected_area, cv2.COLOR_BGR2GRAY)
                _, black_mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
                black_ratio = np.sum(black_mask == 255) / black_mask.size

                if black_ratio > fully_rotted_threshold:
                    stage = "Rotted"
                elif black_ratio > start_rotting_threshold:
                    stage = "Started Rotting"
                    if not notification_sent:
                        send_twilio_notification()
                        notification_sent = True
                else:
                    stage = "Good"

                cv2.putText(frame, "Banana", (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Stage: {stage}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()

def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def rotting_index(request):
    return render(request, 'user/rotting.html')

def community(request):
    return render(request, 'user/community.html')

# ============ REAL-TIME FRUIT DETECTION ============
def process_frame(frame):
    global detected_objects, model
    
    if model is None:
        model = YOLO("yolov8n.pt")
        model.to('cpu')
    
    results = model(frame)
    boxes = results[0].boxes.xyxy
    labels = results[0].names
    confidences = results[0].boxes.conf

    detected_objects.clear()
    processed_items = set()  # Track processed items this frame

    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        label = labels[int(results[0].boxes.cls[i].item())]
        confidence = confidences[i].item()

        # Filter: Only fruits and vegetables
        if not is_fruit_or_vegetable(label):
            continue
        
        # Avoid duplicate processing
        if label in processed_items:
            continue
        processed_items.add(label)
        
        # Try database first
        try:
            food_item = FoodItem.objects.filter(name__iexact=label).first()
            if food_item and food_item.expiry_date:
                if isinstance(food_item.expiry_date, str):
                    expiry_date_obj = datetime.strptime(food_item.expiry_date, '%d %b %Y').date()
                else:
                    expiry_date_obj = food_item.expiry_date
                
                days_left = (expiry_date_obj - date.today()).days
                expiry_text = f"{days_left} days" if days_left != 1 else "1 day"
                
                print(f"📦 {label}: {days_left} days left, confidence: {confidence*100:.1f}%")
                
                # Check notification (confidence >= 60% AND days_left <= 5)
                if confidence >= 0.60 and days_left <= 5:
                    check_and_notify_expiry(label, days_left, confidence)
            else:
                # Calculate based on default + confidence
                base_days = FRUITS_VEGETABLES.get(label.lower(), 7)
                
                # Adjust based on confidence
                if confidence < 0.5:
                    days_left = max(1, base_days - 4)
                elif confidence < 0.7:
                    days_left = max(2, base_days - 2)
                else:
                    days_left = base_days
                
                expiry_text = f"{days_left} days" if days_left != 1 else "1 day"
                
                print(f"🧮 {label}: {days_left} days left (calculated), confidence: {confidence*100:.1f}%")
                
                # Check notification (confidence >= 60% AND days_left <= 5)
                if confidence >= 0.60 and days_left <= 5:
                    check_and_notify_expiry(label, days_left, confidence)
                
        except Exception as e:
            logger.error(f"Error processing {label}: {e}")
            days_left = 7
            expiry_text = "7 days"

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        # Display text
        label_text = f"{label} - {expiry_text} left"
        confidence_text = f"{(confidence * 100):.1f}%"

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, label_text, (x1, y1 - 10), font, 1.0, (0, 255, 0), 2, lineType=cv2.LINE_AA)
        cv2.putText(frame, confidence_text, (x1, y2 + 20), font, 1.0, (0, 255, 0), 2, lineType=cv2.LINE_AA)

        detected_objects.append({
            'class': label,
            'confidence': round(confidence, 2),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'expiry': expiry_text
        })

    return frame

def generate_frames():
    global cap
    
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 30)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_resized = cv2.resize(frame, (640, 480))
        frame_processed = process_frame(frame_resized)

        ret, buffer = cv2.imencode('.jpg', frame_processed)
        if not ret:
            continue
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def index1(request):
    return render(request, 'user/fruit_detection.html')

def video_feed1(request):
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def get_detections1(request):
    return JsonResponse(detected_objects, safe=False)

def chatbot_view(request):
    return render(request, 'pages/chatbot.html')

def chatbot_send(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            genai.configure(api_key='AIzaSyD_a5l81e9k32EqlvDZKPGYTKh7D7hoP94')
            model = genai.GenerativeModel('gemini-2.0-flash')

            prompt = f"""You are a helpful food and recipe assistant. 
            User question: {user_message}
            
            Provide helpful, friendly responses about recipes, ingredients, cooking tips, and food-related queries."""
            
            response = model.generate_content(prompt)
            
            return JsonResponse({
                'success': True,
                'response': response.text
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# REPLACE YOUR EXISTING recipe_generator and generate_recipe_api functions with these:

def recipe_generator(request):
    """Render the recipe generator page"""
    return render(request, 'user/recipe_generator.html')
# Add this helper function to your views.py (above generate_recipe_api):

def format_recipe_response(text):
    """Convert Markdown-style recipe text to HTML"""
    import re
    
    # Replace headers (## Header -> <h3>Header</h3>)
    text = re.sub(r'^##\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^\#\#\#\s+(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    
    # Replace bold (**text** -> <strong>text</strong>)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # Replace bullet points (* item -> <li>item</li>)
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        # Check for bullet points
        if re.match(r'^\s*\*\s+', line):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            # Remove the * and add <li>
            item = re.sub(r'^\s*\*\s+', '', line)
            formatted_lines.append(f'<li>{item}</li>')
        # Check for numbered lists
        elif re.match(r'^\s*\d+\.\s+', line):
            if not in_list:
                formatted_lines.append('<ol>')
                in_list = True
            # Remove the number and add <li>
            item = re.sub(r'^\s*\d+\.\s+', '', line)
            formatted_lines.append(f'<li>{item}</li>')
        else:
            # Close list if we were in one
            if in_list:
                if '<ul>' in formatted_lines[-10:]:  # Check recent lines
                    formatted_lines.append('</ul>')
                else:
                    formatted_lines.append('</ol>')
                in_list = False
            formatted_lines.append(line)
    
    # Close any open list at the end
    if in_list:
        if '<ul>' in '\n'.join(formatted_lines[-20:]):
            formatted_lines.append('</ul>')
        else:
            formatted_lines.append('</ol>')
    
    text = '\n'.join(formatted_lines)
    
    # Replace line breaks
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')
    
    return text


# NOW UPDATE your generate_recipe_api function:

@csrf_exempt
def generate_recipe_api(request):
    """API endpoint to generate recipes using Gemini"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            time_available = data.get('time_available', 30)
            num_people = data.get('num_people', 2)
            diet_preference = data.get('diet_preference', 'Regular')
            experience_level = data.get('experience_level', 'Beginner')
            ingredients = data.get('ingredients', '')
            
            if not ingredients.strip():
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter some ingredients!'
                })
            
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""Generate a detailed recipe with the following parameters:

Time Available: {time_available} minutes
Number of People: {num_people}
Diet Preference: {diet_preference}
Experience Level: {experience_level}
Available Ingredients: {ingredients}

Please provide a complete recipe including:
1. Recipe name (make it catchy and appetizing!)
2. Complete ingredients list with exact measurements
3. Step-by-step cooking instructions (numbered)
4. Estimated prep time and cooking time breakdown
5. Difficulty level
6. Pro tips for best results

Make sure the recipe is suitable for a {experience_level} cook and can be completed in approximately {time_available} minutes.
Format the response in a clear, easy-to-read way with proper spacing and sections."""
            
            response = model.generate_content(prompt)
            
            # Format the recipe with proper HTML
            formatted_recipe = format_recipe_response(response.text)
            
            return JsonResponse({
                'success': True,
                'response': formatted_recipe  # Return formatted HTML
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error generating recipe: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method. Please use POST.'
    })
@csrf_exempt
def generate_recipe_api(request):
    """API endpoint to generate recipes using Gemini"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get parameters (matching the frontend variable names)
            time_available = data.get('time_available', 30)
            num_people = data.get('num_people', 2)
            diet_preference = data.get('diet_preference', 'Regular')
            experience_level = data.get('experience_level', 'Beginner')
            ingredients = data.get('ingredients', '')
            
            if not ingredients.strip():
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter some ingredients!'
                })
            
            # Configure Gemini (using your existing API key)
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Create detailed prompt
            prompt = f"""Generate a detailed recipe with the following parameters:

Time Available: {time_available} minutes
Number of People: {num_people}
Diet Preference: {diet_preference}
Experience Level: {experience_level}
Available Ingredients: {ingredients}

Please provide a complete recipe including:
1. Recipe name (make it catchy and appetizing!)
2. Complete ingredients list with exact measurements
3. Step-by-step cooking instructions (numbered)
4. Estimated prep time and cooking time breakdown
5. Difficulty level
6. Pro tips for best results

Make sure the recipe is suitable for a {experience_level} cook and can be completed in approximately {time_available} minutes.
Format the response in a clear, easy-to-read way with proper spacing and sections."""
            
            # Generate response
            response = model.generate_content(prompt)
            # Format the recipe with proper HTML
            formatted_recipe = format_recipe_response(response.text)
            
            return JsonResponse({
                'success': True,
                'response': formatted_recipe
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error generating recipe: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method. Please use POST.'
    })