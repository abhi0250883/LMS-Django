from django.shortcuts import render,redirect,get_object_or_404
from myapp.models import *
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum, Count
from django.db.models import Q
from datetime import datetime, timedelta
import random
import stripe
from .models import Coupon, course, CouponUsage
# Create your views here.
def nav(request):
    return render(request,"nav.html")

def certificate(request):
    return render(request,'certificate.html')

def userregister(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        mobile = request.POST.get('mobile')

        if password != confirm_password:
            return render(request, "signup.html", {
                'msg': "Password & Confirm Password do not match"
            })

        # Check duplicate
        if student_reg.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                'msg': "Username already exists"
            })

        if student_reg.objects.filter(user_email=email).exists():
            return render(request, "signup.html", {
                'msg': "Email already exists"
            })

        # Generate OTP
        
        otp = random.randint(1000, 9999)

        
        subject = "Email Verification OTP"
        message = f"Your OTP is: {otp}"
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, message, email_from, [email])

        
        return render(request, "otp_page.html", {'otp': otp,'username': username,'email': email,    'first_name': first_name,'last_name': last_name,'password': password,'mobile': mobile, })

    return render(request, "signup.html")


def otp_verify(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        real_otp = request.POST.get("real_otp")

        if entered_otp != real_otp:
            return render(request, "otp_page.html", {'msg': "Incorrect OTP!"})

        
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        mobile = request.POST.get("mobile")

        
        student = student_reg()
        student.username = username
        student.user_email = email
        student.first_name = first_name
        student.last_name = last_name
        student.password = password
        student.mobile = mobile

        student.save()

        #return render(request, "student_login.html", {'msg': "Account created successfully!"})
        
        subject = "Registration Successful"
        message = f"Hi {first_name},\n\nYour admission/registration is completed successfully!"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        return redirect('/thankyou')
    return render(request, "otp_page.html")



def login(request):
    if request.method =="POST":
        u=request.POST.get('username')
        e=request.POST.get('email')
        p=request.POST.get('password')
        res=student_reg.objects.filter( user_email=e,password=p)
        length=len(res)
        
        if length>0:
            request.session['email']=e
            #request.session['username']=u
            return redirect("/home")
        else:
            return render(request,'login.html',{"msg":"Invalid candidate"})
    else:
        return render(request,'login.html')
    
def logout(request):
    if not request.session.has_key('email'):
        return redirect('/login')
    del request.session['email']
    return redirect('/home')

def home(request):
    return render(request,"index.html")
    
def contact(request):
    return render(request,'contact.html')

def all_course(request):
    res=course.objects.all()
    return render(request,'./admin/course.html',{'course':res})

def viewcourse(request):
    course_obje = course.objects.all()
    return render(request, 'view_course.html', {'course': course_obje})

def testmail(request):
    if request.method == "POST":
        e=request.POST.get('user_email')
        subject="Wecome to the Elearing LMS Group"
        message="Welcome to Elearning LMS"
        email_from=settings.EMAIL_HOST_USER
        recipient=[e,]
        send_mail(subject,message,email_from,recipient)
        msg="Congratulation! You have join your favourite course through Elearning LMS"
        return render(request, 'test_mail.html',{'msg':msg})
    else:
        return render(request, 'test_mail.html')


def thankyou(request):
    return render(request, "thankyou.html")

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request,id):
    Course=course.objects.get(id=id)
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data' : {
                'currency' : 'usd',
                'product_data' : {
                    'name': Course.title,
                },
                'unit_amount': 1000,
            },
            'quantity':1,
        }],
        mode='payment',
        success_url = f"http://127.0.0.1:8000/payment-success/{id}/",
        cancel_url = f"http://127.0.0.1:8000/payment-failed",
    ) 
    print(session.url)

    return redirect(session.url)

def payment_success(request,id):
    Course = get_object_or_404(course,id=id)
    
    #Try to find user by session or manually retrieve email
    user_email=  request.session.get('email') # Check session email is stored
    
    if not user_email:
        return render(request,'payment-failed.html',{'error': "User email not found"})
    
    user = get_object_or_404(student_reg, user_email=user_email)
    #add course to purchased_courses
    user.purchased_courses.add(Course)
    print(user)
    
    return render(request, 'payment-success.html')
    
def payment_failed(request):
    return render(request, 'payment-failed.html')

def check_out(request):
    res2=course.objects.all()
    return render(request,'checkout.html',{'data':res2})

def purchase_course(request):
    user_email = request.session.get('email')
    
    if user_email:
        user = student_reg.objects.get(user_email=user_email)
        print(user)
        purchased_course = user.purchased_courses.all().order_by('id')
        print(purchased_course)
    else:
        purchased_course = []
    return render(request, 'purchased_course.html',{"purchased_courses":purchased_course})

def view_lesson(request,id):
    co =course.objects.get(id=id)
    print(id)
    print("co:----", co)
    res=lesson.objects.filter(Course=co)
    print(res)
    mcqs = MCQQuestion.objects.filter(course=co)
    return render(request,'view_lesson.html', {'lessons':res,'mcqs': mcqs,"coid" : id})

def take_test(request, id):
    co = course.objects.get(id=id)
    mcqs = MCQQuestion.objects.filter(course=co)

    if request.method == "POST":
        score = 0
        total = mcqs.count()

        for mcq in mcqs:
            user_ans = request.POST.get(f"q{mcq.id}")
            if user_ans == mcq.correct_option:
                score += 1

        percentage = (score / total) * 100

        # Get student from session email
        stu_email = request.session.get("email")
        stu = student_reg.objects.get(user_email=stu_email)

        return render(request, "test_result.html", {
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "course_id": co.id,
            "student_id": stu.id,
        })

    return render(request, "take_test.html", {"mcqs": mcqs})



def certificate_detail(request,id,sid):
    user_emai=  request.session.get('email')
    cert=course.objects.get(id=id)
    stu=student_reg.objects.get(id=sid)
    return render(request,'certificate.html',{'cert':cert,'user_email': user_emai,'stu':stu})


def save_progress(request):
    if request.method == "POST":
        lesson_id = request.POST.get("lesson_id")   

        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson_id=lesson_id
        )

        progress.watched_2min = True
        progress.save()

        return redirect(request.META.get('HTTP_REFERER'))
  

#Admin part
def adminpanel(request):
    return render(request,'./admin/admin_panel.html')

def admin_sidebar(request):
    return render(request,'admin_sidebar.html')

def course_detail(request):
    res1=course.objects.all()
    return render(request,'./admin/course_detail.html',{"data":res1})



def view_admin_course(request):
    course_obje = course.objects.all().order_by('-created_at')
    
    total_value = course_obje.aggregate(total=Sum('price'))['total'] or 0
    
    # Get unique instructors count
    unique_instructors = course_obje.values('instructor').distinct().count()
    
    # Count courses created this month
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    new_this_month = course_obje.filter(created_at__gte=first_day_of_month).count()
    
    # Get list of unique instructors for filter dropdown
    instructors_list = course_obje.values_list('instructor', flat=True).distinct()
    
    context = {
        'course': course_obje,
        'total_value': total_value,
        'unique_instructors': unique_instructors,
        'new_this_month': new_this_month,
        'instructors_list': instructors_list,
    }
    
    return render(request, './admin/view_admin_course.html', context)

def edit_course(request,id):
    course_obj=course.objects.get(id=id)
    if request.method == "POST":
        course_obj.title=request.POST.get('title')
        course_obj.description=request.POST.get('description')
        course_obj.prerequisites=request.POST.get('prerequisites')
        course_obj.instructor=request.POST.get('instructor')
        course_obj.price=request.POST.get('price')
        if request.FILES.get('image'):
            course_obj.image = request.FILES.get('image')
        if request.FILES.get('pdf_material'):
            course_obj.pdf_material = request.FILES.get('pdf_material')
        course_obj.save()
        return redirect('/coursedetail')
    else:
        return render(request,'./admin/edit_course.html',{'course_obj':course_obj})
    
def delete_course(request,id):
    corse=course.objects.get(id=id)
    corse.delete()
    return redirect('/coursedetail')

def singlecoursedetail(request,id):
    corse=course.objects.get(id=id)
    return render(request,'./admin/single_course_detail.html',{'corse':corse})

def add_course(request):
    
    if request.method=="POST":
        t=request.POST.get('title')
        d=request.POST.get('description')
        req=request.POST.get('prerequisites')
        i=request.POST.get('instructor')
        img=request.FILES.get('image')
        pdf=request.FILES.get('pdf_material')
        
        price=request.POST.get('price')
        duration=request.POST.get('courseduration')

        if course.objects.filter(title=t).exists():
            return render(request,'./admin/addcourse.html',{'msg': "This course name already exsists in the list"})
        
        else:
            add=course()
            add.title=t
            add.description=d
            add.prerequisites=req
            add.instructor=i
            add.image=img
            add.pdf_material=pdf
            add.price=price
            add.course_duration=duration
            add.save()
            return render(request,'./admin/addcourse.html',{'msg':"Your course is saved successfully"})
    else:
        return render(request,'./admin/addcourse.html')

'''
not in use 
def add_lesson(request, id):
    current_course = course.objects.get(id=id)
    courses = course.objects.all()

    if request.method == "POST":
        t = request.POST.get('title')
        c = request.POST.get('content')
        vi = request.FILES.get('video_url')
        pdf = request.FILES.get('pdf_material')

        
        if lesson.objects.filter(title=t, Course=current_course).exists():
            return render(request, './admin/add_lesson.html', {
                "error": f"Lesson '{t}' already exists in this course!",
                "current_course": current_course,
                "courses": courses
            })

        
        new_lesson = lesson(
            Course=current_course,
            title=t,
            content=c,
            video_url=vi,
            pdf_material=pdf
        )
        new_lesson.save()

        return render(request, 'left_side_lesson.html', {
            "success": "Lesson added successfully!",
            "current_course": current_course,
            "courses": courses
        })

    return render(request, 'left_side_lesson.html', {
        'current_course': current_course,
        'courses': courses
    })
'''



def admin_view_lessons(request):
    courses = course.objects.all().order_by('title')   
    lessons = lesson.objects.select_related('Course').all().order_by('-id')

    # GET se course filter
    course_id = request.GET.get('course')
    if course_id:
        lessons = lessons.filter(Course_id=course_id)

    context = {
        'courses': courses,
        'lessons': lessons,
        'selected_course_id': int(course_id) if course_id else None,
    }
    return render(request, './admin/view_admin_lesson.html', context)

def admin_view_lesson(request, id):
    Lesson=lesson.objects.filter(Course=id)
    if request.method == "POST":
        t = request.POST.get('title')
        c = request.POST.get('content')
        vi = request.FILES.get('video_url')
        pdf = request.FILES.get('pdf_material')
        
        if lesson.objects.filter(title=t).exists():
            return render(request,"left_side_lesson.html",{"msg":"This chapter is already available in the lesson"})
        else:
            add = lesson()
            add.title=t,
            add.content=c,
            add.video_url=vi,
            add.pdf_material=pdf
            add.save()
    else:   
        return render(request,"./admin/left_side_lesson.html",{"lesson":Lesson})

def student_list(request):
    Student = student_reg.objects.all()
    return render(request,"./admin/student_detail.html",{'student':Student})


def admin_create_coupon(request):
    if request.method == "POST":
        code = request.POST.get("code")
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")
        min_amount = request.POST.get("min_amount") or 0
        expiry_date = request.POST.get("expiry_date")
        max_uses_per_user = request.POST.get("max_uses_per_user")
        user_type = request.POST.get("user_type")
        course_ids = request.POST.getlist("allowed_courses")

        coupon = Coupon.objects.create(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            min_amount=min_amount,
            expiry_date=expiry_date if expiry_date else None,
            max_uses_per_user=max_uses_per_user,
            user_type=user_type
        )

        for cid in course_ids:
            coupon.allowed_courses.add(cid)

        coupon.save()

        return render(request, "success.html")

    Courses = course.objects.all()
    return render(request, "./admin/admin_create_coupon.html", {"courses": Courses})



def apply_coupon(request, course_id):
    course = course.objects.get(id=course_id)

    final_price = course.price
    discount_amount = 0
    message = ""
    error = ""

    if request.method == "POST":
        code = request.POST.get("code")
        user = request.user

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except:
            error = "Invalid coupon code."
            return render(request, "checkout.html", {
                "course": course,
                "final_price": final_price,
                "discount": discount_amount,
                "error": error,
            })

        valid, msg = coupon.is_valid(user, course, course.price)

        if not valid:
            error = msg
        else:
            # calculate discount
            if coupon.discount_type == "percent":
                discount_amount = (course.price * coupon.discount_value) // 100
            else:
                discount_amount = coupon.discount_value

            final_price = course.price - discount_amount

            if final_price < 0:
                final_price = 0

            message = "Coupon applied successfully!"

    return render(request, "checkout.html", {
        "course": course,
        "final_price": final_price,
        "discount": discount_amount,
        "message": message,
        "error": error
    })