from django.db import models
from django.conf import settings

# Create your models here.
# =========================
# Tabel Books
# =========================
class Book(models.Model):
    GENRE_CHOICES = [
        ('fiksi', 'Fiksi'),
        ('komik', 'Komik'),
        ('motivasi', 'Motivasi'),
        ('lainnya', 'Lainnya'),
    ]

    judul = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True)
    penulis = models.CharField(max_length=255)
    tahun_terbit = models.IntegerField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='lainnya')
    jumlah_halaman = models.PositiveIntegerField()

    # file otomatis disimpan di content/media/book/pdf/
    file_pdf = models.FileField(upload_to="book/pdf/")

    # cover otomatis disimpan di content/media/book/covers/
    cover_image = models.ImageField(upload_to="book/covers/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.judul

# =========================
# Tabel Favorites
# =========================
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')  # agar tidak duplikat

    def __str__(self):
        return f"{self.user.username} - {self.book.judul}"


# =========================
# Tabel BookKeywords
# =========================
class BookKeyword(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=255)
    score = models.FloatField(default=0.0)  # misal TF-IDF value

    class Meta:
        unique_together = ('book', 'keyword')

    def __str__(self):
        return f"{self.keyword} ({self.book.judul})"