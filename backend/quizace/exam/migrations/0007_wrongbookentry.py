from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0006_practiceattemptitem_awarded_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='WrongBookEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_user_answer', models.TextField(blank=True, verbose_name='最近答案')),
                ('wrong_times', models.PositiveIntegerField(default=1, verbose_name='累计错误次数')),
                ('last_wrong_at', models.DateTimeField(auto_now=True, verbose_name='最后错误时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('last_attempt', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='wrong_book_entries', to='exam.practiceattempt', verbose_name='最近关联练习')),
                ('last_attempt_item', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='wrong_book_entries', to='exam.practiceattemptitem', verbose_name='最近关联作答')),
                ('question', models.ForeignKey(on_delete=models.CASCADE, to='exam.question', verbose_name='题目')),
                ('subject', models.ForeignKey(on_delete=models.CASCADE, to='exam.subject', verbose_name='科目')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='wrong_book_entries', to=settings.AUTH_USER_MODEL, verbose_name='学生')),
            ],
            options={
                'db_table': 'exam_wrong_book_entry',
                'ordering': ('-last_wrong_at', '-id'),
                'verbose_name': '错题本记录',
                'verbose_name_plural': '错题本记录',
            },
        ),
        migrations.AlterUniqueTogether(
            name='wrongbookentry',
            unique_together={('user', 'question')},
        ),
    ]

