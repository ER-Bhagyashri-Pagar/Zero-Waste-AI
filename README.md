# 🌱 Zero Waste AI

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Django-5.2-green?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/YOLOv8-Real--Time_CV-red?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Google-Gemini_2.0-orange?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-Vercel-61DAFB?style=for-the-badge&logo=react&logoColor=black"/>
  <img src="https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
</div>

## 📋 About This Project

**Zero Waste AI** is an AI-powered food waste prevention platform that combines real-time computer vision detection, multimodal OCR, intelligent recipe generation, and graph-optimized distribution networks. This project tackles the global food waste crisis by preventing spoilage through prediction and connecting surplus food with those in need through efficient routing.

**Harmonizing Product, Nature & Life through AI-Driven Waste Prevention**

## 🎯 Project Objectives

### **Mission: Zero Food Waste**
Transform food waste from a crisis into an opportunity by preventing spoilage before it happens and optimizing redistribution to communities in need through intelligent AI systems.

### **What's in it for you?**
- **Smart Food Management**: AI-powered tracking eliminates forgotten and wasted food
- **Cost Savings**: Reduce grocery expenses through optimized purchasing recommendations
- **Environmental Impact**: Minimize your carbon footprint by preventing food disposal
- **Recipe Innovation**: Transform expiring ingredients into delicious meals with AI suggestions

## 🌍 The Problem

### **Global Food Waste Crisis**
- Over **20%** of food produced globally is wasted annually
- Significant economic losses from food spoilage and inefficient distribution
- Major contributor to greenhouse gas emissions (8-10% of global emissions)
- Food insecurity persists despite massive surplus production
- No intelligent real-time tracking systems for household food management

### **Impact on Communities**
- Households struggle with forgotten food leading to waste
- Restaurants and caterers dispose of edible surplus daily
- NGOs lack efficient systems to receive and distribute donations
- Environmental burden from methane emissions in landfills

## 🔍 Our Solution

### **AI-Driven Prevention & Optimization**

#### **🤖 Predict & Prevent**
- Real-time expiry tracking with intelligent alerts
- Computer vision spoilage detection before visible decay
- Voice-enabled and OCR-based food logging
- Consumption pattern analysis for purchase optimization

#### **🍳 Transform Waste into Value**
- AI recipe chatbot suggesting meals from expiring ingredients
- Personalized recommendations based on dietary preferences
- Step-by-step cooking guidance to utilize all available food

#### **🗺️ Optimize Distribution**
- Graph-based route optimization for food donation delivery
- NGO network mapping with geospatial intelligence
- Efficient surplus redistribution to communities in need

## 🏗️ Technical Architecture
```
```
┌──────────────────────────────────────────────┐
│        Django Backend (Primary Service)       │
│  Food Tracking | YOLO Detection | OCR | DB   │
└────────────┬─────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐     ┌──────────────┐
│ React   │     │  External    │
│ Chatbot │     │  APIs        │
│ (Vercel)│     │ Gemini|Twilio│
└─────────┘     └──────────────┘
```

### **System Components**
- **Backend**: Django framework with REST APIs for data processing and AI orchestration
- **Frontend**: React application deployed on Vercel CDN for global distribution
- **AI/ML Services**: YOLOv8 detection, Gemini multimodal AI, OpenCV processing
- **External Integrations**: Twilio messaging, Geopy geocoding, Folium mapping

### **Grain Definition**
**Grain**: One record per food item entry, capturing individual food details at the most granular level including name, expiry date, image, and temporal tracking information.

## 🔧 Technology Stack

### **Backend & AI/ML**
- **🔧 Framework**: Django 5.2 for web application and database management
- **🤖 Computer Vision**: YOLOv8 (Ultralytics) for real-time object detection
- **🧠 Multimodal AI**: Google Gemini 2.0-Flash for OCR and natural language processing
- **👁️ Image Processing**: OpenCV for video streaming and color analysis
- **📊 Data Analytics**: NumPy and Pandas for numerical computations
- **🗺️ Geospatial**: Geopy, Folium, NetworkX for routing optimization

### **Frontend & Integration**
- **⚛️ UI Framework**: React deployed on Vercel for recipe chatbot interface
- **🎨 Styling**: Bootstrap 5 (Argon Dashboard theme) for responsive design
- **💬 Messaging**: Twilio API for SMS/WhatsApp notifications
- **☁️ Deployment**: Vercel CDN for frontend, Railway/Render ready for backend

### **Database & Infrastructure**
- **💾 Database**: SQLite (development), PostgreSQL (production-ready)
- **🔐 Security**: Environment variables for API key management
- **📦 Dependencies**: pip with virtual environment isolation


```

## 🚀 Getting Started

### **Prerequisites**
- Python 3.11 or higher
- Webcam (for real-time detection features)
- Google Gemini API key
- (Optional) Twilio account for notifications

### **Installation & Setup**

1. **Clone Repository**
```bash
git clone https://github.com/Pagar-Bhagyashri/ZeroWaste-AI.git
cd ZeroWaste-AI
```

2. **Create Virtual Environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install django pillow google-generativeai ultralytics twilio python-dotenv opencv-python numpy geopy folium
```

4. **Configure Environment Variables**
Create `.env` file in project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_sid  # Optional
TWILIO_AUTH_TOKEN=your_twilio_token  # Optional
```

**Get API Keys:**
- Gemini API: https://aistudio.google.com/apikey
- Twilio: https://www.twilio.com/console

5. **Setup Database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Run Development Server**
```bash
python manage.py runserver
```

**Access Application:** http://127.0.0.1:8000/

## 🔍 Core Features & Capabilities

### **Real-Time Computer Vision Detection**
- **YOLOv8 Object Detection**: Real-time fruit and vegetable recognition at 15 FPS
- **Spoilage Analysis**: Color-based rot detection using OpenCV thresholding
- **Live Streaming**: MJPEG video feed with bounding box annotations
- **Multi-Object Tracking**: Simultaneous detection of multiple food items

### **AI-Powered OCR & Prediction**
- **Expiry Date Extraction**: Gemini 2.0 multimodal AI extracts dates from packaging images
- **Format Flexibility**: Handles multiple date formats and languages
- **Voice Input**: Natural language food logging with NLP parsing
- **Smart Predictions**: Consumption pattern analysis for purchase optimization

### **Recipe Generation & Meal Planning**
- **Intelligent Chatbot**: AI-powered recipe suggestions from expiring ingredients
- **Personalization**: Dietary preferences, cooking time, and skill level customization
- **Recipe Database**: Browse curated recipes with filtering and search
- **Meal Planning**: Weekly planner with shopping list generation

### **NGO Donation Network**
- **Route Optimization**: Dijkstra's shortest path algorithm for efficient delivery
- **Interactive Maps**: Folium visualization of nearby NGOs and food banks
- **Geospatial Matching**: Location-based donor-recipient connections
- **Impact Tracking**: Monitor donation metrics and community reach

### **Dashboard Analytics**
- **Expiry Monitoring**: Color-coded status indicators (Expired, Expiring Soon, Good)
- **Impact Metrics**: Track waste prevented, CO₂ reduced, money saved
- **Consumption Insights**: Analyze patterns by food category and time period
- **Visual Analytics**: Charts and graphs for data-driven decision making

## 🏆 Business Impact & Value

### **🎯 Environmental Sustainability**
- **Waste Reduction**: Prevents food from reaching landfills through early intervention
- **Carbon Footprint**: Reduces greenhouse gas emissions from decomposing food
- **Resource Conservation**: Preserves water, energy, and agricultural resources
- **Circular Economy**: Promotes sustainable consumption patterns

### **📈 Economic Benefits**
- **Cost Savings**: Reduces household grocery expenses through waste prevention
- **Purchase Optimization**: AI-driven recommendations prevent over-buying
- **Donation Efficiency**: Optimized logistics reduce redistribution costs
- **Revenue Recovery**: Helps restaurants and caterers monetize surplus

### **🌍 Social Impact**
- **Food Security**: Connects surplus with communities experiencing food insecurity
- **Community Building**: Facilitates local food sharing networks
- **Accessibility**: Voice input and simple UI for diverse user groups
- **Education**: Raises awareness about food waste and sustainability
