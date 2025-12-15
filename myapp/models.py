from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import date
from django.contrib.auth.models import User

# Create your models here.
class course(models.Model):
    title=models.CharField(max_length=100)
    description=models.TextField()
    prerequisites=models.TextField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    instructor=models.CharField(max_length=100)
    image=models.ImageField(upload_to='course_image/',blank=True,null=True)
    pdf_material=models.FileField(upload_to='course_pdfs/',blank=True,null=True)
    price=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    course_duration=models.CharField(max_length=255,blank=True,null=True)
    
    def __str__(self):
        return f"{self.id} - {self.title}"
    
class student_reg(models.Model):
    username=models.CharField(max_length=100)
    user_email=models.CharField(max_length=100)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    mobile=models.CharField(max_length=11)
    purchased_courses = models.ManyToManyField(course,blank=True,null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
class lesson(models.Model):
    Course=models.ForeignKey(course, on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    content=RichTextUploadingField() #CKeditor Field
    #video_url=models.URLField(blank=True,null=True)
    video_url=models.FileField(blank=True,null=True)
    pdf_material=models.FileField(upload_to='course_pdfs/',blank=True,null=True)
    
    def __str__(self):
        return self.title

class MCQQuestion(models.Model):
    course=models.ForeignKey('course', on_delete=models.CASCADE, related_name="mcqs")
    question_text=models.TextField()
    option_a=models.CharField(max_length=255)
    option_b=models.CharField(max_length=255)
    option_c=models.CharField(max_length=255)
    option_d=models.CharField(max_length=255)
    correct_option=models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D'),])
    explanation=models.TextField(blank=True,null=True)
    
    def __str__(self):
        return self.question_text
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)

    discount_type = models.CharField(
        max_length=10,
        choices=(("percent", "Percent"), ("flat", "Flat"))
    )
    discount_value = models.IntegerField()

    active = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True)

    min_amount = models.IntegerField(default=0)

    # only per-user usage
    max_uses_per_user = models.IntegerField(null=True, blank=True)

    # specific courses
    allowed_courses = models.ManyToManyField('Course', blank=True)

    # new or existing users
    user_type = models.CharField(
        max_length=20,
        choices=(("all", "All Users"),
                 ("new", "New Users"),
                 ("existing", "Existing Users")),
        default="all"
    )

    def __str__(self):
        return self.code

    def is_valid(self, user, course, price):

        if not self.active:
            return False, "Coupon is not active."

        if self.expiry_date and self.expiry_date < date.today():
            return False, "Coupon expired."

        if price < self.min_amount:
            return False, f"Minimum order amount is ₹{self.min_amount}."

        # course validation
        if self.allowed_courses.exists() and course not in self.allowed_courses.all():
            return False, "This coupon is not valid for this course."

        # user type condition
        if self.user_type == "new":
            if Payment.objects.filter(user=user).exists():
                return False, "Valid only for new users."

        if self.user_type == "existing":
            if not Payment.objects.filter(user=user).exists():
                return False, "Valid only for existing users."

        # per-user limit
        used_count = CouponUsage.objects.filter(user=user, coupon=self).count()
        if self.max_uses_per_user and used_count >= self.max_uses_per_user:
            return False, "You have already used this coupon."

        return True, "Coupon is valid."


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
