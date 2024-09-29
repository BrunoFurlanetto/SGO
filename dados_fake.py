import os
import django

# Defina a variável de ambiente DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetoCEU.settings')

# Inicialize o Django
django.setup()

# Importe os modelos e a biblioteca Faker
from django.contrib.auth.models import User
from peraltas.models import Monitor, NivelMonitoria
from faker import Faker
import random

# Instancie o Faker
fake = Faker('pt_BR')
# Defina quantos monitores você quer criar
NUM_MONITORES = 15

for _ in range(NUM_MONITORES):
    # Crie um usuário fake
    username = fake.user_name()
    password = 'senha_segura'
    email = fake.email()
    first_name = fake.first_name()
    last_name = fake.last_name()
    nivel_monitoria = NivelMonitoria.objects.get(id=random.randint(17, 36))

    try:
        user = User.objects.create(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
    except Exception as e:
        print(e)
    else:
        # Crie um monitor fake associado ao usuário
        monitor = Monitor.objects.create(
            usuario=user,
            telefone=fake.msisdn()[0:11],
            cidade_horigem=fake.city(),
            valor_diaria=random.uniform(100, 200),
            valor_diaria_coordenacao=random.uniform(150, 250),
            valor_diaria_biologo=random.uniform(130, 220),
            nivel=nivel_monitoria,
            aceite_do_termo=fake.boolean(),
            biologo=fake.boolean(),
            tecnica=fake.boolean(),
            fixo=fake.boolean(),
            nota=round(random.uniform(0, 5), 2),
            n_avaliacoes=random.randint(1, 100)
        )

        print(f"Monitor {monitor.usuario.username} criado com sucesso!")

input()
