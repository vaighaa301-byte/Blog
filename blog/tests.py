from io import BytesIO
import os
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Post


class BlogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="writer",
            password="test-password-123",
        )
        self.other_user = User.objects.create_user(
            username="reader",
            password="test-password-123",
        )
        self.post = Post.objects.create(
            title="First post",
            content="Hello blog",
            author=self.user,
        )

    def test_post_list_is_public(self):
        response = self.client.get(reverse("post_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First post")

    def test_post_search_matches_title_and_content(self):
        Post.objects.create(
            title="Another story",
            content="Searchable phrase in the post body",
            author=self.user,
        )
        Post.objects.create(
            title="Unrelated",
            content="Nothing to find here",
            author=self.other_user,
        )

        title_response = self.client.get(reverse("post_list"), {"q": "First"})
        content_response = self.client.get(
            reverse("post_list"),
            {"q": "searchable phrase"},
        )
        no_results_response = self.client.get(
            reverse("post_list"),
            {"q": "not found"},
        )

        self.assertContains(title_response, "First post")
        self.assertNotContains(title_response, "Unrelated")
        self.assertContains(content_response, "Another story")
        self.assertNotContains(content_response, "Unrelated")
        self.assertContains(no_results_response, "No matching posts")

    def test_post_list_paginates_and_keeps_search_query(self):
        for number in range(6):
            Post.objects.create(
                title=f"Search story {number}",
                content="Pagination test",
                author=self.user,
            )

        first_page = self.client.get(reverse("post_list"), {"q": "Search"})
        second_page = self.client.get(
            reverse("post_list"),
            {"q": "Search", "page": "2"},
        )

        self.assertEqual(first_page.context["page_obj"].number, 1)
        self.assertEqual(first_page.context["page_obj"].paginator.num_pages, 2)
        self.assertContains(first_page, "Page 1 of 2")
        self.assertContains(
            first_page,
            '?q=Search&amp;page=2',
            html=False,
        )
        self.assertEqual(second_page.context["page_obj"].number, 2)
        self.assertContains(second_page, "Page 2 of 2")
        self.assertContains(second_page, "Search story 0")

    def test_url_paths_are_clean(self):
        paths = {
            "register": "/register/",
            "login": "/login/",
            "logout": "/logout/",
            "post_list": "/",
            "post_create": "/posts/create/",
            "post_detail": f"/posts/{self.post.pk}/",
            "post_edit": f"/posts/{self.post.pk}/edit/",
            "post_delete": f"/posts/{self.post.pk}/delete/",
            "admin:index": "/admin/",
        }
        post_args = {
            "post_detail": [self.post.pk],
            "post_edit": [self.post.pk],
            "post_delete": [self.post.pk],
        }

        for name, expected_path in paths.items():
            with self.subTest(name=name):
                self.assertEqual(
                    reverse(name, args=post_args.get(name, [])),
                    expected_path,
                )

    def test_required_pages_render(self):
        self.client.force_login(self.user)
        pages = [
            (reverse("post_list"), "Latest posts"),
            (reverse("post_detail", args=[self.post.pk]), "First post"),
            (reverse("post_create"), "Write a post"),
            (reverse("post_edit", args=[self.post.pk]), "Edit post"),
            (reverse("post_delete", args=[self.post.pk]), "Delete post"),
        ]

        for url, page_text in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, page_text)

        self.client.logout()
        for url, page_text in [
            (reverse("login"), "Log in"),
            (reverse("register"), "Create an account"),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, page_text)

    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new-writer",
                "password1": "A-strong-password-543",
                "password2": "A-strong-password-543",
            },
        )

        self.assertRedirects(response, reverse("post_list"))
        self.assertTrue(
            User.objects.filter(username="new-writer").exists()
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_required_for_post_create(self):
        urls = [
            reverse("post_create"),
            reverse("post_edit", args=[self.post.pk]),
            reverse("post_delete", args=[self.post.pk]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={url}",
                )

    def test_user_can_log_in_and_log_out(self):
        login_response = self.client.post(
            reverse("login"),
            {"username": "writer", "password": "test-password-123"},
        )
        self.assertRedirects(login_response, reverse("post_list"))

        logout_response = self.client.post(reverse("logout"))
        self.assertRedirects(logout_response, reverse("post_list"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logged_in_user_can_create_post(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("post_create"),
            {"title": "A new post", "content": "Post content"},
        )

        new_post = Post.objects.get(title="A new post")
        self.assertRedirects(response, reverse("post_detail", args=[new_post.pk]))
        self.assertEqual(new_post.author, self.user)

    def test_empty_title_and_content_show_validation_errors(self):
        self.client.force_login(self.user)
        post_count = Post.objects.count()

        response = self.client.post(
            reverse("post_create"),
            {"title": "   ", "content": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a title.")
        self.assertContains(response, "Please enter the post content.")
        self.assertEqual(Post.objects.count(), post_count)

    def test_logged_in_user_can_upload_featured_image(self):
        image_data = BytesIO()
        Image.new("RGB", (1, 1)).save(image_data, format="PNG")
        image = SimpleUploadedFile(
            "cover.png",
            image_data.getvalue(),
            content_type="image/png",
        )
        self.client.force_login(self.user)

        with tempfile.TemporaryDirectory() as media_dir:
            with override_settings(MEDIA_ROOT=media_dir):
                response = self.client.post(
                    reverse("post_create"),
                    {
                        "title": "Post with image",
                        "content": "Post content",
                        "featured_image": image,
                    },
                )
                post = Post.objects.get(title="Post with image")

                self.assertRedirects(
                    response,
                    reverse("post_detail", args=[post.pk]),
                )
                self.assertTrue(post.featured_image.name.startswith("post_images/"))
                self.assertTrue(os.path.isfile(post.featured_image.path))
                image_url = post.featured_image.url
                list_response = self.client.get(reverse("post_list"))
                detail_response = self.client.get(
                    reverse("post_detail", args=[post.pk])
                )

                self.assertContains(list_response, f'src="{image_url}"')
                self.assertContains(detail_response, f'src="{image_url}"')

    def test_only_author_can_edit_or_delete_post(self):
        self.client.force_login(self.other_user)

        edit_response = self.client.get(
            reverse("post_edit", args=[self.post.pk])
        )
        delete_response = self.client.get(
            reverse("post_delete", args=[self.post.pk])
        )

        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)

    def test_author_can_edit_and_delete_post(self):
        self.client.force_login(self.user)
        original_updated_at = self.post.updated_at

        edit_response = self.client.post(
            reverse("post_edit", args=[self.post.pk]),
            {"title": "Updated title", "content": "Updated content"},
        )
        self.assertRedirects(edit_response, reverse("post_detail", args=[self.post.pk]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated title")
        self.assertGreaterEqual(self.post.updated_at, original_updated_at)

        delete_response = self.client.post(
            reverse("post_delete", args=[self.post.pk])
        )
        self.assertRedirects(delete_response, reverse("post_list"))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_admin_can_manage_posts_and_search_by_title(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin-password-123",
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:blog_post_changelist"),
            {"q": "First post"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First post")
        self.assertContains(response, self.user.username)
        self.assertContains(response, "author")
        self.assertContains(response, "created_at")

    def test_admin_can_open_user_management(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin-password-123",
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:auth_user_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
