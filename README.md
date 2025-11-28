Sistema de Agendamento

> Aplicação web modular de agendamento online construída em Python (Streamlit), ideal para gerenciar clientes e serviços de barbearias de forma intuitiva e segura. Este projeto demonstra proficiência em arquitetura modular, gestão de estado (session state) e segurança básica de aplicações.

---

## ✨ Funcionalidades e Destaques

Este projeto foi desenvolvido com foco em estabilidade, segurança e experiência do usuário (UX):

* **Arquitetura Modular:** Separação clara de lógica entre a aplicação principal (`app.py`), *views* (`cliente_view.py`, `admin_view.py`) e persistência de dados (`data_manager.py`).
* **Autenticação Admin Segura:** Painel administrativo protegido por credenciais, utilizando o sistema nativo de segredos (`st.secrets`) para gestão segura de acesso.
* **Fluxo de Agendamento em 3 Passos:** Processo guiado e intuitivo para o cliente (1. Serviço → 2. Data/Hora → 3. Confirmação).
* **Design Profissional Customizado:** Uso de CSS *inline* para customização do tema (preto/dourado), proporcionando uma experiência de usuário moderna, além da utilização do ícone da Navalha 💈.
* **Persistência Multi-Tenant (Protótipo):** Implementação básica de isolamento de dados, onde cada barbearia gerencia seu próprio arquivo de dados (CSV) de forma independente.

---

## 🛠️ Tecnologias Utilizadas

O projeto é majoritariamente construído em Python, utilizando o ecossistema de Data Apps:

| Categoria | Tecnologia | Foco |
| :--- | :--- | :--- |
| **Linguagem Principal** | Python | Lógica de negócio, processamento e *backend*. |
| **Framework Web** | Streamlit | Construção rápida e interativa da interface web. |
| **Gestão de Dados** | Pandas | Manipulação e persistência de dados em arquivos CSV. |
| **Bancos de Dados** | PostgreSQL (Próxima Fase) | Planejado para escalabilidade em produção. |
| **Frontend** | HTML, CSS, JavaScript | Customização avançada de tema e interação. |
| **Controle de Versão** | Git | Gerenciamento de histórico e colaboração. |

---


## 🔑 Acesso e Uso

Ao iniciar a aplicação, você terá duas opções na barra lateral:

1.  **Modo Cliente:** Acesse a aplicação e siga o fluxo de agendamento de 3 passos (Seleção de Serviço, Seleção de Data/Hora, Confirmação).
2.  **Modo Administrador:** Selecione "Administrador" e insira as credenciais para acessar o painel de gerenciamento, que exibe métricas e a lista de agendamentos.
