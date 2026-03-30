import json

from django.db import models
import django.utils.timezone as timezone

class SeedToFace(models.Model):
    choices = (
        (1, '男'), (2, '女')
    )
    sex = models.IntegerField(choices=choices)
    # image = models.ImageField(upload_to='images/')  # 存储图片
    landmarks = models.TextField()  # 存储关键点坐标，使用 JSONField
    seed = models.IntegerField(default=0)
    def __str__(self):
        return "SeedToFace for "+self.image.name

    def set_landmarks(self, landmarks):
        self.landmarks = json.dumps(landmarks)  # 将列表转为 JSON 字符串

    def get_landmarks(self):
        return json.loads(self.landmarks)  # 将 JSON 字符串转回列表


# Create your models here.
class FaceFeature(models.Model):
    choices = (
        (1, '男'), (2, '女')
    )
    sex = models.IntegerField(choices=choices)
    image = models.ImageField(upload_to='images/')  # 存储图片
    relative_landmarks = models.TextField()  # 存储关键点坐标，使用 JSONField

    def __str__(self):
        return "FaceFeature for "+self.image.name

    def set_landmarks(self, relative_landmarks):
        self.relative_landmarks = json.dumps(relative_landmarks)  # 将列表转为 JSON 字符串

    def get_landmarks(self):
        return json.loads(self.relative_landmarks)  # 将 JSON 字符串转回列表

class User(models.Model):
    username = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    def __str__(self):
        return self.username

class Post(models.Model):
    title = models.CharField(max_length=20)
    cover = models.ImageField(upload_to='image/')
    language = models.CharField(max_length=20)
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

class PostNew(models.Model):
    cover = models.ImageField(upload_to='image/')
    choices = (
        (1, '男'), (2, '女')
    )
    sex = models.IntegerField(choices=choices)
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

class PostNewImage(models.Model):
    cover1 = models.ImageField(upload_to='image/')
    choices = (
        (1, '男'), (2, '女')
    )
    cover2 = models.ImageField(upload_to='image/')
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title