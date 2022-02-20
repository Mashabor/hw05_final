import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django import forms

from ..models import Post, Group, Comment
from ..conf import POSTS_COUNT, TEST_POSTS


User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test-title',
            description='test-description',
            slug='test-slug'
        )
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        posts = [Post(
            author=cls.author,
            group=cls.group,
            text=f'test-text {i}',
            image=uploaded
        ) for i in range(TEST_POSTS)]

        cls.posts = Post.objects.bulk_create(posts)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

        @classmethod
        def tearDownClass(cls):
            super().tearDownClass()
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """в URL-адрес передан соответствующий шаблон."""
        templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'NoName'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': '1'}
            ): 'posts/post_create.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_test_object = response.context['page_obj'][0]
        post_author_0 = first_test_object.author.username
        post_text_0 = first_test_object.text
        post_group_0 = first_test_object.group.title
        self.assertEqual(
            post_author_0,
            'NoName'
        )
        self.assertEqual(
            post_text_0,
            'test-text 12'
        )
        self.assertEqual(
            post_group_0,
            'test-title'
        )

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test-slug'}
        ))
        first_test_object = response.context['page_obj'][0]
        post_author_0 = first_test_object.author.username
        post_text_0 = first_test_object.text
        post_group_0 = first_test_object.group.title
        self.assertEqual(
            post_author_0,
            'NoName'
        )
        self.assertEqual(
            post_text_0,
            'test-text 12'
        )
        self.assertEqual(
            post_group_0,
            'test-title'
        )
        self.assertEqual(response.context['group'], self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'NoName'}
        ))
        first_test_object = response.context['page_obj'][0]
        post_author_0 = first_test_object.author.username
        post_text_0 = first_test_object.text
        post_group_0 = first_test_object.group.title
        test_author = response.context['author']
        test_posts_amount = response.context['posts_amount']
        self.assertEqual(
            post_author_0,
            'NoName'
        )
        self.assertEqual(
            post_text_0,
            'test-text 12'
        )
        self.assertEqual(
            post_group_0,
            'test-title'
        )
        self.assertEqual(test_author, self.author)
        self.assertEqual(test_posts_amount, self.author.posts.count())

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        id = 12
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': id}
        ))
        test_title = response.context['title']
        test_full_post = response.context['post']
        test_posts_amount = response.context['posts_amount']
        post = Post.objects.get(pk=id)
        self.assertEqual(test_title, post.text[:15])
        self.assertEqual(test_full_post, post)
        self.assertEqual(test_posts_amount, self.author.posts.count())

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.MultipleChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get('text')
                self.assertIsInstance(form_field, form_fields['text'])

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': '1'}
        ))
        form_fields = {
            'text': forms.fields.CharField
        }
        test_is_edit = response.context['is_edit']
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get('text')
                self.assertIsInstance(form_field, form_fields['text'])
        self.assertTrue(test_is_edit)

    def authorized_client_can_comments(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий к посту'
        }
        responce = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        last_comment = Comment.objects.latest('created')
        self.assertRedirects(
            response, reverse('posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.author, self.author)

    class PaginatorViewsTest(TestCase):
        def test_first_page_index_contains_ten_records(self):
            response = self.client.get(reverse('index'))
            self.assertEqual(len(response.context['object_list']), POSTS_COUNT)

        def test_second_page_index_contains_three_records(self):
            response = self.client.get(reverse('index') + '?page=2')
            self.assertEqual(len(response.context['object_list']), 3)

        def test_first_page_group_posts_contains_ten_records(self):
            response = self.client.get(reverse('posts:group_posts'))
            self.assertEqual(len(response.context['object_list']), POSTS_COUNT)

        def test_second_page_group_posts_contains_three_records(self):
            response = self.client.get(
                reverse('posts:group_posts') + '?page=2')
            self.assertEqual(len(response.context['object_list']), 3)

        def test_first_page_profile_contains_ten_records(self):
            response = self.client.get(reverse('posts:profile'))
            self.assertEqual(len(response.context['object_list']), POSTS_COUNT)

        def test_second_page_profile_contains_three_records(self):
            response = self.client.get(reverse('posts:profile') + '?page=2')
            self.assertEqual(len(response.context['object_list']), 3)
