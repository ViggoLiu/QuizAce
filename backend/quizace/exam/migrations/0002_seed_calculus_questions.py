import json

from django.db import migrations


OBJECTIVE_DATA = [
    {
        "content": "函数 f(x)=sin x 的导数是?",
        "options": {
            "A": "cos x",
            "B": "-cos x",
            "C": "sin x",
            "D": "-sin x"
        },
        "answer": "A",
        "analysis": "sin x 的导数为 cos x",
    },
    {
        "content": "若 f(x)=x^2, 则 f'(1)=?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "2",
            "D": "3"
        },
        "answer": "C",
        "analysis": "f'(x)=2x, 代入 x=1 得 2",
    },
    {
        "content": "∫_0^1 x dx 等于?",
        "options": {
            "A": "1/2",
            "B": "1",
            "C": "0",
            "D": "2"
        },
        "answer": "A",
        "analysis": "原函数为 x^2/2, 上下限相减得 1/2",
    },
    {
        "content": "极限 lim_{x→0} sin x / x 的值为?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "不存在",
            "D": "∞"
        },
        "answer": "B",
        "analysis": "常见极限, 值为 1",
    },
    {
        "content": "若 f''(x) > 0, 则 f(x) 的图像?",
        "options": {
            "A": "开口向上",
            "B": "开口向下",
            "C": "水平",
            "D": "无法判断"
        },
        "answer": "A",
        "analysis": "二阶导数大于0表示函数凸, 图像开口向上",
    },
    {
        "content": "曲线 y = x^3 在 x = 0 处的切线斜率?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "3",
            "D": "不存在"
        },
        "answer": "A",
        "analysis": "导数为 3x^2, 代入 0 得 0",
    },
    {
        "content": "若 y = ln x, 则 dy/dx = ?",
        "options": {
            "A": "1/x",
            "B": "x",
            "C": "ln x",
            "D": "e^x"
        },
        "answer": "A",
        "analysis": "对数函数导数为 1/x",
    },
    {
        "content": "若 f(x)=e^x, f(0)=?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "e",
            "D": "2"
        },
        "answer": "B",
        "analysis": "e^0 = 1",
    },
    {
        "content": "下列哪个积分结果为 ln|x| + C?",
        "options": {
            "A": "∫ 1/x dx",
            "B": "∫ x dx",
            "C": "∫ e^x dx",
            "D": "∫ cos x dx"
        },
        "answer": "A",
        "analysis": "1/x 的不定积分为 ln|x| + C",
    },
    {
        "content": "若∫ f'(x) dx = ?",
        "options": {
            "A": "f(x) + C",
            "B": "f'(x) + C",
            "C": "xf(x)",
            "D": "无法确定"
        },
        "answer": "A",
        "analysis": "导数积分回原函数 f(x) + C",
    },
]

SUBJECTIVE_DATA = [
    {
        "content": "求函数 f(x)=x^3-3x 在 x=1 处的导数，并写出该点切线方程。",
        "answer": "f'(x)=3x^2-3, f'(1)=0, 切线方程 y=f(1)= -2",
        "analysis": "导数为 3x^2-3, 在 x=1 处斜率 0, 过点 (1,-2) 的水平线",
    },
    {
        "content": "计算定积分 ∫_0^{\pi} sin x dx。",
        "answer": "2",
        "analysis": "原函数 -cos x, 代入 π 与 0 得 2",
    },
    {
        "content": "判断级数 \sum_{n=1}^{\infty} 1/n^2 是否收敛，并说明理由。",
        "answer": "收敛, p-级数 p=2>1 收敛",
        "analysis": "与积分或 p-series 判别, p>1 收敛",
    },
    {
        "content": "求极限 lim_{x→0} (e^x - 1 - x)/x^2。",
        "answer": "1/2",
        "analysis": "泰勒展开 e^x=1+x+x^2/2+..., 代入取 1/2",
    },
    {
        "content": "设曲线 y = x^2, 求在点 (2,4) 处的法线方程。",
        "answer": "切线斜率 4, 法线斜率 -1/4, 方程 y-4 = -(1/4)(x-2)",
        "analysis": "导数 2x, 代入 2 得 4, 法线斜率 -1/4",
    },
]


def seed_questions(apps, schema_editor):
    Subject = apps.get_model('exam', 'Subject')
    Question = apps.get_model('exam', 'Question')

    subject, _ = Subject.objects.get_or_create(
        name='高等数学',
        defaults={'description': '高数模拟练习科目'}
    )

    for data in OBJECTIVE_DATA:
        Question.objects.get_or_create(
            subject=subject,
            question_type='objective',
            content=data['content'],
            defaults={
                'options': json.dumps(data['options']),
                'answer': data['answer'],
                'analysis': data['analysis'],
                'score': 5,
            }
        )

    for data in SUBJECTIVE_DATA:
        Question.objects.get_or_create(
            subject=subject,
            question_type='subjective',
            content=data['content'],
            defaults={
                'answer': data['answer'],
                'analysis': data['analysis'],
                'score': 5,
            }
        )


def remove_questions(apps, schema_editor):
    Subject = apps.get_model('exam', 'Subject')
    Question = apps.get_model('exam', 'Question')

    try:
        subject = Subject.objects.get(name='高等数学')
    except Subject.DoesNotExist:
        return

    Question.objects.filter(subject=subject).delete()
    subject.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_questions, remove_questions),
    ]
