# 🚀 Lambda - Recategorização de Eventos Financeiros

## 🎯 Contexto de Negócio

- Lambda responsável **recategoriza eventos financeiros em tempo real** conforme as
preferências do usuário. Processa transações (💳 Cartão, 🏦 Corrente, 📱 PIX) disparadas
por DynamoDB Streams, integra com API de categorização e persiste resultados com
observabilidade em CloudWatch.

**Tipos suportados**: CREDIT_CARD, CHECKING_ACCOUNT, PIX

---

## ❓ Problema & Solução

### Problema
- Eventos financeiros chegam com a finalidade de categorizados dinamicamente
- Precisão de categorização varia e não considera preferências do usuário
- Sem observabilidade centralizada dos processos
- Múltiplos ambientes precisam de configuração manual

### Solução Implementada
✅ Lambda serverless processando eventos via DynamoDB Streams
✅ Circuit breaker + retry para falhas da API externa
✅ Logs estruturados em CloudWatch (ECS format)
✅ Infrastructure as Code (Terraform) para 3 ambientes
✅ Testes automáticos (27 testes, >80% coverage)
✅ CI/CD com GitHub Actions

---

## 🚀 Setup Local

### 1️⃣ Pré-requisitos
```bash
python --version        # 3.12+
terraform --version     # 1.6+
aws --version           # v2
git --version           # 2.40+
```

### 2️⃣ Clonar & Preparar
```bash
git clone https://github.com/seu-org/lambda-gfrecategorizacao-producer.git
cd lambda-gfrecategorizacao-producer

# Criar virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
# ou: venv\Scripts\activate # Windows
```

### 3️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
# ou: make install
```

### 4️⃣ Configurar .env
```bash
cp .env.example .env

# Editar .env com seus valores:
export ENVIRONMENT=dev
export AWS_REGION=us-east-1
export CATEGORIZER_ENDPOINT=https://api-dev.categorizer.example.com/api/v1/categorize
export CATEGORIZER_TOKEN=seu_token_aqui
export LOG_LEVEL=DEBUG
```

### 5️⃣ Verificar Setup
```bash
# Verificar imports
python -c "import boto3, pytest; print('✅ OK')"

# Verificar AWS credentials
aws sts get-caller-identity
```

---

## 🧪 Executar Testes

### Testes Básicos
```bash
# Rodar todos os testes
pytest tests/ -v

# Com coverage report
pytest tests/ --cov=src --cov-report=html

# Ver resultado
open htmlcov/index.html

# Modo watch (rerun automático)
make test-watch
```

### Testes Específicos
```bash
# Um arquivo
pytest tests/unit/test_models.py -v

# Um teste
pytest tests/unit/test_models.py::test_transaction_validation -v

# Debug mode
pytest tests/unit/test_models.py -v -s --pdb
```

**Meta**: >80% coverage no `src/`

---

## 🏗️ Estrutura do Projeto

```
src/                               # Código Lambda
├── lambda_handler.py             # Entry point
├── models/                       # DATA MODELS
│   ├── transaction.py            # TransactionType enum
│   └── categorization.py         # Categorization com TTL
├── services/                     # BUSINESS LOGIC
│   ├── event_processor.py        # Orquestrador principal
│   ├── categorizer_service.py    # API externa + circuit breaker
│   └── dynamodb_service.py       # DB + retry logic
└── utils/                        # UTILITIES
    ├── logger.py                 # CloudWatch estruturado
    └── exceptions.py             # Exceções customizadas

tests/                            # 27 TESTES (>80% coverage)
├── unit/
│   ├── test_models.py            # 9 testes
│   ├── test_event_processor.py   # 7 testes
│   ├── test_categorizer_service.py # 8 testes
│   └── test_lambda_handler.py    # 3 testes
└── fixtures/
    └── mock_events.py            # 12+ cenários

terraform/                        # INFRASTRUCTURE AS CODE
├── main.tf                       # Lambda + DynamoDB + CloudWatch
├── variables.tf                  # Input variables
├── backend.tf                    # S3 state
└── environments/
    ├── dev.tfvars               # On-demand, 256MB Lambda
    ├── hom.tfvars               # Provisioned, 256MB Lambda
    └── prod.tfvars              # Provisioned+autoscale, 512MB Lambda

.github/workflows/               # CI/CD AUTOMATION
├── ci.yml                       # Lint + test + validate
├── deploy-hom.yml               # Auto-deploy homolog
└── deploy-prod.yml              # Manual approval + prod

Makefile                         # Comandos úteis
requirements.txt                 # 13 dependências Python
.env.example                     # Template variáveis
```

---

## 📊 Arquitetura do Fluxo

```
DynamoDB Stream (eventos INSERT/MODIFY)
        ↓ (batch 100 records)
    Lambda (trigger)
        ↓
Event Processor
        ├→ Validar evento
        ├→ Parse transaction
        ├→ Fetch user preferences
        ├→ Chamar Categorizer API
        ├→ Persistir result (DynamoDB)
        └→ Log (CloudWatch)
        ↓
    Success Payload
        ↓
    DynamoDB Categorizations Table
        (TTL 90 dias)
```

**Padrões de Resiliência**:
- ✅ Retry: 3x com exponential backoff (0.5s, 1s, 2s)
- ✅ Circuit Breaker: Abre após 100 falhas, recupera em 300s
- ✅ Timeout: 5s para API externa
- ✅ Per-record error tolerance: Continua em erro

---

## 🚀 Deploy Local (Dev)

### 1️⃣ Setup Backend S3 (primeira vez)
```bash
cd terraform

# Criar bucket
aws s3api create-bucket \
  --bucket tfstate-gfrecategorizacao-producer \
  --region us-east-1

# Criar tabela DynamoDB para lock
aws dynamodb create-table \
  --table-name tfstate-lock-gfrecategorizacao-producer \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Inicializar Terraform
terraform init
```

### 2️⃣ Deploy em DEV
```bash
cd terraform

terraform validate
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"

# Ver resultado
terraform output
```

### 3️⃣ Deploy em HOM/PROD
```bash
# Homolog
terraform apply -var-file="environments/hom.tfvars"

# Produção
terraform apply -var-file="environments/prod.tfvars"
```

---

## Invocar Lambda com Payload

### 1️⃣ Teste Local (sem deploy)
```bash
# Payload de exemplo
python -c "
import json
from src.main import lambda_handler

event = {
    'Records': [
        {
            'eventID': 'test-event-1',
            'eventVersion': '1.0',
            'dynamodb': {
                'Keys': {'transaction_id': {'S': 'txn_12345'}},
                'NewImage': {
                    'transaction_id': {'S': 'txn_12345'},
                    'user_id': {'S': 'usr_67890'},
                    'type': {'S': 'CREDIT_CARD'},
                    'amount': {'N': '150.50'},
                    'merchant': {'S': 'Supermercado XYZ'},
                    'description': {'S': 'Compra de alimentos'},
                    'timestamp': {'S': '2024-12-11T14:30:00Z'}
                }
            },
            'eventName': 'INSERT',
            'eventSource': 'aws:dynamodb'
        }
    ]
}

result = lambda_handler(event, None)
print(json.dumps(result, indent=2))
"
```

### 2️⃣ Invocar Lambda em AWS (via CLI)
```bash
# Payload em arquivo
cat > payload.json << 'EOF'
{
  \"Records\": [
    {
      \"eventID\": \"test-event-1\",
      \"eventVersion\": \"1.0\",
      \"dynamodb\": {
        \"Keys\": {\"transaction_id\": {\"S\": \"txn_abc123\"}},
        \"NewImage\": {
          \"transaction_id\": {\"S\": \"txn_abc123\"},
          \"user_id\": {\"S\": \"usr_xyz789\"},
          \"type\": {\"S\": \"CREDIT_CARD\"},
          \"amount\": {\"N\": \"250.75\"},
          \"merchant\": {\"S\": \"Amazon\"},
          \"description\": {\"S\": \"Livro Python\"},
          \"timestamp\": {\"S\": \"2024-12-11T15:45:00Z\"}
        }
      },
      \"eventName\": \"INSERT\",
      \"eventSource\": \"aws:dynamodb\"
    }
  ]
}
EOF

# Invocar função
aws lambda invoke \
  --function-name recategorization-producer-dev \
  --payload file://payload.json \
  --region us-east-1 \
  response.json

# Ver resposta
cat response.json | jq .
```

### 3️⃣ Testar com pytest
```bash
# Teste genérico
pytest tests/test_main.py::TestLambdaHandler::test_process_valid_event -v

# Com print da saída
pytest tests/test_main.py -v -s

# Executar um fixture específico
python -c "
import sys
sys.path.insert(0, '.')
from tests.test_main import valid_dynamodb_stream_event
import json
print(json.dumps(valid_dynamodb_stream_event(), indent=2))
"
```

### 4️⃣ Teste de Carga (boto3)
```python
import json
import boto3
from src.main import lambda_handler

# Simular múltiplos eventos
events = [
    {
        'transaction_id': f'txn_{i}',
        'user_id': f'usr_{i % 10}',
        'type': 'CREDIT_CARD' if i % 2 == 0 else 'PIX',
        'amount': float(100 + i),
        'merchant': f'Store {i}',
        'description': f'Purchase {i}',
        'timestamp': '2024-12-11T16:00:00Z'
    }
    for i in range(100)
]

# Preparar payload em formato DynamoDB Stream
dynamodb_records = {
    'Records': [
        {
            'eventID': f'event-{i}',
            'eventVersion': '1.0',
            'dynamodb': {
                'Keys': {'transaction_id': {'S': evt['transaction_id']}},
                'NewImage': {
                    'transaction_id': {'S': evt['transaction_id']},
                    'user_id': {'S': evt['user_id']},
                    'type': {'S': evt['type']},
                    'amount': {'N': str(evt['amount'])},
                    'merchant': {'S': evt['merchant']},
                    'description': {'S': evt['description']},
                    'timestamp': {'S': evt['timestamp']}
                }
            },
            'eventName': 'INSERT',
            'eventSource': 'aws:dynamodb'
        }
        for i, evt in enumerate(events)
    ]
}

# Invocar
result = lambda_handler(dynamodb_records, None)
print(f"Processados: {result.get('processed_count', 0)}")
print(f"Erros: {result.get('error_count', 0)}")
```

### 5️⃣ Invocar via API Gateway (em produção)
```bash
# Após configurar API Gateway pointing to Lambda

curl -X POST https://api.example.com/categorize \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_12345",
    "user_id": "usr_67890",
    "type": "CREDIT_CARD",
    "amount": 150.50,
    "merchant": "Supermercado XYZ",
    "description": "Compra de alimentos",
    "timestamp": "2024-12-11T14:30:00Z"
  }'
```

---

## 🔧 Variáveis de Ambiente

### Local (.env)
```env
AWS_REGION=us-east-1
ENVIRONMENT=dev
DYNAMODB_TRANSACTIONS_TABLE=GestaoFinanceira-Transacoes-dev
DYNAMODB_CATEGORIZATIONS_TABLE=GestaoFinanceira-Categorizacoes-dev
CATEGORIZER_ENDPOINT=https://api-dev.categorizer.example.com/api/v1/categorize
CATEGORIZER_TOKEN=seu_token
LOG_LEVEL=DEBUG
SERVICE_VERSION=1.0.0
```

### GitHub Secrets (Produção)
```
AWS_ROLE_TO_ASSUME
CATEGORIZER_TOKEN_DEV
CATEGORIZER_TOKEN_HOM
CATEGORIZER_TOKEN_PROD
SLACK_WEBHOOK
```

---

## ⚙️ Comandos Úteis

```bash
# Setup
make install              # Instalar dependências
make test                 # Rodar testes
make test-coverage        # Coverage report
make lint                 # Validar código
make format               # Formatar código

# Terraform
make tf-init              # Inicializar
make tf-plan              # Planejar (dev)
make tf-apply             # Aplicar (dev)
make tf-destroy           # Destruir (dev)

# Limpeza
make clean                # Remover temporários
make clean-all            # Remover tudo
```


# 🔄 GitFlow & CI/CD Pipeline

## Branches & Estratégia

```
feature/** ──┐
             ├─→ develop ──┐ (CI Tests)
feature/** ──┘             │
                           ├─→ merge-develop-to-feature-flag (PR automático)
                           │
                           └─→ feature-flag ──┐ (Deploy Homolog)
                                              │
                                              ├─→ pr-develop-to-feature-flag (PR automático)
                                              │
                                              └─→ main ──→ (Deploy Production)
```

## Fluxo Detalhado

### 1️⃣ Feature Development
```bash
git checkout -b feature/sua-feature develop
# Aplicar mudanças...
git push origin feature/sua-feature
```
→ **Triggers**: `ci.yml` (testes, linting, coverage)

### 2️⃣ Merge em Develop (via PR)
```bash
# Abrir PR: feature/sua-feature → develop
# → Todos os testes precisam passar ✅
# → Review & merge em develop
```
→ **Triggers**: `merge-develop-to-feature-flag.yml`
  - Roda CI tests
  - Cria PR automático: develop → feature-flag

### 3️⃣ Homolog (Feature-Flag)
PR automática é criada para feature-flag
```bash
# feature-flag é atualizada automaticamente
# → Deploy automático em homolog
# → Testes smoke rodam
```
→ **Triggers**: `deploy-hom.yml`
  - Terraform plan
  - Deploy em environment `hom`
  - Testes pós-deploy

### 4️⃣ Produção (Main)
Quando feature-flag está estável:
```bash
# Approve & merge PR: feature-flag → main
# → PR automática para main é criada
```

---

## 🐛 Troubleshooting Rápido

**Erro ao importar boto3?**
```bash
deactivate && rm -rf venv
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**Testes falhando?**
```bash
pytest tests/ -v -s --pdb  # Debug mode
```

**AWS credentials inválidas?**
```bash
aws sts get-caller-identity
aws configure
```

**Terraform error?**
```bash
terraform validate
terraform init -reconfigure
```
---

**Versão**: 1.0.0 | **Status**: ✅ PRONTO PARA DEPLOYMENT | **Última atualização**: 2026-03-21

## 🔐 Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `CATEGORIZER_ENDPOINT` | URL do serviço de categorização |
| `DYNAMODB_TABLE` | Tabela DynamoDB |
| `LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR |
| `ENVIRONMENT` | dev, hom, prod |

---

## 📞 Suporte

- **Issues**: Abra uma issue no GitHub
- **PRs**: Siga o workflow de branching (develop → feature → PR para hom → PR para prod)

