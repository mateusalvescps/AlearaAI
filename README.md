# Elara AI - Assistente de Recomendação de Restaurantes

Elara AI é um chatbot inteligente projetado para fornecer recomendações personalizadas de restaurantes com base nas preferências e localização do usuário. Este projeto utiliza os modelos de IA Generativa do Google e a API do Google Maps para oferecer uma experiência interativa e fluida para usuários em busca de opções de refeições.

## Funcionalidades

- Processamento de linguagem natural para entender as preferências do usuário
- Análise de imagens para reconhecimento de alimentos
- Busca de restaurantes baseada na localização
- Recomendações personalizadas de restaurantes
- Integração com o Google Maps para fácil navegação

## Componentes

### Classe GeminiHandler

O núcleo da aplicação é a classe `GeminiHandler`, que gerencia as seguintes funcionalidades:

1. **Inicialização do Modelo de IA**: Configura os modelos de IA Gemini para processamento de texto e imagem.
2. **Análise de Entrada do Usuário**: Processa as mensagens do usuário e extrai informações relevantes.
3. **Análise de Imagem**: Reconhece itens alimentares em imagens carregadas.
4. **Gerenciamento de Preferências**: Rastreia e atualiza as preferências do usuário quanto à culinária, localização, distância e faixa de preço.
5. **Busca de Restaurantes**: Utiliza a API do Google Maps para encontrar restaurantes que correspondam aos critérios do usuário.
6. **Geração de Recomendações**: Cria recomendações personalizadas de restaurantes com base nos resultados da busca.

### Métodos Principais

- `analyze_input()`: Processa a entrada do usuário e gera respostas.
- `extract_information()`: Analisa os dados JSON gerados pela IA para as preferências do usuário.
- `update_user_preferences()`: Mantém os dados de preferência do usuário.
- `get_user_coordinates()`: Geocodifica a localização do usuário para buscas precisas.
- `buscar_restaurantes()`: Realiza a busca de restaurantes usando a API do Google Maps.
- `get_restaurant_recommendations()`: Gera recomendações formatadas de restaurantes.

## Configuração e Instalação

Para usar esta aplicação, você precisará:

1. Configurar as credenciais do Google Cloud para acesso à IA Generativa e à API do Maps.
2. Configurar as chaves de API necessárias na classe `GeminiHandler`.
3. Garantir que todas as bibliotecas Python necessárias estejam instaladas (google.generativeai, PIL, googlemaps, etc.).

## Uso

Integre a classe `GeminiHandler` em sua aplicação de chat. Use o método `analyze_input()` para processar as mensagens do usuário e receber respostas geradas pela IA.

## Observação

Este README fornece uma visão geral do sistema de recomendação de restaurantes Elara AI. Para instruções detalhadas de implementação e integração, consulte o código-fonte e os comentários dentro da classe `GeminiHandler`.
