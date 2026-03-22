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

### Solução para Implementação
```
[] Lambda serverless processando eventos via DynamoDB Streams
[] Circuit breaker + retry para falhas da API externa
[] Logs estruturados em CloudWatch (ECS format)
[] Infrastructure as Code (Terraform) para 3 ambientes
[] Testes automáticos (27 testes, >80% coverage)
[] CI/CD com GitHub Actions
```


## 📞 Suporte

- **Issues**: Abra uma issue no GitHub
- **PRs**: Siga o workflow de branching (develop → feature → PR para hom → PR para prod)

