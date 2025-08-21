
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.db import models
import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
import fitz
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict
from rest_framework import status
from django.http import JsonResponse
from .models import Book, Favorite, BookKeyword
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import shutil
from pprint import pprint



def profil(request):
     return render(request, 'index.html')

def create_book_masterdata(request):
     return render(request, 'book/create.html')
 
 
class BookMasterStore(APIView):
    def post(self, request, *args, **kwargs):
        try:
            
            # Ambil data dari request.POST
            judul = request.POST.get("judul", "").strip()
            deskripsi = request.POST.get("deskripsi", "").strip()
            penulis = request.POST.get("penulis", "").strip()
            tahun_terbit = request.POST.get("tahun_terbit", "").strip()
            genre = request.POST.get("genre", "").strip()
            jumlah_halaman = request.POST.get("jumlah_halaman", "").strip()
            file_pdf = request.FILES.get("file_pdf")

            # Validasi sederhana
            if not judul or not penulis or not tahun_terbit or not genre or not jumlah_halaman or not file_pdf:
                return Response({
                    "data": False,
                    "message": "Semua field wajib diisi."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Konversi tipe data
            try:
                tahun_terbit = int(tahun_terbit)
                jumlah_halaman = int(jumlah_halaman)
            except ValueError:
                return Response({
                    "data": False,
                    "message": "Tahun terbit & jumlah halaman harus angka."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Simpan dulu ke database → biar dapat book.id
            book = Book.objects.create(
                judul=judul,
                deskripsi=deskripsi,
                penulis=penulis,
                tahun_terbit=tahun_terbit,
                genre=genre,
                jumlah_halaman=jumlah_halaman,
                file_pdf=file_pdf,
                cover_image=None
            )

            # --- Convert PDF ke gambar ---
            pdf_path = book.file_pdf.path  # path PDF yg baru diupload
            output_dir = os.path.join(settings.MEDIA_ROOT, "book", "pages", str(book.id))
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                doc = fitz.open(pdf_path)
            except Exception as e:
                return Response({"data": False, "message": f"PDF invalid: {str(e)}"})

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # scale biar HD
                img_name = f"page_{page_num+1}.png"
                img_path = os.path.join(output_dir, img_name)
                pix.save(img_path)

            doc.close()

            return Response({
                "data": True,
                "message": f"Buku '{book.judul}' berhasil disimpan & PDF diubah jadi gambar."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "data": False,
                "message": f"Terjadi error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
def book_masterdata(request):
    books = Book.objects.all()
    
    # Siapkan data untuk ditampilkan di tabel
    books_data = []
    for book in books:
        desc_words = book.deskripsi.split()[:15]  # ambil 15 kata pertama
        short_desc = ' '.join(desc_words)
        if len(book.deskripsi.split()) > 15:
            short_desc += ' ...'
        books_data.append({
            'judul': book.judul,
            'deskripsi': short_desc,
            'genre': book.genre,
        })

    context = {
        'books_data': books_data
    }

    return render(request, 'book/index.html', context)


@login_required
def book_masterdata_ajax(request):
    favorited_only = request.GET.get('favorited') == '1'
    
    if favorited_only:
        # Hanya buku yang difavorit user saat ini
        books = Book.objects.filter(favorited_by__user=request.user)
    else:
        # Semua buku
        books = Book.objects.all()

    books_data = []

    for book in books:
        # Ambil 15 kata pertama dari deskripsi
        desc_words = book.deskripsi.split()[:15]
        short_desc = ' '.join(desc_words)
        if len(book.deskripsi.split()) > 15:
            short_desc += ' ...'

        # Status favorit: 1 jika user sudah favorit, 0 jika belum
        is_favorited = 1 if Favorite.objects.filter(user=request.user, book=book).exists() else 0

        books_data.append({
            'judul': book.judul,
            'deskripsi': short_desc,
            'genre': book.genre,
            'favorited': is_favorited,  # ini field boolean 0/1 eksplisit
            'action': f'''
                <a href="{reverse('detail_book_masterdata', args=[book.id])}" class="btn btn-sm btn-info">Detail</a>
            '''
        })

    return JsonResponse({'data': books_data})


class BookMasterUpdate(APIView):
    def post(self, request, *args, **kwargs):
        try:
            book_id = request.GET.get('id') or request.POST.get('id')
            if not book_id:
                return Response({
                    "data": False,
                    "message": "ID buku tidak ditemukan."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Ambil buku dari DB
            book = get_object_or_404(Book, id=book_id)

            # Ambil data dari request
            judul = request.POST.get("judul", "").strip()
            deskripsi = request.POST.get("deskripsi", "").strip()
            penulis = request.POST.get("penulis", "").strip()
            tahun_terbit = request.POST.get("tahun_terbit", "").strip()
            genre = request.POST.get("genre", "").strip()
            jumlah_halaman = request.POST.get("jumlah_halaman", "").strip()
            file_pdf = request.FILES.get("file_pdf")  # opsional

            # Validasi sederhana
            if not judul or not penulis or not tahun_terbit or not genre or not jumlah_halaman:
                return Response({
                    "data": False,
                    "message": "Semua field wajib diisi (kecuali file PDF)."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Konversi tipe data
            try:
                tahun_terbit = int(tahun_terbit)
                jumlah_halaman = int(jumlah_halaman)
            except ValueError:
                return Response({
                    "data": False,
                    "message": "Tahun terbit & jumlah halaman harus angka."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update data utama
            book.judul = judul
            book.deskripsi = deskripsi
            book.penulis = penulis
            book.tahun_terbit = tahun_terbit
            book.genre = genre
            book.jumlah_halaman = jumlah_halaman

            # Folder gambar lama
            images_dir = os.path.join(settings.MEDIA_ROOT, "book", "pages", str(book.id))

            # Jika ada PDF baru, hapus file lama dan folder gambar lama
            if file_pdf:
                # Hapus file PDF lama
                if book.file_pdf and book.file_pdf.name:
                    old_file_path = os.path.join(settings.MEDIA_ROOT, book.file_pdf.name)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                # Hapus folder gambar lama beserta isinya
                if os.path.exists(images_dir):
                    import shutil
                    shutil.rmtree(images_dir)

                # Simpan file PDF baru
                book.file_pdf = file_pdf
                book.save()  # <<< penting, baru setelah save, book.file_pdf.path valid

                # pprint({
                #     "pdf_path": book.file_pdf ,
                  
                # })

                # # Hentikan sementara eksekusi agar seperti dd() di Laravel
                # return Response({"message": "PDF sudah di-dump, cek console"}, status=200)
                # Buat folder baru untuk gambar
                os.makedirs(images_dir, exist_ok=True)

                # --- Convert PDF ke gambar ---
                try:
                    doc = fitz.open(book.file_pdf.path)
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # HD
                        img_name = f"page_{page_num+1}.png"
                        img_path = os.path.join(images_dir, img_name)
                        pix.save(img_path)
                    doc.close()
                except Exception as e:
                    return Response({
                        "data": False,
                        "message": f"PDF invalid atau gagal konversi: {str(e)}"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Simpan perubahan
            book.save()

            return Response({
                "data": True,
                "message": f"Buku '{book.judul}' berhasil diperbarui."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "data": False,
                "message": f"Terjadi error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
def edit_book_masterdata(request, pk):
    # Ambil buku berdasarkan primary key
    book = get_object_or_404(Book, pk=pk)

    # Render halaman edit dengan data buku
    context = {
        "book": book,
        "GENRE_CHOICES": Book.GENRE_CHOICES
    }
    return render(request, "book/edit.html", context)
    
@csrf_exempt  # karena kita mengirim POST via fetch, pastikan CSRF token dikirim juga
def delete_book_masterdata(request, pk):
    if request.method == 'POST':
        try:
            book = Book.objects.get(pk=pk)

            # Hapus file PDF
            if book.file_pdf and book.file_pdf.name:
                pdf_path = os.path.join(settings.MEDIA_ROOT, 'book', 'pdf', os.path.basename(book.file_pdf.name))
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

            # Hapus folder gambar beserta isinya
            images_dir = os.path.join(settings.MEDIA_ROOT, 'book', 'pages', str(book.id))
            if os.path.exists(images_dir):
                shutil.rmtree(images_dir)

            # Hapus semua keyword terkait
            BookKeyword.objects.filter(book=book).delete()

            # Hapus semua favorit terkait
            Favorite.objects.filter(book=book).delete()

            # Hapus record book dari DB
            book.delete()

            return JsonResponse({'success': True, 'message': f"Buku '{book.judul}' berhasil dihapus beserta data terkait."})

        except Book.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Buku tidak ditemukan."})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Terjadi error: {str(e)}"})
    else:
        return JsonResponse({'success': False, 'message': "Metode tidak diperbolehkan."})
    
def detail_book_masterdata(request, pk):
    import os
    from django.conf import settings

    # Ambil buku berdasarkan primary key
    book = get_object_or_404(Book, pk=pk)

    # Cek apakah buku ini sudah menjadi favorit user saat ini
    favorited = False
    if request.user.is_authenticated:
        favorited = Favorite.objects.filter(user=request.user, book=book).exists()

    # Ambil keyword terkait buku
    keywords = book.keywords.all().order_by('-score')  # pakai related_name 'keywords'

    # Ambil gambar halaman pertama (page_1.png)
    image_url = None
    images_dir = os.path.join(settings.MEDIA_ROOT, 'book', 'pages', str(book.id))
    page_1_path = os.path.join(images_dir, 'page_1.png')
    if os.path.exists(page_1_path):
        # Untuk URL bisa menggunakan MEDIA_URL
        image_url = os.path.join(settings.MEDIA_URL, 'book', 'pages', str(book.id), 'page_1.png')

    # Siapkan context untuk template
    context = {
        "book": book,
        "GENRE_CHOICES": Book.GENRE_CHOICES,
        "favorited": favorited,
        "keywords": keywords,     # variabel keyword
        "page_1_url": image_url   # variabel gambar halaman pertama
    }

    return render(request, "book/detail.html", context)



def preview_book_ajax(request, book_id):
    book = Book.objects.filter(id=book_id).first()
    if not book:
        return JsonResponse({'success': False, 'message': 'Buku tidak ditemukan'})

    # folder tempat gambar per halaman
    images_dir = os.path.join(settings.MEDIA_ROOT, 'book', 'pages', str(book.id))
    if not os.path.exists(images_dir):
        return JsonResponse({'success': False, 'message': 'Folder halaman buku tidak ditemukan'})

    # hitung jumlah halaman (PNG)
    pages = sorted([f for f in os.listdir(images_dir) if f.lower().endswith('.png')])
    total_pages = len(pages)

    return JsonResponse({
        'success': True,
        'total_pages': total_pages,
    })

@method_decorator(login_required, name='dispatch')
class BookMasterFavorite(APIView):
    """
    Toggle favorite: jika belum ada -> buat, jika sudah ada -> hapus
    """
    def post(self, request, book_id):
        user = request.user
        book = get_object_or_404(Book, pk=book_id)

        favorite, created = Favorite.objects.get_or_create(user=user, book=book)

        if created:
            # Data baru dibuat
            return Response({"success": True, "favorited": True, "message": f"'{book.judul}' ditambahkan ke favorit."}, status=status.HTTP_201_CREATED)
        else:
            # Sudah ada -> hapus
            favorite.delete()
            return Response({"success": True, "favorited": False, "message": f"'{book.judul}' dihapus dari favorit."}, status=status.HTTP_200_OK)



def analyze_keyword_ajax(request, pk):
    # Pastikan resource tersedia
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Metode POST required."})
    
    book = get_object_or_404(Book, pk=pk)

    try:
        pdf_path = book.file_pdf.path
        doc = fitz.open(pdf_path)

        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()

        doc.close()

        # Tokenisasi & filtering
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        words = [w for w in tokens if w.isalpha() and w not in stop_words]

        # Hitung frekuensi
        counter = Counter(words)
        most_common = counter.most_common(20)  # 20 keyword teratas

        # Simpan ke model BookKeyword
        BookKeyword.objects.filter(book=book).delete()  # hapus dulu keyword lama
        for word, count in most_common:
            BookKeyword.objects.create(book=book, keyword=word, score=float(count))

        return JsonResponse({
            "success": True,
            "message": f"Keyword berhasil dianalisis untuk buku '{book.judul}'.",
            "keywords": [{"keyword": w, "score": c} for w, c in most_common]
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})    
    
    