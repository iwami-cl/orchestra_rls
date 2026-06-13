import uuid

from django.db import models

# Create your models here.
"""
通知テーブル
"""
# class Notification(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     tenant = models.ForeignKey("user.Tenant", on_delete=models.CASCADE, related_name="notifications")
#     title = models.CharField(max_length=255)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey("user.TenantUser", on_delete=models.CASCADE, related_name="notifications")

#     def __str__(self):
#         return f"{self.tenant.name} - {self.title}"