# Generated manually for question draft refactor
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def remove_calculus_subject(apps, schema_editor):
    Subject = apps.get_model('exam', 'Subject')
    Question = apps.get_model('exam', 'Question')
    PracticeAttemptItem = apps.get_model('exam', 'PracticeAttemptItem')
    WrongBookEntry = apps.get_model('exam', 'WrongBookEntry')
    try:
        subject = Subject.objects.get(name='高等数学')
    except Subject.DoesNotExist:
        return
    related_questions = Question.objects.filter(subject=subject)
    PracticeAttemptItem.objects.filter(question__in=related_questions).delete()
    WrongBookEntry.objects.filter(question__in=related_questions).delete()
    related_questions.delete()
    subject.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0009_auto_20251206_2249'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_questions', to=settings.AUTH_USER_MODEL, verbose_name='录入教师'),
        ),
        migrations.AddField(
            model_name='question',
            name='media_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='题干图片地址'),
        ),
        migrations.AddField(
            model_name='question',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, verbose_name='扩展信息'),
        ),
        migrations.AddField(
            model_name='question',
            name='source_mode',
            field=models.CharField(choices=[('ocr', 'OCR解析'), ('manual', '手动录入')], default='manual', max_length=16, verbose_name='录入方式'),
        ),
        migrations.AddField(
            model_name='question',
            name='status',
            field=models.CharField(choices=[('draft', '草稿'), ('ready', '可用'), ('archived', '已归档')], default='ready', max_length=16, verbose_name='状态'),
        ),
        migrations.AddField(
            model_name='question',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now, verbose_name='更新时间'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='QuestionDraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(choices=[('objective', '客观题'), ('subjective', '主观题')], max_length=16, verbose_name='题目类型')),
                ('source_mode', models.CharField(choices=[('ocr', 'OCR解析'), ('manual', '手动录入')], default='manual', max_length=16, verbose_name='来源模式')),
                ('status', models.CharField(choices=[('uploaded', '已上传'), ('processing', '解析中'), ('parsed', '解析完成'), ('failed', '解析失败'), ('published', '已发布')], default='uploaded', max_length=16, verbose_name='处理状态')),
                ('media', models.FileField(blank=True, null=True, upload_to='exam/questions/', verbose_name='题干文件')),
                ('media_url', models.CharField(blank=True, max_length=255, verbose_name='题干文件地址')),
                ('parsed_title', models.CharField(blank=True, max_length=255, verbose_name='解析标题')),
                ('parsed_content', models.TextField(blank=True, verbose_name='解析题干')),
                ('parsed_options', models.JSONField(blank=True, default=list, verbose_name='解析选项')),
                ('parsed_answer', models.TextField(blank=True, verbose_name='解析答案')),
                ('parsed_analysis', models.TextField(blank=True, verbose_name='解析说明')),
                ('error_message', models.TextField(blank=True, verbose_name='解析错误信息')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('question', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='draft', to='exam.question', verbose_name='发布后的题目')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='question_drafts', to='exam.subject', verbose_name='科目')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_drafts', to=settings.AUTH_USER_MODEL, verbose_name='上传教师')),
            ],
            options={
                'verbose_name': '题目草稿',
                'verbose_name_plural': '题目草稿',
                'db_table': 'exam_question_draft',
                'ordering': ('-updated_at', '-id'),
            },
        ),
        migrations.RunPython(remove_calculus_subject, migrations.RunPython.noop),
    ]
