from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings

def upload_location(instance, filename):
	return "%s/%s" %(instance.id, filename)

class Post(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
	title = models.CharField(max_length=200)
	slug = models.SlugField(unique=True)
	image = models.ImageField(upload_to=upload_location,
		null=True, 
		blank=True, 
		width_field="width_field", 
		height_field="height_field")
	height_field = models.IntegerField(default=0)
	width_field = models.IntegerField(default=0)
	text = models.TextField()
	created_date = models.DateTimeField(default=timezone.now)
	published_date = models.DateTimeField(blank=True, null=True)


	def publish(self):
		self.published_date = timezone.now()
		self.save()

	def __str__(self):
		return self.title
	
def get_absolute_url(self):
	return reverse("posts:detail", kwargs={"slug": self.slug})

#class Meta:
#	ordering = ["-created_date", "-published_date"]

def pre_save_post_receiver (sender, instance, *args, **kwargs):
	slug = slugify(instance.title)
	exists = Post.objects.filter(slug=slug).exists()
	if exists:
		slug = "%s-%s" %(slug, instance.id)
	instance.slug = slug

pre_save.connect(pre_save_post_receiver, sender=Post)
	
