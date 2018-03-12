from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Event(models.Model):
    event_name = models.CharField(max_length=100, default='')
    event_content = models.TextField(default='')
    owner = models.ManyToManyField(User, related_name='owner')
    vendor = models.ManyToManyField(User, related_name='vendor')
    guest = models.ManyToManyField(User, related_name='guest')
    invite = models.ManyToManyField(User, related_name='invite')
    
    def __str__(self):  
        return self.event_name
      
      
class Question(models.Model):
    name = models.CharField(max_length = 128, default='')
    event_belong = models.ForeignKey(Event, on_delete=models.CASCADE)
    multi = models.BooleanField(default = True)
    expired = models.BooleanField(default = False)
    vendor = models.ManyToManyField(User, related_name ='question_vendor')
    def __str__(self):
        return self.name

class Choice(models.Model):
    choice_text = models.CharField(max_length=200, default='')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text
    

class Answer(models.Model):
    answer_text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guest = models.BooleanField(default = False)
    def __str__(self):
        return self.answer_text
'''
class UserProfile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    description = models.CharField(max_length=100, default='')
    city = models.CharField(max_length=100, default='')
    website = models.URLField(default='')
    phone = models.IntegerField(default=0)


def create_profile(sender, **kwargs):
        if kwargs['created']:
            user_profile = UserProfile.objects.create(user=kwargs(['instance'])

post_save.connect(create_profile, sender=User)
'''
