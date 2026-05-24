# Allosteric Challenge 三資料集交叉分析報告

## 檢查範圍

本報告交叉檢查 Cleveland Clinic challenge 中三個 minimum target families：

- KRAS G12C (Oncology): `4OBE` -> `6OIM`
- BCR-ABL1 (Oncology): `1OPL` -> `5MO4`
- Cardiac Myosin (Cardiology): `5TBY` -> `6C1H`

所有新增資料均由 RCSB 官方頁面與 API 下載，並由本 repo 的 scripts 產生可重跑分析。

## 跨資料集維度總覽

| Dataset | Input | Validation | Input graph nodes | Validation graph nodes | Target / marker | Target contacts | Exploratory contacts | Pair check | Risk note |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| KRAS G12C Oncology | 4OBE | 6OIM | 169 | 167 | MOV / AMG 510 bound form | 22 | 22 | 166 CA, RMSD 1.362 A | low; holo ligand marker present |
| BCR-ABL1 Oncology | 1OPL | 5MO4 | 451 | 429 | Asciminib / ABL001 candidate component AY7 | 46 | 46 | 429 CA, RMSD 0.98 A | The validation structure also contains an ATP-site inhibitor, so allosteric-vs-orthosteric ligand labels must be kept separate. |
| Cardiac Myosin Cardiology | 5TBY | 6C1H | 954 | 729 | No Mavacamten-like validation ligand detected in 6C1H by PDB component ID/name. | 0 | 2 | 729 CA, RMSD 34.002 A | RCSB describes 6C1H as actin-bound myosin-IB cryo-EM, not a cardiac myosin Mavacamten holo complex; treat it as a structural validation proxy only after challenge-organizer confirmation. |

## 特徵維度覆蓋檢查

| Dataset | RCSB files | Metadata | Chain dimensions | Ligands | Validation contacts | Contact graph | Pair comparison |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KRAS G12C Oncology | yes | yes | yes | yes | yes | yes | yes |
| BCR-ABL1 Oncology | yes | yes | yes | yes | yes | yes | yes |
| Cardiac Myosin Cardiology | yes | yes | yes | yes | risk/needs review | yes | yes |

## 主要交叉觀察

1. KRAS G12C 是三者中最乾淨的 apo/holo validation pair：`6OIM` 明確包含 AMG 510 bound-form ligand `MOV`，可直接形成 residue-level ground truth。
2. BCR-ABL1 的 `5MO4` 包含 Asciminib candidate ligand marker `AY7`，但同時也有其他 kinase inhibitor/heterogen；後續模型必須把 myristoyl-pocket allosteric marker 與 ATP-site inhibitor 分開。
3. Cardiac Myosin 的 PDF challenge label 與 `6C1H` RCSB metadata 存在明顯語義落差：`6C1H` 是 actin-bound myosin-IB cryo-EM structure，且未偵測到 Mavacamten-like ligand。這一組可以先做 structural/mechanical proxy 分析，但提交前應向 challenge organizer 確認 validation label。
4. Contact graph node counts 差異很大，代表 coarse-graining 策略不能一體套用：KRAS 是百級 residue graph，BCR-ABL1 是 kinase/regulatory domain 中型 graph，Myosin 是大型 multi-chain motor/actin complex。

## 後續建模建議

- 先為每組資料明確定義「可用於 blind input 的 features」與「只能用於 validation 的 labels」。
- 對 BCR-ABL1 與 Myosin 這類多 domain 或跨蛋白資料，優先建立 domain-level chain selection 與 residue numbering 對應表。
- 對 Cardiac Myosin，先不要把 `6C1H` 當作 Mavacamten holo ground truth；可暫時作為 mechanical state comparison target。
