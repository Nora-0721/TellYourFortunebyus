# posts/forms.py
from django import forms
from .models import Post,PostNew

class PostForm(forms.ModelForm):

	class Meta:
		model = Post
		fields = ['title', 'cover','language']

	def __init__(self,*args,**kwargs):
		super(PostForm,self).__init__(*args,**kwargs)
		self.fields['title'].label = '您的名字'
		self.fields['cover'].label = '您的图片'
		self.fields['language'].label = '您的图片'

    

class PostPhoneForm(forms.ModelForm):

	class Meta:
		model = Post
		fields = ['title', 'cover']

	def __init__(self,*args,**kwargs):
		super(PostPhoneForm,self).__init__(*args,**kwargs)
		self.fields['title'].label = '您的名字'
		self.fields['cover'].label = '您的图片'