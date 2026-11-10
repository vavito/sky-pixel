# Sky Pixel

Protótipo em Python para classificar fotografias externas diurnas pela aparência do céu. A primeira versão trabalha com céu visível na parte superior da foto e retorna `ceu_limpo`, `ceu_encoberto` ou `indeterminado` quando as pistas são insuficientes ou conflitantes.

**Fluxo** — Foto → recorte do céu → conversão para HSV → máscaras → medidas → classificação.

## Escopo e divisão das fotos

As classes descrevem a aparência visual em **iluminação diurna**:

- `ceu_limpo`: céu predominantemente aberto; pode conter nuvens isoladas ou finas. As fotos limpas 1, 2 e 10 permanecem nessa classe.
- `ceu_encoberto`: céu coberto ou quase inteiramente coberto por nuvens, inclusive nuvens escuras.
- Casos difíceis: cenas sem predominância clara de céu aberto ou encoberto, pouco céu visível, obstruções no recorte e iluminação de pôr do sol ou crepúsculo. São analisados qualitativamente, sem assumir um rótulo binário esperado. `indeterminado` é uma saída das regras, não uma terceira classe meteorológica.

| Conjunto atual | Céu encoberto | Céu limpo | Total |
| --- | ---: | ---: | ---: |
| Calibração | 6 | 8 | 14 |
| Teste reservado | 10 | 10 | 20 |
| Casos difíceis (sem divisão binária) | — | — | 9 |
| **Total de fotos originais** | | | **43** |

A divisão original tinha 20 fotos de calibração e três casos difíceis. Após inspeção visual e definição do escopo, seis fotos da calibração foram transferidas para `refs/caso_dificil/`, mantendo os bytes e a numeração original no nome:

| Origem em `refs/calibracao/` | Novo nome em `refs/caso_dificil/` | Motivo |
| --- | --- | --- |
| `ceu_encoberto/ceu_encoberto_2.jpg` | `origem_calibracao_ceu_encoberto_2.jpg` | Parcialmente nublado; rótulo ambíguo. |
| `ceu_encoberto/ceu_encoberto_4.jpg` | `origem_calibracao_ceu_encoberto_4.jpg` | Pôr do sol. |
| `ceu_encoberto/ceu_encoberto_8.jpg` | `origem_calibracao_ceu_encoberto_8.jpg` | Iluminação alaranjada/crepuscular. |
| `ceu_encoberto/ceu_encoberto_9.jpg` | `origem_calibracao_ceu_encoberto_9.jpg` | Pôr do sol. |
| `ceu_limpo/ceu_limpo_7.jpg` | `origem_calibracao_ceu_limpo_7.jpg` | Crepúsculo. |
| `ceu_limpo/ceu_limpo_8.jpg` | `origem_calibracao_ceu_limpo_8.jpg` | Crepúsculo com nuvens rosadas. |

Essas seis fotos **já participaram da calibração**: a análise posterior delas é qualitativa, sem tratá-las como exemplos independentes de teste. A seleção foi feita após observar os resultados, por critérios de escopo e ambiguidade visual; por isso, os totais da calibração anterior e atual não são uma comparação de desempenho. Os limiares foram mantidos, inclusive escolhas originalmente influenciadas pelas fotos transferidas. Os 20 arquivos de teste e seus rótulos foram preservados e não foram usados para ajustar valores nesta revisão. A adequação deles ao escopo deverá ser conferida na etapa 5 antes de calcular as métricas; eventuais exclusões devem ser justificadas e registradas, sem selecionar pelos acertos.

Para voltar à meta de dez fotos por classe na calibração, faltam quatro encobertas e duas limpas diurnas, novas e independentes do teste. Essa ampliação é opcional para o protótipo e exige nova versão do registro antes da avaliação.

## Executar as etapas 3 e 4

Requer Python 3.10 ou superior. Na pasta do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py caminho/foto.jpg
python main.py caminho/foto.jpg --rule both --diagnostics diagnostics/foto
python main.py caminho/foto.jpg --rule both --json
```

`classifier.py` contém a leitura, a extração e as duas regras; `main.py` oferece a CLI. `--rule blue` executa a referência, `--rule combined` executa a combinada (padrão) e `--rule both` compara ambas usando as mesmas medidas. Arquivos ausentes ou inválidos encerram com código 2 e uma mensagem de erro.

O diagnóstico salva `recorte.png`, `mascara_azul.png` e `mascara_claros.png`. Nas máscaras, branco indica pixel marcado e preto indica pixel descartado. Cada porcentagem é a quantidade de pixels marcados dividida pela área total do recorte. Use uma pasta por foto: arquivos de diagnóstico com os mesmos nomes são substituídos. O recorte usa as primeiras `altura // 3` linhas, com mínimo de uma linha.

### Calibração v3 — escopo diurno consolidado em 2026-11-10

O conjunto atual contém 14 fotos de `refs/calibracao` (seis encobertas e oito limpas), provenientes do commit `d30b21a` após as transferências documentadas acima. `calibration.json` registra os caminhos atuais, hashes SHA-256, versões das bibliotecas, medidas, decisões, observações visuais e a origem das seis transferências. `THRESHOLDS`, em `classifier.py`, é a fonte dos limiares usados na execução.

Os registros anteriores foram preservados em `calibration_v1.json` (quatro fotos) e `calibration_v2.json` (20 fotos). Os caminhos neles são históricos: seis originais agora estão em `refs/caso_dificil/`, com correspondência e hashes registrados em `calibration.json`. Todos os limiares foram mantidos e o estado atual é `congelado_2026-11-10_calibracao_v3`.

Na revisão v2, geramos e inspecionamos 20 recortes e 40 máscaras. A conferência automática dos PNGs verificou o terço superior original, pixels de máscara apenas 0/255 e correspondência com as medidas calculadas. Os diagnósticos das seis transferidas foram movidos para `diagnostics/caso_dificil/<novo_nome_sem_extensão>/`.

HSV segue a escala OpenCV: H de 0 a 179 e S/V de 0 a 255. Os intervalos das máscaras incluem os extremos.

| Medida ou regra | Valor congelado |
| --- | --- |
| Máscara azul | H entre 90 e 130, S ≥ 100 e V ≥ 50 |
| Máscara de claros de baixa saturação | S ≤ 50 e V ≥ 180 |
| Referência: céu limpo | Azul ≥ 70% |
| Referência: céu encoberto | Azul ≤ 20% |
| Referência: indeterminado | Azul entre 20% e 70% |
| Combinada: céu limpo | Azul ≥ 70% e claros < 35% |
| Combinada: céu encoberto | Azul ≤ 20% e claros ≥ 35% |
| Combinada: indeterminado | Demais casos |

Na calibração inicial (v1, antes da revisão do conjunto), a inspeção dos recortes e máscaras mostrou que S ≥ 60 marcava nuvens escuras como azul (72,49% na primeira foto encoberta). Com S ≥ 100, essa proporção caiu para 0,02%, mantendo mais de 93% de azul nas duas fotos limpas. Escolhemos 70% como mínimo de azul para céu limpo, mantivemos 20% como máximo para encoberto e reduzimos o mínimo de claros de 50% para 35%, abaixo dos 39,09% observados na segunda foto encoberta. Os demais limites HSV foram mantidos. São escolhas exploratórias sobre uma amostra pequena, sem garantia de generalização.

| Foto em `refs/calibracao` | Azul | Claros | Referência | Combinada |
| --- | ---: | ---: | --- | --- |
| `ceu_encoberto/ceu_encoberto_1.jpg` | 0,02% | 1,63% | ceu_encoberto | indeterminado |
| `ceu_encoberto/ceu_encoberto_3.jpg` | 0,00% | 0,00% | ceu_encoberto | indeterminado |
| `ceu_encoberto/ceu_encoberto_5.jpg` | 0,00% | 11,60% | ceu_encoberto | indeterminado |
| `ceu_encoberto/ceu_encoberto_6.jpg` | 0,00% | 20,73% | ceu_encoberto | indeterminado |
| `ceu_encoberto/ceu_encoberto_7.jpg` | 22,20% | 0,00% | indeterminado | indeterminado |
| `ceu_encoberto/ceu_encoberto_10.jpg` | 0,00% | 97,23% | ceu_encoberto | ceu_encoberto |
| `ceu_limpo/ceu_limpo_1.jpg` | 99,93% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo/ceu_limpo_2.jpg` | 93,23% | 0,34% | ceu_limpo | ceu_limpo |
| `ceu_limpo/ceu_limpo_3.jpg` | 100,00% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo/ceu_limpo_4.jpg` | 80,35% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo/ceu_limpo_5.jpg` | 94,44% | 1,57% | ceu_limpo | ceu_limpo |
| `ceu_limpo/ceu_limpo_6.jpg` | 94,23% | 1,70% | ceu_limpo | ceu_limpo |
| `ceu_limpo/ceu_limpo_9.jpg` | 100,00% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo/ceu_limpo_10.jpg` | 85,22% | 6,28% | ceu_limpo | ceu_limpo |

Esses são resultados de **calibração, não de teste**. No conjunto atual, a referência coincide com os rótulos em 13/14 fotos e se abstém em uma (encoberta 7). A combinada coincide em 9/14 e se abstém em cinco (encobertas 1, 3, 5, 6 e 7). Nenhuma retorna a classe oposta. As duas classificam as oito fotos limpas. Esses números descrevem o conjunto revisado, não estimam desempenho em fotos novas nem demonstram melhoria em relação à v2.

Limitações mantidas no relatório:

- **Nuvens escuras:** nas encobertas 1 e 3, a máscara de claros fica quase vazia; nas 5 e 6, marca apenas as partes mais iluminadas. Essas fotos continuam na calibração: nuvens escuras pertencem ao escopo, mesmo quando provocam abstenção.
- **Nuvens azuladas:** na encoberta 7, parte das nuvens ativa a máscara azul (22,20%). Nuvens finas também entram nessa máscara na limpa 1. As máscaras são pistas de cor e não uma segmentação perfeita.
- **Recorte fixo:** pode perder nuvens abaixo do terço superior. Na limpa 6, a neve fica fora do recorte e o sol ativa parcialmente a máscara de claros. Objetos brancos também podem ativá-la.

As decisões descrevem a aparência do recorte e não medem condições meteorológicas físicas. Mantivemos os limiares e documentamos as abstenções.

Os diagnósticos atuais ficam em `diagnostics/calibracao/<classe>/<foto>/`. Os painéis em `diagnostics/revisao_calibracao/painel_1.jpg` até `painel_4.jpg` são o registro histórico da inspeção v2 das 20 fotos, com nomes e agrupamentos anteriores à transferência (primeiros dois: antigas encobertas; últimos dois: antigas limpas). A pasta `diagnostics/` é ignorada pelo Git. Para regenerar os PNGs do conjunto atual, execute na raiz do projeto, com o ambiente virtual ativado:

```python
from pathlib import Path
from classifier import extract_features, load_image, save_diagnostics

for foto in sorted(Path("refs/calibracao").glob("*/*.jpg")):
    medidas = extract_features(load_image(foto))
    destino = Path("diagnostics/calibracao") / foto.parent.name / foto.stem
    save_diagnostics(medidas, destino)
```

Para reproduzir uma decisão, use as porcentagens sem arredondamento do JSON; os valores da tabela são arredondados. Os arquivos `*_preview.jpg` antigos são apenas visualizações auxiliares e não são usados no cálculo.

A avaliação em lote (`evaluate.py`), a matriz de confusão e a análise do caso difícil ficam para a etapa 5. Se os limiares forem alterados após observar os resultados de teste, uma nova avaliação deverá usar fotos independentes.

## Responsáveis e passagem de trabalho

Cada integrante assume duas etapas inteiras. O próximo recebe um bloco validado e continua a partir do material entregue.

| Ordem | Responsável | Etapas | O que passa adiante |
| --- | --- | --- | --- |
| 1 | João Victor Moreira Almeida | 1 e 2 | Escopo definido, fotos rotuladas e separadas em calibração e teste, ambiente Python configurado e CLI capaz de abrir uma imagem. |
| 2 | João Vitor Justiniano Barbosa | 3 e 4 | Classificador executável pela CLI, recorte e máscaras disponíveis para inspeção, duas regras de decisão e limiares congelados usando a calibração. |
| 3 | Pedro Crispim Pereira | 5 e 6 | Avaliação reproduzível no conjunto de teste, resultados registrados no README e demonstração pronta para a entrega. |

- [x] **João Victor → João Vitor.** Conferir que os caminhos das fotos são utilizáveis, que os grupos estão identificados e que a CLI abre uma foto de calibração.
- [x] **João Vitor → Pedro.** Demonstrar que as duas regras rodam com os mesmos arquivos, que as máscaras podem ser salvas e que os limiares ficaram registrados antes do teste.
- [ ] **Pedro → entrega.** Conferir a execução a partir de um clone limpo e registrar os resultados obtidos e os exemplos usados na demonstração.

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

- [ ] Implementar a avaliação em lote em `evaluate.py`.
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
