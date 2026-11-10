# Plano de trabalho e contribuições

[Voltar à apresentação](../README.md)

## Responsáveis e passagem de trabalho

Cada integrante assume duas etapas inteiras. O próximo recebe um bloco validado e continua a partir do material entregue.

| Ordem | Responsável | Etapas | O que passa adiante |
| --- | --- | --- | --- |
| 1 | João Victor Moreira Almeida | 1 e 2 | Escopo definido, fotos rotuladas e separadas em calibração e teste, ambiente Python configurado e CLI capaz de abrir uma imagem. |
| 2 | João Vitor Justiniano Barbosa | 3 e 4 | Classificador executável pela CLI, recorte e máscaras disponíveis para inspeção, duas regras de decisão e limiares congelados usando a calibração. |
| 3 | Pedro Crispim Pereira | 5 e 6 | Avaliação reproduzível no conjunto de teste, resultados registrados no README e demonstração pronta para a entrega. |

- [x] **João Victor → João Vitor.** Conferir que os caminhos das fotos são utilizáveis, que os grupos estão identificados e que a CLI abre uma foto de calibração.
- [x] **João Vitor → Pedro.** Demonstrar que as duas regras rodam com os mesmos arquivos, que as máscaras podem ser salvas e que os limiares ficaram registrados antes do teste.
- [x] **Pedro → entrega.** Conferir a execução a partir de um clone limpo e registrar os resultados obtidos e os exemplos usados na demonstração.

## 1. Definir o escopo e preparar as fotos

- [x] Definir as duas classes com exemplos rotulados. Separar céu parcialmente nublado, pouco céu visível e prédios no recorte como casos difíceis.
- [x] Dividir as imagens em calibração e teste antes de ajustar o algoritmo. Manter fotos quase idênticas no mesmo grupo.
- [ ] Completar novamente dez fotos diurnas por classe na calibração: faltam quatro encobertas e duas limpas após a revisão do escopo. O teste reservado já contém dez por classe.
- [x] Reservar nove casos difíceis para análise qualitativa em `refs/caso_dificil/`: três originais (prédios, vista aérea e nuvem fora do recorte) e seis transferidos da calibração por ambiguidade ou iluminação crepuscular. Registrar sua procedência e uso anterior na calibração.

**Critério de aceite.** Os dois conjuntos contêm exemplos das duas classes, com rótulos definidos antes da execução. Os casos difíceis estão separados para análise qualitativa.

## 2. Preparar o projeto Python

No PowerShell, execute estes comandos a partir da raiz do projeto.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py refs/calibracao/ceu_limpo/ceu_limpo_1.jpg
```

Passe o caminho de uma foto disponível no seu computador. O comando abre a imagem e exibe as proporções das máscaras e a classificação.

- [x] Criar um ambiente virtual e registrar `opencv-python` e `numpy` em `requirements.txt`.
- [x] Usar OpenCV e NumPy para carregar as imagens.
- [x] Criar a linha de comando com `argparse` em `main.py`.
- [x] Tratar caminhos inexistentes e arquivos de imagem inválidos com mensagens claras.

**Critério de aceite.** Outra pessoa do grupo consegue instalar as dependências seguindo o README, abrir uma foto e identificar o problema ao fornecer um arquivo inválido.

## 3. Extrair as características da imagem

- [x] Implementar o processamento em `classifier.py` e usar NumPy para calcular as proporções de pixels.
- [x] Recortar o terço superior da foto como aproximação da região do céu.
- [x] Converter o recorte de BGR para HSV e gerar duas máscaras. A primeira marca pixels azuis com saturação suficiente. A segunda marca pixels claros de baixa saturação, que podem indicar nuvens claras.
- [x] Calcular a porcentagem de pixels marcados em cada máscara sobre a área total do recorte.
- [x] Adicionar uma opção de diagnóstico para salvar o recorte e as máscaras.

**Critério de aceite.** Ao executar o processamento em uma foto de cada classe, o grupo consegue abrir o recorte e as máscaras e conferir se as porcentagens correspondem às áreas marcadas.

## 4. Implementar e calibrar as regras

- [x] Criar uma regra de referência usando apenas a proporção de azul.
- [x] Criar uma regra combinada. Muito azul favorece `ceu_limpo`. Pouco azul junto com muitos pixels claros de baixa saturação favorece `ceu_encoberto`. Sinais insuficientes ou conflitantes resultam em `indeterminado`.
- [x] Ajustar os limiares com as fotos de calibração, centralizar os valores no código e congelá-los antes do teste.
- [x] Exibir o rótulo, as duas porcentagens e a condição aplicada.

**Critério de aceite.** Outra pessoa consegue reproduzir uma decisão a partir das porcentagens e dos limiares. Uma foto que cai fora das duas regras retorna `indeterminado`.

## 5. Avaliar em fotos separadas

- [x] Implementar a avaliação em lote em `evaluate.py`.
- [x] Executar as duas regras no mesmo conjunto de teste e registrar por foto o rótulo esperado, o resultado e as porcentagens das máscaras.
- [x] Apresentar matriz de confusão, acurácia geral e quantidade de abstenções. Na acurácia geral, uma abstenção em foto rotulada conta como resultado sem acerto.
- [x] Mostrar um acerto de cada classe, se houver, e explicar um erro ou uma abstenção olhando o recorte e as máscaras.
- [x] Avaliar os casos difíceis separadamente. Verificar, por exemplo, se um prédio branco ativa a máscara de nuvens ou se nuvens escuras escapam dela.

**Critério de aceite.** A avaliação é repetível com as mesmas fotos e limiares. O relatório apresenta acertos, erros e abstenções e compara as duas regras. Se os limiares forem ajustados depois do teste, uma nova avaliação usa fotos independentes.

## 6. Preparar a entrega

- [x] Atualizar o README com comandos para instalar, classificar uma foto, salvar as máscaras e executar a avaliação.
- [x] Preparar uma demonstração com uma foto de cada classe e um caso difícil. Mostrar a foto original, o recorte, as máscaras e a decisão.
- Não exigido pela disciplina: ~~se a entrega exigir API, expor a mesma função com FastAPI em `POST /classify`~~.
- Não exigido pela disciplina: ~~se a entrega exigir deep learning, treinar uma MobileNetV2 por transferência de aprendizado e comparar com a abordagem clássica~~.

**Critério de aceite.** Alguém do grupo consegue executar a demonstração pelo README e explicar uma decisão pelas máscaras. A API e o modelo treinado entram na validação final quando forem requisitos da disciplina.
