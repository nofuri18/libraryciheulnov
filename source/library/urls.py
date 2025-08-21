from django.urls import path, re_path
from  .views import *
urlpatterns = [
      path('profil', profil, name="profil"), 
      path('book/create', create_book_masterdata, name="create_book_masterdata"), 
      path('book/store', BookMasterStore.as_view(), name="store_book_masterdata"), 
      path('book/index', book_masterdata, name="book_masterdata"), 
      path('book/index/pagination', book_masterdata_ajax, name="book_masterdata_ajax"), 
      path('book/edit/<int:pk>', edit_book_masterdata, name="edit_book_masterdata"), 
      path('book/detail/<int:pk>', detail_book_masterdata, name="detail_book_masterdata"), 
      path('book/update', BookMasterUpdate.as_view(), name="update_book_masterdata"), 
      path('book/delete/<int:pk>', delete_book_masterdata, name="delete_book_masterdata"),
      path('book/favorite/<int:book_id>/', BookMasterFavorite.as_view(), name="book_favorite"),
      path('book/detail/preview/<int:book_id>/', preview_book_ajax, name='preview_book_ajax'),
       path('book/detail/analyzekey/<int:pk>/', analyze_keyword_ajax, name='analyze_keyword_ajax'),
]