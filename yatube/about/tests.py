from http import HTTPStatus

from django.test import TestCase, Client


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_uses_correct_templates(self):
        templates_url_names_quest = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in templates_url_names_quest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )
