## 0. 수정 전반의 큰 그림 (논리 보강의 한 줄 요약)

원본은 *"splice/cCRE가 일찍 settle한다 → 따라서 biological grammar"* 라는 단순한 내러티브에 가까웠으나, 이는 §3.2의 flank-shuffle 결과(*shuffle하면 더 일찍 settle*)와 표면적으로 충돌한다. 수정본은 다음과 같이 논리 구조를 재배치했다.

1. **§2 Framework** 도입부에서 `c(t)`의 양면성을 \"feature, not flaw\"로 **선언**한다 — 더 낮은 `c(t)`는 (a) 더 강한 biological signal 또는 (b) 더 단순한 surrounding context 둘 다에 의해 발생할 수 있다.
2. **§3.2 Motif/flank** 실험은 이 양면성을 \"활용한 dissociation 실험\"으로 재정의된다: motif-edit는 `c(t)`를 깊게(deepen), flank-shuffle는 얕게(lift) 만든다 — **두 방향 모두**가 \"flanking grammar requires deeper integration\"의 증거다.
3. **§3.3 Variant**에서 synonymous variant가 가장 깊은 layer에서 peak하는 것은 \"protein-semantic 정보가 깊은 layer에 consolidate된다\"는 해석으로 보강된다.
4. **§4 Discussion**에서 \"depth signature is bidirectional\"임을 명시 — 이로써 abstract부터 결론까지 일관된 논리 골격이 만들어진다.

결과적으로 \"Biological Grammar\"라는 메시지는 **약화되지 않고 오히려 더 정밀해진다**: \"grammar\"는 단순히 \"motif\"가 아니라 \"motif + flanking context의 통합\"임을 양방향 perturbation이 입증한다.

---

## 1. 즉시 수정 항목 (correction.md K절 1-6)

### C1. Dunn–Bonferroni 인용 오류 (L214)

- **변경 전**: `Adjacent-pair Dunn--Bonferroni tests~\cite{mann1947whitney,benjamini1995fdr}`
- **변경 후**: `Adjacent-pair Dunn tests with Bonferroni correction~\cite{dunn1964multiple}`
- **근거**: `mann1947whitney`는 Mann-Whitney U test, `benjamini1995fdr`는 BH FDR procedure로 Dunn 검정 인용으로 부적절. Dunn (1964) "Multiple comparisons using rank sums"이 정확한 인용. Bonferroni는 통상 인용 생략.


### B1. Spearman ρ ≤ 0.15 거짓 주장 정합화 (L200, L259, App C)

- **문제**: 본문 \"$|\rho|\leq 0.15$\"는 App C Table 3의 splice acceptor $\rho=-0.152$, intron $\rho=-0.108$과 모순.
- **변경**: 임계값을 `|ρ|≤0.16`으로 일관 조정하고 \"the largest non-UTR coupling is splice acceptor at $|\rho|=0.152$, with intron at $|\rho|=0.108$\"를 부록에 명시.



### B5. ℓ=30 best-cos tap 모순 해결 (App C Table 5)

- **문제**: AUROC $0.729$가 \"interpretively distinct하지 않다\"고 §App A에서 단정한 block 30에서 나오는 모순. 게다가 Table 5에 ℓ=30, ℓ=31이 같은 값으로 따로 보고됨(B5의 \"같은 텐서 두 번 보고\" 문제).
- **변경**:
  - Although block~30 is the rotation step that aligns the representation with $\hnorm$, it remains highly informative for downstream tasks. Indeed, in our variant pathogenicity probing (\S\ref{app:auroc-detail}), the best single-layer AUROC for the cosine lens occurs precisely at $\ell=30$ ($0.729$). This is expected: once the residual stream has rotated into the final-norm frame, it carries maximal signal for classification. We therefore retain $L^\star=29$ as the deepest \emph{interpretively distinct} tap for the settling-depth metric, while acknowledging that the post-rotation representation ($\ell=30$) is optimal for linear probing. 와 같은 내용을 추가함으로써 “우리가 일부러 L^*=29을 선택한 이유”와 “AUROC에서 ℓ=30이 좋은 이유”를 명확히 구분하면서, 결과의 일관성을 유지할 수 있게 함.

---

## 2. Reviewer 방어 강화 항목 (correction.md K절 7-9)

### A1. Settling-depth 양면성을 §2 도입부에서 미리 선언

- **이 선언이 §3.2와 결합되는 방식**: §3.2의 두 perturbation은 양면성을 **활용**한 dissociation 실험으로 재서술됨. \"two perturbations push c̄ in opposite directions --- exactly the asymmetry expected if the depth signature is reading out grammar integration, not motif strength alone.\"


### G3. Composition control 부재의 limitation 강화

- **변경 전 (§4)**: \"k-mer rarity, GC content, and dinucleotide composition are natural next composition-matched controls\"  — future work로 미루는 톤.
- **변경 후**: limitation을 reviewer가 가장 먼저 의심할 confounder로 명시.
- **Conclusion §5에도 반영**: \"composition-matched negative controls\" 한 줄을 future-work 목록의 두 번째 항목으로 승격.

---

## 3. 문체 / 통일성 보정 (correction.md K절 10-12)

### E7. 비표준 용어 \"shallows\" 교체

- 본문 §3.2 (i)/(ii) 병렬 구조 정비:
  - 변경 전: \"shallows $\bar c$ by $3.18$ layers\"
  - 변경 후: \"**lifts** $\bar c$ to a shallower value by $3.18$ layers\"
- App.~\ref{app:motif-flank} 본문 및 Table~\ref{tab:motif-flank} 캡션도 동일 변경.
- (i)와 (ii)의 동사형 평행 구조 일치: 양쪽 모두 gerund(\"Replacing...deepens\", \"Dinucleotide-shuffling...lifts\").

### B2. Cohen's d 본문 vs.\ 표 불일치 해소 (L207 vs Table 8 L829)

- 변경 전: 본문 \"$d=-0.09$\", 표 \"$d=-0.086$\"
- 변경 후: 본문도 \"$d=-0.086$\"로 통일 (표를 정밀 값으로 두고 본문도 같은 정밀도로 일치).

### E10. Section heading 대소문자 통일 (Title Case)

- 모든 본문 section과 appendix subsection을 **Title Case**로 통일.
  - \"Discussion and limitations\" → \"Discussion and Limitations\"
  - \"Method details\" → \"Method Details\"
  - \"Reproducibility\" 유지 (단어 1개로 변화 없음)
  - 모든 appendix subsection (\"Hyperparameter sensitivity\" → \"Hyperparameter Sensitivity\", \"Entropy decoupling per context\" → \"Entropy Decoupling per Context\" 등) 일관 적용.

### 표/그림 캡션 정보 보강

- **F3 (Fig.~\ref{fig:auroc})**: (c) 캡션에 \"best single tap is $\ell=29$ for JSD and $\ell=30$ for cosine (the latter is the post-norm rotation block, not the canonical interpretive tap)\" 명시.

---

## 4. 추가로 함께 적용한 작은 보정

### J1. 단위 명료화 (L294)

- 변경 전: \"$6\,$kb $\times$ 100 windows\"
- 변경 후: \"100 windows of 6\,kb each\"

### J2. \"paired DeLong test\" 표준 표기 (L226)

- 변경 전: \"DeLong~\\cite{delong1988comparing} paired comparisons\"
- 변경 후: \"Paired DeLong tests~\\cite{delong1988comparing}\"


### J4. Position 데이터 개수 정합화 (B3)

- 본문/Table 모두 $n=719{,}000$ analysed positions로 통일하고, 그 차이의 사유(window edge에서의 truncated logits)를 App.~\ref{app:entropy-decoup}에 한 줄로 명시.


### J10. Tuned-lens 임계값 98% 정당화 (G6)

- App.~\ref{app:tuned-lens} 본문: \"the 98\\% threshold is descriptive of the empirical recovery distribution rather than a pre-registered cut-off\" — reverse-engineered cut-off의 인상을 제거.


### J13. Correlational vs.\ Interventional 분리 (E9)

- 변경 전 (§4): \"Settling depth is a correlational readout of representational dynamics; ...\"
- 변경 후: \"The genome-wide context-level findings (§3.1) are correlational; the motif/flank perturbations (§3.2) are interventional but limited to a single locus class.\" — §3.2가 명확히 interventional임을 인정.

### J14. Conclusion 메시지 정렬

- Conclusion 본문이 \"depth signature is bidirectional\" + \"detection plus context integration\" + \"synonymous variants peak at the deepest layers\"의 세 메시지를 명시적으로 거론하도록 재작성. Abstract → §2 → §3 → §4 → §5의 메시지 일관성 확보.



