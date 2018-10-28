from django.db import models


class SeoData(models.Model):
    """
    Модель для корректировки title, description, keywords
    """
    title = models.CharField('title', max_length=255, blank=True)
    description = models.TextField('description', blank=True)
    keywords = models.CharField('keywords', max_length=255,  blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'SEO'
        verbose_name_plural = 'SEO'
