# Generated by Django 4.1.3 on 2022-11-15 08:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('splitwise_friend_id', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('receipt_code', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('receipt_type', models.CharField(blank=True, choices=[('Grabfood', 'Grabfood'), ('Foodpanda', 'Foodpanda')], max_length=30)),
                ('delivery_date', models.CharField(max_length=30)),
                ('receipt_total_fee', models.DecimalField(decimal_places=2, max_digits=6)),
                ('is_assigned', models.BooleanField(default=False)),
                ('assignment', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Receipt_items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('total_item_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='EmployeeApp.item')),
                ('receipt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='EmployeeApp.receipt')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ReceiptItem_Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='EmployeeApp.friend')),
                ('receipt_items', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='EmployeeApp.receipt_items')),
            ],
        ),
        migrations.AddField(
            model_name='receipt',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='EmployeeApp.vendor'),
        ),
    ]
