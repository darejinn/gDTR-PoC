# Phase 1 Execution Plan — gDTR on Evo 2 7B (DigitalOcean H200)

**Project**: Genomic Deep-Thinking Ratio (gDTR)
**Phase**: 1 — Method calibration on Evo 2 7B (server-specific execution rendering)
**Document version**: 2026-04-26 v1.0
**Status**: Server-specific executable plan derived from `PHASE1_DECISIONS.md` (locked)
**Predecessors**: `PHASE1_DECISIONS.md`, `PHASE0_FINDINGS.md`, `phase0_design.md`, `260426_연구계획서.docx`

---

## 0. Status (2026-04-26)

### 0.1 Predecessor documents (binding)

본 문서는 다음 lock된 입력의 **server-specific 실행 매뉴얼**이다. 본 문서는 임계값을 새로 설정하지 않으며, `PHASE1_DECISIONS.md`의 모든 gate threshold·hyperparameter starting point·decision tree를 그대로 차용한다.

| 문서 | 역할 | 상태 |
|---|---|---|
| `PHASE1_DECISIONS.md` v1.0 (2026-04-26) | Phase 1 method spec, 14-day schedule, gates A_evo/B_evo/C_evo, HP starting point, decision tree, risk matrix, reproducibility | LOCKED |
| `PHASE0_FINDINGS.md` v1.0 (2026-04-26) | F1/F2/F3 + L7 D1-D5 mechanistic decomposition, E1/E2/E5 extension 결과 | LOCKED |
| `phase0_design.md` v1.0 (2026-04-26) | Phase 0 사전등록 design + Appendix C model spec corrections (5건) | LOCKED |
| `260426_연구계획서.docx` | 연구 전체 계획서 (학회 제출본). PHASE1_DECISIONS.md가 이를 derive | REFERENCE |

### 0.2 본 문서가 추가하는 것

`PHASE1_DECISIONS.md`가 *what & why*라면, 본 문서는 *where & how* 이다:

- **Where**: DigitalOcean H200 server (host `ml-ai-ubuntu-gpu-h200x1-141gb-atl1`), Vortex 프레임워크 사용
- **How**: 각 sub-stage의 concrete shell command, mcp tool invocation, 산출 파일 경로, verification criterion
- **Code adaptation roadmap**: Phase 0 vessl `/root/gDTR-PoC/`로부터 DigitalOcean `/root/gDTR/`로의 reuse / rewrite / new file 분류
- **Parallel agent assignment**: 각 sub-stage가 background agent에 위임 가능한지 명시

### 0.3 Critical adaptation finding (2026-04-26 신규)

본 세션에서 다음 두 가지 사실이 추가로 lock되었으며, `PHASE1_DECISIONS.md`의 implementation assumption에 반영되어야 한다:

1. **Evo 2는 HF transformers가 아니라 Vortex 프레임워크를 사용한다.** Repo: `github.com/ArcInstitute/evo2`. 따라서 Phase 0의 HuggingFace `output_hidden_states=True` 패턴이 그대로 적용되지 않는다. 새 패턴:
   ```python
   from evo2 import Evo2
   model = Evo2('evo2_7b')
   outputs, embeddings = model(
       input_ids,
       return_embeddings=True,
       layer_names=['blocks.31.mlp.l3']  # 명시적 layer 이름 필요
   )
   ```
2. **Server는 H100 80GB이 아니라 H200 141GB이다.** Compute capability 동일(9.0)이라 코드 portable. 메모리 1.76× 더 크므로 batch 더 키우면 wall clock 단축 가능. PHASE1_DECISIONS.md §1.4의 "~120 hr" 추정은 그대로 가져가되, 실측 후 조정.

이 두 사실은 본 문서 §2 Architecture Adaptation에서 detail.

---

## 1. Server & Environment

### 1.1 Hardware

| 항목 | Value |
|---|---|
| Host | `ml-ai-ubuntu-gpu-h200x1-141gb-atl1` (DigitalOcean GPU droplet) |
| GPU | NVIDIA H200 SXM5 141GB (HBM3e) |
| Compute capability | 9.0 (Hopper) — H100과 동일 |
| CUDA driver | 13.1 |
| CUDA runtime (PyTorch wheel) | 12.1 (cu121) — 호환 |
| System RAM | 240 GB+ |
| Disk free | ~698 GB on `/` |
| OS | Ubuntu 22.04 LTS |

### 1.2 Project layout

```
/root/gDTR/                              ← Phase 1+ project root (DigitalOcean)
├── src/                                 ← Python source (모듈)
│   ├── constants.py                     [REWRITE] Evo 2 vocab, layer config, dtype
│   ├── model_loader.py                  [REWRITE] Vortex Evo2 loader
│   ├── logit_lens.py                    [REWRITE] return_embeddings + layer_names
│   ├── tuned_lens.py                    [NEW] last 2 blocks affine training
│   ├── block_type.py                    [NEW] attention vs hyena 분류
│   ├── calibration.py                   [NEW] region-adaptive q70 protocol
│   ├── gdtr.py                          [REUSE] settling depth, c_interp
│   ├── ur_gdtr.py                       [REUSE] cosine lens
│   ├── variant_delta.py                 [REUSE] ΔD vector + Δc_interp
│   ├── controls.py                      [REUSE] dinuc shuffle, GC matched
│   └── stats.py                         [REUSE] MWU + Cohen's d + Bonferroni
├── scripts/
│   ├── 00_smoke_evo2.py                 [NEW] Phase 1.0 smoke test
│   ├── 10_gate_a_evo.py                 [NEW] Phase 1.1 block-stratified Gate A_evo
│   ├── 12_train_tuned_lens.py           [NEW] Phase 1.2 affine training
│   ├── 13_gate_a_evo_tuned.py           [NEW] Phase 1.3 post-tuned Gate A_evo
│   ├── 14_calibration.py                [NEW] Phase 1.4 region-adaptive q70
│   ├── 15_hp_sweep.py                   [NEW] Phase 1.5 γ_cos × ρ reduced grid
│   ├── 16_chr22_gate_b.py               [NEW] Phase 1.6 chr22 Gate B_evo
│   └── 99_make_figures.py               [REUSE w/ patches] regenerate figures
├── data/
│   ├── GRCh38/                          (chr17.fa, chr22.fa)
│   ├── GENCODE/                         (gencode.v44.annotation.chr17_22.gff3.db)
│   ├── ClinVar/                         (clinvar_2026-04.vcf.gz)
│   └── DATA_VERSIONS.txt                ← MD5 / source URL / download date
├── results/
│   ├── runs/                            ← per-stage JSON sidecars
│   ├── tables/                          ← CSV tables
│   ├── figures/                         ← PDF / PNG figures
│   ├── caches/                          ← .npz hidden state caches
│   └── tuned_lens/                      ← A_31, A_32 checkpoint (≈120MB)
├── logs/                                ← stdout/stderr (`{stage}_{date}.log`)
├── venv/                                ← Python venv (PyTorch 2.3.1+cu121, evo2)
├── requirements_phase1.lock.txt         ← pip freeze 결과 lock
├── PHASE1_EXECUTION_PLAN.md             ← 본 문서 (server copy)
├── PHASE1_APPENDIX_C.md                 ← Phase 1.0 산출, Vortex API 정정 기록
└── PHASE1_DECISION.md                   ← Phase 1.7 최종 산출
```

### 1.3 Local mirror (Mac)

```
/Users/yoonjincho/Project/ICML/gDTR-Phase1/
├── ... (위와 동일 구조의 mirror; rsync로 동기화)
└── PHASE1_EXECUTION_PLAN.md             ← 본 문서 (local copy)
```

Mac은 로컬 편집 + git push 용도. 실제 forward pass와 학습은 DigitalOcean에서만 수행.

### 1.4 Software environment (locked at Phase 1.0)

```
Python              3.10.12
torch               2.3.1+cu121
transformers        4.49.0      (Phase 0 lock; Evo 2 호환성 Phase 1.0에서 재검증)
flash-attn          2.8.0.post2 (no-build-isolation 필수)
evo2                latest from arcinstitute/evo2 GitHub
biopython           1.87
pyfaidx             0.9.0.4
pyBigWig            0.3.25
gffutils            0.14
statannotations     0.7.2
numpy               1.24.4
pandas              2.2.2
scipy               1.14.0
scikit-learn        1.5.1
seaborn             0.13.2
matplotlib          3.9.2
ninja               (flash-attn 빌드용)
```

Phase 1.0 완료 시 `pip freeze > /root/gDTR/requirements_phase1.lock.txt`. 이후 stage는 이 lock으로부터 재현.

### 1.5 MCP tools used

| Tool | Purpose |
|---|---|
| `mcp__digitalocean-gpu__exec` | 일반 shell 명령 (forward, training, file ops) |
| `mcp__digitalocean-gpu__sudo-exec` | apt install, ulimit 등 root 작업 |

본 plan의 모든 server command는 `mcp__digitalocean-gpu__exec`로 실행됨을 가정하며, 명령 내 `cd /root/gDTR && ...` 패턴을 사용한다.

---

## 2. Critical Architecture Adaptation

### 2.1 Why Evo 2 ≠ HF transformers

`PHASE1_DECISIONS.md` §3.4 Gate priority section은 "Evo 2의 hidden state 추출 메커니즘이 다를 가능성"을 risk로 명시했다. 본 세션에서 이것이 확정되었다:

- Evo 2는 ArcInstitute의 **Vortex** framework로 구현됨 (`github.com/ArcInstitute/evo2`)
- HuggingFace `AutoModel.from_pretrained(...)` 패턴 적용 안 됨
- Hidden state 추출은 `output_hidden_states=True`가 아니라 **explicit layer names**를 통함

### 2.2 Vortex API quirks (Phase 0의 HF API와 다른 점)

| Aspect | Phase 0 (HF, HyenaDNA) | Phase 1 (Vortex, Evo 2) |
|---|---|---|
| Loading | `AutoModelForCausalLM.from_pretrained` | `from evo2 import Evo2; Evo2('evo2_7b')` |
| Hidden states | `model(..., output_hidden_states=True)` returns tuple | `model(..., return_embeddings=True, layer_names=[...])` returns dict |
| Layer naming | implicit indices | string keys e.g. `'blocks.31.mlp.l3'` |
| Tokenizer | `AutoTokenizer` from HF | Vortex 자체 tokenizer (single-nt + special) |
| Layer type access | `model.layers[i].__class__.__name__` | Vortex config의 block schedule (attention vs hyena) |
| ln_f position | `model.hyena.backbone.ln_f` | Vortex 별도 named module (Phase 1.0에서 catalog) |
| Forward에서 logits | `out.logits` | `outputs[0]` 또는 `outputs.logits` (Phase 1.0에서 확정) |

### 2.3 Code reuse audit

PHASE0 `/root/gDTR-PoC/` (vessl) → Phase 1 `/root/gDTR/` (DigitalOcean) 이전 매핑:

| File | Status | Reason |
|---|---|---|
| `src/gdtr.py` | **REUSE** as-is | running_min, c_discrete, c_interp 모두 model-agnostic |
| `src/ur_gdtr.py` | **REUSE** as-is | cosine distance는 hidden state shape만 받음 |
| `src/variant_delta.py` | **REUSE** as-is | ΔD vector·Δc_interp는 D array에 대해서만 작동 |
| `src/controls.py` | **REUSE** as-is | dinucleotide shuffle, GC-matched sampler — 시퀀스 레벨 |
| `src/stats.py` | **REUSE** as-is | MWU, Cohen's d, Bonferroni, partial Spearman |
| `src/constants.py` | **REWRITE** | Vocab=12 → 512, L=8 → 32, dtype, model name |
| `src/model_loader.py` | **REWRITE** | HF AutoModel → Vortex Evo2 |
| `src/logit_lens.py` | **REWRITE** | output_hidden_states 패턴 → return_embeddings + layer_names |
| `src/tuned_lens.py` | **NEW** | E5 prototype을 d=4096 scale로 확장 |
| `src/block_type.py` | **NEW** | attention vs hyena 분류기 (hybrid 전용) |
| `src/calibration.py` | **NEW** | region-adaptive q70 통합 module |

### 2.4 Phase 1.0 산출물

`PHASE1_APPENDIX_C.md`를 Phase 0 design Appendix C와 동일 형식으로 작성한다. 5+ 개 항목 예상:

- C.1 Hidden state 추출 정확한 API call signature
- C.2 Layer name schedule (attention/hyena alternation)
- C.3 Tokenizer BOS/EOS 처리
- C.4 lm_head tying status (storage + value 둘 다)
- C.5 Vocab size + token id range
- C.6 Forward dtype + autocast 동작
- C.7 Memory profile (6kb/32kb/256kb context)

본 산출은 Phase 1.1 이후 모든 sub-stage의 input.

---

## 3. Sub-stage Execution (14 days)

본 §은 PHASE1_DECISIONS.md §4.1 14-day schedule을 server command 수준으로 풀어낸다. 각 sub-stage 본격 detail은 §9 Sub-stage Detailed Specs를 참조.

| Sub-stage | Days | Goal | Decision rule from PHASE1_DECISIONS |
|---|---|---|---|
| 1.0 Smoke test | Day 1 (+1d for Vortex API discovery → ~Day 1-2) | API 정정, HF revision SHA lock, hidden state shape 확인 | smoke fail이면 patch & retry; OK면 1.1 진입 |
| 1.1 Gate A_evo untuned | Day 3-4 | Block-stratified per-layer M2; UR M2_global ≥ 0.50? | M2 ≥ 0.50 → 1.2 진입; 0.30-0.50 → tuned lens 더 절실; <0.30 → Evo 1 fallback 검토 |
| 1.2 Tuned lens training | Day 5 | A_31, A_32 affine 학습 (10-15 epochs) | Loss converges, identity init guarantees ≥ baseline |
| 1.3 Gate A_evo tuned | Day 6 | M2 회복 ≥ 0.85? | 회복 → 가설 (c) confirmed; 부분회복 → UR primary 유지; 없음 → mechanistic 추가 분석 |
| 1.4 Calibration | Day 7-8 | region-adaptive γ_cos_q70 protocol; 6kb/32kb/1M sensitivity | γ_cos region 변동 ±50% 이내면 OK; 초과 시 Bonferroni sensitivity |
| 1.5 HP sweep | Day 9 | reduced grid γ_cos × ρ | best (γ_cos, ρ) 선정 (Cohen's d 기준) |
| 1.6 Gate B_evo chr22 | Day 9-13 | ~16,000 windows × UR-gDTR; exon vs intron MWU | p < 1e-50, d ≥ 0.5, intron > exon → PASS → Phase 2; weak → 32kb context retry; fail → Phase 2 보류 |
| 1.7 Write-up | Day 14 | PHASE1_DECISION.md 산출 | gate verdicts + Phase 2 권고 |

각 sub-stage의 상세 spec(input/output/concrete commands/verification criteria)는 §9에 있다.

---

## 4. Data Pipeline

Phase 0와 동일한 source URL·MD5·workflow를 사용. 단 Phase 1은 chr22를 추가로 다운로드.

### 4.1 GRCh38 reference genome

```bash
# UCSC primary assembly per-chromosome
URL_BASE="https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes"
mkdir -p /root/gDTR/data/GRCh38
cd /root/gDTR/data/GRCh38

# chr17 (TP53, BRCA1; from Phase 0)
wget ${URL_BASE}/chr17.fa.gz
md5sum chr17.fa.gz   # expected: 023ccefd...  (Phase 0와 일치 검증)
gunzip chr17.fa.gz

# chr22 (Phase 1.6 Gate B_evo target)
wget ${URL_BASE}/chr22.fa.gz
md5sum chr22.fa.gz   # 새로 record
gunzip chr22.fa.gz

# pyfaidx index
python -c "from pyfaidx import Fasta; Fasta('chr17.fa'); Fasta('chr22.fa')"
```

### 4.2 GENCODE v44 annotation

```bash
URL="https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gff3.gz"
mkdir -p /root/gDTR/data/GENCODE
cd /root/gDTR/data/GENCODE
wget ${URL}
md5sum gencode.v44.annotation.gff3.gz   # record
gunzip gencode.v44.annotation.gff3.gz

# chr17 + chr22 subset (Phase 0 reusable function)
python -c "
import gffutils
db = gffutils.create_db(
    'gencode.v44.annotation.gff3',
    dbfn='gencode.v44.chr17_22.db',
    force=True, keep_order=True, merge_strategy='merge', sort_attribute_values=True,
    pragmas={'foreign_keys': 'OFF'}
)
"
```

### 4.3 ClinVar 2026-04 release

Phase 3에서 사용할 예정이지만, Phase 1.7 write-up 시 Gate C_evo design 명시를 위해 미리 lock.

```bash
URL="https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz"
mkdir -p /root/gDTR/data/ClinVar
cd /root/gDTR/data/ClinVar
wget ${URL} -O clinvar_2026-04.vcf.gz
md5sum clinvar_2026-04.vcf.gz   # record + check release date in header
zcat clinvar_2026-04.vcf.gz | head -30 | grep "##fileDate"   # confirm 2026-04
```

### 4.4 Versioning

```
/root/gDTR/data/DATA_VERSIONS.txt:
GRCh38_chr17    md5 023ccefd...    2026-04-26    https://hgdownload.../chr17.fa.gz
GRCh38_chr22    md5 <new>           2026-04-XX    https://hgdownload.../chr22.fa.gz
GENCODE_v44     md5 <new>           2026-04-XX    EBI FTP gencode.v44
ClinVar_202604  md5 <new>           2026-04-XX    NCBI FTP clinvar.vcf.gz
```

`gDTR/data/DATA_VERSIONS.txt`는 모든 forward의 첫 번째 input. 변경 시 reproducibility 깨짐 → git에 commit.

---

## 5. Parallel Execution Strategy

### 5.1 Background-agentable sub-stages

Long-running하고 결과가 명확한 stage는 background agent에 위임 가능:

| Sub-stage | Why agentable | Estimated wall-clock |
|---|---|---|
| 1.1 Gate A_evo untuned | 100 sequence × 32 layers, 단순 forward + per-layer M2 산출 | ~2 hr |
| 1.2 Tuned lens training | E5 패턴 그대로 scale up, deterministic loss curve | ~30-60 min |
| 1.4 Calibration phase | random 50 sequence × 6kb forward + q70 산출, region별 반복 | ~1-2 hr |
| 1.5 HP sweep | 3×3 grid × cached hidden states (no new forward 가능) | ~30 min |
| **1.6 chr22 Gate B_evo** | **~16,000 window × forward = 가장 ideal한 background job** | **~30 hr (H200)** |

### 5.2 User-attention sub-stages

각 sub-stage 종료 후 gate decision은 **사용자 review 필수**:

| Sub-stage | Decision required |
|---|---|
| 1.0 smoke | Vortex API quirks confirmation → APPENDIX_C.md 사인오프 |
| 1.1 Gate A_evo verdict | M2 < 0.50인 경우 Evo 1 fallback 결정 |
| 1.3 Tuned lens verdict | 가설 (c) causal claim level 결정 (confirmed / partial / rejected) |
| 1.6 Gate B_evo verdict | direction 다르면 cancer-gene bias 분석 추가 결정 |
| 1.7 PHASE1_DECISION.md | Phase 2 진입 여부 결정 |

### 5.3 H200 compute budget vs PHASE1_DECISIONS.md §1.4

PHASE1_DECISIONS.md §1.4는 H100 80GB 기준 ~120 hr, $273 추정. H200 141GB는:

- Memory 1.76× → batch 1.76× 가능 → wall clock 약 0.6× → **~70 hr 예상**
- 단 Vortex framework가 H200에 fully optimized 안 되어 있을 수 있음 → conservative하게 ~120 hr 그대로 유지
- DigitalOcean H200 시간당 비용은 별도 — Phase 1 종료 후 실제 비용 정산
- Phase 1.0에서 6kb/32kb/256kb forward의 wall-clock + memory를 측정해 batch tuning

---

## 6. Reproducibility

### 6.1 Reproducibility checklist (Phase 0와 동일 + Phase 1 추가분)

- [x] **Seed = 42** 모든 stage. `numpy.random.seed(42)` + `torch.manual_seed(42)` + `torch.cuda.manual_seed_all(42)` + per-script sub-seed offsets
- [x] **HF revision SHA lock**: Phase 1.0 smoke test에서 `arcinstitute/evo2_7b` 의 HF revision SHA를 record
- [x] **Vortex git SHA lock**: Phase 1.0에서 `git -C $(python -c "import evo2; print(evo2.__path__[0])") rev-parse HEAD`
- [x] **pip freeze**: `/root/gDTR/requirements_phase1.lock.txt`
- [x] **Data versions**: `/root/gDTR/data/DATA_VERSIONS.txt` (md5 + source URL + download date)
- [x] **Hardware lock**: H200 141GB instance ID + CUDA 13.1 + driver version recorded in PHASE1_APPENDIX_C.md
- [x] **All compute logged**: `/root/gDTR/logs/{stage}_{YYYYMMDD_HHMMSS}.log`
- [x] **Results 위치**: `/root/gDTR/results/{runs,tables,figures,caches}/`

### 6.2 Per-stage JSON sidecar

각 stage는 다음을 `/root/gDTR/results/runs/stage_{N}_{name}.json`에 record:

```json
{
  "stage": "1.1_gate_a_evo_untuned",
  "started_at": "2026-04-28T03:14:15Z",
  "ended_at": "2026-04-28T05:42:01Z",
  "wall_clock_s": 8866,
  "host": "ml-ai-ubuntu-gpu-h200x1-141gb-atl1",
  "gpu": "H200_141GB",
  "seed": 42,
  "model_revision_sha": "<filled at smoke test>",
  "evo2_git_sha": "<filled at smoke test>",
  "input_data_md5": {"GRCh38_chr17": "...", "GENCODE_v44": "..."},
  "outputs": {
    "cache": "results/caches/stage_1.1_hidden_states.npz",
    "table": "results/tables/stage_1.1_per_layer_m2.csv",
    "figure": "results/figures/stage_1.1_block_stratified_m2.png"
  },
  "metrics": {
    "M2_jsd_global": null,
    "M2_ur_global": null,
    "M2_per_layer": [...]
  },
  "verdict": "..."
}
```

### 6.3 Code repository

Phase 1 시작 직후 GitHub repo public publish 검토. 단 Evo 2 access 조건상 model weights는 포함하지 않고, Hugging Face Hub에서 가져오는 명령만 포함.

---

## 7. Risk Mitigations (server-specific)

PHASE1_DECISIONS.md §6 Risk matrix를 server-specific risk로 보강.

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Vortex API surprises (예: layer name schema 변동) | Med | High | Phase 1.0 smoke test가 catch; ArcInstitute GitHub examples + issue tracker fallback |
| flash-attn 컴파일 실패 | Med | Med | `apt install ninja-build` 선행 + `pip install --no-build-isolation` 재시도 + pre-built wheel from PyPI fallback |
| H200 memory access 패턴 비호환 | Low | Med | Phase 1.0에서 6kb forward 정상 작동 확인 → 32kb/256kb 단계적 검증 |
| Disk 부족 | Very Low | Low | 698 GB 가용. Evo 2 weights ~14 GB + GRCh38 ~3 GB + ClinVar ~3 GB + caches ~50 GB ≪ 698 GB |
| HF gated model access 거부 | Low | High (Phase 1 blocking) | 사용자가 `huggingface.co/arcinstitute/evo2_7b`에서 접근 신청 + token 환경변수 설정 (사전 confirm 필요) |
| Long-running job timeout | Med | Med | `nohup ... > logs/{stage}.log 2>&1 &` 패턴으로 detach; ssh 재연결 시 tail로 진행 확인 |
| GPU memory fragmentation | Low | Med | `torch.cuda.empty_cache()` between forward; 필요 시 `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128` |
| Lambda → DigitalOcean 비용 차이 | N/A | N/A | PHASE1_DECISIONS.md §1.4 추정($273)은 Lambda 기준; 실제 DigitalOcean 비용은 Phase 1 종료 후 정산 보고 |

### 7.1 Critical pre-Phase-1.0 user action

**HF gated access**: Phase 1.0 smoke test 실행 전 사용자가 다음을 완료해야 한다:

1. `huggingface.co/arcinstitute/evo2_7b` 페이지에서 access 신청
2. 승인 후 HF token 발급 (`huggingface.co/settings/tokens`)
3. DigitalOcean에 token export:
   ```bash
   echo 'export HUGGING_FACE_HUB_TOKEN=hf_...' >> ~/.bashrc
   source ~/.bashrc
   ```

이 단계가 완료되지 않으면 Phase 1.0 model load가 fail. **TBD: 사용자에게 confirm 필요**.

---

## 8. Decision Gates (carried from PHASE1_DECISIONS.md)

본 §은 PHASE1_DECISIONS.md §3의 gate 정의를 그대로 가져온다. **임계값 변경 없음**. 본 plan에서 변경되는 것은 임계값이 아니라 그 임계값에 도달하기 위한 server command이다.

### 8.1 Gate A_evo (blocking) — Phase 1.1 + 1.3

| Sub-gate | Threshold | Action on fail |
|---|---|---|
| Gate A_evo_attn | per-block-attention M2 ≥ 0.85 | attention block fix |
| Gate A_evo_hyena | per-block-Hyena M2 ≥ 0.85 OR tuned lens 후 ≥ 0.85 | tuned lens 사용 (예상되는 path) |
| Gate A_evo_overall | UR-gDTR M2_global ≥ 0.50 | 강한 fail (<0.30) → Evo 1 fallback |

### 8.2 Gate B_evo (blocking) — Phase 1.6

- chr22 exon vs intron Mann-Whitney U two-sided **p < 1×10⁻⁵⁰** (Bonferroni × 6 contexts)
- Cohen's d ≥ 0.5 (large)
- Direction: intron > exon (Phase 0와 일치)

### 8.3 Gate C_evo (informational, post-Phase 1) — Phase 3 carry-over

- ΔD vector logistic regression P/LP vs B/LB AUROC ≥ 0.65 (10-fold CV) → primary
- 0.55 ≤ AUROC < 0.65 → mixed signal, ensemble framing
- AUROC < 0.55 → informative negative

### 8.4 Gate priority & abort condition

PHASE1_DECISIONS.md §3.4에 따라, 두 blocking gate(A_evo, B_evo)가 동시에 fail이면 Phase 1 본실험 중단 및 method 재검토. Risk matrix §7의 mitigation 활성화.

---

## 9. Sub-stage Detailed Specs

### 9.1 Phase 1.0 — Smoke test (Day 1, +1d for Vortex API discovery)

**Goal**. Vortex Evo 2 API 패턴 확인, HF revision SHA lock, hidden state extraction 정확한 호출 signature 정정. PHASE1_APPENDIX_C.md 작성.

**Inputs**.
- Network access to `huggingface.co/arcinstitute/evo2_7b` (gated; 사용자 token 필요)
- 6kb random sequence (seed=42 dinucleotide-shuffled, length=6001 with BOS)

**Outputs**.
- `/root/gDTR/PHASE1_APPENDIX_C.md` — Vortex API facts (Phase 0 Appendix C 형식)
- `/root/gDTR/results/runs/stage_1.0_smoke.json` — JSON sidecar
- `/root/gDTR/requirements_phase1.lock.txt` — pip freeze
- `/root/gDTR/logs/stage_1.0_smoke_*.log`

**Server commands**.

```bash
# 0. 환경 준비 (sudo-exec)
sudo apt-get update && sudo apt-get install -y ninja-build python3.10-venv git

# 1. Project root + venv
mkdir -p /root/gDTR/{src,scripts,data,results/{runs,tables,figures,caches,tuned_lens},logs}
cd /root/gDTR
python3.10 -m venv venv
source venv/bin/activate

# 2. Base packages (Phase 0와 동일)
pip install --upgrade pip wheel setuptools
pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cu121
pip install transformers==4.49.0 biopython pyfaidx pyBigWig gffutils statannotations \
            numpy==1.24.4 pandas==2.2.2 scipy==1.14.0 scikit-learn==1.5.1 \
            seaborn==0.13.2 matplotlib==3.9.2

# 3. flash-attn (수동 빌드)
pip install flash-attn==2.8.0.post2 --no-build-isolation

# 4. Evo 2 (Vortex)
pip install evo2

# 5. HF gated model 접근 (사용자 token 사전 export 필요)
huggingface-cli login --token "$HUGGING_FACE_HUB_TOKEN"

# 6. Smoke test 실행
python /root/gDTR/scripts/00_smoke_evo2.py \
    --seed 42 \
    --context_len 6001 \
    --layer_name_probe 'blocks.31.mlp.l3' \
    --output /root/gDTR/results/runs/stage_1.0_smoke.json \
    2>&1 | tee /root/gDTR/logs/stage_1.0_smoke_$(date +%Y%m%d_%H%M%S).log

# 7. pip freeze lock
pip freeze > /root/gDTR/requirements_phase1.lock.txt

# 8. Vortex git SHA record
python -c "import evo2, subprocess; p = evo2.__path__[0]; \
           print(subprocess.check_output(['git','-C',p,'rev-parse','HEAD']).decode())" \
    > /root/gDTR/results/runs/evo2_git_sha.txt
```

**Verification criteria** (모두 만족해야 1.1 진입):

- [ ] Evo 2 모델이 정상 로드되고 6kb forward가 성공
- [ ] `outputs, embeddings = model(..., return_embeddings=True, layer_names=[...])` 시그니처 확인
- [ ] 32 layer hidden states 추출 가능 (`blocks.0..31.mlp.l3`)
- [ ] Hidden size = 4096 확인
- [ ] Vocab size 확인 (~512, 정확한 값 PHASE1_APPENDIX_C.md에 기록)
- [ ] BOS token id + 처리 방식 명확
- [ ] `lm_head.weight` storage + value 둘 다 검사 (E1 정정사항 반영)
- [ ] Block type schedule 확인 (각 layer가 attention인지 hyena인지)
- [ ] Memory profile: 6kb 단일 forward < 30GB on H200
- [ ] PHASE1_APPENDIX_C.md에 5+ 정정사항 + 확인사항 기록

**Decision rule**. PHASE1_DECISIONS.md §7 decision tree:
- "Critical mismatch (e.g., hidden_states layout, BOS handling, dtype) → patch and retry"
- "OK → Phase 1.1"

### 9.2 Phase 1.1 — Block-stratified Gate A_evo untuned (Day 3-4)

**Goal**. 100 random sequence × 32 layer hidden states 추출 → per-layer M2(JSD + UR), block type별 분리. Gate A_evo_attn / Gate A_evo_hyena / Gate A_evo_overall 검증.

**Inputs**.
- `/root/gDTR/data/GRCh38/chr17.fa` (Phase 0와 동일 region에서 샘플링)
- 100 sequence (50 GC-matched chr17 intergenic + 50 dinucleotide-shuffled)
- PHASE1_APPENDIX_C.md (block type 정보)

**Outputs**.
- `/root/gDTR/results/caches/stage_1.1_hidden_states.npz` — `(100, 6000, 32, 4096)` float16 (≈ 1.5 TB! → chunked save 필요)
- `/root/gDTR/results/tables/stage_1.1_per_layer_m2.csv` — Layer × {M1_jsd, M2_jsd, M2_ur, block_type, M2_jsd_CI, M2_ur_CI}
- `/root/gDTR/results/figures/stage_1.1_block_stratified_m2.png`
- `/root/gDTR/results/runs/stage_1.1_gate_a_evo.json`

**중요한 implementation note**: 32 layer × 100 seq × 6000 pos × 4096 = 750 GB float16. Hidden state 전체를 cache 안 됨. 대안:
- Per-layer로 D 계산 후 hidden state는 discard
- 또는 ΔD vector만 cache (32 × 100 × 6000 = 7.7 GB float16) — Phase 1.5에서 재사용 가능
- Tuned lens 학습 (Phase 1.2)에는 last 2 block hidden states만 필요 → `(100, 6000, 2, 4096) ≈ 5 GB float16` cache OK

**Server commands**.

```bash
cd /root/gDTR
source venv/bin/activate

# Background로 실행 (long-running)
nohup python scripts/10_gate_a_evo.py \
    --seed 42 \
    --num_sequences 100 \
    --gc_matched 50 --shuffled 50 \
    --context_len 6001 \
    --num_layers 32 \
    --output_table results/tables/stage_1.1_per_layer_m2.csv \
    --output_figure results/figures/stage_1.1_block_stratified_m2.png \
    --output_json results/runs/stage_1.1_gate_a_evo.json \
    --cache_last_2_layers results/caches/stage_1.1_h_31_32.npz \
    > logs/stage_1.1_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $! > /root/gDTR/logs/stage_1.1.pid
```

**Verification criteria**.

- [ ] 100 sequence 모두 forward 성공
- [ ] 32 layer × 4096 hidden 추출
- [ ] Per-layer M2_jsd, M2_ur 산출
- [ ] Block type별 평균 M2 산출 (attention vs hyena)
- [ ] Bootstrap 95% CI 산출
- [ ] Last 2 layer (h_31, h_32) cache 저장 (Phase 1.2 input)
- [ ] PHASE1_DECISIONS.md §3.1 표 형식의 verdict 기록

**Decision rule** (PHASE1_DECISIONS.md §7 decision tree).

```
M2_global ≥ 0.50 across both block types → Phase 1.2 (proceed)
M2_global ∈ [0.30, 0.50)                  → tuned lens 더 절실, 1.2 진입
M2_global < 0.30                          → 모델 사용 적합성 재검토, Evo 1 fallback 검토
```

### 9.3 Phase 1.2 — Tuned lens training (Day 5)

**Goal**. PHASE1_DECISIONS.md §2.2 spec대로 last 2 blocks affine `A_31, A_32 ∈ ℝ^4096×4096` 학습. E5 (HyenaDNA) 패턴을 d=4096 scale로 확장.

**Inputs**.
- `/root/gDTR/results/caches/stage_1.1_h_31_32.npz` (Phase 1.1 cache)
- Disjoint training corpus: 200 sequence × 6kb (Phase 1.1과 별개로 추가 forward; 또는 Phase 1.1의 50 sequence를 train, 50을 eval split — disjoint 확보)

**Outputs**.
- `/root/gDTR/results/tuned_lens/A_31.pt`
- `/root/gDTR/results/tuned_lens/A_32.pt`
- `/root/gDTR/results/tuned_lens/training_loss.csv`
- `/root/gDTR/results/figures/stage_1.2_loss_curve.png`
- `/root/gDTR/results/runs/stage_1.2_tuned_lens.json`

**Hyperparameters** (PHASE1_DECISIONS.md §2.2):
- Affine init: identity + zero bias (untuned lens 일치 보장)
- Loss: `MSE(lm_head(A_ℓ(h_ℓ)), out.logits)` averaged over positions
- Optimizer: Adam, lr=1e-3
- Epochs: ≥10 (15 권고; E5에서 5 epochs PARTIAL, 15 epochs CONFIRMED)
- Batch: H200 메모리 활용 → 시퀀스 2-4개 동시 (실측 후 조정)
- Params per affine: 4096×4096 + 4096 = 16.78M → 2×16.78M = 33.6M total
- Checkpoint size: ~120MB (float32) 또는 ~60MB (float16)

**Server commands**.

```bash
cd /root/gDTR
source venv/bin/activate

nohup python scripts/12_train_tuned_lens.py \
    --seed 42 \
    --hidden_states_cache results/caches/stage_1.1_h_31_32.npz \
    --num_train_sequences 200 \
    --target_layers 31,32 \
    --hidden_size 4096 \
    --epochs 15 \
    --lr 1e-3 \
    --batch_size 2 \
    --init identity \
    --output_dir results/tuned_lens \
    --output_json results/runs/stage_1.2_tuned_lens.json \
    > logs/stage_1.2_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $! > /root/gDTR/logs/stage_1.2.pid
```

**Verification criteria**.

- [ ] Loss가 epoch에 따라 monotone 감소 (E5: 93.96 → 0.71, 132× reduction)
- [ ] `A_31`의 SVD top SV가 ‖A_31 − I‖_F와 비슷한 magnitude (E5: 9.45 ≈ 9.19)
- [ ] Identity init 시 loss 시작값이 untuned lens loss와 일치 (sanity)
- [ ] Eval set의 last-block reconstruction MSE가 baseline 대비 ≥ 50× 감소
- [ ] A_31.pt, A_32.pt 파일 ~60-120MB 정상 저장

**Decision rule**. Loss converges → 1.3 진입. Loss diverge 또는 NaN → init 또는 lr 점검.

### 9.4 Phase 1.3 — Gate A_evo with tuned lens (Day 6)

**Goal**. Phase 1.1과 동일 평가 setup에서 tuned lens 적용 후 M2 재측정. **Phase 1의 가장 중요한 causal test**: 가설 (c) "trained readout subspace alignment"가 Evo 2에서도 dominant mechanism인지.

**Inputs**.
- `/root/gDTR/results/tuned_lens/A_31.pt`, `A_32.pt`
- Phase 1.1과 동일 100 sequence (또는 disjoint eval set)
- `src/logit_lens.py` (tuned lens applied 버전)

**Outputs**.
- `/root/gDTR/results/tables/stage_1.3_per_layer_m2_tuned.csv`
- `/root/gDTR/results/figures/stage_1.3_m2_untuned_vs_tuned.png` (Phase 1.1과 비교 dual panel)
- `/root/gDTR/results/runs/stage_1.3_gate_a_evo_tuned.json`

**Server commands**.

```bash
cd /root/gDTR
source venv/bin/activate

python scripts/13_gate_a_evo_tuned.py \
    --seed 42 \
    --num_sequences 100 \
    --tuned_lens_dir results/tuned_lens \
    --baseline_table results/tables/stage_1.1_per_layer_m2.csv \
    --output_table results/tables/stage_1.3_per_layer_m2_tuned.csv \
    --output_figure results/figures/stage_1.3_m2_untuned_vs_tuned.png \
    --output_json results/runs/stage_1.3_gate_a_evo_tuned.json \
    2>&1 | tee logs/stage_1.3_$(date +%Y%m%d_%H%M%S).log
```

**Verification criteria** (PHASE1_DECISIONS.md §7 decision tree):

- [ ] Tuned lens 적용 후 M2_(L-1)=M2_31 이 baseline 대비 회복
- [ ] UR-gDTR M2는 변화 없음 (sanity — UR은 lm_head 우회)

**Decision rule**.

```
M2 회복 (≥ 0.85)        → 가설 (c) causally confirmed, JSD lens primary 가능 (UR과 함께)
M2 부분 회복 (0.50–0.85) → 가설 (c) 부분 확인, UR primary 유지
M2 회복 안 됨            → 가설 (c) 부분 기각, mechanistic 추가 분석 (E1 결과 reference)
```

### 9.5 Phase 1.4 — Calibration: region-adaptive q70 protocol (Day 7-8)

**Goal**. PHASE1_DECISIONS.md §2.3 region-adaptive calibration protocol을 Evo 2에서 implement + 6kb / 32kb / 1M context sensitivity 분석.

**Inputs**.
- `/root/gDTR/data/GRCh38/chr17.fa`, `chr22.fa`
- Multiple regions: TP53 region, BRCA1 region, chr22 random region 3개 (총 5+ region)

**Outputs**.
- `/root/gDTR/results/tables/stage_1.4_calibration_per_region.csv` — region × {γ_cos_q70, n_samples, std}
- `/root/gDTR/results/tables/stage_1.4_context_sensitivity.csv` — context_len × {γ_cos_q70}
- `/root/gDTR/results/figures/stage_1.4_q70_distribution.png`
- `/root/gDTR/results/runs/stage_1.4_calibration.json`

**Protocol** (PHASE1_DECISIONS.md §2.3):

1. 각 region에서 random 50 sequence × 6kb forward
2. Penultimate layer (L-1=31) running-min D_cos 분포
3. q70 → γ_cos_region
4. Sanity check: region 간 γ_cos 변동 ±50% 이내?
5. Context sensitivity: 6kb / 32kb / 1M context 에서 q70 비교 (특히 Phase 0 design § 11 carry-over question 3)

**Server commands**.

```bash
cd /root/gDTR
source venv/bin/activate

# 5 region calibration
python scripts/14_calibration.py \
    --seed 42 \
    --regions tp53,brca1,chr22_random_1,chr22_random_2,chr22_random_3 \
    --num_sequences_per_region 50 \
    --context_len 6001 \
    --output_table results/tables/stage_1.4_calibration_per_region.csv \
    --output_figure results/figures/stage_1.4_q70_distribution.png \
    --output_json results/runs/stage_1.4_calibration.json \
    2>&1 | tee logs/stage_1.4_calibration_$(date +%Y%m%d_%H%M%S).log

# Context sensitivity (TP53 region only)
python scripts/14_calibration.py \
    --seed 42 \
    --regions tp53 \
    --num_sequences_per_region 50 \
    --context_lens 6001,32001,1048577 \
    --output_table results/tables/stage_1.4_context_sensitivity.csv \
    2>&1 | tee logs/stage_1.4_context_$(date +%Y%m%d_%H%M%S).log
```

**Verification criteria**.

- [ ] 5 region에서 γ_cos_q70 산출 완료
- [ ] Region 간 변동 ±50% 이내 (변동 크면 Bonferroni sensitivity 분석 추가)
- [ ] 6kb / 32kb / 1M context에서 γ_cos_q70 추세 기록 (1M에서 다르면 Phase 2 strategy 영향)

**Decision rule**. PHASE1_DECISIONS.md §2.3:
- 변동 ±50% 이내 → calibration protocol 그대로 진행
- 초과 → "calibration 자체에 문제" → Bonferroni-corrected sensitivity 분석 추가

### 9.6 Phase 1.5 — HP sweep reduced grid (Day 9, 1.6과 병행)

**Goal**. PHASE1_DECISIONS.md §2.4 reduced grid (γ_cos ∈ {0.4, 0.5, 0.6}, ρ ∈ {0.8, 0.85, 0.9}) 9 combination 평가.

**Inputs**.
- Phase 1.4의 cached hidden states + γ_cos_region (region별)
- TP53 + BRCA1 region (Phase 0 cross-replication 그대로 — Cohen's d 비교)

**Outputs**.
- `/root/gDTR/results/tables/stage_1.5_hp_sweep.csv` — (γ_cos, ρ) × {Cohen_d, MWU_p, mean_c_interp_exon, mean_c_interp_intron}
- `/root/gDTR/results/figures/stage_1.5_hp_heatmap.png` — 3×3 heatmap of Cohen's d
- `/root/gDTR/results/runs/stage_1.5_hp_sweep.json`

**Server commands**.

```bash
cd /root/gDTR
source venv/bin/activate

python scripts/15_hp_sweep.py \
    --seed 42 \
    --regions tp53,brca1 \
    --gamma_cos_grid 0.4,0.5,0.6 \
    --rho_grid 0.8,0.85,0.9 \
    --output_table results/tables/stage_1.5_hp_sweep.csv \
    --output_figure results/figures/stage_1.5_hp_heatmap.png \
    --output_json results/runs/stage_1.5_hp_sweep.json \
    2>&1 | tee logs/stage_1.5_$(date +%Y%m%d_%H%M%S).log
```

**Verification criteria**.

- [ ] 9 combination 모두 평가
- [ ] Best (γ_cos, ρ) 기록 (Phase 0 starting point γ_cos=0.5, ρ=0.85 robust한지 확인)

**Decision rule**. Best가 starting point에서 크게 벗어나면 Phase 1.6은 best 적용; 비슷하면 starting point 그대로.

### 9.7 Phase 1.6 — Gate B_evo chr22 genome-wide (Day 9-13)

**Goal**. PHASE1_DECISIONS.md §3.2 Gate B_evo. chr22 ~50Mb를 6kb stride 3kb로 ~16,000 windows. UR-gDTR profile + GENCODE annotation overlay + exon vs intron MWU.

**Inputs**.
- `/root/gDTR/data/GRCh38/chr22.fa`
- `/root/gDTR/data/GENCODE/gencode.v44.chr17_22.db`
- Phase 1.4 calibration: chr22 region별 γ_cos_q70
- Phase 1.5 best (γ_cos, ρ)

**Outputs**.
- `/root/gDTR/results/tables/stage_1.6_chr22_per_window.parquet` — ~16,000 row × {start, end, gDTR_mean, gDTR_std, GC, entropy, dominant_context}
- `/root/gDTR/results/tables/stage_1.6_context_summary.csv` — 6 context × {n, mean, std, MWU_p_vs_intron, Cohen_d_vs_intron}
- `/root/gDTR/results/figures/stage_1.6_chr22_track.pdf` — chromosome-wide track
- `/root/gDTR/results/figures/stage_1.6_violin_by_context.pdf`
- `/root/gDTR/results/runs/stage_1.6_chr22_gate_b.json`

**Compute estimate**. ~16,000 windows × 6kb forward × ~3-5s on H200 = ~13-22 hr. Background agent 가장 ideal.

**Server commands**.

```bash
cd /root/gDTR
source venv/bin/activate

# Background agent로 위임 가능. Long-running → nohup
nohup python scripts/16_chr22_gate_b.py \
    --seed 42 \
    --chrom chr22 \
    --window_size 6001 \
    --stride 3000 \
    --gencode_db data/GENCODE/gencode.v44.chr17_22.db \
    --gamma_cos_per_region results/tables/stage_1.4_calibration_per_region.csv \
    --rho 0.85 \
    --batch_size 4 \
    --output_parquet results/tables/stage_1.6_chr22_per_window.parquet \
    --output_summary results/tables/stage_1.6_context_summary.csv \
    --output_track_figure results/figures/stage_1.6_chr22_track.pdf \
    --output_violin_figure results/figures/stage_1.6_violin_by_context.pdf \
    --output_json results/runs/stage_1.6_chr22_gate_b.json \
    > logs/stage_1.6_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $! > /root/gDTR/logs/stage_1.6.pid

# 모니터링 (이후 별도 터미널에서)
tail -f logs/stage_1.6_*.log
```

**Verification criteria** (PHASE1_DECISIONS.md §3.2).

- [ ] ~16,000 window 모두 forward 완료
- [ ] 6 context (exon, intron, 5'UTR, 3'UTR, splice±10, intergenic)에 분류 완료
- [ ] Bonferroni-corrected α = 1.7×10⁻⁵¹
- [ ] 각 context의 MWU two-sided p, Cohen's d 산출
- [ ] Direction sanity check: intron > exon (Phase 0와 같은 방향)

**Decision rule** (PHASE1_DECISIONS.md §7 decision tree).

```
PASS (p < 1e-50, d ≥ 0.5, intron > exon)  → Phase 2 → 3 진입
PASS but 다른 direction                    → cancer-gene bias 분석 (gene class stratification)
Weak (p ∈ [1e-20, 1e-50])                  → context size 32kb로 확장 후 재시도
FAIL (p > 1e-20)                           → Phase 2 보류, method 재검토
```

### 9.8 Phase 1.7 — PHASE1_DECISION.md write-up (Day 14)

**Goal**. Phase 1 모든 결과를 종합한 final decision document 작성.

**Inputs**.
- `/root/gDTR/results/runs/stage_*.json` 모두
- `/root/gDTR/results/tables/*.csv`, `*.parquet`
- `/root/gDTR/results/figures/*.{png,pdf}`
- 본 plan + PHASE1_DECISIONS.md

**Outputs**.
- `/root/gDTR/PHASE1_DECISION.md` — gate verdicts (A_evo, B_evo, C_evo design lock) + Phase 2 권고
- `/root/gDTR/PHASE1_FINDINGS.md` (optional, PHASE0_FINDINGS.md 형식의 narrative 산출)

**Sections** (template).

```
# Phase 1 Decision — gDTR on Evo 2 7B

## 0. TL;DR
3-paragraph summary: gate verdicts + key finding + Phase 2 권고

## 1. Gate Verdicts
### 1.1 Gate A_evo
  - untuned: M2_global = ?, attn = ?, hyena = ?
  - tuned: M2_global = ?
  - Verdict: PASS / PARTIAL / FAIL
  - 가설 (c) verdict: causally confirmed / partial / rejected
### 1.2 Gate B_evo
  - chr22 exon vs intron: p = ?, d = ?, direction: ?
  - Verdict: PASS / WEAK / FAIL
### 1.3 Gate C_evo (design lock for Phase 3)
  - 임계값 그대로 유지: AUROC ≥ 0.65 primary

## 2. Hyperparameter Final Selection
γ_cos = ?, ρ = ?, region-adaptive: yes/no

## 3. Phase 2 Recommendation
  - 진입 / 보류 / 변경 방향
  - 변경된 method spec (있을 시)

## 4. Compute Cost Actual
  - Wall clock: ? hr
  - Cost: $?
  - PHASE1_DECISIONS.md §1.4 추정 ($273)과 비교

## 5. Open Questions for Phase 2/3
  - PHASE1_DECISIONS.md §8 carry-over 중 Phase 1에서 답한 것 / 답 못 한 것

## 6. Limitations
  - Phase 0 limitation (PHASE0_FINDINGS.md §8) 중 Phase 1에서 해소된 것 / 안 된 것

## Appendix — Tables / Figures
```

**Server commands**. 이 stage는 사용자 + agent 협업; 주로 Mac에서 작성하고 서버에 업로드.

```bash
# 결과 파일 일괄 다운로드 (Mac으로)
rsync -avz root@<digitalocean_ip>:/root/gDTR/results/ \
            /Users/yoonjincho/Project/ICML/gDTR-Phase1/results/
rsync -avz root@<digitalocean_ip>:/root/gDTR/PHASE1_APPENDIX_C.md \
            /Users/yoonjincho/Project/ICML/gDTR-Phase1/

# 작성 후 업로드
rsync -avz /Users/yoonjincho/Project/ICML/gDTR-Phase1/PHASE1_DECISION.md \
            root@<digitalocean_ip>:/root/gDTR/
```

**Verification criteria**.

- [ ] 3 gate 모두 verdict 명시
- [ ] PHASE1_DECISIONS.md §8 7개 open question 모두 status 기록
- [ ] Phase 2 진입 / 보류 / 변경 권고 명확
- [ ] 모든 figure / table 참조 정상

---

## 10. Open Questions (Phase 0 carry-over from PHASE1_DECISIONS.md §8)

본 문서는 PHASE1_DECISIONS.md §8의 7개 open question을 그대로 carry over한다. Phase 1.7 write-up 시 각 항목 status를 [answered / partial / unanswered]로 분류한다.

1. **Evo 2 hybrid의 last-block alignment spike**: 32-layer hybrid에서 L31→L32에서 같은 magnitude의 spike가 나타나는가? Attention vs Hyena block이 다른가?
   - Answered by: Phase 1.1 + 1.3
2. **Tuned lens 회복 효과**: tuned lens 적용 후 JSD lens M2가 0.85 이상으로 회복되는가?
   - Answered by: Phase 1.3
3. **Calibration stability across context sizes**: 6kb, 32kb, 1M context에서 q70 γ_cos가 stable한가?
   - Answered by: Phase 1.4 context sensitivity sub-analysis
4. **Cross-gene generalization**: chr22 genome-wide에서 cancer driver gene의 패턴(intron > exon)이 다른 gene class에도 적용되는가?
   - Answered by: Phase 1.6
5. **Variant signal at 7B scale**: ClinVar 2K+ variants에서 ΔD(ℓ) vector AUROC ≥ 0.65를 달성하는가?
   - Carry over to: Phase 3 (본 plan에서는 design lock만)
6. **Block-type interaction**: hybrid에서 attention block 직후 vs Hyena block 직후의 settling pattern이 systematic하게 다른가?
   - Answered by: Phase 1.1 (block-stratified analysis)
7. **Tied vs untied 일반화 (E1 결과로 부분 답)**: untied head는 모든 modern genomic CLM의 공통 issue. Tied embedding을 갖는 모델로 비교 가능?
   - Phase 1.0 smoke test에서 Evo 2의 lm_head tying status 확인 후 partial answer

---

## 11. Status Tracking

각 sub-stage에 다음 status row를 유지한다. 본 문서는 sub-stage 완료 시 manually patch하여 history record로 보존.

| Sub-stage | Status | Started | Ended | Verdict | JSON sidecar |
|---|---|---|---|---|---|
| 1.0 Smoke test | pending | — | — | — | results/runs/stage_1.0_smoke.json |
| 1.1 Gate A_evo untuned | pending | — | — | — | results/runs/stage_1.1_gate_a_evo.json |
| 1.2 Tuned lens training | pending | — | — | — | results/runs/stage_1.2_tuned_lens.json |
| 1.3 Gate A_evo tuned | pending | — | — | — | results/runs/stage_1.3_gate_a_evo_tuned.json |
| 1.4 Calibration | pending | — | — | — | results/runs/stage_1.4_calibration.json |
| 1.5 HP sweep | pending | — | — | — | results/runs/stage_1.5_hp_sweep.json |
| 1.6 Gate B_evo chr22 | pending | — | — | — | results/runs/stage_1.6_chr22_gate_b.json |
| 1.7 Write-up | pending | — | — | — | (manual) |

Status legend: `pending` / `in_progress` / `completed` / `failed (retry)` / `aborted (gate fail)`.

최종 산출: `/root/gDTR/PHASE1_DECISION.md` (gate verdicts + Phase 2 권고)

---

## Appendix A — Vortex API Reference

본 Appendix는 Phase 1.0 smoke test 종료 시 채워진다. Phase 0 Appendix C 형식으로 5+ 항목 예상.

### A.1 모델 로딩
```python
# (Phase 1.0에서 확정 후 patch)
```

### A.2 Hidden state 추출 정확한 호출 signature
```python
# (Phase 1.0에서 확정 후 patch)
```

### A.3 Layer name schedule (block type 매핑)
```
Layer 0 : ?  (attention / hyena)
Layer 1 : ?
...
Layer 31: ?
```

### A.4 Tokenizer

- Vocab size: ?
- BOS token id: ?
- EOS token id: ?
- BOS prepended? Where?

### A.5 lm_head tying status

- `lm_head.weight.data_ptr()` vs `embedding.weight.data_ptr()`: ?
- Frobenius norm of difference: ?
- Verdict: storage-tied / storage-untied / value-tied

### A.6 Forward dtype + autocast 동작

- Default dtype: ?
- Hidden states dtype: ?
- Logits dtype: ?

### A.7 Memory profile

| Context | Peak VRAM | Wall clock per forward |
|---|---|---|
| 6kb | ? | ? |
| 32kb | ? | ? |
| 256kb | ? | ? |
| 1M | ? | ? |

---

## Appendix B — Code Adaptation Patches

본 Appendix는 Phase 1.0 ~ 1.2 진행 중 채워진다. PoC `/root/gDTR-PoC/` (vessl) → Phase 1 `/root/gDTR/` (DigitalOcean) 코드 변경의 diff/patch 기록.

### B.1 `src/constants.py`

```python
# Phase 0 (HyenaDNA)
VOCAB_SIZE = 12
NUM_LAYERS = 8
HIDDEN_SIZE = 256
DEFAULT_GAMMA_COS = 0.50
DEFAULT_RHO = 0.85

# Phase 1 (Evo 2 7B) — Phase 1.0에서 정확한 값으로 patch
VOCAB_SIZE = ?      # ~512 expected
NUM_LAYERS = 32
HIDDEN_SIZE = 4096
DEFAULT_GAMMA_COS = 0.50  # carry-over from Phase 0 HP sweep
DEFAULT_RHO = 0.85
```

### B.2 `src/model_loader.py`

```python
# (Phase 1.0에서 확정 후 patch)
def load_evo2_7b(...):
    from evo2 import Evo2
    model = Evo2('evo2_7b')
    return model
```

### B.3 `src/logit_lens.py`

```python
# (Phase 1.0에서 확정 후 patch)
# Phase 0: outputs = model(input_ids, output_hidden_states=True)
#          hidden_states = outputs.hidden_states  # tuple of 10
# Phase 1: outputs, embeddings = model(input_ids, return_embeddings=True,
#                                       layer_names=['blocks.0.mlp.l3', ...])
```

### B.4 `src/tuned_lens.py` (NEW)

E5 prototype을 d=4096 scale로 확장. PHASE1_DECISIONS.md §2.2 spec 그대로.

### B.5 `src/block_type.py` (NEW)

```python
def classify_block(layer_idx: int, model_config) -> str:
    """Return 'attention' or 'hyena' for given layer index."""
    # (Phase 1.0에서 schedule 확인 후 implement)
```

---

## Appendix C — Compute Log

본 Appendix는 각 sub-stage 종료 시 append된다. PHASE1_DECISIONS.md §1.4의 "~120 hr / $273" 추정과 실제 비교.

### C.1 Sub-stage compute summary

| Sub-stage | Wall clock (hr) | GPU-hour | DigitalOcean cost ($) | Notes |
|---|---:|---:|---:|---|
| 1.0 Smoke test | TBD | TBD | TBD | Vortex API discovery |
| 1.1 Gate A_evo untuned | TBD | TBD | TBD | 100 seq × 32 layer |
| 1.2 Tuned lens training | TBD | TBD | TBD | 200 seq, 15 epochs |
| 1.3 Gate A_evo tuned | TBD | TBD | TBD | re-evaluation |
| 1.4 Calibration | TBD | TBD | TBD | 5 region × 50 seq |
| 1.5 HP sweep | TBD | TBD | TBD | 9 combinations |
| 1.6 Gate B_evo chr22 | TBD | TBD | TBD | ~16,000 window |
| 1.7 Write-up | (no GPU) | — | — | — |
| **Total** | TBD | TBD | TBD | vs $273 budget |

### C.2 Per-stage details

(각 sub-stage 종료 시 채움; PHASE1_DECISIONS.md §1.4 budget 대비 deviation 보고)

---

**End of Phase 1 Execution Plan**

Document author: Phase 0 chain agent + Phase 1 server-adaptation agent.
Date locked: 2026-04-26.
Update history: v1.0 initial.
