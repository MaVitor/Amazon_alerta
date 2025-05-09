### Amazon Alerta - Sistema de Monitoramento de Preços

Este é um guia detalhado para configurar e executar o sistema Amazon Alerta, um aplicativo Django para monitorar preços de produtos na Amazon e enviar notificações via WhatsApp quando os preços atingirem o valor desejado.

## Índice

1. [Visão Geral](#visão-geral)
2. [Tecnologias Utilizadas](#tecnologias-utilizadas)
3. [Requisitos do Sistema](#requisitos-do-sistema)
4. [Configuração do Ambiente](#configuração-do-ambiente)
5. [Criação de Conta no ScraperAPI](#criação-de-conta-no-scraperapi)
6. [Configuração do Banco de Dados PostgreSQL](#configuração-do-banco-de-dados-postgresql)
7. [Instalação das Dependências](#instalação-das-dependências)
8. [Configuração do Arquivo .env](#configuração-do-arquivo-env)
9. [Migrações do Banco de Dados](#migrações-do-banco-de-dados)
10. [Criação de Superusuário](#criação-de-superusuário)
11. [Execução do Servidor](#execução-do-servidor)
12. [Uso do Sistema](#uso-do-sistema)
13. [Configuração do WhatsApp para Notificações](#configuração-do-whatsapp-para-notificações)
14. [Configuração de Tarefas Agendadas](#configuração-de-tarefas-agendadas)
15. [Solução de Problemas Comuns](#solução-de-problemas-comuns)
16. [Créditos](#créditos)


## Visão Geral

O Amazon Alerta é um sistema que permite monitorar preços de produtos na Amazon e receber notificações via WhatsApp quando os preços caírem abaixo do valor desejado. O sistema utiliza o ScraperAPI para extrair os preços dos produtos e o PyWhatKit para enviar notificações via WhatsApp.

## Tecnologias Utilizadas

Este projeto foi desenvolvido utilizando as seguintes tecnologias:

### Backend

- **Django 4.2.7**: Framework web Python de alto nível que incentiva o desenvolvimento rápido e design limpo
- **PostgreSQL 12+**: Sistema de gerenciamento de banco de dados relacional
- **Python 3.8+**: Linguagem de programação de alto nível


### Frontend

- **Bootstrap 5.3**: Framework CSS para desenvolvimento de interfaces responsivas
- **Chart.js**: Biblioteca JavaScript para criação de gráficos interativos
- **HTML5/CSS3**: Linguagens de marcação e estilo para estruturação e apresentação do conteúdo


### APIs e Serviços

- **ScraperAPI**: Serviço para extrair dados de websites sem ser bloqueado
- **PyWhatKit**: Biblioteca Python para automação do WhatsApp


### Ferramentas de Desenvolvimento

- **Git**: Sistema de controle de versão
- **pip**: Gerenciador de pacotes Python
- **venv**: Ferramenta para criar ambientes virtuais Python isolados


## Requisitos do Sistema

- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- Navegador web moderno (Chrome, Firefox, Edge)
- Conexão com a internet
- Conta no ScraperAPI (gratuita para até 5.000 requisições)
- WhatsApp instalado no celular


## Configuração do Ambiente

### 1. Clone o Repositório

```shellscript
git clone https://github.com/seu-usuario/amazon-alerta.git
cd amazon-alerta
```

### 2. Crie um Ambiente Virtual

```shellscript
# No Windows
python -m venv venv
venv\Scripts\activate

# No Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

## Criação de Conta no ScraperAPI

O ScraperAPI é utilizado para extrair os preços dos produtos da Amazon sem ser bloqueado. Siga os passos abaixo para criar uma conta gratuita:

1. Acesse [ScraperAPI](https://www.scraperapi.com/) e clique em "Sign Up Free"
2. Preencha o formulário com seu e-mail e senha
3. Confirme seu e-mail
4. Faça login na sua conta
5. No dashboard, você verá sua API Key. Copie-a para usar posteriormente
6. O plano gratuito oferece 5.000 requisições por mês, o que é suficiente para monitorar vários produtos


## Configuração do Banco de Dados PostgreSQL

O PostgreSQL é um sistema de banco de dados relacional poderoso e de código aberto. Aqui está um guia detalhado para instalá-lo e configurá-lo localmente.

### Instalação do PostgreSQL

#### Windows

1. Baixe o instalador do [site oficial do PostgreSQL](https://www.postgresql.org/download/windows/)
2. Execute o instalador e siga as instruções
3. Durante a instalação, você será solicitado a:

1. Definir uma senha para o usuário `postgres`
2. Selecionar os componentes a serem instalados (mantenha todos selecionados)
3. Escolher o diretório de instalação
4. Escolher a porta (mantenha a padrão 5432)



4. Conclua a instalação


#### Linux (Ubuntu/Debian)

```shellscript
# Atualize os repositórios
sudo apt update

# Instale o PostgreSQL e as ferramentas de linha de comando
sudo apt install postgresql postgresql-contrib

# Verifique se o serviço está em execução
sudo systemctl status postgresql
```

#### macOS

```shellscript
# Usando Homebrew
brew install postgresql

# Inicie o serviço
brew services start postgresql
```

### Configuração do PostgreSQL

#### Acessando o PostgreSQL

```shellscript
# No Linux, mude para o usuário postgres
sudo -u postgres psql

# No Windows, use o pgAdmin ou o SQL Shell (psql)
# No macOS
psql postgres
```

#### Criando um Banco de Dados e Usuário

Uma vez conectado ao PostgreSQL, execute os seguintes comandos SQL:

```sql
-- Crie um usuário para o projeto
-- Substitua 'postgres' e 'sua_senha_aqui' pelos valores desejados
CREATE USER postgres WITH PASSWORD 'sua_senha_aqui';

-- Crie o banco de dados
CREATE DATABASE amazon;

-- Conceda todos os privilégios ao usuário
GRANT ALL PRIVILEGES ON DATABASE amazon TO postgres;

-- Saia do PostgreSQL
\q
```

#### Configuração Alternativa com pgAdmin

Se preferir uma interface gráfica:

1. Instale o [pgAdmin](https://www.pgadmin.org/download/)
2. Abra o pgAdmin e conecte-se ao servidor PostgreSQL
3. Clique com o botão direito em "Databases" e selecione "Create" > "Database"
4. Dê um nome ao banco de dados (ex: "amazon")
5. Clique com o botão direito em "Login/Group Roles" e selecione "Create" > "Login/Group Role"
6. Configure o nome de usuário, senha e privilégios


### Configurando o Django para Usar o PostgreSQL

Após criar o banco de dados, configure o Django para usá-lo editando o arquivo `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'amazon'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'sua_senha_aqui'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

### Verificando a Conexão

Para verificar se o Django pode se conectar ao banco de dados:

```shellscript
python manage.py check
```

Se não houver erros, a conexão está funcionando corretamente.

## Instalação das Dependências

Instale todas as dependências necessárias usando o pip:

```shellscript
# Certifique-se de que o ambiente virtual está ativado
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Atualize o pip para a versão mais recente
pip install --upgrade pip

# Instale as dependências
pip install -r requirements.txt
```

### Detalhes das Dependências Principais

O arquivo `requirements.txt` contém as seguintes dependências principais:

```plaintext
Django==4.2.7
psycopg2-binary==2.9.9
requests==2.31.0
python-dotenv==1.0.0
pywhatkit==5.4
selenium==4.10.0
pillow==9.5.0
webdriver-manager==3.8.6
```

## Configuração do Arquivo .env

### Como Funciona o .env

O arquivo `.env` é utilizado para armazenar variáveis de ambiente que contêm informações sensíveis ou configurações específicas do ambiente. O Django usa a biblioteca `python-dotenv` para carregar essas variáveis automaticamente.

### Criando e Configurando o .env

1. Crie um arquivo chamado `.env` na raiz do projeto:


```shellscript
touch .env  # No Linux/Mac
# Ou crie manualmente no Windows
```

2. Adicione suas variáveis de ambiente no formato `CHAVE=VALOR`:


```plaintext
# API Keys
SCRAPER_API_KEY=sua_chave_api_aqui

# Database
DB_NAME=amazon
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=True
```

3. No arquivo `settings.py`, as variáveis são carregadas assim:


```python
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Usa as variáveis
SCRAPER_API_KEY = os.getenv('SCRAPER_API_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

### Importante:

- **Nunca** cometa o arquivo `.env` no controle de versão (Git)
- Crie um arquivo `.env.example` com a estrutura, mas sem os valores reais, para documentação
- Cada ambiente (desenvolvimento, teste, produção) deve ter seu próprio arquivo `.env`


## Migrações do Banco de Dados

Execute as migrações para criar as tabelas no banco de dados:

```shellscript
python manage.py makemigrations
python manage.py migrate
```

## Criação de Superusuário

Crie um superusuário para acessar o painel administrativo:

```shellscript
python manage.py createsuperuser
```

Siga as instruções para criar um nome de usuário, e-mail e senha.

## Execução do Servidor

Inicie o servidor de desenvolvimento:

```shellscript
python manage.py runserver
```

O servidor estará disponível em `http://127.0.0.1:8000/`.

## Uso do Sistema

### 1. Acesse o Sistema

Abra seu navegador e acesse `http://127.0.0.1:8000/`.

### 2. Cadastre Contatos

1. Clique em "Contatos" no menu superior
2. Clique em "Novo Contato"
3. Preencha o formulário com o nome e número de telefone (formato internacional, ex: +5511999999999)
4. Marque a opção "Ativo" para que o contato receba notificações
5. Clique em "Salvar"


### 3. Cadastre Produtos

1. Clique em "Produtos" no menu superior
2. Clique em "Novo Produto"
3. Preencha o formulário:

1. **Nome**: Um nome descritivo para o produto
2. **URL**: A URL completa do produto na Amazon (ex: [https://www.amazon.com.br/dp/B0BZ418DCW](https://www.amazon.com.br/dp/B0BZ418DCW))
3. **Preço Alvo**: O preço máximo que você está disposto a pagar
4. **Ativo**: Marque esta opção para que o produto seja monitorado



4. Clique em "Salvar"


### 4. Verificar Preços

1. Na página de produtos, clique no botão de atualização ao lado do produto para verificar o preço atual
2. Ou clique em "Verificar Todos os Preços" para atualizar todos os produtos de uma vez


### 5. Visualizar Histórico

1. Clique em "Histórico" no menu superior para ver o histórico de preços de todos os produtos
2. Use o filtro para selecionar um produto específico e ver seu histórico de preços em um gráfico


### 6. Visualizar Alertas

Clique em "Alertas" no menu superior para ver todos os alertas enviados.

## Configuração do WhatsApp para Notificações

O sistema utiliza o PyWhatKit para enviar notificações via WhatsApp. Na primeira vez que uma notificação for enviada, você precisará autenticar o WhatsApp:

1. Clique em "Verificar Preços" ou envie uma notificação de teste
2. Uma janela do navegador será aberta com o WhatsApp Web
3. Escaneie o QR code com seu celular:

1. Abra o WhatsApp no seu celular
2. Toque em Menu (três pontos) ou Configurações
3. Selecione "Dispositivos conectados"
4. Toque em "Conectar um dispositivo"
5. Aponte a câmera do seu celular para o QR code exibido na tela do computador



4. Após escanear o QR code, o WhatsApp Web estará conectado e as notificações poderão ser enviadas


**Nota**: Você só precisa escanear o QR code uma vez. O WhatsApp Web manterá a sessão ativa por um período, geralmente de algumas semanas, a menos que você desconecte manualmente.

## Configuração de Tarefas Agendadas

Para verificar os preços automaticamente, você pode configurar uma tarefa agendada (cron job):

### No Linux/Mac

```shellscript
# Abra o editor de cron
crontab -e

# Adicione a linha abaixo para verificar os preços a cada 6 horas
0 */6 * * * cd /caminho/para/seu/projeto && /caminho/para/seu/venv/bin/python manage.py check_prices
```

### No Windows

Use o Agendador de Tarefas do Windows:

1. Abra o Agendador de Tarefas
2. Clique em "Criar Tarefa Básica"
3. Dê um nome como "Verificar Preços Amazon"
4. Escolha a frequência (diariamente, por exemplo)
5. Configure o horário
6. Escolha "Iniciar um programa"
7. Navegue até o Python do seu ambiente virtual e adicione os argumentos:

1. Programa: `C:\caminho\para\venv\Scripts\python.exe`
2. Argumentos: `manage.py check_prices`
3. Iniciar em: `C:\caminho\para\seu\projeto`





## Solução de Problemas Comuns

### 1. Erro ao conectar ao banco de dados

Verifique se:

- O PostgreSQL está em execução
- As credenciais no arquivo `settings.py` estão corretas
- O banco de dados foi criado corretamente


### 2. Erro ao extrair preços

Verifique se:

- Sua chave API do ScraperAPI está correta no arquivo `.env`
- Você não excedeu o limite de requisições (5.000 por mês no plano gratuito)
- A URL do produto está correta e acessível


### 3. Erro ao enviar notificações via WhatsApp

Verifique se:

- Você escaneou o QR code corretamente
- O número de telefone está no formato internacional correto (+5511999999999)
- O WhatsApp está instalado no seu celular
- Sua conexão com a internet está funcionando


### 4. O gráfico de preços não aparece

Verifique se:

- Há histórico de preços para o produto
- O JavaScript está habilitado no seu navegador
- Não há erros no console do navegador (F12 > Console)


### 5. Erro "ModuleNotFoundError"

Se você encontrar um erro como "ModuleNotFoundError", verifique se:

- Todas as dependências foram instaladas corretamente
- O ambiente virtual está ativado
- Você está executando o comando no diretório correto


### Solução de Problemas Comuns com PostgreSQL

1. **Erro de conexão recusada**:

1. Verifique se o serviço PostgreSQL está em execução
2. Verifique se a porta 5432 está aberta
3. Verifique as configurações de host em `pg_hba.conf`



2. **Erro de autenticação**:

1. Verifique se o usuário e senha estão corretos
2. Verifique se o usuário tem permissão para acessar o banco de dados



3. **Banco de dados não existe**:

1. Verifique se o banco de dados foi criado corretamente
2. Verifique se o nome do banco de dados está correto em `settings.py`



4. **Erro ao instalar psycopg2**:

1. No Windows, instale o Visual C++ Build Tools
2. No Linux, instale os pacotes de desenvolvimento do PostgreSQL:

```shellscript
sudo apt install libpq-dev python3-dev
```


3. No macOS:

```shellscript
brew install postgresql
```







## Créditos

Este projeto foi desenvolvido por **Mateus Vitor** com o auxílio da inteligência artificial **v0** da Vercel.

O sistema Amazon Alerta foi criado para demonstrar a integração de várias tecnologias modernas de desenvolvimento web e automação, combinando o poder do Django, PostgreSQL, ScraperAPI e automação do WhatsApp para criar uma solução prática de monitoramento de preços.

---

Espero que este guia tenha sido útil para configurar e executar o sistema Amazon Alerta. Se você tiver alguma dúvida ou sugestão, não hesite em entrar em contato.

Boa sorte com o monitoramento de preços!