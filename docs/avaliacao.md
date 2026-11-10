# Avaliação e demonstração

[Voltar à apresentação](../README.md)

## Avaliação no conjunto de teste (etapa 5)

`evaluate.py` executa as duas regras sobre as mesmas 20 fotos de `refs/teste/` (10 por classe) e, separadamente, sobre os 9 casos difíceis. A saída inclui os resultados por foto, as matrizes de confusão e o resumo de cada regra. Com `--csv`/`--json`, os mesmos dados são salvos em arquivo; com `--diagnostics`, recorte e máscaras de cada foto vão para `<pasta>/teste/<classe>/<foto>/` e `<pasta>/caso_dificil/<foto>/`. Os limiares usados são os congelados (`congelado_2026-11-10_calibracao_v3`); **nenhum valor foi alterado depois de ver o teste**.

Definições: **acurácia geral** = acertos / total, com abstenção (`indeterminado`) contando como sem acerto; **cobertura** = fotos em que a regra decidiu / total; **acurácia quando decide** = acertos / fotos decididas.

### Conferência de escopo antes das métricas

Inspecionamos as 20 fotos de teste antes de tirar conclusões: todas são diurnas, sem pôr do sol nem crepúsculo. A única ressalva é `ceu_encoberto_1.jpg`: o céu é de cúmulos espalhados com bastante azul visível, o mesmo perfil de "parcialmente nublado; rótulo ambíguo" que motivou a transferência de `calibracao/ceu_encoberto_2.jpg`. Para não selecionar pelos acertos, **as métricas principais usam as 20 fotos com os rótulos originais**, e a exclusão aparece só como análise de sensibilidade. As duas regras se abstêm nessa foto, então excluí-la não muda nenhum acerto, apenas o denominador.

### Resultados por foto

| Foto em `refs/teste` | Esperado | Azul | Claros | Referência | Combinada |
| --- | --- | ---: | ---: | --- | --- |
| `ceu_encoberto_1.jpg` | ceu_encoberto | 31,95% | 43,83% | indeterminado | indeterminado |
| `ceu_encoberto_2.jpg` | ceu_encoberto | 0,00% | 8,48% | ceu_encoberto | indeterminado |
| `ceu_encoberto_3.jpg` | ceu_encoberto | 0,80% | 0,55% | ceu_encoberto | indeterminado |
| `ceu_encoberto_4.jpg` | ceu_encoberto | 0,00% | 0,00% | ceu_encoberto | indeterminado |
| `ceu_encoberto_5.jpg` | ceu_encoberto | 17,20% | 11,35% | ceu_encoberto | indeterminado |
| `ceu_encoberto_6.jpg` | ceu_encoberto | 11,46% | 74,32% | ceu_encoberto | ceu_encoberto |
| `ceu_encoberto_7.jpg` | ceu_encoberto | 4,21% | 7,48% | ceu_encoberto | indeterminado |
| `ceu_encoberto_8.jpg` | ceu_encoberto | 0,20% | 40,94% | ceu_encoberto | ceu_encoberto |
| `ceu_encoberto_9.jpg` | ceu_encoberto | 0,00% | 14,14% | ceu_encoberto | indeterminado |
| `ceu_encoberto_10.jpg` | ceu_encoberto | 0,00% | 45,96% | ceu_encoberto | ceu_encoberto |
| `ceu_limpo_1.jpg` | ceu_limpo | 100,00% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo_2.jpg` | ceu_limpo | 99,81% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo_3.jpg` | ceu_limpo | 0,00% | 1,12% | **ceu_encoberto** | indeterminado |
| `ceu_limpo_4.jpg` | ceu_limpo | 99,08% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo_5.jpg` | ceu_limpo | 0,10% | 5,37% | **ceu_encoberto** | indeterminado |
| `ceu_limpo_6.jpg` | ceu_limpo | 91,99% | 5,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo_7.jpg` | ceu_limpo | 100,00% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_limpo_8.jpg` | ceu_limpo | 0,00% | 61,96% | **ceu_encoberto** | **ceu_encoberto** |
| `ceu_limpo_9.jpg` | ceu_limpo | 69,07% | 6,73% | indeterminado | indeterminado |
| `ceu_limpo_10.jpg` | ceu_limpo | 73,78% | 0,00% | ceu_limpo | ceu_limpo |

Em negrito, as saídas da classe oposta (erros).

### Matrizes de confusão

Referência (só azul):

| Esperado \ Saída | ceu_encoberto | ceu_limpo | indeterminado |
| --- | ---: | ---: | ---: |
| ceu_encoberto | 9 | 0 | 1 |
| ceu_limpo | 3 | 6 | 1 |

Combinada:

| Esperado \ Saída | ceu_encoberto | ceu_limpo | indeterminado |
| --- | ---: | ---: | ---: |
| ceu_encoberto | 3 | 0 | 7 |
| ceu_limpo | 1 | 6 | 3 |

| Regra | Acurácia geral | Erros | Abstenções | Cobertura | Acurácia quando decide | Sem `ceu_encoberto_1` (sensibilidade) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Referência | 15/20 (75,00%) | 3 | 2 | 90,00% | 15/18 (83,33%) | 15/19 (78,95%) |
| Combinada | 9/20 (45,00%) | 1 | 10 | 50,00% | 9/10 (90,00%) | 9/19 (47,37%) |

### Comparação das regras

- **A referência decide mais e erra mais.** Acerta 15 de 20, mas manda três fotos limpas para `ceu_encoberto`. Como só olha o azul, qualquer céu limpo pouco saturado (abaixo de S = 100) vira "pouco azul" e, portanto, encoberto.
- **A combinada é conservadora.** Erra só uma vez, mas se abstém em metade das fotos. Ela exige prova positiva de nuvem clara (claros ≥ 35%) para dizer `ceu_encoberto`, e por isso não confunde céu limpo desbotado com nuvem (limpas 3 e 5 viram `indeterminado` em vez de erro). Em compensação, não reconhece nuvens escuras: seis das sete abstenções em encobertas têm claros abaixo de 15% (encobertas 2, 3, 4, 5, 7 e 9), o mesmo padrão já visto na calibração.
- Nenhuma das regras confunde encoberto com limpo: os erros são sempre de céu limpo classificado como encoberto.
- Os números vêm de 20 fotos e servem para descrever este conjunto, não para estimar o desempenho em geral.

### Acertos e erros explicados pelas máscaras

Para gerar os PNGs citados abaixo, rode `python evaluate.py --diagnostics diagnostics/avaliacao`.

- **Acerto, céu limpo — `ceu_limpo_1.jpg`:** o recorte é só céu azul saturado; a máscara azul fica inteiramente branca (100%) e a de claros, vazia. As duas regras dizem `ceu_limpo`. O prédio branco está fora do terço superior e não interfere.
- **Acerto, céu encoberto — `ceu_encoberto_10.jpg`:** nuvens cinza-claras cobrem o recorte; a máscara azul fica vazia (0%) e a de claros marca a faixa iluminada das nuvens (45,96%). As duas regras dizem `ceu_encoberto`.
- **Erro da referência / abstenção da combinada — `ceu_limpo_3.jpg`:** céu limpo com névoa, azul-acinzentado. A saturação do céu fica abaixo de 100, então a máscara azul fica preta (0,00%). A referência conclui `ceu_encoberto`. A combinada procura nuvem clara, não encontra (claros 1,12%) e devolve `indeterminado`. `ceu_limpo_5.jpg` repete o padrão: foto dessaturada, quase em tons de cinza.
- **Erro das duas regras — `ceu_limpo_8.jpg`:** céu limpo e esbranquiçado, com cirros finos e névoa perto do horizonte. Sem saturação, o céu cai inteiro na máscara de claros (61,96%) e nada na azul. Pela cor, ele é indistinguível de um céu encoberto claro. É uma limitação das pistas HSV, não algo que se resolva só mudando um limiar.
- **Abstenção no limite — `ceu_limpo_9.jpg`:** 69,07% de azul, contra o mínimo de 70%. A faixa inferior do recorte pega cúmulos e a linha das árvores, o que derruba a proporção.
- **Abstenção por nuvem escura — `ceu_encoberto_4.jpg`:** céu de tempestade cinza-escuro. As duas máscaras ficam vazias (0% e 0%), porque as nuvens não são azuis nem claras (V < 180). A referência acerta só porque "pouco azul" basta para ela; a combinada se abstém.

### Casos difíceis (análise qualitativa)

| Foto em `refs/caso_dificil` | Situação | Azul | Claros | Referência | Combinada |
| --- | --- | ---: | ---: | --- | --- |
| `caso_dificil_1.jpg` | Prédios espelhados contra céu branco | 16,39% | 53,71% | ceu_encoberto | ceu_encoberto |
| `caso_dificil_2.jpg` | Nuvem grande abaixo do recorte | 98,54% | 1,26% | ceu_limpo | ceu_limpo |
| `caso_dificil_3.jpg` | Vista aérea sobre nuvens | 89,66% | 1,88% | ceu_limpo | ceu_limpo |
| `origem_calibracao_ceu_encoberto_2.jpg` | Parcialmente nublado | 10,78% | 39,09% | ceu_encoberto | ceu_encoberto |
| `origem_calibracao_ceu_encoberto_4.jpg` | Pôr do sol | 33,80% | 0,00% | indeterminado | indeterminado |
| `origem_calibracao_ceu_encoberto_8.jpg` | Nuvens alaranjadas | 0,00% | 0,00% | ceu_encoberto | indeterminado |
| `origem_calibracao_ceu_encoberto_9.jpg` | Pôr do sol | 0,00% | 0,00% | ceu_encoberto | indeterminado |
| `origem_calibracao_ceu_limpo_7.jpg` | Crepúsculo | 99,99% | 0,00% | ceu_limpo | ceu_limpo |
| `origem_calibracao_ceu_limpo_8.jpg` | Crepúsculo com nuvens rosadas | 70,94% | 0,00% | ceu_limpo | ceu_limpo |

As seis fotos `origem_calibracao_*` participaram da calibração e não servem como teste independente.

- **Prédios no recorte (`caso_dificil_1`):** a máscara de claros marca o céu branco e também os reflexos nas fachadas de vidro, e a azul pega parte do vidro. O resultado é `ceu_encoberto` sem que o recorte seja só céu. Confirma o risco previsto no plano: objetos brancos e reflexos ativam a máscara de nuvens.
- **Nuvem fora do recorte (`caso_dificil_2`):** o terço superior é quase todo azul (98,54%), mas a nuvem grande fica abaixo dele. As regras dizem `ceu_limpo` sobre um recorte que não representa a cena inteira. É a limitação do recorte fixo.
- **Crepúsculo (`origem_calibracao_ceu_limpo_7` e `_8`):** o céu roxo-azulado cai dentro de H 90–130 com saturação alta, e a máscara azul marca quase tudo. As regras não percebem que a iluminação está fora do escopo diurno e respondem `ceu_limpo` com segurança.
- **Pôr do sol com nuvens escuras (`origem_calibracao_ceu_encoberto_8` e `_9`):** as duas máscaras ficam vazias. A referência devolve `ceu_encoberto` só pela falta de azul, e a combinada se abstém. Aqui a abstenção é a resposta mais honesta.

Os limiares continuam congelados. Se forem ajustados a partir destes resultados, uma nova avaliação precisa usar fotos independentes deste teste.

## Demonstração (etapa 6)

Uma foto de cada classe e um caso difícil, com a foto original, o recorte, as máscaras e a decisão das duas regras. Com o ambiente ativado:

```bash
python main.py refs/teste/ceu_limpo/ceu_limpo_1.jpg --rule both --diagnostics diagnostics/demo/limpo
python main.py refs/teste/ceu_encoberto/ceu_encoberto_10.jpg --rule both --diagnostics diagnostics/demo/encoberto
python main.py refs/caso_dificil/caso_dificil_1.jpg --rule both --diagnostics diagnostics/demo/caso_dificil
```

Saída esperada:

| Foto | Azul | Claros | Referência | Combinada |
| --- | ---: | ---: | --- | --- |
| `ceu_limpo_1.jpg` | 100,00% | 0,00% | ceu_limpo | ceu_limpo |
| `ceu_encoberto_10.jpg` | 0,00% | 45,96% | ceu_encoberto | ceu_encoberto |
| `caso_dificil_1.jpg` | 16,39% | 53,71% | ceu_encoberto | ceu_encoberto |

Roteiro: abra a foto original e mostre `recorte.png` (o terço superior analisado). Em seguida, abra `mascara_azul.png` e `mascara_claros.png` (branco = pixel marcado) e explique a decisão pelas porcentagens e pela tabela de limiares. No caso difícil, aponte que a máscara de claros marca o reflexo nos prédios, não só o céu. Para mostrar uma abstenção, use `refs/teste/ceu_encoberto/ceu_encoberto_4.jpg` (nuvens escuras, as duas máscaras vazias).
