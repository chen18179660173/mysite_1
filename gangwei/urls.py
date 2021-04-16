from django.urls import path
from . import  views

urlpatterns = [
    path('',views.index,name='index'),
    path('Login/',views.login,name='login'),
    path("Logout/",views.logout,name='loginOut'),
    path('Query/',views.query,name='query'),
    path('NationalQuery/',views.NationalQuery,name='NationalQuery'),  # 国编列表
    path('NationalQuery/NationalResp/',views.NationalResp,name='NationalResp'), # 搜索
    path('NationalQuery/<int:National_pk>/',views.National_detail,name='National_detail'), # 详情页
    # 国编
    path('NationalQuery/edit/<int:Student_pk>/',views.National_edit,name='National_edit'),  # 修改
    path('NationalQuery/doEdit/<int:Student_pk>/',views.National_doedit,name='National_doedit'),# 执行修改
    path('NationalQuery/add/<int:National_pk>/',views.National_add,name='National_add'),    # 添加
    path('NationalQuery/doAdd/<int:National_pk>/',views.National_doadd,name='National_doadd'),  # 执行添加
    path('NationalQuery/delete/<int:Student_pk>/',views.National_delete,name='National_delete'),# delete
    # 特岗
    path('SpecialQuery/',views.SpecialQuery,name='SpecialQuery'), # 特岗列表
    path('SpecialQuery/SpecialResp/',views.SpecialResp,name='SpecialResp'), # 搜索
    path('SpecialQuery/<int:Special_pk>/', views.Special_detail, name='Special_detail'),  # 详情页
    path('SpecialQuery/edit/<int:Student_pk>/',views.Special_edit,name='Special_edit'), # 修改
    path('SpecialQuery/doEdit/<int:Student_pk>/',views.Special_doedit,name='Special_doedit'),# 执行修改
    path('SpecialQuery/add/<int:Special_pk>/', views.Special_add, name='Special_add'),  # 添加
    path('SpecialQuery/doAdd/<int:Special_pk>/', views.Special_doadd, name='Special_doadd'),  # 执行添加
    path('SpecialQuery/delete/<int:Student_pk>/',views.Special_delete,name='Special_delete'),# delete
    # 学生表
    path('Student/',views.StudentList,name='StudentList'),
    path('Student/StudentResp/', views.StudentResp, name='StudentResp'),  # 搜索
    path('Student/<int:Student_pk>/', views.Student_detail, name='Student_detail'),  # 详情页

    # 岗位填报
    path('Nationaltb/',views.Nationaltb,name='Nationaltb'),
    path('Nationaltb/NationaltbResp/',views.NationaltbResp,name='NationaltbResp'), # 搜索
    path('Nationaltb/<int:National_pk>/',views.Nationaltb_detail,name='Nationaltb_detail'), # 详情页
    path('Nationaltb_doadd/<int:National_pk>/',views.Nationaltb_doadd,name='Nationaltb_doadd'), # 详情页

    path('Specialtb/',views.Specialtb,name='Specialtb'),
    path('Specialtb/SpecialtbResp/',views.SpecialtbResp,name='SpecialtbResp'),
    path('Specialtb/<int:Special_pk>/', views.Specialtb_detail, name='Specialtb_detail'),  # 详情页
    path('Specialtb_doadd/<int:Special_pk>/',views.Specialtb_doadd,name='Specialtb_doadd'), # 详情页

    # path('Nationalred/',views.Nationalred,name='Nationalred'), # 详情页
]
