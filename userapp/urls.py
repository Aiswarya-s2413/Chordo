from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('userSignup/', views.userSignup,name='userSignup'),
    path('userLogin/', views.userLogin,name='userLogin'),
    path('userLogout/', views.userLogout,name='userLogout'),
    path('userOtp/', views.userOtp,name='userOtp'),
    path('passwordOtp/', views.passwordOtp,name='passwordOtp'),
    path('', views.userHome,name='userHome'),
    path('userCategories/', views.userCategories,name='userCategories'),
    path('resend_otp/', views.resend_otp,name='resend_otp'),
    path('resend_otp_password/', views.resend_otp_password,name='resend_otp_password'),
    path('forgetPassword/', views.forgetPassword,name='forgetPassword'),
    path('resetPassword/', views.resetPassword,name='resetPassword'),
    path('productList/', views.productList,name='productList'),
    path('productView/<int:id>/', views.productView,name='productView'),
    path('categoryList/<int:id>/', views.categoryList,name='categoryList'),
    path('userProfile/', views.userProfile,name='userProfile'),
    path('addAddress/', views.addAddress,name='addAddress'),
    path('editAddress/<int:id>/', views.editAddress,name='editAddress'),
    path('deleteAddress/<int:id>/', views.deleteAddress,name='deleteAddress'),
    path('changePassword/', views.changePassword,name='changePassword'),
    path('userCart/', views.userCart,name='userCart'),
    path('addToCart/<int:id>/', views.addToCart,name='addToCart'),
    path('removeFromCart/<int:id>/', views.removeFromCart,name='removeFromCart'),
    path('updateCartItem/<int:item_id>/', views.updateCartItem,name='updateCartItem'),
    path('userCheckout/',views.userCheckout,name='userCheckout'),
    path('trackOrder/', views.trackOrder,name='trackOrder'),
    path('cancelOrder/<int:id>/', views.cancelOrder, name='cancelOrder'),
    path('returnOrder/<int:id>/', views.returnOrder, name='returnOrder'),
    path('orderHistory/', views.orderHistory,name='orderHistory'),
    path('addReview/<int:id>/', views.addReview, name='addReview'),
    # path('browseProduct/', views.browseProduct,name='browseProduct'),
    path('verifyPayment/', views.verifyPayment,name='verifyPayment'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('addToWishlist/<int:id>/', views.addToWishlist,name='addToWishlist'),
    path('removeFromWishlist/<int:id>/', views.removeFromWishlist,name='removeFromWishlist'),
    path('myWallet/',views.myWallet,name='myWallet'),
    path('addMoney/',views.addMoney,name='addMoney'),
    path("wallet/payment-success/", views.walletPaymentSuccess, name="walletPaymentSuccess"),
    path('downloadInvoice/<int:order_id>/', views.downloadInvoice, name='downloadInvoice'),
    path('handlePaymentFailure/<int:order_id>/', views.handlePaymentFailure, name='handlePaymentFailure'),
    path('retryPayment/<int:order_id>/', views.retryPayment, name='retryPayment'),
    path('paymentSuccess/', views.paymentSuccess,name='paymentSuccess'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
