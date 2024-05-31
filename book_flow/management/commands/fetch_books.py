import requests
import random
from datetime import datetime
from django.core.management.base import BaseCommand
from book_flow.models import Book, Author, Genre
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Generate books from Google Books API'

    def handle(self, *args, **kwargs):
        API_KEY = 'AIzaSyCPvHmtlFLs3BrJ-G_LmmvTFZen9ifa0YI'
        total_books_to_fetch = 2000
        books_fetched = 0
        subjects = ['classic', 'adventure', 'fiction']
        max_results = 40

        for subject in subjects:
            start_index = 0

            while books_fetched < total_books_to_fetch:
                url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{subject}&startIndex={start_index}&maxResults={max_results}&key={API_KEY}'
                response = requests.get(url)
                data = response.json()

                if 'items' not in data:
                    break

                for item in data['items']:
                    volume_info = item['volumeInfo']

                    title = volume_info.get('title', 'Unknown Title')
                    published_date = volume_info.get('publishedDate', '2000-01-01')
                    authors = volume_info.get('authors', [])
                    categories = volume_info.get('categories', [])
                    image_links = volume_info.get('imageLinks', {})
                    isbn_list = volume_info.get('industryIdentifiers', [])
                    isbn = None

                    for identifier in isbn_list:
                        if identifier['type'] == 'ISBN_13':
                            isbn = identifier['identifier']
                            break

                    if isbn is None or Book.objects.filter(isbn=isbn).exists():
                        continue

                    try:
                        if len(published_date) == 4:
                            published_date = datetime.strptime(published_date, '%Y').date()
                        elif len(published_date) == 7:
                            published_date = datetime.strptime(published_date, '%Y-%m').date()
                        else:
                            published_date = datetime.strptime(published_date, '%Y-%m-%d').date()
                    except ValueError:
                        published_date = datetime.strptime('2000-01-01', '%Y-%m-%d').date()

                    # Ensure the author exists
                    author_name = authors[0] if authors else 'Unknown Author'
                    author_obj, created = Author.objects.get_or_create(name=author_name)

                    genre_objs = []

                    if not categories:
                        categories = ["Unknown"]

                    for category in categories:
                        genre_obj, created = Genre.objects.get_or_create(name=category)
                        genre_objs.append(genre_obj)

                    stock = random.randint(1, 20)
                    currently_borrowed = random.randint(0, stock)

                    book = Book(
                        author=author_obj,
                        title=title,
                        published_date=published_date,
                        stock=stock,
                        total_borrowed=random.randint(currently_borrowed, currently_borrowed + 20),
                        currently_borrowed=currently_borrowed,
                        image_url=image_links.get('thumbnail', ''),
                        isbn=isbn,
                    )

                    try:
                        book.save()
                        book.genre.add(*genre_objs)
                        books_fetched += 1
                        self.stdout.write(self.style.SUCCESS(f'Added book: {title}'))
                    except IntegrityError:
                        self.stdout.write(self.style.ERROR(f'Book with ISBN {isbn} already exists'))

                    if books_fetched >= total_books_to_fetch:
                        break

                start_index += max_results

                if books_fetched >= total_books_to_fetch:
                    break

        self.stdout.write(self.style.SUCCESS(f'Successfully fetched {books_fetched} books'))
