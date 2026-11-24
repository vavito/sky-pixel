# Roteiro da apresentação final — Sky Pixel

Duração estimada: **10 a 12 minutos** + perguntas. São 12 slides divididos entre duas pessoas:

- **Apresentador A**: slides 1 a 6 (problema, HSV e as duas regras antigas) e o fechamento no slide 12.
- **Apresentador B**: slides 7 a 11 (falhas, a regra nova, resultados e validação) e a demonstração ao vivo, se houver tempo.

As falas abaixo são sugestões. Não precisam ser decoradas: o importante é saber explicar cada algoritmo com as próprias palavras. A parte "Como cada algoritmo funciona" serve de estudo para os dois.

---

## Como cada algoritmo funciona (para estudar antes)

### O caminho comum às três regras

1. **Recorte.** Pegamos só o terço de cima da foto (`altura // 3` linhas). Supomos que ali está o céu.
2. **HSV.** A foto vem em BGR (azul, verde, vermelho). Convertemos para HSV, que separa:
   - **H (matiz)**: *qual* cor. No OpenCV vai de 0 a 179. O azul do céu fica entre **90 e 130**.
   - **S (saturação)**: *quão viva* é a cor. 0 é cinza, 255 é cor pura.
   - **V (brilho)**: *quão clara* é. 0 é preto, 255 é o mais claro.

   A vantagem: "é azul?" vira uma pergunta só sobre H, sem se misturar com a luz.
3. **Máscara.** Para cada pixel perguntamos "tem a característica X?". Sim vira branco (255) e não vira preto (0). É uma imagem em preto e branco do mesmo tamanho do recorte.
4. **Porcentagem.** Pixels brancos ÷ total de pixels do recorte.
5. **Regra.** Comparamos as porcentagens com limiares fixos e saímos com `ceu_limpo`, `ceu_encoberto` ou `indeterminado`.

### Regra 1: referência (só azul)

- **Máscara azul:** H entre 90 e 130, **S ≥ 100** (azul forte) e V ≥ 50.
- **Decisão:** azul ≥ 70% dá limpo. Azul ≤ 20% dá encoberto. Entre os dois, indeterminado.
- **Intuição:** "se o céu é azul, está limpo".
- **Ponto fraco:** "pouco azul" não prova que há nuvem. Um céu limpo com névoa é azul *pálido* (S < 100), a máscara fica vazia e a regra diz "encoberto", o que é um erro.

### Regra 2: combinada (azul + claros)

- **Máscara de claros:** **S ≤ 50** (quase sem cor) e **V ≥ 180** (claro). É o "branco de nuvem".
- **Decisão:** limpo se azul ≥ 70% **e** claros < 35%. Encoberto se azul ≤ 20% **e** claros ≥ 35%. Qualquer outro caso dá indeterminado.
- **Intuição:** só diz "encoberto" quando *vê* nuvem branca, não apenas pela falta de azul.
- **Ponto fraco:** nuvem de **tempestade** é cinza-**escura** (V < 180) e não entra na máscara de claros. A regra se abstém muito: 10 das 20 fotos de teste.

### Regra 3: céu aberto (nova; cor + brilho + textura)

Um pixel só conta como "céu aberto" se passar nos **três filtros ao mesmo tempo**:

| Filtro | Condição | O que elimina |
| --- | --- | --- |
| Cor | H entre 90 e 130 e **S ≥ 30** | Nuvem cinza ou branca (sem cor). Aceita o azul pálido da névoa. |
| Brilho | **V ≥ 100** | Nuvem escura de tempestade. |
| Textura | Desvio padrão do brilho numa janela **7×7** **< 4** | Nuvem com relevo, bordas e "fofura". |

- **Textura, explicada de forma simples:** para cada pixel olhamos os 49 vizinhos (7×7) e medimos o quanto o brilho varia entre eles (o desvio padrão). Céu limpo é um degradê suave, então varia quase nada. Nuvem tem bordas claras e escuras lado a lado, então varia muito. Usamos `cv2.blur` para calcular a média local de forma rápida: desvio = √(média de x² − (média de x)²).
- **Antes de medir**, a foto é reduzida para **320 pixels de largura**. Assim a textura não depende da resolução da câmera (numa foto de 4000 px, a mesma nuvem parece "mais lisa" de perto).
- **Decisão:** céu aberto ≥ 50% dá limpo. ≤ 30% dá encoberto. Entre os dois, indeterminado.
- **Por que funciona onde as outras falham:**
  - Névoa: azul pálido passa no filtro de cor (S ≥ 30). Céu aberto 98%, limpo.
  - Tempestade: escura, reprovada no brilho. Céu aberto 5%, encoberto.
  - Nuvens azuladas: passam na cor (96%), mas não são lisas (14%). Céu aberto 12%, encoberto.
  - Céu esbranquiçado com cirros: as áreas lisas entre os cirros somam 63%, limpo.

### Números para ter na ponta da língua

| Regra | Acertos no teste (20 fotos) | Erros | Abstenções |
| --- | ---: | ---: | ---: |
| Referência | 15 (75%) | 3 | 2 |
| Combinada | 9 (45%) | 1 | 10 |
| **Céu aberto** | **20 (100%)** | **0** | **0** |

Validação da regra nova (`python crossval.py`):

- **Calibração → teste:** o programa escolhe sozinho os parâmetros entre 80 combinações usando só as 14 fotos de calibração e depois mede no teste. Resultado: **18/20 (90%)**. Erra as limpas 5 e 8 do teste.
- **Leave-one-out:** 34 rodadas. Em cada uma, uma foto fica de fora, os parâmetros são escolhidos com as outras 33 e a foto de fora é classificada. Resultado: **34/34**.
- **Folga:** com os parâmetros finais, a foto limpa com *menos* céu aberto tem 63% e a encoberta com *mais* tem 22%. São 41 pontos de distância, e os limiares (30% e 50%) ficam nesse intervalo.

---

## Fala por slide

### Slide 1 · Capa (A, ~30 s)
"Boa tarde! O nosso projeto se chama Sky Pixel. A pergunta é simples: olhando uma foto tirada de dia, o computador consegue dizer se o céu está limpo ou encoberto? E a gente quis responder isso sem rede neural, com regras que dá para explicar pixel por pixel."

### Slide 2 · O problema (A, ~45 s)
"O classificador responde uma de duas classes: céu limpo ou céu encoberto. Ele também pode dizer 'indeterminado' quando não tem certeza, porque um chute errado é pior que uma abstenção. Separamos as fotos antes de mexer em qualquer coisa: 14 para calibrar, 20 para testar, que não usamos para ajustar as regras antigas, e 9 casos difíceis só para discutir."

### Slide 3 · Pipeline (A, ~45 s)
"Todas as regras seguem o mesmo caminho. Recortamos o terço de cima, onde o céu costuma estar. Trocamos a forma de descrever a cor para HSV. Criamos máscaras, imagens em preto e branco em que branco quer dizer 'esse pixel tem o que procuro'. Contamos a porcentagem de branco e uma regra de limiar decide."

### Slide 4 · HSV (A, ~1 min)
"HSV separa três perguntas. H é 'qual cor': o azul do céu fica entre 90 e 130, a faixa com contorno laranja. S é 'quão viva': zero é cinza. V é o brilho: zero é preto. A intuição para o resto da apresentação é esta: céu limpo tem matiz azul, nuvem tem pouca saturação, e nuvem escura tem também pouco brilho."

### Slide 5 · Regra 1 (A, ~45 s)
"A primeira regra é a mais intuitiva: se é azul, está limpo. A máscara marca pixels de azul forte. Na foto limpa dá 100%, na nublada dá 0%. Com 70% ou mais, céu limpo. Com 20% ou menos, encoberto. O problema é que 'pouco azul' não prova que tem nuvem."

### Slide 6 · Regra 2 (A, ~45 s, depois passa a palavra)
"A segunda regra exige prova de nuvem: a máscara de claros marca pixels quase sem cor e bem claros, o branco de nuvem. Na foto nublada, 46% é claro e 0% é azul, então ela diz encoberto. Se as pistas não concordam, ela se abstém. Ela quase não erra, mas o [nome do B] vai mostrar o preço disso."

### Slide 7 · Onde elas tropeçam (B, ~1 min)
"No teste apareceram dois problemas. Nuvem de tempestade é escura: não é azul nem clara, as duas máscaras ficam vazias e a combinada desiste. Céu com névoa é azul pálido: a máscara azul não pega nada e a referência diz 'encoberto', errado. A referência fez 15 de 20 e a combinada só 9, porque se absteve em metade. Conclusão: só cor não basta."

### Slide 8 · Regra 3, céu aberto (B, ~1 min 30 s; é o slide mais importante)
"A nova regra pergunta 'quanto do recorte parece céu aberto?'. Um pixel conta se passar em três filtros. Cor: matiz azul, aceitando azul pálido. Brilho: não pode ser escuro, e isso elimina tempestade. Textura: medimos o quanto o brilho varia na vizinhança 7×7. Céu é um degradê liso, nuvem tem relevo. Neste exemplo as nuvens são azuladas: 96% passa na cor, então a cor sozinha nos enganaria. Mas só 14% é liso, e no fim só 12% é céu aberto, então o resultado é encoberto."

### Slide 9 · Na prática (B, ~1 min)
"As três fotos que mais davam problema: névoa vira 98% de céu aberto, limpo, quando antes a referência errava. Tempestade vira 5%, encoberto, quando antes a combinada desistia. Céu esbranquiçado, em que as duas regras erravam, tem áreas lisas entre os cirros que somam 63%, limpo."

### Slide 10 · Resultados (B, ~45 s)
"Nas mesmas 20 fotos de teste: referência 75%, combinada 45% e céu aberto 100%, sem nenhum erro e sem nenhuma abstenção."

### Slide 11 · Validação (B, ~1 min 15 s)
"Uma pergunta justa: vocês ajustaram a regra para acertar o teste? A ideia da textura veio depois de vermos os erros, então conferimos de dois jeitos. No protocolo estrito, o programa escolhe os parâmetros só com as 14 fotos de calibração e depois testa: 18 de 20, 90%, contra 75% da melhor regra antiga. No deixa-uma-de-fora, cada uma das 34 fotos é classificada por uma regra que nunca a viu: 34 de 34. E a separação entre as classes é larga, 41 pontos."

### Slide 12 · Limites e conclusão (A, ~1 min)
"Ainda há limites. O recorte é fixo: aqui a nuvem está abaixo da linha e a regra só vê azul. Pôr do sol está fora do escopo, mas a regra nova pelo menos se abstém. E 34 fotos é pouco. Próximos passos: detectar o horizonte, coletar mais fotos e comparar com uma rede neural. Para fechar: com três pistas simples, cor, brilho e textura, saímos de 75% para algo entre 90% e 100%, e cada decisão continua explicável. Obrigado! Perguntas?"

---

## Demonstração ao vivo (opcional, ~1 min, B)

Com o ambiente ativado, na raiz do projeto:

```bash
python main.py refs/teste/ceu_limpo/ceu_limpo_3.jpg --rule all --diagnostics diagnostics/demo/nevoa
python main.py refs/teste/ceu_encoberto/ceu_encoberto_4.jpg --rule all --diagnostics diagnostics/demo/tempestade
python evaluate.py
```

O primeiro comando mostra a mesma foto com névoa: `blue: ceu_encoberto`, `combined: indeterminado`, `open: ceu_limpo`. Abra `diagnostics/demo/nevoa/mascara_ceu_aberto.png` para mostrar a máscara quase toda branca. O `evaluate.py` imprime as três matrizes de confusão.

> No PowerShell, se aparecerem caracteres estranhos nos acentos, rode antes: `$env:PYTHONIOENCODING="utf-8"`.

---

## Perguntas prováveis da banca

**"Por que não usaram deep learning?"**
O objetivo era ter regras explicáveis: dá para abrir a máscara e ver por que o programa decidiu. Com 34 fotos rotuladas, uma rede neural também teria pouco dado para treinar. Fica como próximo passo para comparar.

**"100% não é bom demais?"**
É o número otimista, porque a regra foi pensada depois de vermos os erros do teste. Por isso mostramos também os 90% do protocolo estrito e os 34/34 do leave-one-out. Com mais fotos, esperamos algo entre esses valores.

**"Por que 7×7 e desvio 4?"**
São parâmetros escolhidos numa busca em grade. O ponto principal é que muitas combinações vizinhas também separam bem as classes, e a folga é de 41 pontos. O resultado não depende de um número exato.

**"Por que reduzir a foto para 320 px?"**
A textura depende da escala. Numa foto enorme, uma janela 7×7 cobre um pedaço minúsculo da nuvem e tudo parece liso. Reduzindo antes, a janela cobre sempre a mesma fração da cena.

**"E se tiver um prédio no terço de cima?"**
Prédios e reflexos podem enganar as máscaras. Está nos casos difíceis. A solução seria detectar a região do céu ou o horizonte em vez de usar um recorte fixo.

**"O que é o indeterminado?"**
Não é uma terceira classe de tempo. É a regra dizendo "não tenho pistas suficientes". Na regra nova, isso acontece quando o céu aberto fica entre 30% e 50%, como no crepúsculo e na vista aérea dos casos difíceis.
