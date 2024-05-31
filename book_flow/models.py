from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser


class Author(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Author Name'), help_text=_('Enter the name of the author'))
    date_of_birth = models.DateField(verbose_name=_('Date of Birth'), null=True, blank=True)
    date_of_death = models.DateField(verbose_name=_('Date of Death'), null=True, blank=True)

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(verbose_name=_('Genre'), max_length=50, help_text='Enter the name of the genre')

    class Meta:
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name=_('Author'), related_name='books')
    genre = models.ManyToManyField(Genre, verbose_name=_('Genre'))
    borrow_history = models.ManyToManyField(CustomUser, through='BorrowHistory', related_name='borrowed_books')
    title = models.CharField(verbose_name=_('Title'), max_length=100, help_text=_('Enter the title of the book'))
    published_date = models.DateField(verbose_name=_('Published Date'))
    stock = models.IntegerField(verbose_name=_('Stock'), validators=[MinValueValidator(0)])
    total_borrowed = models.PositiveIntegerField(verbose_name=_('Total Borrowed'), default=0, null=True, blank=True,
                                                 validators=[MinValueValidator(0)])
    currently_borrowed = models.PositiveIntegerField(verbose_name=_('Currently Borrowed'), default=0, null=True,
                                                     blank=True, validators=[MinValueValidator(0)])
    image_url = models.URLField(verbose_name=_('Image URL'), max_length=200, null=True, blank=True)
    isbn = models.PositiveIntegerField(verbose_name=_('ISBN'), null=True, blank=True, unique=True)

    class Meta:
        ordering = ['title', 'stock']
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __str__(self):
        return f"{self.title} by {self.author.name}"

    def clean(self):
        super().clean()
        if self.currently_borrowed > self.stock:
            raise ValidationError({
                'currently_borrowed': _('Currently borrowed books cannot exceed the total stock.')
            })

    def get_image_id(self):
        if self.image_url:
            try:
                # Extract the image ID from the URL
                return self.image_url.split('/')[-1].split('-')[0]
            except IndexError:
                return None
        return None


class BorrowHistory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    issued = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("Borrow History")
        verbose_name_plural = _("Borrow Histories")

    def __str__(self):
        return f"{self.book} borrowed by {self.borrower}"

    @property
    def isbn(self):
        return self.book.isbn
