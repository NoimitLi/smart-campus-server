from django.db import models
from Base.Model import BaseModel
from authSystem.models import UserModel
from django.core.exceptions import ValidationError


class DepartmentModel(BaseModel):
    """部门模型（使用MPTT优化树形结构）"""

    class Meta:
        db_table = 'department'
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
        ordering = ['order', 'id']
        # constraints = []  # 添加约束

    id = models.AutoField(primary_key=True, verbose_name='部门ID')
    name = models.CharField(verbose_name='部门名称', max_length=50, null=False)
    code = models.CharField(verbose_name='部门编码', max_length=20, null=False, unique=True,
                            error_messages={'unique': '部门编码必须唯一'})
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级部门',
    )
    order = models.IntegerField('排序', default=0)
    leader = models.CharField('负责人', max_length=20, blank=True, null=True)
    phone = models.CharField('联系电话', max_length=20, blank=True, null=True)
    email = models.EmailField('邮箱', blank=True, null=True)
    status = models.BooleanField('状态', default=True)
    description = models.TextField('描述', blank=True, null=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    # def clean(self):
    #     """自定义验证逻辑"""
    #     super().clean()
    #
    #     # 检查同级部门名称唯一性
    #     qs = DepartmentModel.objects.filter(parent=self.parent, name=self.name)
    #     if self.pk:  # 如果是更新操作，排除自己
    #         qs = qs.exclude(pk=self.pk)
    #
    #     if qs.exists():
    #         raise ValidationError(
    #             {'name': f'在 {self.parent.name if self.parent else "顶级"} 层级下已存在名为 {self.name} 的部门'}
    #         )
    #
    #     # 其他验证
    #     if self.parent and self.parent.id == self.id:
    #         raise ValidationError({'parent': '不能将部门设置为自己的上级'})
    #
    # def save(self, *args, **kwargs):
    #     """重写save方法确保验证执行"""
    #     self.full_clean()  # 这会调用clean()和字段验证
    #     super().save(*args, **kwargs)

    def get_ancestors(self):
        """获取所有祖先部门"""
        ancestors = []
        parent = self.parent
        while parent is not None:
            ancestors.append(parent)
            parent = parent.parent
        return ancestors[::-1]

    def get_descendants(self, include_self=False):
        """获取所有后代部门"""
        descendants = []
        if include_self:
            descendants.append(self)
        children = DepartmentModel.objects.filter(parent=self)
        for child in children:
            descendants.extend(child.get_descendants(include_self=True))
        return descendants

    def get_full_path(self):
        """获取部门完整路径"""
        ancestors = self.get_ancestors()
        path_parts = [dept.name for dept in ancestors] + [self.name]
        return " / ".join(path_parts)


class UserDepartment(BaseModel):
    """用户-部门关联模型"""

    class Meta:
        db_table = 'user_department'
        unique_together = [('user', 'department')]

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='department_relations',
        verbose_name='用户'
    )
    department = models.ForeignKey(
        DepartmentModel,
        on_delete=models.CASCADE,
        related_name='user_relations',
        verbose_name='部门'
    )
    is_primary = models.BooleanField('主部门', default=False)
    position = models.CharField('职位', max_length=50, blank=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return f"{self.user.username} -> {self.department.name}"

    def save(self, *args, **kwargs):
        """保存时自动设置主部门"""
        if self.is_primary:
            # 取消该用户的其他主部门设置
            UserDepartment.objects.filter(
                user=self.user,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)
