from django.db import models
from django.contrib.auth.models import User

# 国编
class National(models.Model):
    city = models.CharField(max_length=30,default="",verbose_name="招聘市(区)县")
    company = models.CharField(max_length=30,default="",verbose_name="招聘单位")
    post = models.CharField(max_length=30,default="",verbose_name="招聘岗位")
    code = models.CharField(max_length=20,default="",verbose_name="岗位代码")
    condition = models.TextField(default="",verbose_name="岗位条件")
    number = models.IntegerField(default=0,verbose_name="招聘人数")
    remarks = models.TextField(default="",verbose_name="备注")
    class Meta:
        verbose_name_plural = "国编"
        ordering = ['id']

# 特岗
class Special(models.Model):
    post = models.CharField(max_length=30,default="", verbose_name="岗位名称")
    code = models.CharField(max_length=20,default="",verbose_name="岗位代码")
    number = models.IntegerField(default=0, verbose_name="招聘人数")
    class Meta:
        verbose_name_plural = "特岗"
        ordering = ['id']

# 学生表
class Student(models.Model):
    name = models.CharField(max_length=5,default="无",verbose_name="姓名")
    phone = models.CharField(max_length=11,default="无",verbose_name="电话")
    edit = models.DateTimeField(auto_now=True,verbose_name="修改日期")
    teacher = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="操作老师",default=1)
    national_id = models.ForeignKey(National,on_delete=models.CASCADE,default=1,verbose_name="国编id")
    special_id = models.ForeignKey(Special,on_delete=models.CASCADE,default=1,verbose_name="特岗id")
    remarks = models.TextField(default="无",verbose_name="备注")
    score_1 = models.FloatField(default=0.0)
    score_2 = models.FloatField(default=0.0)
    score_3 = models.FloatField(default=0.0)
    score_4 = models.FloatField(default=0.0)
    score_5 = models.FloatField(default=0.0)
    class Meta:
        verbose_name_plural = "学生表"
        ordering = ['id']