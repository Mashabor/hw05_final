from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test-title',
            description='test-description',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test-text'
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_urls_uses_correct_template(self):
        templates_url_names_guest = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_urls_unexisting_page_guest(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

    def test_create_url_redirect_guest_client(self):
        url = reverse('posts:post_create')
        response = self.guest_client.get(url)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_url_redirect_guest_client(self):
        url = reverse('posts:post_edit', kwargs={'post_id': '1'})
        response = self.guest_client.get(url)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

        templates_url_names_authorized = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'
        }
        for address, template in templates_url_names_authorized.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_urls_unexisting_page_authorized(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )
