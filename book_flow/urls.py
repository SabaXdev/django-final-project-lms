from django.urls import path, re_path
from django.views.generic import RedirectView

from book_flow.views import BookListCreateView, BookDetailView, MostBorrowedBooksView, BookIssueCountView, \
    TopLateReturnedBooksView, TopLateReturnUsersView, BookList, BookDetail, ReturnBookView, IssueBookView

app_name = 'book_flow'

urlpatterns = [
    # Class-based views
    # REST framework
    path('', BookList.as_view(), name='home'),
    path('books/', BookListCreateView.as_view(), name='get_books'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='get_book'),
    # Website
    path('book_list', BookList.as_view(), name='book_list'),
    path('book_detail/<int:pk>/', BookDetail.as_view(), name='book_detail'),
    path('return-book/<int:book_id>/', ReturnBookView.as_view(), name='return_book'),
    path('issue-book/<int:book_id>/', IssueBookView.as_view(), name='issue_book'),
    # re_path(r'^.*$', RedirectView.as_view(pattern_name='book_flow:book_list')),
    # API Endpoints
    path('most-borrowed-books/', MostBorrowedBooksView.as_view(), name='most-borrowed-books'),
    path('book-issue-count/', BookIssueCountView.as_view(), name='book-issue-count'),
    path('top-late-returned-books/', TopLateReturnedBooksView.as_view(), name='top-late-returned-books'),
    path('top-late-return-users/', TopLateReturnUsersView.as_view(), name='top-late-return-users'),
]
