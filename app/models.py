from django.db import models

class UserPoint(models.Model):
    user_id = models.CharField(max_length=50, unique=True)
    balance = models.IntegerField(default=0)

    class Meta:
        managed = False   # ✅ Django가 migrate로 테이블을 만들지 않는다
        db_table = 'user_point'