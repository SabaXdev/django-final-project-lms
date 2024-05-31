from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from book_flow.models import Book
from users.models import CustomUser


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    def validate(self, data):
        instance = Book(**data)
        instance.clean()  # Call the model's clean method
        return data


class MostBorrowedBooksSerializer(ModelSerializer):
    total_borrows = serializers.IntegerField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'total_borrows']


class BookIssueCountSerializer(ModelSerializer):
    issue_count = serializers.IntegerField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'issue_count']


class TopLateReturnedBooksSerializer(ModelSerializer):
    late_returns = serializers.IntegerField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'late_returns']


class TopLateReturnUsersSerializer(ModelSerializer):
    late_returns = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'late_returns']
