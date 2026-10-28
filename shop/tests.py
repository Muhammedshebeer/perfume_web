import io
import shutil
import tempfile
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from .models import Brand, Category, Product, ProductImage

TEST_MEDIA=tempfile.mkdtemp(prefix='classio_tests_')

def image_file(name='sample.jpg', format='JPEG'):
    data=io.BytesIO()
    Image.new('RGB',(64,64),color='#dac6ae').save(data,format=format)
    return SimpleUploadedFile(name,data.getvalue(),content_type={'JPEG':'image/jpeg','PNG':'image/png','WEBP':'image/webp'}[format])

@override_settings(MEDIA_ROOT=TEST_MEDIA)
class ProductUploadTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA,ignore_errors=True)
    def setUp(self):
        self.brand=Brand.objects.create(name='Test Brand',slug='test-brand')
        self.category=Category.objects.create(name='Test Category',slug='test-category')
        self.staff=get_user_model().objects.create_user(username='staff',password='safe-password-123',is_staff=True)
        self.payload={'name':'Velvet Noir','slug':'velvet-noir','sku':'CN-001','brand':self.brand.pk,
            'category':self.category.pk,'description':'A luxurious scent','price':'249.00',
            'size_ml':100,'concentration':'Eau de Parfum','stock':9,'is_active':'on'}
    def login(self): self.client.force_login(self.staff)
    def create(self,**extra):
        self.login()
        payload={**self.payload,'image':image_file(),**extra}
        return self.client.post(reverse('product_add'),payload)
    def test_valid_upload_and_multiple_gallery(self):
        response=self.create(gallery_images=[image_file('second.png','PNG'),image_file('third.webp','WEBP')])
        self.assertRedirects(response,reverse('manage_products'))
        p=Product.objects.get(slug='velvet-noir')
        self.assertTrue(p.image.name)
        self.assertEqual(p.gallery.count(),2)
    def test_reject_fake_image_content(self):
        response=self.create(image=SimpleUploadedFile('bad.jpg',b'not-image',content_type='image/jpeg'))
        self.assertEqual(response.status_code,200)
        self.assertFalse(Product.objects.exists())
    def test_reject_invalid_extension(self):
        response=self.create(image=SimpleUploadedFile('bad.txt',b'hello',content_type='text/plain'))
        self.assertEqual(response.status_code,200)
        self.assertFalse(Product.objects.exists())
    @override_settings(MAX_PRODUCT_IMAGE_MB=1)
    def test_reject_oversized_upload(self):
        response=self.create(image=SimpleUploadedFile('large.jpg',b'x'*(1024*1024+1),content_type='image/jpeg'))
        self.assertEqual(response.status_code,200)
        self.assertFalse(Product.objects.exists())
    def test_main_image_required_for_new_product(self):
        self.login()
        self.client.post(reverse('product_add'),self.payload)
        self.assertFalse(Product.objects.exists())
    def test_edit_preserves_images(self):
        self.create(gallery_images=[image_file('gallery.jpg')]); p=Product.objects.get()
        main_name=p.image.name
        gallery_pk=p.gallery.first().pk
        resp=self.client.post(reverse('product_edit',args=[p.pk]),{**self.payload,'name':'New Name'})
        self.assertEqual(resp.status_code,302)
        p.refresh_from_db()
        self.assertEqual(p.image.name,main_name)
        self.assertTrue(p.gallery.filter(pk=gallery_pk).exists())
    def test_replace_main_image(self):
        self.create();p=Product.objects.get();old=p.image.name
        resp=self.client.post(reverse('product_edit',args=[p.pk]),{**self.payload,'image':image_file('replacement.png','PNG')})
        self.assertEqual(resp.status_code,302)
        p.refresh_from_db();self.assertNotEqual(old,p.image.name)
    def test_delete_gallery_image(self):
        self.create(gallery_images=[image_file('detail.jpg')]);p=Product.objects.get();picture=p.gallery.first()
        resp=self.client.post(reverse('product_edit',args=[p.pk]),{**self.payload,'remove_gallery':[picture.pk]})
        self.assertEqual(resp.status_code,302)
        self.assertFalse(ProductImage.objects.filter(pk=picture.pk).exists())
    def test_anonymous_cannot_upload_or_delete(self):
        self.client.logout()
        response=self.client.post(reverse('product_add'),{**self.payload,'image':image_file()})
        self.assertEqual(response.status_code,302)
        self.assertFalse(Product.objects.exists())
    def test_product_detail_gallery(self):
        self.create(gallery_images=[image_file('other.jpg')]);p=Product.objects.get()
        response=self.client.get(p.get_absolute_url())
        self.assertContains(response,'data-gallery-src',count=2)
