# Sky Pixel

Protótipo em Python para classificar fotografias externas diurnas pela aparência do céu. A primeira versão trabalha com céu visível na parte superior da foto e retorna `ceu_limpo`, `ceu_encoberto` ou `indeterminado` quando as pistas são insuficientes ou conflitantes.

**Fluxo** — Foto → recorte do céu → conversão para HSV → máscaras → medidas → classificação.

## 1. Definir o escopo e preparar as fotos

- [ ] Definir as duas classes com exemplos rotulados. Separar céu parcialmente nublado, pouco céu visível e prédios no recorte como casos difíceis.
- [ ] Dividir as imagens em calibração e teste antes de ajustar o algoritmo. Manter fotos quase idênticas no mesmo grupo.
- [ ] Se houver tempo, reunir 10 fotos por classe para calibração e outras 10 por classe para teste.

**Critério de aceite.** Os dois conjuntos contêm exemplos das duas classes, com rótulos definidos antes da execução. Os casos difíceis estão separados para análise qualitativa.

## 2. Preparar o projeto Python

- [ ] Criar um ambiente virtual e registrar `opencv-python` e `numpy` em `requirements.txt`.
- [ ] Usar OpenCV para leitura, conversão HSV e máscaras. Usar NumPy para calcular as proporções de pixels.
- [ ] Organizar a linha de comando com `argparse` em `main.py`, o processamento em `classifier.py` e a avaliação em lote em `evaluate.py`.
- [ ] Tratar caminhos inexistentes e arquivos de imagem inválidos com mensagens claras.

**Critério de aceite.** Outra pessoa do grupo consegue instalar as dependências seguindo o README, abrir uma foto e identificar o problema ao fornecer um arquivo inválido.

## 3. Extrair as características da imagem

- [ ] Recortar o terço superior da foto como aproximação da região do céu.
- [ ] Converter o recorte de BGR para HSV e gerar duas máscaras. A primeira marca pixels azuis com saturação suficiente. A segunda marca pixels claros de baixa saturação, que podem indicar nuvens claras.
- [ ] Calcular a porcentagem de pixels marcados em cada máscara sobre a área total do recorte.
- [ ] Adicionar uma opção de diagnóstico para salvar o recorte e as máscaras.

**Critério de aceite.** Ao executar o processamento em uma foto de cada classe, o grupo consegue abrir o recorte e as máscaras e conferir se as porcentagens correspondem às áreas marcadas.

## 4. Implementar e calibrar as regras

- [ ] Criar uma regra de referência usando apenas a proporção de azul.
- [ ] Criar uma regra combinada. Muito azul favorece `ceu_limpo`. Pouco azul junto com muitos pixels claros de baixa saturação favorece `ceu_encoberto`. Sinais insuficientes ou conflitantes resultam em `indeterminado`.
- [ ] Ajustar os limiares com as fotos de calibração, centralizar os valores no código e congelá-los antes do teste.
- [ ] Exibir o rótulo, as duas porcentagens e a condição aplicada.

**Critério de aceite.** Outra pessoa consegue reproduzir uma decisão a partir das porcentagens e dos limiares. Uma foto que cai fora das duas regras retorna `indeterminado`.

## 5. Avaliar em fotos separadas

- [ ] Executar as duas regras no mesmo conjunto de teste e registrar por foto o rótulo esperado, o resultado e as porcentagens das máscaras.
- [ ] Apresentar matriz de confusão, acurácia geral e quantidade de abstenções. Na acurácia geral, uma abstenção em foto rotulada conta como resultado sem acerto.
- [ ] Mostrar um acerto de cada classe, se houver, e explicar um erro ou uma abstenção olhando o recorte e as máscaras.
- [ ] Avaliar os casos difíceis separadamente. Verificar, por exemplo, se um prédio branco ativa a máscara de nuvens ou se nuvens escuras escapam dela.

**Critério de aceite.** A avaliação é repetível com as mesmas fotos e limiares. O relatório apresenta acertos, erros e abstenções e compara as duas regras. Se os limiares forem ajustados depois do teste, uma nova avaliação usa fotos independentes.

## 6. Preparar a entrega

- [ ] Atualizar o README com comandos para instalar, classificar uma foto, salvar as máscaras e executar a avaliação.
- [ ] Preparar uma demonstração com uma foto de cada classe e um caso difícil. Mostrar a foto original, o recorte, as máscaras e a decisão.
- [ ] Se a entrega exigir API, expor a mesma função com FastAPI em `POST /classify`. O endpoint recebe uma imagem e retorna o rótulo e as medidas em JSON.
- [ ] Se a entrega exigir deep learning, treinar uma MobileNetV2 por transferência de aprendizado com as mesmas classes e a mesma divisão das fotos. Comparar os resultados com a abordagem clássica.

**Critério de aceite.** Alguém do grupo consegue executar a demonstração pelo README e explicar uma decisão pelas máscaras. A API e o modelo treinado entram na validação final quando forem requisitos da disciplina.

## Ordem para o dia da entrega

Priorizar o fluxo completo de uma foto até uma classificação explicável. A separação e a rotulagem das imagens podem avançar em paralelo. Depois de validar o classificador, rodar a avaliação e preparar a demonstração antes de adicionar interface ou novas classes.
