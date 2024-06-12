from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from book_flow.models import Book, BorrowHistory
from django.db.models import Count, F, Q, OuterRef, Subquery
from book_flow.permissions import IsLibrarian
from users.models import CustomUser
from book_flow.serializers import MostBorrowedBooksSerializer, BookIssueCountSerializer, TopLateReturnedBooksSerializer, TopLateReturnUsersSerializer, BookSerializer


class BookListCreateView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['author', 'title', 'genre']
    search_fields = ['author__name', 'title']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsLibrarian()]
        return [AllowAny()]

    def get_authenticators(self):
        if self.request.method == 'POST':
            return [BasicAuthentication()]
        return super().get_authenticators()


class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_url_kwarg = 'book_id'

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAuthenticated(), IsLibrarian()]
        return [AllowAny()]


class MostBorrowedBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.order_by('-total_borrowed')[:10]
        serializer = MostBorrowedBooksSerializer(books, many=True)
        return Response(serializer.data)


class BookIssueCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        one_year_ago = timezone.now() - timezone.timedelta(days=365)
        books = Book.objects.annotate(
            issue_count=Count('borrowhistory', filter=Q(borrowhistory__borrow_date__gte=one_year_ago))
        ).order_by('-issue_count')
        serializer = BookIssueCountSerializer(books, many=True)
        return Response(serializer.data)


class TopLateReturnedBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expected_return_date_subquery = BorrowHistory.objects.filter(
            book=OuterRef('pk'),
        ).annotate(expected_return_date=F('borrow_date') + timezone.timedelta(days=14))

        books = Book.objects.annotate(
            late_returns=Count('borrowhistory', filter=Q(
                borrowhistory__return_date__gt=Subquery(expected_return_date_subquery.values('expected_return_date'))
            ))
        ).order_by('-late_returns')[:100]
        serializer = TopLateReturnedBooksSerializer(books, many=True)
        return Response(serializer.data)


class TopLateReturnUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expected_return_date_subquery = BorrowHistory.objects.filter(
            borrower=OuterRef('pk'),
        ).annotate(expected_return_date=F('borrow_date') + timezone.timedelta(days=14))

        users = CustomUser.objects.annotate(
            late_returns=Count('borrowed_books', filter=Q(
                borrowhistory__borrow_date__in=Subquery(expected_return_date_subquery.values('expected_return_date')),
                borrowhistory__return_date__gt=Subquery(expected_return_date_subquery.values('expected_return_date'))
            ))
        ).order_by('-late_returns')[:100]
        serializer = TopLateReturnUsersSerializer(users, many=True)
        return Response(serializer.data)


class BookList(ListView):
    model = Book
    template_name = 'book_flow/book_list.html'
    context_object_name = 'books'
    paginate_by = 9


class BookDetail(DetailView):
    model = Book
    template_name = 'book_flow/book_detail.html'
    context_object_name = 'book'


class IssueBookView(View):
    template_name = 'book_flow/book_issue.html'

    @method_decorator(login_required(login_url='/users/login/'))
    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        if book.currently_borrowed < book.stock:
            BorrowHistory.objects.create(book=book, borrower=self.request.user, issued=True)
            book.currently_borrowed += 1
            book.total_borrowed += 1
            book.save()

        messages.success(request, 'Book - {} Requested successfully'.format(book.title))
        return render(request, self.template_name, {"book": book})


class ReturnBookView(View):
    permission_classes = [IsAuthenticated]

    @method_decorator(login_required(login_url='/users/login/'))
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)

        borrow_history = BorrowHistory.objects.filter(book=book, borrower=self.request.user).first()
        if borrow_history:
            book.currently_borrowed -= 1
            book.save()
            borrow_history.returned = True
            borrow_history.return_date = timezone.now()
            borrow_history.save()
        messages.success(request, 'Book - {} Returned successfully'.format(book.title))
        return redirect(reverse('users:profile'))
