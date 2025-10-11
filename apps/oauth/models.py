from django.db import models
from Base.Model import BaseModel
from utils.encrypt import AESHelper


class RoleModel(BaseModel):
    """角色表"""
    id = models.AutoField(primary_key=True, verbose_name="角色ID")
    name = models.CharField(max_length=32, verbose_name="角色名称", null=False, blank=False, unique=True)
    code = models.CharField(max_length=32, verbose_name="角色编码", null=False, blank=False, unique=True)
    status = models.BooleanField(default=True, verbose_name="状态")
    description = models.TextField(verbose_name="描述")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", null=False)

    class Meta:
        db_table = "role"


class UserModel(BaseModel):
    """用户表"""
    id = models.AutoField(primary_key=True, verbose_name="用户ID")
    account = models.CharField(max_length=32, verbose_name="账号", unique=True, null=False)
    username = models.CharField(max_length=32, verbose_name="用户名", unique=True, null=False)
    password = models.CharField(max_length=255, verbose_name="密码")
    nickname = models.CharField(max_length=50, verbose_name="昵称")
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', verbose_name="头像", null=True,
                               default='avatars/0001/01/01/default.png')
    phone = models.CharField(max_length=11, verbose_name="手机号", null=False)
    email = models.EmailField(max_length=32, verbose_name="邮箱", null=False)
    description = models.TextField(verbose_name="个人简介", null=False)
    signature = models.TextField(verbose_name="个性签名", null=False)
    status = models.BooleanField(default=True, verbose_name="状态")
    last_login_time = models.DateTimeField(auto_now=True, verbose_name="上次登录时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", null=False)

    class Meta:
        db_table = "user"

    def check_password(self, password):
        """检查密码是否正确"""
        aes_helper = AESHelper()
        # print("查询到的密码：",self.password)
        return password == aes_helper.aes_decrypt(self.password)


class UserRoleModel(BaseModel):
    """用户角色表"""
    id = models.AutoField(primary_key=True, verbose_name="ID")
    user = models.ForeignKey(to=UserModel, on_delete=models.CASCADE, null=False, verbose_name="用户ID")  # 外键，关联用户表
    role = models.ForeignKey(to=RoleModel, on_delete=models.CASCADE, null=False, verbose_name="角色ID")  # 外键，关联角色表

    class Meta:
        db_table = "user_roles"


class PermissionModel(BaseModel):
    """权限表"""
    id = models.AutoField(primary_key=True, verbose_name="权限ID")
    code = models.CharField(max_length=100, unique=True, null=False, verbose_name="权限编码")  # 权限编码
    name = models.CharField(max_length=100, null=False, verbose_name="权限名称")  # 权限名称
    description = models.TextField(verbose_name="权限描述")  # 权限描述
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", null=False)

    class Meta:
        db_table = "permissions"


class RolePermissionModel(BaseModel):
    """角色-权限表"""
    id = models.AutoField(primary_key=True, verbose_name="角色-权限ID")
    role = models.ForeignKey(RoleModel, on_delete=models.CASCADE, verbose_name="角色ID")
    permission = models.ForeignKey(PermissionModel, on_delete=models.CASCADE, verbose_name="权限ID")

    class Meta:
        db_table = "role_permissions"


class MenuModel(BaseModel):
    """菜单表"""
    MENU_TYPE_CHOICES = (
        (0, '目录'),
        (1, '菜单'),
        (2, '按钮')
    )
    id = models.AutoField(primary_key=True, verbose_name="菜单ID")
    name = models.CharField(max_length=32, verbose_name="菜单名称")
    code = models.CharField(max_length=64, unique=True, verbose_name="权限标识")
    path = models.CharField(max_length=128, null=True, blank=True, verbose_name="路由路径")
    component = models.CharField(max_length=128, null=True, blank=True, verbose_name="组件路径")
    title = models.CharField(max_length=64, null=True, blank=True, verbose_name='标题')
    icon = models.CharField(max_length=64, null=True, blank=True, verbose_name="图标")
    order = models.IntegerField(default=0, verbose_name="排序权重")
    type = models.IntegerField(choices=MENU_TYPE_CHOICES, default=0, verbose_name="类型")
    visible = models.BooleanField(default=True, verbose_name="是否可见")
    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',  # 反向查询，后续序列化中通过这个字段动态生成children数组
        verbose_name="父菜单"
    )

    class Meta:
        db_table = "system_menu"
        ordering = ['order']

    # class MPTTMeta:
    #     order_insertion_by = ['order']  # 插入时自动排序

    def __str__(self):
        return f"{self.name}({self.get_type_display()})"


class RoleMenuModel(BaseModel):
    """角色-菜单表"""
    id = models.AutoField(primary_key=True, verbose_name="角色-菜单ID")
    role = models.ForeignKey(RoleModel, on_delete=models.CASCADE, verbose_name="角色ID")
    menu = models.ForeignKey(MenuModel, on_delete=models.CASCADE, verbose_name="菜单ID")

    class Meta:
        db_table = "role_menu"
