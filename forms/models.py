from django.db import models

# class FormsGroup(models.Model):
#
#     title = models.CharField(max_length=255, unique=True, help_text='Группа для форм')
#     title_gui = models.CharField(max_length=25, default="", blank=True, help_text='GUI-название группы формы')
#     is_active = models.BooleanField(default=False,help_text="Скрыть группу форм")
#     comment = models.TextField(max_length=255, default="", blank=True, help_text='Описание')
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         verbose_name = 'Группа форм'
#         verbose_name_plural = 'Группа форм'

class FormsList(models.Model):
    # form_group = models.ForeignKey(FormsGroup, null=True, db_index=True, help_text='Наименование группы для форм', on_delete=models.CASCADE)
    # title = models.IntegerField(unique=True, help_text='Название формы')
    title = models.DecimalField(max_digits=5, decimal_places=2,unique=True,
                  help_text='Номер формы (3 знака целого числа-это группа, остальные- номер формы В ГРУППЕ)',db_index=True)
    # title_gui = models.CharField(max_length=25, default="", blank=True, help_text='GUI-название формы')
    # type_number = models.PositiveIntegerField(unique=True, blank=False, help_text='Номер типа формы')
    is_active = models.BooleanField(default=True, help_text="Активность формы",db_index=True)
    comment = models.CharField(max_length=255, default="", blank=True, help_text='Описание')

    def __int__(self):
        return self.title

    class Meta:
        verbose_name = 'Cписки форм'
        verbose_name_plural = 'Списки форм'

# class FormsTemplate(models.Model):
#     form_name = models.ForeignKey(FormsList, help_text='Наименование формы',on_delete='Cascade')
#     section_name = models.CharField(max_length=255,default="", blank=True, help_text='Название раздела/реквизита для формы')
#     is_print_section = models.BooleanField(default=False)
#     template_text = models.TextField(help_text='Текст для формы', blank=True, default='')
#
#     def __str__(self):
#         return "{}".format(self.form_name)
#
#
#     class Meta:
#         verbose_name = 'Cписки текстов для форм'
#         verbose_name_plural = 'Списки текстов для форм'
