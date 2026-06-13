from django.db import models

# Create your models here.
# 商品マスタ
class Product(models.Model):
    # 商品名
    name = models.CharField(max_length=100)
    # 商品概要
    description = models.CharField(max_length=255, blank=True, null=True)
    # 商品ID（★stripeの商品IDを値に用いる）
    stripe_product_id = models.CharField(max_length=100)
    # 商品写真登録用のファイル
    file = models.FileField(upload_to="product_files/", blank=True, null=True)
    # 商品詳細ページのリンク
    url  = models.URLField()

    # admin画面で商品名表示
    def __str__(self):
        return self.name

# 価格マスタ
class Price(models.Model):
    # 外部キーで商品マスタを紐付け
    product = models.ForeignKey(Product, related_name='Prices', on_delete=models.CASCADE)
    # 価格ID（★stripeの価格IDを値に用いる）
    stripe_price_id = models.CharField(max_length=100)
    # 価格
    price = models.IntegerField(default=0)
    
    # Django画面に表示する価格
    def get_display_price(self):
        return self.price
