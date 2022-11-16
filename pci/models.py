from django.db import models

# Create your models here.
class Data(models.Model):
    orgao = models.CharField(max_length=400, default="")
    uf = models.CharField(max_length=2, default="")
    salario = models.FloatField(default=0)
    endereco = models.CharField(max_length=1000, default="")
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    link = models.CharField(max_length=400, default="")
    cargos = models.CharField(max_length=400, default="")
    nivel = models.CharField(max_length=50, default="")
    inscricoes_ate = models.CharField(max_length=50, default="")
    vagas = models.CharField(max_length=50, default="")

    class Meta:
        verbose_name_plural = "Dados"
    
    def __str__(self):
        return self.orgao
    
