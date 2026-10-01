from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Post


class BlogViewsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
        )
        self.other_user = User.objects.create_user(
            username="reader",
        )
        self.post = Post.objects.create(
            title="First post",
            content="Post content",
            author=self.author,
        )

    def test_post_list_and_detail_are_public(self):
        self.assertEqual(self.client.get(reverse("post_list")).status_code, 200)
        self.assertEqual(
            self.client.get(
                reverse("post_detail", kwargs={"pk": self.post.pk})
            ).status_code,
            200,
        )

    def test_title_search_filters_posts(self):
        Post.objects.create(
            title="A different title",
            content="Another post",
            author=self.author,
        )
        response = self.client.get(reverse("post_list"), {"q": "First"})
        self.assertContains(response, "First post")
        self.assertNotContains(response, "A different title")

    def test_uploaded_image_is_saved_and_shown(self):
        image_buffer = BytesIO()
        Image.new("RGB", (2, 2), color="green").save(image_buffer, format="PNG")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("post_create"),
            {
                "title": "Post with image",
                "content": "An image is attached.",
                "featured_image": SimpleUploadedFile(
                    "post.png",
                    image_buffer.getvalue(),
                    content_type="image/png",
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(title="Post with image")
        self.addCleanup(post.featured_image.delete, save=False)
        self.assertTrue(post.featured_image.name.startswith("post_images/"))
        self.assertContains(
            self.client.get(reverse("post_detail", args=[post.pk])),
            post.featured_image.url,
        )
        self.assertContains(
            self.client.get(reverse("post_list")),
            post.featured_image.url,
        )

    def test_registration_logs_in_new_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_writer",
                "password1": "A-strong-test-password-742!",
                "password2": "A-strong-test-password-742!",
            },
        )

        self.assertRedirects(response, reverse("post_list"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_and_logout_pages_are_available(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.client.force_login(self.author)
        self.assertRedirects(
            self.client.post(reverse("logout")),
            reverse("post_list"),
        )

    def test_create_requires_login_and_sets_current_user_as_author(self):
        create_url = reverse("post_create")
        response = self.client.get(create_url)
        self.assertRedirects(response, f"{reverse('login')}?next={create_url}")

        self.client.force_login(self.other_user)
        response = self.client.post(
            create_url,
            {"title": "New post", "content": "Some content"},
        )

        new_post = Post.objects.get(title="New post")
        self.assertRedirects(response, reverse("post_detail", args=[new_post.pk]))
        self.assertEqual(new_post.author, self.other_user)

    def test_users_cannot_edit_or_delete_another_users_post(self):
        self.client.force_login(self.other_user)
        edit_url = reverse("post_edit", kwargs={"pk": self.post.pk})
        delete_url = reverse("post_delete", kwargs={"pk": self.post.pk})

        self.assertEqual(self.client.get(edit_url).status_code, 404)
        self.assertEqual(self.client.get(delete_url).status_code, 404)
        self.assertEqual(
            self.client.post(delete_url).status_code,
            404,
        )
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_owner_can_edit_and_delete_post(self):
        self.client.force_login(self.author)
        edit_url = reverse("post_edit", kwargs={"pk": self.post.pk})
        delete_url = reverse("post_delete", kwargs={"pk": self.post.pk})

        response = self.client.post(
            edit_url,
            {"title": "Updated title", "content": "Updated content"},
        )
        self.assertRedirects(
            response,
            reverse("post_detail", kwargs={"pk": self.post.pk}),
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated title")

        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("post_list"))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_empty_title_and_content_are_rejected(self):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("post_create"),
            {"title": "", "content": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.", count=2)
        self.assertEqual(Post.objects.count(), 1)
