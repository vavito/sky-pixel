# Metodologia e guia de execução

[Voltar à apresentação](../README.md)

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

## Como executar

Requer Python 3.10 ou superior. Na pasta do projeto, crie o ambiente e instale as dependências.

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Com o ambiente ativado, os comandos são os mesmos nos dois sistemas:

```bash
# Classificar uma foto (regra combinada)
python main.py refs/teste/ceu_limpo/ceu_limpo_1.jpg

# Comparar as duas regras e salvar recorte e máscaras
python main.py refs/teste/ceu_limpo/ceu_limpo_1.jpg --rule both --diagnostics diagnostics/demo/limpo

# Saída em JSON
python main.py refs/teste/ceu_limpo/ceu_limpo_1.jpg --rule both --json

# Avaliação em lote: teste + casos difíceis
python evaluate.py
python evaluate.py --csv diagnostics/avaliacao.csv --json diagnostics/avaliacao.json --diagnostics diagnostics/avaliacao
```

`classifier.py` contém a leitura, a extração e as duas regras; `main.py` oferece a CLI; `evaluate.py` faz a avaliação em lote. `--rule blue` executa a referência, `--rule combined` executa a combinada (padrão) e `--rule both` compara ambas usando as mesmas medidas. Arquivos ausentes ou inválidos encerram com código 2 e uma mensagem de erro.

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
