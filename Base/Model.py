from django.db import models
from django.db.models import DateTimeField, ManyToManyField


class BaseModel(models.Model):
    """模型基类"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=False)

    class Meta:
        abstract = True  # 抽象基类

    def to_dict(self, fields=None, exclude=None):
        """转为字典"""
        data = {}
        for f in self._meta.concrete_fields + self._meta.many_to_many:
            value = f.value_from_object(self)

            if fields and f.name not in fields:
                continue

            if exclude and f.name in exclude:
                continue

            if isinstance(f, ManyToManyField):
                value = [i.id for i in value] if self.pk else None

            if isinstance(f, DateTimeField):
                value = value.strftime('%Y-%m-%d %H:%M:%S') if value else None

            data[f.name] = value

        return data
