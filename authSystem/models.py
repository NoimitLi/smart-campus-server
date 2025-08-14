from django.db import models


# Create your models here.
class RoleModel(models.Model):
    """角色表"""
    id = models.AutoField(primary_key=True, verbose_name="角色ID")
    name = models.CharField(max_length=32, verbose_name="角色名称", null=False)
    code = models.CharField(max_length=32, verbose_name="角色编码")
    status = models.BooleanField(default=True, verbose_name="状态")
    description = models.TextField(verbose_name="描述")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=False)
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", null=False)

    class Meta:
        db_table = "role"


class UserModel(models.Model):
    """用户表"""
    id = models.AutoField(primary_key=True, verbose_name="用户ID")
    account = models.CharField(max_length=32, verbose_name="账号", unique=True, null=False)
    username = models.CharField(max_length=32, verbose_name="用户名")
    password = models.CharField(max_length=32, verbose_name="密码")
    nickname = models.CharField(max_length=50, verbose_name="昵称")
    avatar = models.ImageField(upload_to='avatars/', verbose_name="头像")
    phone = models.CharField(max_length=11, verbose_name="手机号")
    email = models.EmailField(max_length=32, verbose_name="邮箱")
    description = models.TextField(verbose_name="个人简介")
    signature = models.TextField(verbose_name="个性签名")
    last_login_time = models.DateTimeField(verbose_name="上次登录时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=False)
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", null=False)

    class Meta:
        db_table = "user"


class UserRoleModel(models.Model):
    """用户角色表"""
    id = models.AutoField(primary_key=True, verbose_name="ID")
    user_id = models.ForeignKey(to=UserModel, on_delete=models.CASCADE, null=False, verbose_name="用户ID")  # 外键，关联用户表
    role_id = models.ForeignKey(to=RoleModel, on_delete=models.CASCADE, null=False, verbose_name="角色ID")  # 外键，关联角色表
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=False)

    class Meta:
        db_table = "user_roles"


class PermissionModel(models.Model):
    """权限表"""
    id = models.AutoField(primary_key=True, verbose_name="权限ID")
    code = models.CharField(max_length=100, unique=True, null=False, verbose_name="权限编码")  # 权限编码
    name = models.CharField(max_length=100, null=False, verbose_name="权限名称")  # 权限名称
    description = models.TextField(verbose_name="权限描述")  # 权限描述
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=False)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间", null=False)

    class Meta:
        db_table = "permissions"


class RolePermissionModel(models.Model):
    """角色-权限表"""
    id = models.AutoField(primary_key=True, verbose_name="角色-权限ID")
    role_id = models.ForeignKey(RoleModel, on_delete=models.CASCADE, verbose_name="角色ID")
    permission_id = models.ForeignKey(PermissionModel, on_delete=models.CASCADE, verbose_name="权限ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=False)

    class Meta:
        db_table = "role_permissions"
