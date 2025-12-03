from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0002_seed_calculus_questions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PracticeAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(choices=[('objective', '客观题'), ('subjective', '主观题')], max_length=16, verbose_name='题型')),
                ('duration_seconds', models.PositiveIntegerField(default=1800, verbose_name='限时(秒)')),
                ('total_questions', models.PositiveIntegerField(default=0, verbose_name='题目数量')),
                ('correct_count', models.PositiveIntegerField(default=0, verbose_name='客观题正确数')),
                ('status', models.CharField(choices=[('ongoing', '进行中'), ('completed', '已完成'), ('expired', '已过期')], default='ongoing', max_length=16, verbose_name='状态')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='开始时间')),
                ('submitted_at', models.DateTimeField(blank=True, null=True, verbose_name='提交时间')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.subject', verbose_name='科目')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practice_attempts', to=settings.AUTH_USER_MODEL, verbose_name='学生')),
            ],
            options={
                'verbose_name': '练习记录',
                'verbose_name_plural': '练习记录',
                'db_table': 'exam_practice_attempt',
            },
        ),
        migrations.CreateModel(
            name='PracticeAttemptItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='题目顺序')),
                ('user_answer', models.TextField(blank=True, null=True, verbose_name='学生答案')),
                ('is_correct', models.BooleanField(blank=True, null=True, verbose_name='是否正确')),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='exam.practiceattempt', verbose_name='练习记录')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='exam.question', verbose_name='题目')),
            ],
            options={
                'verbose_name': '练习题目记录',
                'verbose_name_plural': '练习题目记录',
                'db_table': 'exam_practice_attempt_item',
                'ordering': ('order', 'id'),
            },
        ),
    ]
