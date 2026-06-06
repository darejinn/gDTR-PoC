# `gdtr_paper_ICML.tex` 수정 내역 — v3 → v4 (`ICML_0509_v4/`)

본 문서는 [`correction.md`](correction.md)의 지시 사항에 따라
`/Users/yoonjincho/Project/ICML/ICML_0429_v3/gdtr_paper_ICML.tex`(=v11.6 시점의 v3 원고)를 받아
`/Users/yoonjincho/Project/ICML/ICML_0509_v4/gdtr_paper_ICML.tex`로 정리한 모든 변경 사항을
정리한 것이다. 각 항목은 (1) 원본 위치, (2) 변경 전/후 텍스트, (3) 한글 근거 순으로
기술한다. 라인 번호는 **원본 v3 `gdtr_paper_ICML.tex`** 기준이다 (수정본에서는
§2의 새 문단·§App C의 새 문단이 추가되어 일부가 밀렸다).

---

## A. 논리 골격 보강 (correction §0, §2 도입부 + §3.2 + §3.3 + §4 + §5)

수정 전 원고는 *"splice/cCRE가 일찍 settle한다 → 따라서 biological grammar"* 라는
단방향 내러티브에 가까워, §3.2의 flank-shuffle 결과(*shuffle하면 더 일찍 settle*)와
표면적으로 충돌했다. 수정본은 "settling depth가 양면적(bidirectional) readout"임을
§2에서 미리 선언하고, §3.2를 그 양면성을 활용한 dissociation 실험으로 재서술하며,
§4·§5 결론까지 같은 메시지를 일관되게 흐르게 했다. 다음의 다섯 곳을 손봤다.

### A1. §2 Framework — `Settling depth is two-sided` 단락 신설 (원본 L169 직후 삽입)

- **변경 전**: 없음 (Eq. ~\ref{eq:settling} 직후 바로 "Evo 2's idle final block" paragraph로 넘어감).
- **변경 후**: 다음 paragraph 신설 후 "Evo 2's idle final block"로 연결.
  ```
  \paragraph{Settling depth is two-sided.} A lower $c(t)$ does not by itself imply a stronger biological signal. A token can settle early because (a) its representation is constrained by a biological grammar that the model commits to early, \emph{or} (b) its surrounding context is simpler, so the running-min envelope reaches $\gamma_{\cos}$ with little integration. We treat this two-sidedness as a feature of the metric rather than a flaw: the perturbation experiments in \S\ref{sec:motif-controls} are designed to push $c(t)$ in opposite directions, separately stressing motif detection and flanking-grammar integration. Throughout the paper we therefore interpret depth signatures as \emph{bidirectional} --- both directions of movement carry information about how the model integrates biological grammar.
  ```
- **근거**: settling depth가 "강한 biological signal에 의해 깊은 commit으로 일찍 안정화"
  또는 "단순한 surrounding context로 인한 얕은 안정화" 양쪽 모두에서 낮아질 수 있다는
  양면성을 §2에서 미리 선언해야, §3.2의 motif-edit (deepens) ↔ flank-shuffle (lifts)
  결과가 모순이 아니라 "두 perturbation이 반대 방향으로 밀어내는 dissociation 실험"으로
  자연스럽게 읽힌다. reviewer가 가장 먼저 의심할 "왜 shuffle하면 더 얕아지는가?"라는
  질문을 framework 단계에서 미리 무력화한다.

### A2. §3.2 Motif/flank — "two-sidedness exploitation" framing + 양방향 메시지 명시 (원본 L207)

- **변경 전**:
  > Settling depth is not simply a meter of motif intrinsic strength. We dissociate central motif detection from flanking-context integration on $1{,}000$ canonical GT-AG donors ...
  > ... (ii) Dinucleotide-shuffling the $\pm 100$~bp flank while preserving the central GT \emph{shallows} $\bar c$ by $3.18$ layers ($d=+0.51$, $p=4.1\times10^{-59}$): the isolated GT becomes easier to stabilise, whereas the real donor context requires deeper flanking-grammar integration. The within-splice motif breakdown in App.~\ref{app:splice-canonical} follows the same cautionary logic: rare or non-canonical motifs can settle earlier than canonical GC-AG, so $c(t)$ should be interpreted as detection plus context integration, not as motif strength alone.
- **변경 후**:
  > Settling depth is not simply a meter of motif intrinsic strength. **We exploit its two-sided behaviour (\S\ref{sec:framework}) in a dissociation experiment** on $1{,}000$ canonical GT-AG donors ...
  > ... (ii) Dinucleotide-shuffling the $\pm 100$~bp flank while preserving the central GT **\emph{lifts} $\bar c$ to a shallower value** by $3.18$ layers ($d=+0.51$, $p=4.1\times10^{-59}$): the isolated GT becomes easier to stabilise, whereas the real donor context requires deeper flanking-grammar integration. **The two perturbations push $\bar c$ in opposite directions --- exactly the asymmetry expected if the depth signature is reading out grammar integration rather than motif strength alone.** The within-splice motif breakdown in App.~\ref{app:splice-canonical} follows the same cautionary logic: rare or non-canonical motifs can settle earlier than canonical GC-AG, so $c(t)$ should be interpreted as detection plus context integration.
- **근거**: §2 도입부의 양면성 선언과 §3.2 실험을 명시적으로 연결(A1과 호응); motif-edit과
  flank-shuffle가 "같은 결론을 양쪽에서 입증"하는 것이 아니라 "비대칭(asymmetry) 자체가
  grammar integration을 읽는다는 증거"라는 한 단계 더 정밀한 메시지로 강화.

### A3. §3.3 Variant — synonymous-deepest 해석 보강 (원본 L214)

- **변경 전**:
  > The interpretable result is therefore a population-level depth shift from early-truncating consequences toward missense and splice disruptions.
- **변경 후**:
  > The interpretable result is a population-level depth shift from early-truncating consequences (intron, frameshift, nonsense) toward missense and splice disruptions, **and onward to synonymous substitutions, which peak at the deepest layers --- consistent with protein-semantic information consolidating in late layers, where coding-frame--dependent disruptions register earlier and identity-preserving substitutions register only after codon-level meaning has been integrated.**
- **근거**: 원본은 "intron < frameshift < nonsense < missense ≈ canonical splice < synonymous"
  순서를 사실로만 제시하고 멈췄다. 가장 흥미로운 **synonymous 변이가 가장 깊은 layer에서
  peak한다**는 사실에 mechanistic 해석을 붙이지 않으면 reviewer가 자연스럽게 "why?"를
  묻게 된다. "protein-semantic information consolidates at deeper layers" 해석으로
  단조 증가 순서에 "frame-disruption first, semantics last"라는 생물학적 의미를 부여하고
  §1의 "layer hierarchy" 메시지와 정합화한다.

### A4. §4 Discussion — "bidirectional" 명시 + (i) interventional 분리 + (iii) composition confounder 강화 (원본 L259)

- **변경 전**:
  > Four scope conditions frame the interpretation. *(i)* Settling depth is a correlational readout of representational dynamics; ... *(iii)* The current entropy control isolates next-token uncertainty; $k$-mer rarity, GC content, and dinucleotide composition are natural next composition-matched controls. ...
- **변경 후**:
  > **The depth signature is \emph{bidirectional}: motif edits deepen $\bar c$ while flank-shuffles lift it, and both directions are evidence that $c(t)$ reads out grammar integration rather than motif strength alone (\S\ref{sec:framework}, \S\ref{sec:motif-controls}).** Four scope conditions then frame the interpretation. *(i)* **The genome-wide context-level findings (\S\ref{sec:shallowness}) are correlational readouts of representational dynamics, while the motif/flank perturbations (\S\ref{sec:motif-controls}) are interventional but limited to a single locus class**; establishing causal circuits at scale will require broader interventional follow-up (e.g.\ activation patching, sparse-dictionary edits). *(ii)* ... vs.\ $|\rho|\!\le\!0.16$ elsewhere ... *(iii)* The current entropy control isolates next-token uncertainty **but does not control for sequence composition: $k$-mer rarity, GC content, and dinucleotide composition are the most plausible alternative explanation a reviewer would raise for the depth ordering, and we explicitly flag this as the leading composition confounder pending composition-matched negative controls.** ...
- **근거**: (1) "bidirectional" 메시지가 abstract→§2→§3→§4→§5에 한 단어로 일관되게 흐르도록
  §4에서도 명시. (2) (i) 항목은 J13 지적대로 "all correlational"이 아니라 "§3.1은 correlational,
  §3.2는 interventional but locus-restricted"임을 정직하게 분리. (3) (iii) composition
  confounder를 "natural next ... controls"의 future-work 톤에서 "the leading composition
  confounder" + "pending composition-matched negative controls"로 강화.

### A5. §5 Conclusion — 세 메시지 (bidirectional / detection+context / synonymous-deepest) 명시 + composition control 우선순위 승격 (원본 L268)

- **변경 후**:
  > \gDTR{} establishes a training-free, layer-resolved interpretability axis ... **Three findings define its message.** *(1)* **The depth signature is \emph{bidirectional}** ... *(2)* At the genome scale, splice sites and enhancer-like cCREs stabilise earlier ... so the readout reflects **\emph{detection plus context integration}**, not motif detection in isolation. *(3)* Variant-induced $\DDcos$ peaks at consequence-specific layers, **with synonymous substitutions peaking at the deepest layers, consistent with protein-semantic information consolidating in late layers**. Whole-genome scaling, **composition-matched negative controls ($k$-mer rarity, GC content, dinucleotide composition)**, and integration with sparse-dictionary and causal-edit methods are left to future work.
- **근거**: J14 지적대로 결론이 abstract·§1·§3·§4의 세 핵심 메시지(bidirectional / detection+context / synonymous-deepest)를 (1)(2)(3) 번호 형식으로 명시적으로 거론. composition control이 future-work 목록의 두 번째 항목으로 승격되며 어떤 composition을 통제해야 하는지(k-mer rarity, GC content, dinucleotide composition)까지 명시.

---

## B. 즉시 수정해야 할 사실/인용 오류 (correction §1)

### B1. Dunn–Bonferroni 인용 오류 (C1; 원본 L214)

- **변경 전**: `Adjacent-pair Dunn--Bonferroni tests~\cite{mann1947whitney,benjamini1995fdr}`
- **변경 후**: `Adjacent-pair Dunn tests with Bonferroni correction~\cite{dunn1964multiple}`
- **근거**: `mann1947whitney`는 Mann-Whitney U test, `benjamini1995fdr`는 Benjamini-Hochberg FDR procedure 인용으로, Dunn 검정에는 둘 다 잘못된 인용이다. Dunn (1964) "Multiple comparisons using rank sums"이 정확한 출처. v3 폴더의 `gdtr_paper.bib`에는 **`dunn1964multiple` 항목이 누락**되어 있어 v4에서 마스터 bib(`/Users/yoonjincho/Project/ICML/gdtr_paper.bib`)의 항목을 그대로 추가했다.

### B2. Cohen's d 본문 vs. 표 불일치 해소 (B2; 원본 L207)

- **변경 전**: 본문 "Cohen's $d=-0.09$"
- **변경 후**: 본문 "Cohen's $d=-0.086$"
- **근거**: §App D Table~\ref{tab:motif-flank}에는 동일 GT→AA 결과가 $d=-0.086$으로 보고되어 있다. 표를 정밀 값으로 두고 본문도 같은 정밀도로 통일.

### B3. Spearman ρ 임계값 0.15 → 0.16 정합화 (B1; 원본 L200, L202, L259, L382)

- **변경 전 (네 군데 동일)**: `$|\rho|\!\le\!0.15$`
- **변경 후 (네 군데 동일)**: `$|\rho|\!\le\!0.16$`
- **추가 (App C 본문 + 표 캡션)**: "The largest non-UTR couplings are splice acceptor at $|\rho|=0.152$ and intron at $|\rho|=0.108$"를 부록 본문 + 표 캡션에 명시.
- **근거**: §App C Table~\ref{tab:entropy-decoup}에는 splice acceptor $\rho=-0.152$, intron $\rho=-0.108$이 보고되어 있어, 본문의 "$|\rho|\le 0.15$"는 자기 부록 표와 직접 모순된다(특히 splice acceptor 0.152 > 0.15). 임계값을 0.16으로 한 칸 올려 표·본문·discussion·appendix 네 곳을 동시에 정합화.

### B4. Position 데이터 개수 정합화 (J4; 원본 L202, L378-382, L391)

- **변경 전**: 본문/부록 본문 "720,000 positions", 표 캡션 "720,000 positions". 그러나 표 본문에는 "overall 719,000"으로 보고됨.
- **변경 후**: 본문·부록 본문·표 캡션 모두 "719{,}000 analysed positions"로 통일하고, 차이의 사유("the $1{,}000$ shortfall reflects truncated logits at window edges where the causal context is incomplete")를 §App C 본문에 한 줄 명시 + 표 캡션에도 짧게 명시.
- **근거**: 본문·캡션의 "720,000"과 표 row의 "719,000"이 직접 충돌. causal LM의 window 끝 부분에서는 forward 문맥이 부족해 실제 분석 가능한 position은 1,000개가 적다는 사실을 정직하게 설명.

### B5. ℓ=30 best-cos tap 모순 해결 (B5; App C Table 5 ~ Fig. 4 caption)

- **추가**: §App C "Per-layer ablation" paragraph 직후에 새 paragraph **"Why $L^\star=29$, not $\ell=30$, is the canonical tap"** 신설. 핵심 골자: settling-depth metric (h_ℓ vs h_norm 비교)에서는 ℓ=30이 saturate해 의미가 없지만, linear probing에서는 ℓ=30이 post-rotation frame에 들어가 있어 가장 분류 가능한 feature가 된다는 두 역할의 일관성을 명시. 추가로 ℓ=31의 동일 0.729는 block 31이 residual passthrough이기 때문임을 표 idle-block 인용으로 차단.

### B6. Fig. ~\ref{fig:auroc} 캡션 정보 보강 (B5; 원본 L693-698)

- **변경 전**: "best single tap is $\ell=29$ for JSD; the 32-d vector beats it by $+0.05$ to $+0.12$."
- **변경 후**: "best single tap is $\ell=29$ for JSD and $\ell=30$ for cosine (the latter is the post-norm rotation block, not the canonical interpretive tap; see App.~\ref{app:architectural-quirk}); the 32-d vector beats either by $+0.05$ to $+0.12$."
- **근거**: B5와 동일 — 캡션에서도 두 lens의 best tap이 다르다는 것과 그것이 architectural quirk와 일관됨을 명시.

---

## C. 문체/통일성 보정 (correction §3)

### C1. 비표준 용어 "shallows" 제거 (E7) — 본문 + 부록 본문 + 표 캡션 3곳

- §3.2 본문: `\emph{shallows} $\bar c$ by $3.18$ layers` → `\emph{lifts} $\bar c$ to a shallower value by $3.18$ layers`
- §App D 본문: `dinucleotide-shuffling the $\pm 100$\,bp flank shallows $\bar c$ by $3.18$ layers` → `... lifts $\bar c$ to a shallower value by $3.18$ layers`
- §App D Table 캡션: `shuffling the flank (while keeping GT) \emph{shallows} $\bar c$ by 3.18 layers` → `... \emph{lifts} $\bar c$ to a shallower value by 3.18 layers`
- §3.2 (i)·(ii) 동사형 평행 구조 정리: 양쪽 모두 동명사형으로 "Replacing ... deepens", "Dinucleotide-shuffling ... lifts".
- **근거**: "to shallow"는 일반 영어에서 동사로 거의 쓰이지 않는다. "lifts X to a shallower value"로 (a) 표준 영어, (b) 방향(올라간다=얕아진다) 명시, (c) "deepens"와 형식적 평행 유지가 모두 해결된다.

### C2. Section / Subsection heading Title Case 통일 (E10)

| 위치 | 변경 전 | 변경 후 |
| --- | --- | --- |
| §3.1 | Splice and enhancer annotations settle early | **Splice and Enhancer Annotations Settle Early** |
| §3.2 | Motif edits separate detection from flanking context | **Motif Edits Separate Detection from Flanking Context** |
| §3.3 | Variant disruptions peak at consequence-specific layers | **Variant Disruptions Peak at Consequence-Specific Layers** |
| §3.4 | Robustness and tokenisation limits | **Robustness and Tokenisation Limits** |
| §4 | Discussion and limitations | **Discussion and Limitations** |
| §App A | Method details | **Method Details** |
| §App A.1 | Architectural quirk handling: Evo 2's idle last block | **Architectural Quirk Handling: Evo 2's Idle Last Block** |
| §App A.2 | Hyperparameter sensitivity | **Hyperparameter Sensitivity** |
| §App A.3 | Entropy decoupling per context | **Entropy Decoupling per Context** |
| §App A.4 | Tuned-lens recovery across all 32 layers | **Tuned-Lens Recovery Across All 32 Layers** |
| §App B | Cross-architecture replication: scope, granularity, two-tier structure | **Cross-Architecture Replication: Scope, Granularity, Two-Tier Structure** |
| §App C | Variant pathogenicity: AUROC summary, per-layer ablation, and panels | **Variant Pathogenicity: AUROC Summary, Per-Layer Ablation, and Panels** |
| §App D | Splice anatomy beyond the headline contexts | **Splice Anatomy Beyond the Headline Contexts** |
| §App D.1 | Positional fine-profile around donor / acceptor | **Positional Fine-Profile Around Donor / Acceptor** |
| §App D.2 | Canonical vs. non-canonical splice motif breakdown | **Canonical vs.\ Non-Canonical Splice Motif Breakdown** |
| §App D.3 | Motif and flank perturbation summary | **Motif and Flank Perturbation Summary** |
| §1 / §2 / §3 / §5 / §App E | (이미 Title Case 또는 단일 단어) | 변경 없음 |

- **근거**: 동일 논문 안의 heading 일관성. v3에는 §3.4와 §App A.4 같은 sentence-case heading과 §3 같은 title-case heading이 혼재.

---

## D. 추가 작은 보정 (correction §4)

### D1. 단위 명료화 (J1; §App A.1, 원본 L294)

- **변경 전**: `(6\,kb $\times$ 100 windows)`
- **변경 후**: `(100 windows of 6\,kb each)`

### D2. "paired DeLong test" 표준 표기 (J2; §3.3, 원본 L226 + Fig.~\ref{fig:auroc} 캡션)

- §3.3 본문: `DeLong~\cite{delong1988comparing} paired comparisons` → `Paired DeLong tests~\cite{delong1988comparing}`
- Fig.~\ref{fig:auroc} 캡션 (b): `DeLong paired comparisons:` → `Paired DeLong tests:`
- App C `\paragraph{ROC, DeLong, ...}` 본문: `the DeLong paired comparisons (b) show that ...` → `the Paired DeLong tests in (b) show that ...`

### D3. Tuned-lens 98% 임계값 "descriptive" 정당화 (J10; §App A.4)

- **추가**: "The $98\%$ threshold is descriptive of the empirical recovery distribution rather than a pre-registered cut-off: it summarises where the bulk of the per-layer recovery scores sit, not a criterion that the framework is required to clear at inference (the framework is training-free and uses no affine weights when computing $c(t)$)."

---

## E. v4 추가 housekeeping (correction.md에는 없지만 함께 적용)

### E1. Bib에 `dunn1964multiple` 추가

- v3 폴더 `gdtr_paper.bib`에는 `dunn1964multiple` 항목이 **없었다**(마스터 bib `/Users/yoonjincho/Project/ICML/gdtr_paper.bib`에는 있음). B1의 인용 키 교체가 가능하려면 v4 bib에도 같은 항목을 추가해야 하므로 마스터 bib에서 그대로 가져왔다.

### E2. 어펜딕스 피규어 파일명 정리 (생성성-있는 이름으로)

| 변경 전 | 변경 후 | 사유 |
| --- | --- | --- |
| `figures/fig_appendix_b.png` | `figures/fig_cross_arch_context.png` | 라벨 `fig:cross-arch-context`와 직결 |
| `figures/fig_appendix_b_local.{png,pdf}` | `figures/fig_cross_arch_context_local.{png,pdf}` | 동일 |
| `scripts/regen_fig_appendix_b_local.py` | `scripts/regen_fig_cross_arch_context_local.py` | 동일 |

본문 `\includegraphics`, `figures/README.md`, `scripts/README.md`,
`MANIFEST.md`, `README.md`의 모든 참조도 함께 갱신했다. 다른 figure 파일은
이미 의미 있는 이름을 갖고 있어 변경하지 않았다.

### E3. 매니페스트(`MANIFEST.md`) 강화

각 figure에 대해 (1) tex label/번호, (2) tex include 경로, (3) 출력 파일,
(4) local/remote regen 스크립트, (5) build domain (L/R/B), (6) self-test/sync
constraint, (7) 입력 데이터 한 줄 표를 단일 카드 형태로 정리. 표 매니페스트에는
v3에서 누락되었던 `tab:entropy-decoup`, `tab:splice-fine`, `tab:splice-canonical`,
`tab:motif-flank` 행을 추가.

### E4. README v4 변경 로그 추가

`README.md` "What changed in v4" 섹션을 신설하고, A/B/C/D/E 변경을 한눈에 보이도록 정리.

---

## F. 변경하지 않은 항목

다음 항목은 `correction.md`에 포함되었으나, 현재 v3 원고의 해당 줄/항목이 이미
올바른 형태로 작성되어 있어 변경할 필요가 없었다.

- **App C Table 5의 ℓ=30, ℓ=31 같은 값 행**: 이미 ℓ=31 행이 "$0.729$ ($=h_{30}$)"으로
  표기되어 "같은 텐서임을 보고"하고 있어, 표 자체는 손대지 않았다. 대신 B5
  paragraph에서 그 "중복"의 의미를 한 번 더 짚어 reviewer 의문을 차단했다.
- **§1 "Introduction" / §2 "The gDTR Framework" / §3 "Layer-wise Biological Grammar" /
  §5 "Conclusion" / §App E "Reproducibility"** heading: 이미 Title Case 또는 단일
  단어로 일관성에 부합.
- **`mann1947whitney`, `benjamini1995fdr` bib 항목**: B1의 인용 위치에서만 제거되었고
  bib 자체는 그대로 둔다(다른 곳에서 사용될 수 있는 안전한 reference 자료). LaTeX는
  cited되지 않은 항목을 최종 PDF의 References에 포함하지 않는다.

---

## G. 산출물 요약

- **수정된 tex 파일**: `/Users/yoonjincho/Project/ICML/ICML_0509_v4/gdtr_paper_ICML.tex`
- **갱신된 bib 파일**: `/Users/yoonjincho/Project/ICML/ICML_0509_v4/gdtr_paper.bib` (`dunn1964multiple` 추가)
- **본 문서 (수정 내역)**: `/Users/yoonjincho/Project/ICML/ICML_0509_v4/corrections_applied.md`
- **레퍼런스/라벨 무결성**: 모든 `\cite`는 `gdtr_paper.bib`에 정의되어 있고, 모든 `\ref`는 동일 문서 내 `\label`로 해소됨.
- **누락 텍스트 검증**: "shallows" 동사, "$|\rho|\le 0.15$" 임계값, "720,000",
  "Dunn--Bonferroni", "mann1947whitney + benjamini1995fdr 동반 인용",
  "6 kb × 100 windows", "Cohen's d=-0.09" 모두 0 hit (`grep` 검증 통과).

수정본은 abstract → §2 (양면성 선언) → §3.2 (양방향 dissociation) → §3.3
(synonymous-deepest 해석) → §4 (bidirectional 명시 + interventional 정직 인정) →
§5 (세 메시지 명시 + composition control 승격) 의 한 줄짜리 논리 골격을 끝까지
유지하면서, B1·B2·B3·B4·B5·B6 사실/인용 오류와 "shallows"·sentence case 같은
문체 결함을 모두 해소했다.
