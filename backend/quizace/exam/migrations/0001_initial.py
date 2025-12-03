from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='科目名称')),
                ('description', models.TextField(blank=True, verbose_name='简介')),
            ],
            options={
                'verbose_name': '科目',
                'verbose_name_plural': '科目',
                'db_table': 'exam_subject',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(choices=[('objective', '客观题'), ('subjective', '主观题')], default='objective', max_length=16, verbose_name='题目类型')),
                ('content', models.TextField(verbose_name='题干')),
                ('options', models.TextField(blank=True, null=True, verbose_name='客观题选项(JSON文本)')),
                ('answer', models.TextField(verbose_name='参考答案')),
                ('analysis', models.TextField(blank=True, null=True, verbose_name='解析')),
                ('score', models.PositiveIntegerField(default=5, verbose_name='分值')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='exam.subject', verbose_name='所属科目')),
            ],
            options={
                'verbose_name': '题目',
                'verbose_name_plural': '题目',
                'db_table': 'exam_question',
            },
        ),
    ]
