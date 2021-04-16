import time
from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect,reverse,get_object_or_404
from django.db.models import Count,Q
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.conf import settings
from .models import National,Special,Student
from django.db.models import DateTimeField

filename = 'log.txt'

# 封装函数,分页设置
def get_post_list(request,all_list):
    paginator = Paginator(all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    # 获取url的页面参数(GET请求),默认是1
    page_num = request.GET.get('page', 1)
    # 获取前端的传入的数值，如果没有则返回1
    page_of_post = paginator.get_page(page_num)
    # 获取当前页码前后各2页的范围
    currentr_page_num = page_of_post.number
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + list(range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首码和尾码,如果首码不等于1则在下标为0的位置插入1
    if page_range[0] != 1:
        page_range.insert(0, 1)
    # 如果尾码不等于最大值得话则插入最大值
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    context = {}
    context["page_range"] = page_num
    context['posts'] = page_of_post.object_list
    context['page_of_post'] = page_of_post
    context['page_range'] = page_range
    return context

# 登录界面
def index(request):
    if  request.user.is_authenticated:
        return redirect('query')
    return render(request, 'gangweifx/index.html')


# 执行登录
def login(request):
    if request.method != "POST":
        return render(request, 'gangweifx/index.html', {'message': "非法请求"})
    username = request.POST.get('username','')
    password =  request.POST.get("password",'')
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return redirect('query')
    else:
        return render(request, 'gangweifx/index.html', {'message': "用户名或密码不正确"})


# 退出登录
def logout(request):
    auth.logout(request)
    return redirect('login')


# 登录后的页面
def query(request):
    if not request.user.is_authenticated:
        return redirect('index')
    context = {}
    context["username"] = request.user.username
    context["super"] = request.user.is_superuser
    return render(request,'gangweifx/query.html',context)


# 国编列表
def NationalQuery(request):
    if not request.user.is_authenticated:
        return redirect('index')
    # 国编全部岗位
    National_list = National.objects.annotate(students_num=Count('student'))
    context = get_post_list(request,National_list)
    context["query"] = "请输入招聘岗位或岗位代码(国编)"
    return render(request,'gangweifx/National/NationalList.html',context)

# 执行搜索
def NationalResp(request):
    if not request.user.is_authenticated:
        return redirect('index')
    post = request.GET.get('post')
    select = request.GET.get('select')
    post = "".join(post.split())
    # 如果为空则返回数据
    if post == "":
        query = "请输入值"
        return render(request, 'gangweifx/National/NationalQuery.html', {"query":query})
    if select == "岗位代码":
        selects = National.objects.filter(Q(code__contains=post)).annotate(students_num=Count('student'))
        context = get_post_list(request, selects)
        context["query"] = "一共搜索到" + str(len(selects)) + "条数据"
        context['select'] = select
        context["post"] = post
        return render(request, 'gangweifx/National/NationalQuery.html', context)
    posts = National.objects.filter(Q(post__contains=select)&Q(city__contains=post)).annotate(students_num=Count('student'))
    context = get_post_list(request, posts)
    context["post"] = post
    context['select'] = select
    context["query"] = "一共搜索到" + str(len(posts)) + "条数据"
    return render(request, 'gangweifx/National/NationalQuery.html', context)


# 国编岗位详情页
def National_detail(request,National_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    National_content = get_object_or_404(National,pk=National_pk)
    Student_contents = Student.objects.filter(national_id=National_pk)
    context = {}
    context['National_content'] = National_content
    context['Student_contents'] = Student_contents
    context['user'] = request.user
    return render(request, 'gangweifx/National/National_content.html', context)


# 修改页面
def National_edit(request,Student_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    student = get_object_or_404(Student,pk=Student_pk)
    if request.user.is_superuser == True or student.teacher.pk == request.user.pk:
        referer = request.META.get('HTTP_REFERER', reverse('NationalQuery'))
        context = {}
        context["student"] = student
        context["referer"] = referer
        return render(request, 'gangweifx/National/NationalEdit.html', context)
    return HttpResponse("抱歉你没有权限!!!")



# 执行修改
def National_doedit(request,Student_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        remarks = request.POST.get('remarks')
        referer = request.POST.get("referer")
        teacherID = request.user.pk
        student = get_object_or_404(Student,pk=Student_pk)
        teacher = get_object_or_404(User,pk=teacherID)
        student.name = name
        student.phone = phone
        student.remarks = remarks
        student.teacher = teacher
        student.edit = DateTimeField(auto_now_add=True)
        student.save()
        with open(filename,'a') as file_object:
            file_object.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]" + teacher.username + "修改了"+ student.name + "的资料\n")
        return HttpResponseRedirect(referer)
    return HttpResponse("非法请求")

# 增加
def National_add(request,National_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    national = get_object_or_404(National,pk=National_pk)
    context = {}
    context["national"] = national
    context["referer"] = request.META.get('HTTP_REFERER', reverse('NationalQuery'))
    return render(request, 'gangweifx/National/NationalAdd.html', context)

# 执行增加
def National_doadd(request,National_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        remarks = request.POST.get('remarks')
        referer = request.POST.get("referer")
        teacherID = request.user.pk
        national = get_object_or_404(National,pk=National_pk)
        teacher = get_object_or_404(User,pk=teacherID)
        student = Student()
        student.name = name
        student.phone = phone
        student.national_id = national
        student.teacher = teacher
        student.remarks = remarks
        student.edit = DateTimeField(auto_now_add=True)
        student.save()
        with open(filename,'a') as file_object:
            file_object.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]" + teacher.username + "把"+ student.name + "添加到了国编岗位代码为" + national.code + "的岗位\n")
        return HttpResponseRedirect(referer)

# 删除
def National_delete(request,Student_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    student = get_object_or_404(Student,pk=Student_pk)
    teacherID = request.user.pk
    teacher = get_object_or_404(User, pk=teacherID)
    with open(filename, 'a') as file_object:
        file_object.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]" + teacher.username + "从国编代码为" + student.national_id.code + "中移除了名叫" + student.name + "的学生\n")
    national = get_object_or_404(National,pk=1)
    student.national_id = national
    student.teacher = teacher
    student.edit = DateTimeField(auto_now_add=True)
    student.save()
    referer = request.META.get('HTTP_REFERER',reverse('query'))
    return HttpResponseRedirect(referer)



# 特岗
def SpecialQuery(request):
    if not request.user.is_authenticated:
        return redirect('index')
    Special_list = Special.objects.annotate(students_num=Count('student'))
    context = get_post_list(request, Special_list)
    context["query"] = "请输入岗位名称或岗位代码(特岗)"
    return render(request, 'gangweifx/Special/SpecialList.html',context)


# 特岗查询
def SpecialResp(request):
    if not request.user.is_authenticated:
        return redirect('index')
    post = request.GET.get('post')
    post = "".join(post.split())
    # 如果为空则返回数据
    if post == "":
        query = "请输入值"
        return render(request, 'gangweifx/Special/SpecialQuery.html', {"query":query})
    # 再数据库中查询用户输入的值
    posts = Special.objects.filter(Q(post__contains=post) | Q(code__contains=post)).annotate(students_num=Count('student'))
    context = get_post_list(request, posts)
    # 没有值
    if not posts:
        context["query"] = "一共搜索到" + str(len(posts)) + "条数据"
        return render(request, 'gangweifx/Special/SpecialQuery.html', context)
    context["post"] = post
    context["query"] = "一共搜索到" + str(len(posts)) + "条数据"
    return render(request, 'gangweifx/Special/SpecialQuery.html', context)

# 详情页面
def Special_detail(request,Special_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    Special_content = get_object_or_404(Special,pk=Special_pk)
    Student_contents = Student.objects.filter(special_id=Special_pk)
    context = {}
    context['Special_content'] = Special_content
    context['Student_contents'] = Student_contents
    context['super'] = request.user.is_superuser
    return render(request, 'gangweifx/Special/Special_content.html', context)

# 修改页面
def Special_edit(request,Student_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    student = get_object_or_404(Student, pk=Student_pk)
    if request.user.is_superuser == True or student.teacher.pk == request.user.pk:
        context = {}
        context["student"] = student
        context["referer"] = request.META.get('HTTP_REFERER', reverse('SpecialQuery'))
        return render(request, 'gangweifx/Special/SpecialEdit.html', context)
    return HttpResponse("抱歉你没有权限!!!")



# 执行修改
def Special_doedit(request,Student_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        remarks = request.POST.get('remarks')
        referer = request.POST.get("referer")
        teacherID = request.user.pk
        student = get_object_or_404(Student,pk=Student_pk)
        teacher = get_object_or_404(User,pk=teacherID)
        student.name = name
        student.phone = phone
        student.teacher = teacher
        student.remarks = remarks
        student.edit = DateTimeField(auto_now_add=True)
        student.save()
        with open(filename,'a') as file_object:
            file_object.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]" + teacher.username + "修改了"+ student.name + "的资料\n")
        return HttpResponseRedirect(referer)

# 增加
def Special_add(request,Special_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    special = get_object_or_404(Special,pk=Special_pk)
    context = {}
    context["special"] = special
    context["referer"] = request.META.get('HTTP_REFERER', reverse('SpecialQuery'))
    return render(request, 'gangweifx/Special/SpecialAdd.html', context)

# 执行增加
def Special_doadd(request,Special_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        remarks = request.POST.get('remarks')
        referer = request.POST.get("referer")
        teacherID = request.user.pk
        special = get_object_or_404(Special,pk=Special_pk)
        teacher = get_object_or_404(User,pk=teacherID)
        student = Student()
        student.name = name
        student.phone = phone
        student.special_id = special
        student.teacher = teacher
        student.remarks = remarks
        student.edit = DateTimeField(auto_now_add=True)
        student.save()
        with open(filename,'a') as file_object:
            file_object.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]" + teacher.username + "把"+ student.name + "添加到了特岗岗位代码为" + special.code + "的岗位\n")
        return HttpResponseRedirect(referer)


# 删除
def Special_delete(request,Student_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    student = get_object_or_404(Student,pk=Student_pk)
    teacherID = request.user.pk
    teacher = get_object_or_404(User, pk=teacherID)
    with open(filename, 'a') as file_object:
        file_object.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]" + teacher.username + "从特岗代码为" + student.special_id.code + "中移除了名叫" + student.name + "的学生\n")
    special = get_object_or_404(Special,pk=1)
    student.special_id = special
    student.teacher = teacher
    student.edit = DateTimeField(auto_now_add=True)
    student.save()
    referer = request.META.get('HTTP_REFERER', reverse('query'))
    return HttpResponseRedirect(referer)


# 学生表
def StudentList(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    studentList = Student.objects.all()
    context = get_post_list(request,studentList)
    context["query"] = "请输入姓名或手机号"
    return render(request,'gangweifx/Student/StudentList.html', context)


# 搜索
def StudentResp(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    post = request.GET.get('post')
    post = "".join(post.split())
    # 如果为空则返回数据
    if post == "":
        query = "请输入值"
        return render(request, 'gangweifx/Student/StudentQuery.html', {"query":query})
    # 再数据库中查询用户输入的值
    posts = Student.objects.filter(Q(phone__contains=post) | Q(name__contains=post))
    context = get_post_list(request, posts)
    # 没有值
    if not posts:
        context["query"] = "一共搜索到" + str(len(posts)) + "条数据"
        return render(request, 'gangweifx/Student/StudentQuery.html', context)
    context["post"] = post
    context["query"] = "一共搜索到" + str(len(posts)) + "条数据"
    return render(request, 'gangweifx/Student/StudentQuery.html', context)


# 学生详情页面
def Student_detail(request,Student_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    Student_contents = get_object_or_404(Student,pk=Student_pk)
    context = {}
    avg = Student_contents.score_1 + Student_contents.score_2 + Student_contents.score_3 + Student_contents.score_4 + Student_contents.score_5
    avg = avg/5
    context['Student_contents'] = Student_contents
    context['avg'] = avg
    return render(request, 'gangweifx/Student/Student_content.html', context)


# 国编岗位填报
def Nationaltb(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    studentid = request.GET.get('studentid')
    student = get_object_or_404(Student,pk=studentid)
    National_list = National.objects.annotate(students_num=Count('student'))
    context = get_post_list(request, National_list)
    context["query"] = "请输入招聘岗位或岗位代码(国编)"
    context["student"] = student
    return render(request, 'gangweifx/National_tb/NationalList.html', context)


# 国编岗位填报搜索
def NationaltbResp(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    post = request.GET.get('post')
    studentid = request.GET.get('studentid')
    select = request.GET.get('select')
    student = get_object_or_404(Student,pk=studentid)
    post = "".join(post.split())
    # 如果为空则返回数据
    if post == "":
        query = "请输入值"
        return render(request, 'gangweifx/National_tb/NationalQuery.html', {"query":query})
    if select == "岗位代码":
        selects = National.objects.filter(Q(code__contains=post)).annotate(students_num=Count('student'))
        context = get_post_list(request, selects)
        context["query"] = "一共搜索到" + str(len(selects)) + "条数据"
        context["post"] = post
        context['select'] = select
        context["student"] = student
        return render(request, 'gangweifx/National_tb/NationalQuery.html', context)
    # 再数据库中查询用户输入的值
    posts = National.objects.filter(Q(post__contains=select) & Q(city__contains=post)).annotate(students_num=Count('student'))
    context = get_post_list(request, posts)
    context["post"] = post
    context['select'] = select
    context["student"] = student
    context["query"] = "一共搜索到" + str(len(posts)) + "条数据"
    return render(request, 'gangweifx/National_tb/NationalQuery.html', context)

# 国编岗位填报详情
def Nationaltb_detail(request,National_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    National_content = get_object_or_404(National, pk=National_pk)
    Student_contents = Student.objects.filter(national_id=National_pk)
    studentid =request.GET.get('studentid')
    student = get_object_or_404(Student,pk=studentid)
    context = {}
    context['National_content'] = National_content
    context['Student_contents'] = Student_contents
    context['student'] = student
    context['user'] = request.user
    return render(request, 'gangweifx/National_tb/National_content.html', context)



# 国编岗位填报国编添加
def  Nationaltb_doadd(request,National_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    referer = request.META.get('HTTP_REFERER', reverse('query'))
    studentid = request.GET.get('studentid')
    national = get_object_or_404(National, pk=National_pk)
    student = get_object_or_404(Student,pk=studentid)
    student.national_id = national
    teacherID = request.user.pk
    teacher = get_object_or_404(User, pk=teacherID)
    student.teacher = teacher
    student.edit = DateTimeField(auto_now_add=True)
    student.save()
    with open(filename, 'a') as file_object:
        file_object.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]" + teacher.username + "把" + student.name + "添加到了国编岗位代码为" + national.code + "的岗位\n")
    return HttpResponseRedirect(referer)


# 特岗
def Specialtb(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    studentid = request.GET.get('studentid')
    student = get_object_or_404(Student,pk=studentid)
    Special_list = Special.objects.annotate(students_num=Count('student'))
    context = get_post_list(request, Special_list)
    context["query"] = "请输入招聘岗位或岗位代码(国编)"
    context["student"] = student
    return render(request, 'gangweifx/Special_tb/SpecialList.html', context)


def SpecialtbResp(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    post = request.GET.get('post')
    studentid = request.GET.get('studentid')

    student = get_object_or_404(Student,pk=studentid)
    post = "".join(post.split())
    # 如果为空则返回数据
    if post == "":
        query = "请输入值"
        return render(request, 'gangweifx/Special_tb/SpecialQuery.html', {"query":query})
    # 再数据库中查询用户输入的值
    posts = Special.objects.filter(Q(post__contains=post) | Q(code__contains=post)).annotate(students_num=Count('student'))
    context = get_post_list(request, posts)
    # 没有值
    if not posts:
        context["query"] = "一共搜索到" + str(len(posts)) + "条数据"
        return render(request, 'gangweifx/Special_tb/SpecialQuery.html', context)
    context["post"] = post
    context["student"] = student
    context["query"] = "一共搜索到" + str(len(posts)) + "条数据"
    return render(request, 'gangweifx/Special_tb/SpecialQuery.html', context)


def Specialtb_detail(request,Special_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    Special_content = get_object_or_404(Special,pk=Special_pk)
    Student_contents = Student.objects.filter(special_id=Special_pk)
    studentid =request.GET.get('studentid')
    student = get_object_or_404(Student,pk=studentid)
    context = {}
    context['Special_content'] = Special_content
    context['Student_contents'] = Student_contents
    context['student'] = student
    context['super'] = request.user.is_superuser
    return render(request, 'gangweifx/Special_tb/Special_content.html', context)


def  Specialtb_doadd(request,Special_pk):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.user.is_superuser != True:
        return HttpResponse("抱歉你没有权限！")
    referer = request.META.get('HTTP_REFERER', reverse('query'))
    studentid = request.GET.get('studentid')

    special = get_object_or_404(Special, pk=Special_pk)
    student = get_object_or_404(Student,pk=studentid)
    student.special_id = special
    teacherID = request.user.pk
    teacher = get_object_or_404(User, pk=teacherID)
    student.teacher = teacher
    student.edit = DateTimeField(auto_now_add=True)
    student.save()
    with open(filename, 'a') as file_object:
        file_object.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]" + teacher.username + "把" + student.name + "添加到了特岗岗位代码为" + special.code + "的岗位\n")
    return HttpResponseRedirect(referer)







# def Nationalred(request):
#     filename = 'log.txt'
#     studengt = Student.objects.get(pk=1)
#     with open(filename, 'a') as file_object:
#         file_object.write("["+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"]"+studengt.name+"了\n")
#     # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
#     return HttpResponse("!!!!!!!!!!!!!!")



    # National_list = National.objects.annotate(students_num=Count('student'))
    # for National_lists in National_list:
    #     if National_lists.students_num > National_lists.number:
    #         print(National_lists.code,National_lists.city)



