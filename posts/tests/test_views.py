from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group, Follow, Comment


User = get_user_model()


class PostsTestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_admin')
        cls.authorized_client = Client()        
        cls.authorized_client.force_login(cls.user) 
        cls.unauthorized_client = Client()
        cls.key = make_template_fragment_key('index_page')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-group-1',
            description='Тестовая группа 1'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-group-2',
            description='Тестовая группа 2'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост 1',
            author=cls.user,
            group=cls.group_1
        )

    def test_new_post(self):
        """ проверяем публикацию поста для авторизированного пользователя """
        current_posts_count = Post.objects.count()
        url = reverse('new_post')
        response = self.authorized_client.post(url, {'text': 'Текст публикации', 'group': self.group_1.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), current_posts_count + 1)
    
    def test_post_profile(self):
        """ проверяем наличие поста на странице профиля """
        url = reverse('profile', args=[self.user])
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'][0], self.post)

    def test_post_group(self):
        """ проверяем наличие поста на странице группы """
        url = reverse('group_posts', args=[self.group_1.slug])
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'][0], self.post)

    def test_update_post(self):
        """ изменяем пост и проверяем изменение на странице этого поста """
        url_reverse = [
            reverse('profile', args=[self.user]),
            reverse('group_posts', args=[self.group_2.slug]),
        ]
        
        url = reverse('post_edit', args=[self.user, self.post.id])
        with open('posts/test_image.jpg', 'rb') as img:
            context = {
                'text': 'Это текст публикации',
                'group': self.group_2.id,
                'image': img
            }
            update_post = self.authorized_client.post(url, context, follow=True)

        self.assertEqual(update_post.status_code, 200)
        self.assertEqual(update_post.context['post'].text, 'Это текст публикации')
        self.assertEqual(update_post.context['post'].group, self.group_2)
        self.assertContains(update_post, '<img')

        for url in url_reverse:
            response = self.authorized_client.get(url)
            self.update_commit_test(response)

    def update_commit_test(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'][0].text, 'Это текст публикации')
        self.assertEqual(response.context['page'][0].group, self.group_2)
        self.assertContains(response, '<img')
    
    def test_img(self):
        """проверяем наличие тега img на странице поста, группе, профиле, главной странице"""
        url_reverse = [
            reverse('profile', args=[self.user]),
            reverse('group_posts', args=[self.group_1.slug]),
            reverse('index'),
        ]

        with open('posts/test_image.jpg', 'rb') as img:
            context = {
                'text': 'Это текст публикации',
                'group': self.group_1.id,
                'image': img
            }
            url = reverse('post_edit', args=[self.user, self.post.id])
            update_post = self.authorized_client.post(url, context, follow=True)

        self.assertEqual(update_post.status_code, 200)
        self.assertContains(update_post, '<img')
        
        cache.touch(self.key, 0)
        
        for url in url_reverse:
            response = self.authorized_client.get(url)
            self.img_test(response)

    def img_test(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<img')

    def test_loading_not_images(self):
        """ проверяем механизм защиты от загрузки файлов не-графических форматов """
        with open('posts/admin.py', 'rb') as img:
            context = {
                'text': 'Это текст публикации',
                'group': self.group_1.id,
                'image': img
            }
            url = reverse('new_post')
            response = self.authorized_client.post(url, context, follow=True)
        current_posts_count = Post.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), current_posts_count)
    
    def test_cache_index(self):
        """проверка работы кэширования страницы index"""
        old_response = self.authorized_client.get(reverse('index'))
        url = reverse('new_post')
        response = self.authorized_client.post(url, {'text': 'Текст публикации', 'group': self.group_1.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(old_response.content, response.content)
        cache.touch(self.key, 0)
        new_response = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(old_response.content, new_response.content)

    def test_follow_authorized_user(self):
        """ проверяем возможность пользователя подписаться и отписаться на автора """
        count_follow = Follow.objects.count()
        user_2 = User.objects.create_user(username='test_user')
        authorized_user_2 = Client()
        authorized_user_2.force_login(user_2)
        url = reverse('profile_follow', args=[self.user])
        response = authorized_user_2.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        url = reverse('profile_unfollow', args=[self.user])
        response = authorized_user_2.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_index(self):
        """ првоеряем, что пост появляется только у подписанного пользователя """
        user_2 = User.objects.create_user(username='test_user')
        authorized_user_2 = Client()
        authorized_user_2.force_login(user_2)
        user_3 = User.objects.create_user(username='test_user_2')
        authorized_user_3 = Client()
        authorized_user_3.force_login(user_3)
        url = reverse('profile_follow', args=[self.user])
        response_user_2 = authorized_user_2.get(url, follow=True)
        response_user_3 = authorized_user_3.get(reverse('follow_index'))
        self.assertNotEqual(response_user_2, response_user_3)

    def test_comment_authorized_user(self):
        """ проверяем возможность авторизированного пользователя комментировать пост """
        comment_count = Comment.objects.count()
        url = reverse('add_comment', args=[self.user, self.post.id])
        response = self.authorized_client.post(url, {'text': 'Это текст комментария'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_comment_unauthorized_user(self):
        """ не авторизированный пользователь не может оставить комментарий """
        url = reverse('add_comment', args=[self.user, self.post.id])
        response = self.unauthorized_client.post(url, {'text': 'Это текст комментария'}, follow=True)
        self.assertRedirects(response, reverse('login') + '?next=' + url, status_code=302, target_status_code=200)