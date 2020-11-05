from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_admin')
        cls.authorized_client = Client()        
        cls.authorized_client.force_login(cls.user) 
        cls.unauthorized_client = Client()
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-group-1',
            description='Тестовая группа 1'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост 1',
            author=cls.user,
            group=cls.group,
        )

    def test_homepage(self):
        """ проверяем главную страницу """
        url = reverse('index')
        response = self.unauthorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        """ проверяем страницу профиля """
        url = reverse('profile', args=[self.user])
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_force_login(self):
        """ проверяем возможность создать новый пост
            для авторизированного пользователя """
        url = reverse('new_post')
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_group(self):
        """ проверяем страницу группы """
        url = reverse('group_posts', args=[self.group.slug])
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_newpage(self):
        """ проверяем перенаправление неавторизированного пользователя 
            при создании нового поста """
        url_new = reverse('new_post')
        response = self.unauthorized_client.get(url_new, follow=True)
        self.assertRedirects(response, reverse('login') + '?next=' + url_new, status_code=302, target_status_code=200)

    def test_error_404(self):
        "проверяем возвращает ли сайт ошибку 404"
        response = self.authorized_client.get('/error/')
        self.assertEqual(response.status_code, 404)
        response = self.unauthorized_client.get('/error/')
        self.assertEqual(response.status_code, 404)
    