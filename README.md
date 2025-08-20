# Chordo - E-commerce Platform

Chordo is a full-featured e-commerce web application built with Django, offering a complete online shopping experience with user authentication, product management, shopping cart, wishlist, order management, and payment integration.

## 🚀 Features

### User Features
- **User Authentication**: Registration, login, logout with email verification
- **Google OAuth Integration**: Sign in with Google account
- **User Profile Management**: Profile creation and editing with image upload
- **Product Browsing**: Browse products by categories with search and filtering
- **Product Reviews**: Rate and review products
- **Shopping Cart**: Add/remove items, quantity management
- **Wishlist**: Save favorite products for later
- **Order Management**: Place orders, track order status
- **Multiple Payment Options**: 
  - Cash on Delivery
  - Razorpay payment gateway
  - Wallet payments
- **Address Management**: Multiple shipping addresses
- **Coupon System**: Apply discount coupons
- **Wallet System**: Digital wallet for payments and refunds

### Admin Features
- **Product Management**: Add, edit, delete products and variants
- **Category Management**: Organize products into categories
- **Order Management**: Process orders, update order status
- **User Management**: Manage customer accounts
- **Coupon Management**: Create and manage discount coupons
- **Offer Management**: Product and category-based offers
- **Image Processing**: Automated image optimization and processing

## 🛠️ Technology Stack

- **Backend**: Django 5.1.1
- **Database**: PostgreSQL
- **Authentication**: Django Allauth with Google OAuth
- **Payment Gateway**: Razorpay
- **Image Processing**: Pillow (PIL)
- **Static Files**: WhiteNoise
- **Email**: SMTP (Gmail)
- **Frontend**: HTML, CSS, JavaScript
- **Cloud Storage**: AWS S3 (configured but commented out)

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Git

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Chordo
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd Chordo
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE chordo_db;
   CREATE USER postgres WITH PASSWORD 'chordo_password';
   GRANT ALL PRIVILEGES ON DATABASE chordo_db TO postgres;
   ```

5. **Configure environment variables**
   
   Create a `.env` file in the `Chordo` directory with the following variables:
   ```env
   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com

   # Google OAuth
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret

   # Razorpay Configuration
   RAZORPAY_KEY_ID=your-razorpay-key-id
   RAZORPAY_KEY_SECRET=your-razorpay-key-secret
   ```

6. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://127.0.0.1:8000/`

## 🔑 Configuration

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `https://yourdomain.com/accounts/google/login/callback/`

### Razorpay Setup
1. Sign up at [Razorpay](https://razorpay.com/)
2. Get your API keys from the dashboard
3. Add the keys to your `.env` file

### Email Configuration
1. Enable 2-factor authentication on your Gmail account
2. Generate an app-specific password
3. Use the app password in the `EMAIL_HOST_PASSWORD` setting

## 📁 Project Structure

```
Chordo/
├── Chordo/
│   ├── adminapp/           # Admin functionality
│   ├── userapp/            # User-facing functionality
│   ├── chordoproject/      # Main project settings
│   ├── media/              # User uploaded files
│   ├── staticfiles/        # Collected static files
│   ├── product_images/     # Original product images
│   ├── processed_images/   # Processed product images
│   ├── venv/              # Virtual environment
│   ├── manage.py          # Django management script
│   ├── requirements.txt   # Python dependencies
│   ├── process_images.py  # Image processing script
│   └── .env              # Environment variables
└── README.md             # This file
```

## 🎯 Key Models

- **CustomUser**: Extended user model with email authentication
- **Product**: Product information and details
- **ProductVariant**: Product variations (color, price, quantity)
- **Category**: Product categories
- **Cart/CartItem**: Shopping cart functionality
- **Order/OrderItem**: Order management
- **Wishlist**: User wishlist
- **Coupon**: Discount coupons
- **Wallet**: Digital wallet system
- **Review**: Product reviews and ratings

## 🚀 Deployment

The application is configured for deployment with:
- WhiteNoise for static file serving
- PostgreSQL database
- Environment-based configuration
- CSRF trusted origins for production domains

### Production Settings
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` with your domain
- Set up proper SSL certificates
- Configure email backend for production
- Set up proper database credentials

## 🔧 Image Processing

The project includes an image processing script (`process_images.py`) that:
- Resizes images to optimal dimensions
- Applies sharpening filters
- Enhances contrast and sharpness
- Converts images to JPEG format for web optimization

## 📝 API Endpoints

The application uses Django's URL routing system with separate URL configurations for:
- Admin functionality (`adminapp.urls`)
- User functionality (`userapp.urls`)
- Django Allauth authentication (`allauth.urls`)

**Note**: Make sure to keep your `.env` file secure and never commit it to version control. The file contains sensitive information like API keys and passwords.
