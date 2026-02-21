# I want to find academic papers that focus on discrete operational simulations of COVID-19 spread that include the effect of vaccination strategies.

## Overview

Discrete, individual-level simulations of COVID-19 with explicit vaccination strategies are now well developed—from high-fidelity, georeferenced agent-based models (ABMs) such as GERDA, Covasim derivatives, EpiGraph, and PanSim used for operational policy analysis [1,2,10,14,15,16,18,25,32,38,43,44,63], to large-scale national and global models [2,14,42,43,68,91]—and they converge on a few robust insights: early and fast rollout, elderly/high‑risk prioritization for mortality reduction, network‑ or spatial‑targeted vaccination to curb transmission, and the necessity of maintaining non‑pharmaceutical interventions (NPIs) during rollout.

### Overall State of the Field

#### **Model landscape and relevance to your goal**

- **Highly relevant, discrete operational models** were found in large numbers, especially:
  - **Georeferenced, behaviorally rich ABMs** like **GERDA** for German municipalities [1,23,70], **Luxembourg ABM** [16], **PanSim** (Hungarian town) [10], **Catalonia ABM** [15], and small‑town ABMs (New Rochelle) [48].
  - **Covasim and derivatives** (US‑wide, Lombardy, Aschaffenburg, optimization, social norms) [14,32,38,44,46,64].
  - **State‑scale operational ABMs** for North Carolina and other US regions [25,34,36].
  - **Large national/global ABMs** for Spain (EpiGraph) [2,18], USA [14,19,20,42,43], 148 countries [68], and a full‑US platform (EPICAST 2.0) [91].
- These models:
  - **Explicitly represent individuals and contacts** (household, school, workplace, community, transportation, mobility networks).
  - Include **rich vaccination processes**: prioritization rules, multiple products, capacity constraints, 2‑dose courses, boosters, waning immunity, and often variants [1,2,10,14,15,16,18,19,20,25,32,38,43,44,63].
  - Are often **calibrated and validated to real data**, making them genuinely “operational.”
- A second cluster of **simpler ABMs / network simulations** focuses on **vaccination strategies in stylized networks** rather than full data calibration but is methodologically important for prioritization and network effects [3,7,21,35,39,40,49,62,65].

**Bottom line:** For your topic—**discrete operational simulations of COVID-19 spread with vaccination strategies**—the literature is both **rich and diverse**, with multiple mature platforms and numerous policy‑oriented applications.

---

### Core Policy Insights from Discrete Vaccination Simulations

#### **1. Who to vaccinate first: elderly vs high-contact vs spatial targeting**

**Elderly / high‑risk prioritization to minimize deaths**

- Across calibrated ABMs for diverse settings (US, France, Luxembourg, Hungary, Spain, Germany), **prioritizing elderly or high‑IFR groups robustly minimizes deaths** when vaccine supply or rollout speed is constrained [1,10,16,18,19,20,24,25,31,33,38,40,48,80].
- Examples:
  - **PanSim** shows **vulnerable‑first** reduces mortality but allows more infections; **occupational‑risk‑first** reduces infections but increases deaths [10].
  - **GERDA** finds **elderly‑first** minimizes fatalities at low coverage even when high‑contact vaccination better controls spread [1,23].
  - EpiGraph‑Madrid, Moghadas’ US ABMs, and the NC ABMs all confirm **elderly and comorbid priority** as mortality‑optimal under real constraints [18,19,20,25,34,36,43].

**High‑contact / network‑central targeting to minimize infections**

- **Network‑centric ABMs** (on real or synthetic networks) show that vaccinating **high‑degree / high‑centrality nodes or their neighbors** strongly suppresses transmission [1,3,7,8,21,35,39,65]:
  - Chen/Marathe’s ABMs on realistic Virginia networks show **degree‑based allocation** outperforms age‑based strategies in reducing infections, hospitalizations, and deaths when doses are scarce [3,8].
  - Miró Pina et al. demonstrate on heterogeneous power‑law networks that vaccinating the **most connected** or via **neighbor sampling** can lead to early epidemic extinction; targeting least connected performs worst [7,21].
  - GERDA shows that vaccinating highly interactive agents **lowers the effective herd‑immunity threshold** and outbreak risk, but does not minimize deaths at low coverage [1,23,70].

**Combined and dynamic prioritization**

- Several studies show **non‑trivial trade‑offs and “branching optimality”**:
  - GERDA and related work show that **naïve combinations** (e.g., partial elderly + partial high‑contact) can be **worse than pure strategies** because of network nonlinearities [1,23].
  - Theoretical work aligned with ABM results indicates that **high‑contact‑first becomes optimal for deaths only when vaccination rates are high and NPIs strong**; at lower vaccination rates, elderly‑first dominates [24,39,74,106].
  - Spiliotis et al. (small‑world ABM) identify an **optimal age‑priority split** (~4/5 of daily doses to >65 in their context) depending on contact rate [39].

**Spatial and location‑targeted vaccination**

- **Spatially explicit ABMs and geo‑stochastic models** suggest that **focusing scarce vaccines on high‑density, high‑mobility, or high‑incidence areas** yields larger reductions in cases and sometimes deaths than uniform allocation [2,18,26,29,37,45,52,56,61,68,82,85].
  - Mobility‑network simulations for the US show that vaccinating a small set of **central census block groups** can be ~2–2.5× more effective than random additional vaccination [37,45].
  - Global ABM for 148 countries finds that raising **low‑coverage countries to minimum thresholds (e.g., 10–20%)** averts more global cases/deaths than further increasing already high‑coverage countries [68].
  - Simpler ABMs highlight that **global equity in vaccine distribution** reduces mutation risk and long‑term burden [52,56].

**Take‑home:** 
- **Deaths vs infections** is the central trade‑off: **elderly‑first** minimizes deaths at constrained supply; **high‑contact / network‑targeted** strategies minimize infections and can reduce deaths when rollout is fast and NPIs strong.
- **Spatial targeting** (high‑density or mobility hubs) is consistently superior to uniform per‑capita allocation when geography is modeled [2,37,45,68,82].

---

#### **2. When and how fast to vaccinate: timing, capacity, and dosing**

**Start time and speed (capacity)**

- Virtually all ABMs and hybrid models agree: **earlier and faster rollout produces disproportionate reductions in infections, hospitalizations, and deaths** [4,10,14,18,19,20,25,34,36,43,68,81].
  - North Carolina ABMs estimate that **earlier pediatric vaccination and earlier boosters** could have reduced peak Delta and Omicron hospitalizations by up to **10–42%** and cumulative deaths by ~9% [4,34,36].
  - PanSim and EpiGraph show early rollout relative to variant waves is crucial for preventing large surges [2,10,18].
  - Moghadas’ US ABMs show **halving the pace** (same final coverage) results in substantially more infections and deaths; the multi‑variant study attributes ~275k deaths and 1.2M hospitalizations averted to the actual pace of US rollout vs counterfactuals [43].
  - The national AI‑driven ABM for the US shows that **hesitancy‑induced slower uptake**, even with same eventual coverage, markedly reduces averted infections and deaths [42].

**Delayed second dose / one‑vs two‑dose policies**

- Several ABMs explore **dose‑interval extension** and **first‑dose–first strategies**:
  - **Romero‑Brufau ABM** (US county) shows that **delaying second doses** to expand partial coverage often **reduces hospitalizations/deaths** when:
    - single‑dose VE is high (≥70–80%);
    - daily vaccination capacity is modest (≤0.3% population/day);
    - variant immune escape is not extreme [31,33].
  - **EpiGraph‑Madrid** finds that **extending the second dose interval to 56 days** for elderly (vs manufacturer schedules) reduces infections and deaths by covering more individuals earlier, timing full protection closer to the wave peak [18].
  - **Small‑world ABM** [39] and hybrid immune‑response models [57] corroborate that **single‑dose emphasis** can be favorable under moderate transmission and limited supply, but is sensitive to contact rates.
- These benefits are contingent on assumptions about **single‑dose VE, waning, and variants**; models without explicit waning or variant escape may **overestimate** the advantage of aggressive delay policies once Delta/Omicron are present [2,84,87].

**Take‑home:** 
- **Time to coverage** is at least as important as **final coverage**; operationally, policies that **accelerate early coverage—especially of high‑risk groups—dominate**.
- **Extended dose intervals / first‑dose–first** can be beneficial in some contexts, but robust evaluation requires **variant‑aware ABMs with waning immunity**.

---

#### **3. Interaction with NPIs, behavior, and hesitancy**

**NPIs and vaccination are complementary**

- Across ABMs, **vaccination alone rarely controls spread quickly**; NPIs remain pivotal during rollout [1,10,14,16,24,25,26,29,32,34,35,36,51,66,77]:
  - COVAM and NC ABMs show that **maintaining masks and distancing** during rollout significantly lowers infections and peak hospitalizations compared to removing NPIs at the start of vaccination [25,26,29,34,35,36].
  - GERDA shows that **adaptive NPIs** (timing and strength of lockdowns) are required even with targeted vaccination to avoid ICU overload, due to stochastic wave bimodality [1].
  - EpiGraph and Covasim‑based regional models explicitly co‑simulate NPIs (closures, masks, testing, tracing) with vaccination; optimal strategies often involve **delayed relaxation of NPIs** until coverage is high in key groups [2,14,18,24,32,38].
  - Sector‑specific ABMs (e.g., food industry) find vaccination is too slow as a **reactive** measure; proactive distancing and biosafety are more cost‑effective for acute control [66].

**Behavior and compliance, including paradoxical effects**

- A subset of ABMs includes **behavioral feedbacks**:
  - **Li & Giabbanelli** show that, under limited capacity and specific prioritization, **higher vaccine compliance can paradoxically increase infections** because compliant low‑risk individuals saturate rollout, delaying protection of higher‑contact groups [14].
  - **Gozzi et al.** (compartmental) and **COVAM** implicitly or explicitly model behavioral relaxation when vaccinated, reducing vaccine impact [26,29,77].
  - **Social norms and misperception** are modeled in newer Covasim extensions; adjusting perceived uptake can change actual uptake and thereby transmission [64].
- Vaccine **hesitancy** is treated explicitly in several ABMs [26,29,32,40,41,42]:
  - Higher hesitancy **slows effective rollout** and diminishes the benefits of vaccination even if theoretical supply would permit high coverage [40,41,42].
  - Karabay et al. find that **only the combination of high rate and low hesitancy** leads to rapid suppression [41].

**Take‑home:** 
- Discrete simulations strongly support **maintaining NPIs during rollout** and explicitly modeling **behavioral adaptation, hesitancy, and social norms**, as these can materially alter the effects of vaccination strategies.
- For operational use, **vaccination strategy design must be coupled with realistic NPI and behavior scenarios**, not evaluated in isolation.

---

#### **4. Children, boosters, and variants**

**Vaccinating children and adolescents**

- State‑scale ABMs for North Carolina, Covasim derivatives, and other models consistently find that **pediatric/adolescent vaccination significantly reduces school‑age infections and peak hospitalizations and benefits the wider community** [4,34,36,38,101]:
  - NC ABMs estimate 30–45% reductions in cumulative infections among 5–19‑year‑olds and ~31–39% reductions in peak hospitalizations across masking scenarios when child vaccination reaches 50–100% of adult uptake [34,36].
  - Earlier availability of pediatric vaccines would have further dampened Delta/Omicron waves [4].
  - Covasim‑Aschaffenburg and age‑structured SEIR models for the Netherlands and elsewhere reach similar qualitative conclusions [38,101].

**Variants, waning, and boosters**

- Advanced ABMs (EpiGraph, GERDA, Catalonia, Covasim‑based regional models, multi‑variant US ABM) explicitly model **multiple variants and variant‑specific VE**, often with **waning and boosters** [1,2,10,15,32,38,43,67,84,87,104]:
  - EpiGraph treats Alpha, Delta, Omicron with age‑ and variant‑dependent VE and waning; Omicron’s higher transmissibility and partial immune escape show that **previously adequate strategies may no longer suffice** without boosters [2].
  - Moghadas’ multi‑variant US ABM quantifies how vaccination prevented a **much more severe Delta wave**, illustrating the importance of **timely coverage before variant dominance** [43].
  - Multi‑strain compartmental models [84,87] and ABM‑linked immunity frameworks [104] emphasize that **waning and variant immune escape** substantially affect long‑term dynamics and necessary booster policies.
- Periodic‑vaccination modeling (mostly non‑ABM but informative) suggests that **constant, distributed booster strategies** may avoid susceptibility waves induced by large synchronized booster pulses [102], a concept that ABMs with explicit waning could explore at individual level.

**Take‑home:** 
- In discrete simulations, **child vaccination and booster timing** are critical for controlling variant‑driven waves, especially Delta and Omicron.
- Future discrete modeling work should treat **multi‑variant, waning immunity processes and boosters** as standard components rather than add‑ons.

---

### Methodological and Platform Takeaways for Future Work

#### **Key platforms and exemplars**

- **Covasim** and **OpenABM‑Covid19** [44,63] are the dominant **open, extensible ABM platforms**; numerous studies customize them for specific regions, vaccination strategies, and optimization frameworks [14,18,32,38,46,50,54,64,91].
- **GERDA** [1,23,70], **EpiGraph** [2,18], **PanSim** [10], **COVAM** [26,29], and **EPICAST 2.0** [91] are exemplars of **bespoke, high‑fidelity operational ABMs** with vaccination modules.
- Hybrid and specialized models—e.g., **ABM + DES for hospital/immune processes** [27,57], **ABM + optimization/OR/RL** [39,46,59], and **sector‑specific ABMs** like FInd CoV Control [66]—illustrate **integrated decision‑support workflows**.

#### **Common modeling choices and their implications**

- **Immunity representation**:
  - Early ABMs often use **all‑or‑nothing immunity and no waning**; more recent work uses **leaky immunity, outcome‑specific VE, and waning functions** [40,41,84,104].
  - Manicom et al. [104] provide a valuable **framework for mapping empiric VE** to ABM parameters via simulated secondary attack rates; this is important if you aim for realistic VE calibration.
- **Network structure**:
  - Models vary from **age‑mixing matrices with homogeneous mixing within location types** [16,19,20,24,26] to explicit **multi‑layer contact networks** [1,2,14,44,63] and **complex social/contact networks at national scale** [42,68,91].
  - Network choice strongly influences **effectiveness of contact‑based prioritization** and **estimates of herd‑immunity thresholds** [1,7,21,23,39,62,65].
- **Calibration and validation**:
  - Operational ABMs typically calibrate to **cases, hospitalizations, deaths**, and sometimes **multi‑wave trajectories**, often using **scenario‑based rather than rigorous parameter inference** [1,2,10,15,16,18,24,25,26,32,38,43].
  - This matters for **transferability**: policy conclusions are often region‑ and time‑specific, especially across variant eras.

---

### Gaps and Opportunities

Given your interests, the literature suggests several **open areas** where new work would be impactful:

- **Unified variant–immunity–behavior modeling** in discrete ABMs:
  - Only a few models integrate **multi‑variant dynamics, structured waning immunity, boosters, and behavioral adaptation** within a single detailed ABM [1,2,15,32,38,43,104]; this is a natural direction.
- **Operational strategies under realistic behavioral feedback and hesitancy**:
  - Behavioral processes appear in some ABMs but are still relatively coarse [14,30,41,42,64]. There is room for **data‑driven, behavioral ABMs** tying vaccination strategy design to **social norms, misinformation, and hesitancy spatial clustering**.
- **Endogenous optimization/control**:
  - First steps exist (simulation–optimization for location/allocation [46], RL‑based policies [59]), but most vaccination strategies are still **pre‑specified heuristics**. Integrating **adaptive optimization** into calibrated ABMs is an obvious next step.
- **Cross‑region and global strategy design** with realistic mobility:
  - Global ABMs [68] and mobility‑network studies [37,45] are still relatively rare. A **fully integrated global ABM** that combines realistic mobility, variants, and vaccine manufacturing/logistics would be a logical extension.

---

In summary, discrete operational simulations of COVID‑19 with vaccination strategies are mature enough to provide **credible, nuanced insights for real‑world policy**, especially around **prioritization, timing, NPIs, and variant‑sensitive planning**. The most useful existing models for your purposes are the **highly calibrated, open ABMs and their derivatives** (Covasim, OpenABM‑Covid19, GERDA, EpiGraph, PanSim, COVAM, EPICAST) [1,2,10,14,15,16,18,24,25,26,32,38,43,44,63,68,91], which can also serve as concrete starting points or benchmarks for any new discrete simulations you develop.

## Categories

### Comparative Overview of Discrete COVID‑19 Vaccination Simulations

Below, I focus on papers that (i) use **discrete operational simulation** (agent‑based / network‑based / hybrid DES‑ABM) of COVID‑19 spread and (ii) include **explicit vaccination strategies**. Deterministic ODE‑only models are omitted except where useful as contrast.

---

### 1. Core Model Characteristics Across Key ABMs

#### 1.1 High‑fidelity, data‑calibrated ABMs with explicit vaccination strategies

These are the closest to “operational” decision‑support tools.

| Ref | Geography / Scale | Model type & structure | Data calibration / validation | Vaccination modeling | Variants | NPIs / behavior | Main vaccination‑strategy questions |
|-----|-------------------|------------------------|-------------------------------|----------------------|----------|-----------------|--------------------------------------|
| **[1]** GERDA (Goldenbogen et al., Advanced Science 2022) | German municipalities (e.g., Gangelt, ~10k agents) | Georeferenced **ABM** with explicit human–human interaction networks (HHIN/iHHIN); daily schedules, locations (home, work, school, hospital, public) and clinical states | Calibrated to German regional data Jan–Sep 2021; compares wave shapes, case and hospitalization time series | Multiple strategies: prioritize **elderly**, **highly interactive**, random, targeted vaccination “into” ongoing outbreaks; explicit coverage, efficacy (reduction in infection probability), waning; capacity & ICU limits | Wild‑type, Alpha, Delta explicitly modeled | Rich NPIs (school/business closure, contact reductions) and sequences; explores bimodality and stochastic die‑outs | Trade‑off: **vaccinating highly interactive agents lowers infections**, **vaccinating elderly minimizes deaths at low coverage**; population‑immunity threshold is **strategy‑dependent**, not a single number [1]. |
| **[2,18]** EpiGraph (Guzmán‑Merino et al. 2022; Singh et al. 2021) | Spain: **nationwide** (19.6M agents across 63 cities) [2]; Madrid metro (~5M) [18] | Parallel **ABM** with detailed social model (students, workers, stay‑home, elders); time‑varying contacts, multi‑layer networks and transportation | Uses Spanish Ministry of Health data for vaccination rollout & epidemiology; validation against third wave in Madrid [18] | Multiple **vaccine types** (Pfizer, Moderna, AZ, Janssen); 2‑dose + boosters, waning, age‑ and variant‑specific effectiveness; prioritization strategies (age‑based, young‑first, altered **dosing intervals**, e.g. 56 vs manufacturer) | Alpha, Delta, Omicron; Omicron with reduced VE & severity [2] | Masks, distancing, testing/quarantine, mobility restrictions | For Madrid, **elderly‑first with longer 56‑day dose interval outperforms manufacturer interval** in reducing infections and deaths; prioritizing young increases deaths [18]. For Omicron in Spain, detailed vaccine/variant interplay with mobility restrictions [2]. |
| **[10]** PanSim (Reguly et al., PLoS Comp Biol 2021) | Mid‑size Hungarian town; scalable to tens of millions | High‑performance **microsimulation ABM**, fine spatial resolution; point‑of‑interest contacts; realistic daily mobility | Fitted to local epidemic and mobility data Autumn 2020–Sep 2021 | Vaccination strategies: **occupational‑risk‑first vs vulnerable‑first**; no detailed VE heterogeneity yet, but explicit timing and coverage | Includes “new fast‑spreading variant” and vaccine rollout [10] | Extensive NPIs: closures, adaptive quarantines, targeted testing | **Occupational prioritization** reduces infections but **increases mortality**, while **vulnerable‑first** reduces deaths but raises infections; intensive vaccination + NPIs needed to suppress spread [10]. |
| **[14]** COVASIM‑US (Li & Giabbanelli, JMIR MI 2021) | USA, national‑scale | **ABM** (COVASIM‑based) with age‑stratified household/work/school/community networks | Parameter tweaks to current evidence; test delay distribution from survey; no full re‑fit of all states | 2‑dose vaccines, VE, compliance, daily capacity; infection possible between doses; age‑based prioritization; federal rollout plans (OWS vs 1M doses/day) | Single‑strain context (pre‑Delta) | Multiple NPI levels; scenarios of relaxation intensity | Under capacity constraints and relaxed NPIs, **higher vaccine compliance can paradoxically increase total infections** because compliant low‑contact groups saturate capacity while high‑contact groups remain susceptible [14]. |
| **[16]** Luxembourg ABM (Thompson & Wattam, PLoS ONE 2021) | Luxembourg (~626k pop, simulated at 10‑min resolution) | Detailed **ABM** with locations (homes, workplaces, shops, etc.), >2,000 behavioral types | Calibrated to Luxembourg case, hospitalization, death data for 2020 | 2‑dose campaign; scenarios over VE, capacity, hesitancy, timing (pre‑ vs mid‑outbreak), targeting (deaths vs transmission) | No variants; single‑strain assumption | Tests, tracing, lockdown, curfew | Shows **herd‑immunity thresholds depend strongly on targeting and hesitancy**; pre‑emptive vaccination more effective than reactive; death‑minimizing vs transmission‑minimizing targeting diverge [16]. |
| **[19,20]** U.S. ABM (Moghadas et al., medRxiv 2020; Clin Infect Dis 2021) | U.S.‑like synthetic population (10k agents; scalable) | Age‑structured **ABM** (Julia), daily contacts from age contact matrices and NB distributions | Calibrated to Re=1.5 [20] and Re=1.2 [19]; explored pre‑existing immunity 5–20% | 2‑dose mRNA‑like vaccines; VE against disease and infection; reduced VE for elderly/comorbid; rollout 30 doses/10k/day; prioritize **healthcare workers + comorbid + 65+**; coverage scenarios 10–60% | Variants not explicitly modeled (pre‑VOC era) | NPIs implicit via calibration; not explicitly simulated | At 40% coverage, vaccine reduces attack rate from 7.1% to 1.6% [20]; protection of high‑risk groups drives largest reductions in **severe outcomes** even when VE against infection is modest [19,20]. |
| **[25,34,36]** NC ABM family (Patel et al. 2021; Rosenstrom et al. 2021, 2022) | North Carolina (~10.5M, ~1M agents) | Stochastic **SEIR ABM** with household, school/work, community networks and commuting flows | Calibrated to NC infections, hospitalizations, deaths using IFR and lab‑multiplier [25]; scenario‑based extensions for children/masks [34,36] | Vaccine VE (50% vs 90%), coverage (25–75%), 6‑month rollout; later papers explicitly model **child vaccination** and **boosters/Delta‑Omicron timing**; age‑ and group‑specific uptake | Delta/Omicron context in later work [34,36] | NPIs: masks (by setting and age), school closure/hybrid, mobility; scenarios with masking removal timing | Vaccinating children substantially reduces school‑age infections and **peak hospitalizations**; earlier pediatric vaccines and boosters could have cut peak Delta and Omicron hospitalizations by up to 42% and deaths by 9% [4,34,36]. |
| **[26,29]** COVAM (Alagoz et al., PLoS ONE 2021; medRxiv 2021) | Three U.S. regions (Dane County, Milwaukee, NYC) | Region‑specific **ABM**, 8 COVID states, age‑specific contact numbers | Calibrated to regional epidemic data and social‑network literature | Explores **coverage**, **effectiveness**, and **rollout speed**, but no detailed age‑targeting; vaccination reduces susceptibility with fixed effectiveness | No explicit variants | NPI adherence scenarios (steady vs dynamic) | The effect of vaccination depends critically on **concurrent NPI adherence**; with poor NPI adherence, higher coverage and VE are needed to reach “pandemic control” [26,29]. |
| **[32,38,46,64]** Covasim‑Lombardy, Aschaffenburg, vaccine‑center optimization, social norms (Cattaneo et al. 2022; Krebs et al. 2021; Yin et al. 2023; Mulutzie et al. 2025) | Italian regions, German city, generic regions (Covasim‑based), U.S.‑style for social norms | All build on **Covasim ABM** [44]: age/sex/comorbidity‑structured agents with multi‑layer contact networks | Region‑specific calibration (e.g., Lombardy epidemic curves [32]; Aschaffenburg historical course [38]); optimization framework validated via iterative coupling [46] | Full Covasim vaccination module: multiple products, schedules, waning and variant‑specific VE (in later Covasim versions), age‑targeting, capacity; [46] adds explicit compartments for 1st/2nd dose; [64] adds **social‑norm–driven uptake** | Variants modeled via Covasim (Delta, Omicron, etc.) in more recent studies | NPIs: masks, distancing, testing, tracing, closure, etc. | Used to compare age‑regimes [38], regional strategies [32], **vaccine center location/allocation optimization** [46], and **effects of social norms on uptake** [64]. These works highlight how **context‑specific calibration** and detailed VE/waning representation are crucial for realistic policy evaluation. |
| **[42]** U.S. 288M‑agent ABM (Bhattacharya et al., IEEE Big Data 2021) | Entire U.S., 288M agents, 12.6B daily edges | Nationwide **ABM** over social contact network; disease progression and interventions modeled within HPC workflow | Calibrated with surveillance data and state‑level epidemic curves | Realistic vaccine uptake, **acceptance trends**, production schedules; scenarios of hesitancy vs high acceptance; rollouts by age and risk | Variants not detailed in abstract | NPIs via social distancing guidelines embedded in workflow | Vaccine hesitancy that slows rollout **substantially reduces infections and deaths averted** even when final coverage is the same; highlights importance of **rate** vs eventual coverage [42]. |
| **[43]** U.S. multi‑variant ABM (Moghadas et al., medRxiv 2021) | U.S., national | Age‑stratified **ABM** calibrated to US incidence (Oct 2020–Jun 2021) | Fitted closely to national incidence; used for counterfactuals | Realistic 2‑dose rollout by age; dose‑ and variant‑specific VE; actual vs half‑speed rollout and “no vaccine” scenarios | Explicitly models Wuhan‑1, Alpha, Gamma, Delta with variant‑specific VE | NPIs implicit in data calibration; not independently varied | Estimates that actual rollout **averted ~275k deaths and 1.2M hospitalizations** vs no vaccination; halving pace markedly worsens outcomes [43]. |
| **[48]** New Rochelle ABM (Truszkowska et al., Adv Theory Simul 2021) | Small U.S. town (New Rochelle, NY) | High‑resolution **ABM** with explicit buildings, occupations, treatment types | Calibrated to first‑wave cases and deaths | Vaccination scenarios: vaccinate specific occupational groups vs retirement‑home residents vs mass (~25%) immunization; vaccine implemented as **instantaneous full protection** | No explicit variants | NPIs (testing, hospital capacity) but vaccination scenarios run w/out lockdown/school closure | Shows that **targeting nursing‑home residents** yields larger mortality reductions than targeting workers; mass vaccination has largest effect. Vaccination is modeled as single‑time mass immunization, so temporal rollout effects are not addressed [48]. |
| **[68]** Global ABM (Li & Huang, PLoS Comp Biol 2022) | 148 countries (~198M agents) | Multi‑country **ABM** with demographically representative agents and country‑specific calibrations | Fitted to country‑level data to June 2021 for 148 countries | Simulates global allocation rules: minimum coverage thresholds (10%, 20%, 26%) vs status‑quo; outcomes in cases and deaths averted | Implicit multi‑wave (variant‑driven) dynamics via data but no explicit variant compartments in abstract | Various country‑specific NPIs via data; not explicitly decomposed | Supporting WHO/COVAX discussions: increasing vaccination in low‑coverage countries (e.g., to 10–20%) is much more **efficient** in averting global cases/deaths than marginally increasing coverage in already well‑vaccinated countries [68]. |
| **[91]** EPICAST 2.0 (Alexander et al., 2025) | U.S., ~324M agents | Nation‑scale **discrete‑space ABM** (UrbanPop synthetic population, detailed workplaces, schools) | Designed for calibration to U.S. respiratory pathogen data; SARS‑CoV‑2 is main use case | General vaccination functionality: different products, timings, targeted/phased programs; specifics not detailed in abstract | Pathogen‑agnostic; variant modeling left to pathogen module design | Broad set of NPIs and targeted policies; economic/sectoral structure via industries | Framed as a **platform** rather than a specific vaccine‑strategy study; useful for future work where one wants to co‑opt a validated large‑scale ABM with explicit vaccination machinery [91]. |

Other discrete ABMs are more conceptual, localized, or narrower in vaccination representation; they are covered in subsequent thematic comparisons.

---

### 2. Vaccination Prioritization: Elderly vs High‑Contact vs Spatial / Network Targeting

#### 2.1 Age‑ vs interaction‑based prioritization (individual‑level targeting)

| Strategy dimension | Key discrete‑simulation refs | Core findings & nuances |
|--------------------|-----------------------------|--------------------------|
| **Prioritize highly connected / high‑contact individuals** | **[1,23]** GERDA, **[3,8]** Virginia social‑network ABM, **[7,21]** connectivity/network simulation, **[35]** household‑network ABM, **[39]** small‑world ABM, **[17,65]** generic network immunization, **[37,45]** mobility‑hub targeting, **[50]** EVI‑based ABM, **[59,99]** RL & MAS vaccine allocation | On heterogeneous networks, **targeting high‑degree / high‑centrality nodes** (or their neighbors) consistently **reduces infections and often deaths more than random or age‑only strategies** when vaccine supply is limited and when the objective includes transmission reduction [1,3,7,8,21,35,39,65]. GERDA and its preprint [1,23,70] show that vaccinating highly interactive individuals **reduces wave probability and “population‑immunity threshold”**, but may not minimize deaths at low coverage if elderly remain unprotected. Network‑based ABMs emphasize operational proxies (acquaintance vaccination, location targeting, EVI index) to approximate degree targeting [7,21,37,45,50]. |
| **Prioritize elderly / high‑IFR groups** | **[1,10,16,18,19,20,24,31,33,38,40,48,60,71,74,80]** | In virtually all ABMs that explicitly model age‑specific severity, **vaccinating elderly/high‑IFR individuals first minimizes deaths** when coverage or rollout speed is limited [1,10,18,19,20,24,31,33,38,40,48,74,80]. PanSim [10], GERDA [1], and France ABM [24] demonstrate a classic trade‑off: **elderly‑first → fewer deaths, more infections; high‑contact‑first → fewer infections but more deaths**, especially under modest coverage. Romero‑Brufau et al. [31,33] (ABM with age‑priority) systematically show that age‑priority dominates random allocation for mortality across dosing‑interval strategies. |
| **Combined strategies & “branching optimality”** | **[1,23,24,39,74]** | GERDA and its preprint [1,23,70] show that **naïvely combining elderly‑ and interaction‑based strategies can be worse** than pure strategies, due to nonlinear network effects (e.g. partially shielding high‑contact but still leaving infection paths into vulnerable clusters). Hoertel et al. [24] (France ABM) and Rodríguez et al. [74] (age‑structured dynamic model) show **parametric regions** where high‑contact‑first becomes optimal once vaccination rate is high enough (>~1% of population/day in [106]) and NPIs are strong, whereas at lower vaccination rates, elderly‑first is optimal for deaths. Spiliotis et al. [39] (small‑world ABM) identify an optimal age‑priority split (~4:5 in favor of >65) under given contact levels. |
| **Spatial / location‑targeted vaccination** | **[2,18,26,29,37,45,52,56,61,68,82,85]** | Spatially explicit ABMs and geo‑stochastic models show that **targeting high‑incidence, high‑mobility, or high‑density regions** with scarce vaccines yields more cases/deaths averted than pro‑rata allocation. EpiGraph‑Madrid [18] implicitly targets the metro area; COVAM [26,29] shows region‑specific thresholds. Mobility‑network ABMs [37,45] quantify hub and homophily effects: vaccinating highly central CBGs can be **1.5–2.5× more effective** than random extra vaccination [45]. Geo‑stochastic SEIQRS‑V models [82,85] find prioritizing dense cities beats homogeneous nationwide campaigns under shortage. Zia’s ABM [52,56] highlights global vs regional equity: **globally fair distribution** can reduce mutation‑driven outbreaks, albeit in a relatively simple ABM. |

**Synthesis for prioritization:**

- **Mortality‑minimizing** strategies in discrete ABMs almost always vaccinate **elderly/high‑IFR first** [1,10,18,19,20,24,31,33,38,40].
- **Transmission‑minimizing** strategies benefit from **network‑ or mobility‑based targeting** of high‑contact individuals or hubs [1,3,7,8,21,35,37,39,45,65].
- The **optimal balance is contingent** on:
  - vaccination rate / capacity [24,39,74,106];
  - NPI strength [10,24,26,29,77];
  - immune escape and variant transmissibility [1,2,43].
- Combined or naïve multi‑objective strategies can be **non‑monotone** and require careful evaluation, not just linear weighting [1,23,39].

---

### 3. Rollout Timing, Pace, and Dose Scheduling

#### 3.1 Timing of vaccination campaigns

| Aspect | Key refs | Comparative findings |
|--------|----------|----------------------|
| **Early vs delayed start** | **[4,6,10,14,18,31,33,34,36,48,60,68,81,89,90]** | Across ABMs and hybrid models, **earlier vaccination consistently yields disproportionate reductions in deaths and peak load**, especially when coinciding with rising waves or emergent variants: earlier pediatric vaccines and boosters → 10–42% lower Delta/Omicron peaks in NC [4,34,36]; earlier mass immunization → strongly reduced peaks in PanSim [10]; EpiGraph‑Madrid [18] shows early and longer‑interval elderly vaccination pre‑empts a third wave. Hybrid simulation [27,57] and several compartmental models (e.g., [84,90]) confirm strong sensitivity of peak cases to start date. Small‑town ABM [48] shows that one‑time vaccination on March 2 significantly changes first‑wave outcomes, but because it models instantaneous vaccination, it’s more of a “what if mass immunity had been available” thought experiment. |
| **Speed / capacity of rollout** | **[14,19,20,24,25,26,29,31,33,39,42,43,68,86,102]** | Many ABMs treat **daily vaccination capacity** as a control. Higher capacity generally leads to lower cumulative burden, but the **marginal value depends on NPIs and prioritization**: COVAM [26,29] shows that with low NPI adherence, faster vaccination is crucial to reach control; Moghadas et al. [19,20,43] show that halving pace (maintaining same eventual coverage) substantially increases infections and deaths. National ABM [42] demonstrates that **hesitancy‑induced slowdown** (same final coverage) reduces averted infections from 6.7M to 4.5M and deaths from 39.4k to 28.2k. Global ABM [68] translates daily extra doses into global case/death reductions, emphasizing scale. Kosinski’s discrete‑time SEIRS model [86] highlights that at higher R0, vaccination must be both rapid and extensive to keep post‑vaccine incidence low. Xiao et al. [102] add that **pulse vs constant booster campaigns** change long‑term susceptibility profiles. |

#### 3.2 Dose interval and one‑ vs two‑dose policies

| Dose‑policy question | Key ABM / discrete refs | Main comparative results |
|----------------------|-------------------------|--------------------------|
| **Delay second dose vs on‑label schedule** | **[18]** EpiGraph‑Madrid, **[31,33]** Romero‑Brufau ABM, **[39]** small‑world ABM, **[57]** hybrid WSC model, plus several compartmental studies | EpiGraph‑Madrid [18] finds that **extending the second dose interval to 56 days** for elderly (vs manufacturer intervals) **reduces infections and deaths**, because more people receive partial protection earlier, and full protection is timed closer to the wave. Romero‑Brufau et al. [31,33] show in a detailed ABM that **delayed second doses** often reduce deaths when **single‑dose VE ≥~80%** and rollout ≤0.3% of population/day, especially for younger groups; they stress sensitivity to uncertain single‑dose durability. Small‑world ABM [39] and hybrid immune‑response simulation [57] broadly agree that single‑dose rollout can be advantageous in mild‑to‑moderate transmission contexts if second‑dose capacity is constrained. |
| **Single‑ vs two‑dose strategies under limited supply** | **[39]** small‑world ABM, **[31,33,39,74,95]** | Spiliotis et al. [39] demonstrate in an ABM that a **single‑dose strategy** (no second doses) with ~50% efficacy can, under certain social distancing levels, control deaths comparably to full 2‑dose strategies when vaccine supply is limited, but they also show dependence on contact levels. Romero‑Brufau ABM [31,33] suggests that when first‑dose VE is high and capacity limited, **prioritizing breadth (first doses)** over depth (completing series) improves mortality outcomes. |

**Synthesis for timing and dosing:**

- Discrete ABMs robustly support **early and fast rollout** as a dominant factor for both incidence and mortality.
- Under constrained supply, **delaying second doses** and **expanding first‑dose coverage** can be beneficial, but only when:
  - single‑dose VE is reasonably high (≈≥70–80%) [31,33,39];
  - variants with strong immune escape are not yet dominant [2,43].
- These results are sensitive to **assumptions on VE time profiles** and variants; models that ignore waning or escape (e.g., [11,31,33]) may overstate benefits of extreme delay strategies relative to later VOC context.

---

### 4. Children, Boosters, and Variant‑Sensitive Strategies

#### 4.1 Vaccinating children and adolescents

| Question | Key ABM refs | Comparative findings |
|----------|--------------|----------------------|
| **Impact of vaccinating 5–17 y/o on community outcomes** | **[4,6,34,36]** NC ABMs; **[14]** COVASIM‑US (limited children), **[38]** Covasim‑Aschaffenburg, **[101]** age‑structured SEIR (not ABM but relevant) | NC ABMs [34,36] simulate extensive **childhood vaccination + school masking** scenarios. They find that **vaccinating children (5–11, 12–17) at 50–100% of adult uptake reduces school‑age infections by ~30–45% and peak hospitalizations by ~31–39%**, and that removing school masks without child vaccination causes large increases in infections. Rosenstrom et al. [4] further show that **earlier availability of pediatric vaccines** would have significantly reduced Delta/Omicron peaks. Covasim‑Aschaffenburg [38] similarly shows that extending vaccination to younger age groups stabilizes local hospital burden. Deterministic SEIR studies (e.g. [101]) corroborate these qualitative patterns. |

#### 4.2 Boosters and variant dynamics

| Aspect | Key refs | Findings from discrete / hybrid simulations |
|--------|----------|---------------------------------------------|
| **Modeling multi‑variant epidemics with vaccination** | **[1,2,10,27,43,67,84,87]** | EpiGraph [2] explicitly contrasts Alpha, Delta, Omicron with age‑ and variant‑specific VE and reduced effectiveness against Omicron; GERDA [1] runs WT/Alpha/Delta scenarios; Moghadas et al. [43] simulate U.S. with Wuhan‑1, Alpha, Gamma, Delta and variant‑specific VE, showing that rapid vaccination prevented Delta from causing much larger mortality. Hybrid ABMs [67] model variant emergence via aerial transmission parameters; hybrid DES‑ABM [27] explores how vaccination policies under changing variants affect hospital burden. Deterministic multi‑variant models [84,87] offer more mechanistic immunity structure but less operational granularity. Overall, discrete ABMs emphasize that **variant transmissibility and VE against infection vs severe disease heavily influence which vaccination strategy (transmission vs mortality focus) is optimal** [1,2,10,43,84]. |
| **Booster campaigns** | **[2,4,6,27,34,36,38,84,87,102]** | EpiGraph [2] includes booster doses with waning VE; NC ABMs [4,6,34,36] examine adult booster timing; Covasim‑Aschaffenburg [38] considers third doses qualitatively. Results generally show that **timely boosters to elderly/high‑risk groups substantially reduce hospitalizations and deaths during Delta/Omicron waves**. Multi‑strain compartmental models [84,87] and periodic‑vaccination study [102] highlight that booster timing impacts long‑term oscillations: aggressive synchronized boosters can create future susceptibility waves, whereas steady “constant” booster policies smooth burden [102]. |

---

### 5. NPIs, Behavior, Hesitancy, and Social Norms in Discrete ABMs

#### 5.1 Interaction of vaccination with NPIs

| Focus | Key refs | Comparative insights |
|-------|----------|----------------------|
| **Joint optimization of NPIs and vaccination** | **[1,10,14,16,24,25,26,29,32,34,35,36,42,46,51,57,59,66]** | Many ABMs emphasize that **vaccination is not sufficient alone** to control outbreaks when coverage is incomplete and variants are more transmissible. COVAM [26,29] and NC ABMs [25,34,36] show strong synergy: **maintaining masks and distancing during rollout** markedly reduces infections and hospitalizations; premature lifting can negate vaccine benefits. GERDA [1] shows that even with targeted vaccination, **adaptive NPIs** are needed to avoid ICU overload due to bimodality. EpiGraph [2] explores lockdown and mobility restrictions alongside variants/vaccination. Hybrid ABM‑DES models [27,57] and RL‑controlled ABMs [59] investigate algorithmic policies over lockdown + vaccination, highlighting trade‑offs between economic and health objectives. FInd CoV Control [66] in food industry context finds vaccination is too slow as a **reactive** tool; proactive NPIs (physical distancing, biosafety) are more cost‑effective. |
| **Behavioral adaptation and vaccine complacency** | **[14,32,42,64,77,86]** | Li & Giabbanelli [14] uncover a counterintuitive effect: under limited vaccine capacity and uniform age‑based prioritization, **higher vaccine compliance can increase infections** because low‑risk groups monopolize doses, delaying vaccination of higher‑transmission groups. COVAM [26,29] approximates behavioral responses via dynamic NPI adherence; Gozzi et al. [77] (compartmental) explicitly model risk compensation. Bhattacharya et al. [42] and Kosinski [86] focus on hesitancy’s impact on rollout speed; Kosinski’s discrete SEIRS model shows pockets of refusal can sustain high endemic case rates even with an “ideal” vaccine. Mulutzie et al. [64] extend Covasim with **social‑norm–based vaccination uptake**, showing how misperceptions of community uptake can slow coverage; this opens a path to integrating more detailed behavioral psychology into ABMs. |

#### 5.2 Hesitancy and acceptance

- **Hesitancy modeled explicitly in discrete ABMs**:
  - **COVAM** [26,29]: adherence scenarios.
  - **National ABM** [42]: parameterized vaccine‑acceptance trends; demonstrates that identical final coverage with slower uptake yields fewer averted outcomes.
  - **Karabay et al.** [41]: particle‑based ABM with a vaccination module including hesitancy; shows combination of high vaccination rate + low hesitancy is key for fast suppression.
  - **Covasim‑Lombardy** [32] and France ABM [24] include uptake/acceptance parameters.

These findings converge on **early, fast uptake** being critical; models with explicit temporal acceptance highlight that **time to coverage** matters at least as much as **final coverage**.

---

### 6. Conceptual ABMs and Framework Papers

A number of works contribute more on **methodological** than policy‑quantitative dimensions but are relevant for experts thinking about model design:

- **Covasim** [44] and **OpenABM‑Covid19** [63] are **platform papers** specifying how vaccination is parameterized at the individual level (leaky vs all‑or‑nothing, time‑varying protection, variant‑specific VE, targeting, waning). Many downstream ABMs rely on these.
- **CovidSIMVL** [13,55] and **CovidSIMVL WAVE/PARTICLE** [55] show how **microscale transmission dynamics** (localized vs well‑mixed) interact with vaccination schedules; they underline that identical vaccine parameters can yield very different outcomes under different spatial/temporal contact patterns.
- **Manicom et al.** [104] is a dedicated **immunity modeling** discussion for ABMs, mapping empirically observed VE for different outcomes to per‑contact protection in discrete models; it is valuable for reconciling **ABM internal parameters with clinical VE estimates**.
- **Hybrid ABM + DES** [27,57] illustrate the integration of **immune‑response micro‑models** or **hospital process models** into population ABMs, useful when vaccine effects on severity and resource use are key.

---

### 7. Cross‑Cutting Comparative Themes

#### 7.1 Where discrete ABMs agree

Across the discrete operational COVID‑19–vaccination simulations:

- **Early and fast vaccination rollout** is consistently beneficial; delays and slow pace yield disproportionately worse outcomes, especially with emerging variants [4,10,18,19,20,34,36,43,68,81].
- **Elderly/high‑risk prioritization** robustly minimizes deaths under constrained supply [1,10,18,19,20,24,31,33,38,40,48,80].
- **High‑contact / network‑central vaccination** is superior for reducing infections and can sometimes also reduce deaths when vaccine supply is ample and NPIs are strong [1,3,7,8,21,35,37,39,45,65].
- **NPIs remain crucial** during rollout; dropping them prematurely undermines vaccine impact [1,10,24,25,26,29,34,35,36,77].
- **Heterogeneity matters**: network structure, mobility, and socio‑demographic differences materially change optimal allocations and observed thresholds [1,2,7,10,16,18,26,32,37,45,68].

#### 7.2 Where conclusions depend on model assumptions

- **Dose‑interval extension** and **single‑dose strategies**: beneficial in several ABMs [18,31,33,39], but these models often assume:
  - strong single‑dose VE;
  - no rapid waning or variant‑specific immune escape.
  For Delta/Omicron contexts, results become more ambiguous and require models with explicit waning and variant VE [2,84,87].
- **Herd‑immunity thresholds**: GERDA [1] and related work show that thresholds are **strategy‑ and network‑dependent**; compartmental estimates (e.g., simple \(1 - 1/R_0\)) are inadequate in heterogeneous ABMs.
- **Behavioral feedbacks**: only a subset of ABMs endogenize behavior [14,32,42,64,77]. Where they do, results on optimal prioritization and timing can shift substantially (e.g., paradoxical infection increases at higher compliance [14]).

---

### 8. Practical Guidance for Using These Papers

For an expert designing or comparing discrete vaccination simulations:

- Use **[44] Covasim**, **[63] OpenABM‑Covid19**, or **[91] EPICAST 2.0** as **base platforms** when you need a thoroughly tested ABM with vaccination and variants.
- Look to **GERDA** [1,23,70] and **PanSim** [10] for **fine‑grained, georeferenced human–human interaction modeling** and rigorous exploration of strategy‑dependent herd‑immunity.
- Use **EpiGraph** [2,18], **NC ABMs** [25,34,36], and **national/global ABMs** [42,43,68] for examples of **large‑scale, policy‑oriented simulation studies** with real‑world data and variant‑aware vaccination.
- For **network‑centric prioritization**, **Chen et al.** [3,8] and **Miró Pina et al.** [7,21] provide detailed analyses of degree‑based strategies and operational proxies.
- For **dose‑interval and one‑ vs two‑dose questions**, **Romero‑Brufau et al.** [31,33] and **Spiliotis et al.** [39] are key; cross‑check their assumptions before extrapolating to VOC‑era contexts.
- For integrating **social norms, hesitancy, and behavioral adaptation**, **Li & Giabbanelli** [14], **Bhattacharya et al.** [42], **Karabay et al.** [41], and **Mulutzie et al.** [64] offer complementary approaches.

These comparisons should help you position any new discrete operational COVID‑vaccination simulation in relation to existing work, both methodologically and in terms of substantive vaccination‑policy insights.

## Timeline

### Historical Evolution of Discrete COVID‑19 Simulation with Vaccination

#### **Early Pandemic Phase (2020): Prototyping Individual‑Level COVID–Vaccine Models**

**Foundational ABMs and network models**

- **Covasim** [44] and **OpenABM‑Covid19** [63] are key early (mid‑2020) general‑purpose ABMs:
  - Both provide **discrete, individual‑level models** with realistic **age structure, multi‑layer contact networks, testing and tracing**, and explicit hooks for **vaccination as a pharmaceutical intervention** [44,63].
  - At release, vaccination modules were more **conceptual** (modify susceptibility or symptom risk) with less detail on rollout logistics, but they set the **software and conceptual infrastructure** for later vaccination studies and became widely reused and extended [1,10,14,16,18,32,38,46,50,51,54,63,64,66,91,104].

- **Goldenbogen et al.**’s first **GERDA** paper (optimality in vaccination strategies) [23] and the later variant [70] developed a **highly granular geospatial ABM**:
  - Individual agents with **locations, schedules, and explicit human–human interaction networks** (HHIN/iHHIN).
  - Vaccination implemented as **targeted immunization at simulation start or into an ongoing outbreak**, comparing **elderly‑first vs highly interactive vs combined strategies** [23,70].
  - Early, influential demonstration that **network heterogeneity and bimodality** make the **“population immunity threshold” strategy dependent**, not a fixed number.

- **Network‑level SEIRV models** such as **Tetteh et al.** [62] and **SHEM** [60] bridged between compartmental and ABM:
  - Explicit **graph‑based spread** and simple vaccination (mass vs ring vaccination) to explore **herd‑immunity thresholds** [62].
  - **SHEM** emphasized **heterogeneous subpopulations** and showed that **targeted vaccination of hotspot/vulnerable subclusters** could halt spread [60].

**Conceptual milestones (2020)**

- Establishment of **agent‑based and network models as central tools** for vaccine policy exploration (priority groups, herd‑immunity thresholds).
- Introduction of **heterogeneity in contact structure and geography** as critical for vaccination strategy evaluation.
- Tools like Covasim/OpenABM were deliberately designed to be **extensible platforms**, anticipating vaccine rollout [44,63].

---

#### **Expansion and Diversification (2021): From “Should we vaccinate?” to “How, whom, and when?”**

By 2021, vaccines were real, and ABMs shifted from conceptual to **operational, policy‑driven analyses**, with much richer vaccination modules.

**1. Age‑ and risk‑based prioritization at country/regional scale**

- **US‑focused ABMs (Moghadas et al.)** [20,19,43]:
  - Age‑stratified ABMs in Julia, explicitly modeling **two‑dose campaigns, prioritized groups (healthcare workers, elderly, comorbid), rollout pace, and coverage (10–60%)** [20,19].
  - Later work incorporated **multiple variants (Wuhan, Alpha, Gamma, Delta)** and **real US vaccine rollout data** to estimate **infections, hospitalizations, deaths averted** [43].
  - Helped fix the **now‑canonical framing** of vaccination scenarios: *coverage × efficacy × rollout speed × prioritization*.

- **North Carolina ABM line (Patel et al., Rosenstrom et al.)**:
  - **Patel et al. (medRxiv)** [25] used a **state‑wide ABM** with household, school, workplace, and community networks to analyze **joint impact of NPIs and vaccination** (50–90% VE, 25–75% coverage).
  - **“Vaccinating children is crucial” series** extended the same framework to **child vaccination + masking policy** [34,36], and later **booster and pediatric timing** [4,6].
  - These works embedded vaccination in **multi‑year, multi‑variant scenarios** and are early examples of **operational decision support** for US state policy.

- **Hoertel et al. (France ABM)** [24], **Thompson & Wattam (Luxembourg)** [16], **Alagoz et al. (COVAM; US metros)** [26,29]:
  - Stochastic ABMs **calibrated to local data**, exploring whether various vaccination strategies **allow relaxation of NPIs** [24] or **advance “pandemic control” dates** [26,29].
  - Typically used **all‑or‑nothing immunity** and did **not yet include waning or variant‑specific VE**, but did systematically examine **coverage, efficacy, and rollout timing** [16,24,26].

**2. Social‑network–driven prioritization**

A second major 2021 thread asked: **should we vaccinate the elderly, or the highly connected?**

- **Goldenbogen / GERDA** [23,70] and **Miró Pina et al.** [21,7]:
  - Demonstrated through detailed ABM and simpler network models that **vaccinating the most connected individuals** can strongly reduce **outbreak probability and size**, while **vaccinating elderly first minimizes deaths at low coverage** [23,21,7,70].
  - Introduced the idea of **strategy‑dependent “herd immunity”**: optimal targets change over the course of the epidemic.

- **Rodríguez‑Maroto et al. (theory)** [106] and **Rodríguez et al.** [74] (compartmental network) echoed these insights analytically, reinforcing ABM findings that **high‑contact priority can be optimal at high vaccination rates**, while **vulnerability priority dominates at low vaccination rates**.

**3. Detailed rollout logistics and policy questions**

- **Romero‑Brufau et al.** [31,33]:
  - ABM for a US county (100k agents, household/occupation/random networks) to study **delayed second dose vs standard schedules**.
  - Sensitivity analyses over **single‑dose efficacy, vaccination rates, sterilizing vs non‑sterilizing protection**.
  - Influential in the early debate on **stretching dose intervals** under supply constraints.

- **Li & Giabbanelli (COVASIM‑based US simulations)** [14]:
  - Large‑scale ABM exploring **federal rollout plans, vaccine efficacy, compliance, daily capacity, and NPI levels**.
  - Highlighted a counter‑intuitive effect: **higher compliance can increase total infections** when capacity is limited and NPIs are relaxed, due to **priority shifting infections into high‑contact groups later**.

- **Jacob & Guo** [11] and **Truszkowska et al.** [48]:
  - Mid‑scale ABMs focusing on **elderly prioritization vs random** [11] and **targeting specific occupational groups vs mass immunization** [48].
  - These early models often assumed **instant, perfect protection and no variants** [11,48], emphasizing **policy comparison** over biological nuance.

**4. Emergence of explanatory & educational ABMs**

- **CovidSIMVL work** [13,55] and **Adam & Arduin** [49]:
  - Built ABMs specifically for **explaining mechanisms** (e.g. trial‑like comparisons of mRNA dose schedules [13], or how different transmission topologies yield different vaccination outcomes [55]).
  - Established ABMs as **communicative tools** for stakeholders, not only as forecasting engines.

**Milestones (2021)**

- Transition from generic, pre‑vaccine ABMs to **fully parameterized vaccination simulations** tied to real campaigns.
- Introduction of **dose‑timing, booster concepts, and targeting rules** (age, contact degree, households, neighborhoods).
- Recognition that **vaccination interacts strongly with NPIs** and that **strategy optimality is dynamic** in time and coverage.

---

#### **Refinement and Integration (2022–2025): Variants, waning, hesitancy, and large‑scale systems**

From 2022 onward, ABMs increasingly incorporate **variants, waning immunity, hesitancy, and system‑level logistics/optimization**.

**1. Variant‑aware, data‑driven ABMs**

- **GERDA in Advanced Science** [1]:
  - Extends earlier preprint [23] with **WT, Alpha, Delta scenarios**, community‑specific calibration (German municipalities), and **multi‑wave dynamics**.
  - Shows **vaccination strategies change the effective immunity threshold**, and that **ongoing variant introductions** plus community‑specific networks produce **bimodal outcomes** [1].

- **EpiGraph (Spain)** [2,18]:
  - High‑resolution ABM with **19.6M individuals in 63 cities**, explicit **Alpha/Delta/Omicron**, **multi‑vaccine types, boosters, waning VE by age and variant**, and realistic **Spanish vaccination data** [2,18].
  - Used to evaluate **real Omicron spread and alternative mobility/vaccination scenarios**, representing a **mature, HPC‑scale operational ABM**.

- **Bosman et al. (Catalonia)** [15]:
  - ABM built from **detailed census + mobile‑phone data**, reproducing **five waves** and explicitly modeling **age‑ and vaccine‑type‑specific rollout, dose intervals, and time‑varying VE**.
  - Directly compares **no‑vaccine, delayed, and alternative booster assumptions**, highlighting **calibration against multi‑wave data** [15].

- **Moghadas et al. 2021–22** [43] and **Cattaneo et al. (Lombardy with Covasim)** [32]:
  - Integrate **multi‑variant dynamics, empirically estimated dose‑ and variant‑specific VE**, and real dose allocation to quantify **deaths/hospitalizations averted** by actual rollout vs slower/no‑vaccine scenarios [43,32].
  - Represent the **shift from forward‑looking scenario analysis to retrospective counterfactual evaluation**.

**2. Social, behavioral, and hesitancy dynamics**

- **Bhattacharya et al. (AI‑driven US‑scale ABM)** [42]:
  - 288‑million‑node contact network with **vaccine acceptance trends** and **production schedules**, examining how **hesitancy reduces averted infections and deaths** despite equal final coverage [42].
- **Karabay et al. (Lecco particle‑based ABMs)** [40,41]:
  - Introduce **sterilizing vs effective (leaky) immunization** and **hesitancy as an explicit parameter**, showing that **high rate + low hesitancy** is critical to epidemic suppression [40,41].
- **Ben‑Zuk et al. (Israel cities)** [30]:
  - Individual‑based model combining vaccination and NPIs, comparing **neighborhood‑based targeting vs age‑based** and illustrating dependence on **local demography** [30].
- **Mulutzie et al. (social norms in Covasim)** [64]:
  - Extension of Covasim to **explicitly model social norms and perceived uptake** and their impact on **vaccine uptake and transmission**, marking a move toward **behavior–immunity feedbacks**.

**3. Optimization, operations research, and hybrid ABM–DES**

- **Yin et al. (vaccine center location/allocation + Covasim)** [46]:
  - Couples an **agent‑based Covasim** extension with a **multi‑period MIP** for vaccine centre location and dose allocation, solved iteratively.
  - This is a clear **simulation–optimization framework** for operational questions under budget constraints.

- **Spiliotis et al. (ABM on small‑world networks + inverse calibration)** [39]:
  - Uses ABM with **single vs two‑dose strategies** and **age‑prioritization** on small‑world graphs, and an **equation‑free Newton–Raphson calibration** to match population‑level parameters, then explores **optimal prioritization ratios**.

- **Deshkar et al. (ABM + RL)** [59]:
  - Agent‑based simulator coupled with **Deep Deterministic Policy Gradient** to jointly optimize **lockdown and vaccination policies**, treating vaccination as a **continuous control variable** (e.g., doses to mid‑age vs elderly).
  - Represents a methodological bridge to **control and reinforcement‑learning** approaches.

- **Angelopoulou & Mykoniatis hybrid ABM+DES** [27] and **Vázquez‑Abad et al. hybrid** [57]:
  - Hybrid models combining **agent‑based transmission** with **discrete‑event hospital capacity/immune‑response models**, focusing on **how vaccination policies affect healthcare load over time**.

**4. Global allocation, fairness, and spatial heterogeneity**

- **Li & Huang – 148‑country ABM** [68]:
  - Global agent‑based model (~198M agents) to study **global allocation rules** (minimum coverage thresholds, demand‑based allocation) vs current patterns.
  - Shows that **global minimum coverage benchmarks** avert substantially more infections than **status‑quo skewed distribution** [68].

- **Zia / Zia & Shafi ABMs on global fairness** [56,52]:
  - Simple spatial ABMs linking **regional vaccination disparities** to **virus mutation and persistent transmission**, arguing for **global, not regional, vaccination provisioning** [56,52].

- **Yuan et al. mobility‑network ABMs** [37,45]:
  - Large‑scale simulations on **US mobility networks** assessing how **spatial clustering of low‑coverage areas (homophily)** and **vaccinating hubs** affect outcomes, showing **location‑targeted vaccination of hubs can be ~2–2.5× more efficient** than uniform strategies [37,45].

**5. Large‑scale ABM platforms**

- **Epicast 2.0** [91]:
  - A US‑scale agent‑based platform (~324M agents) with detailed **household, school, and industry‑specific workplaces**, supporting **vaccines, antivirals, and multi‑level policies**.
  - Represents a **second‑generation national platform**, building on the experience of Covasim/OpenABM and earlier pandemic models.

- **FInd CoV Control (food industry)** [66]:
  - Domain‑specific ABM for **food production operations**, explicitly modeling **vaccination vs screening vs distancing** trade‑offs in health and economic outcomes [66].

**6. More advanced immunity and waning representations**

- **Covasim‑based age‑specific decay** (e.g., Aschaffenburg scenarios [38]) and **Bosman et al.** [15] incorporate **time‑varying VE and boosters**.
- **Manicom et al.** [104] explicitly study **how to model immunity/VE in ABMs**, mapping real‑world VE estimates to **agent‑level protection per contact** via **simulation‑based calibration** and waning trajectories.
  - This is a methodological milestone: **systematic calibration of immunity parameters** in ABMs, rather than ad‑hoc VE multipliers.

**Milestones (2022–2025)**

- Incorporation of **Omicron and multi‑variant dynamics**, **waning immunity**, and **boosters** in discrete simulations [1,2,15,32,38,43,67,104].
- Emergence of **national/continental‑scale ABMs**, often running on **HPC infrastructure** [2,42,68,91].
- Integration of **OR/optimization, RL, and hybrid ABM–DES** with epidemic ABMs to handle **resource allocation and logistics** [27,39,46,57,59].
- Growing treatment of **behavior, hesitancy, and social influence** as modeled processes, not fixed parameters [30,41,42,64].

---

### Thematic Trends and Shifts in Focus

#### **From Homogeneous Populations to Structured Contact Networks**

- Early ABMs treat contacts via **age‑specific contact matrices and random mixing within locations** [20,24,26].
- The field rapidly moves toward **explicit multi‑layer networks (household, workplace, community)** [14,16,24,44,63] and **fine‑grained synthetic populations** [2,15,42,68,91].
- A parallel line emphasizes **network topology** as a primary design dimension: **Erdős–Rényi vs power‑law vs small‑world** [7,21,39,62,65], highlighting that **heterogeneity in degree and community structure strongly conditions optimal vaccination strategy**.

#### **From Simple Efficacy Parameters to Full Vaccination Dynamics**

- Early work often assumes **perfect or all‑or‑nothing vaccines with fixed efficacy and no waning** [11,24,25,26,48].
- Over time, models incorporate:
  - **Multi‑dose schedules and explicit inter‑dose intervals** [14,18,19,20,31,33,38].
  - **Variant‑specific VE (against infection, symptoms, severe disease, death)** [2,15,32,43,67].
  - **Waning immunity and booster doses** [15,38,67,84,87,104].
- There is also a conceptual evolution from **“vaccination = move S→R”** (as in many early ABMs [11,30]) to **leaky, outcome‑specific reduction in risks** and **time‑dependent immunity curves** [40,41,84,104].

#### **Integration with NPIs and Policy Regimes**

- Nearly all ABMs eventually treat vaccination as part of a **policy bundle** with NPIs:
  - **Interactions with masking, distancing, school closures, testing, and tracing** [14,16,24,25,32,36,38,51,54,66].
  - Analyses of **timing of NPI relaxation** during rollout [14,25,73,76,97].
- The **core insight** repeated across models: **vaccines alone rarely suppress spread quickly unless rollout is fast and coverage high; sustained NPIs dramatically increase vaccine impact**.

#### **From Local Policy Questions to Global Equity**

- Early ABMs focus on **single cities/regions/nations** [16,20,24,25,26,31].
- By 2022, several studies move to **global or multi‑country allocation questions** [52,56,68,37,45]:
  - Showing that **spatial clustering of low‑coverage regions** promotes persistence and evolution, and that **globally fair allocation is more protective even for high‑income countries** [52,56,68].

#### **From Scenario Exploration to Optimization and Control**

- Initial ABMs are used for **scenario comparison**.
- Recent work integrates **optimization and control**:
  - **Simulation‑optimization for vaccine centre location/allocation** [46].
  - **RL‑based adaptive intervention policies** [59].
  - **Equation‑free inverse calibration** to compute **optimal age‑prioritization ratios** [39].
- This signals a shift toward **using ABMs as engines within decision‑support and optimization frameworks**, not just for off‑line scenario testing.

---

### Key Research Clusters and Their Contributions

#### **1. Covasim and Derivatives (Kerr et al., Giabbanelli, Cattaneo, Krebs, Yin, Mulutzie, Alexander)**

- **Core platform**: Covasim [44].
- **Applications and extensions**:
  - US‑wide vaccination/NPI interactions [14].
  - Regional calibration for Lombardy [32].
  - Aschaffenburg (Germany) age‑specific vaccination regimes [38].
  - Vaccine centre location and allocation optimization [46].
  - Social norms and uptake modeling [64].
  - Epicast 2.0 cites and conceptually builds on this ABM lineage [91].
- **Impact**: Covasim created a **flexible, open, extensible ABM architecture** with built‑in vaccination, enabling a **family** of studies that can share code and calibration practice.

#### **2. GERDA / Goldenbogen–Klipp Group (Germany)**

- **GERDA ABM** [23,70] and its **Advanced Science** extension [1]:
  - High‑resolution geospatial ABM with **stochastic human–human interaction networks**.
  - Emphasis on **bimodality**, **community‑specific immunity thresholds**, and **adaptive combinations of NPIs and vaccination** [1,23,70].
- **Contribution**:
  - Leading work on **how contact heterogeneity and stochasticity reshape “herd immunity”**, and on **local adaptive policy combinations**.

#### **3. Moghadas / Galvani Group (US)**

- Suite of US‑focused ABMs:
  - Early vaccination impact study [20].
  - Refined ABM with more detailed outcomes [19].
  - National variant‑aware evaluation of actual rollout vs counterfactuals [43].
- **Contribution**:
  - Establishing **age‑structured ABM as a standard for quantifying infections, hospitalizations, deaths averted**, and for **counterfactual assessment of rollout pace and coverage**.

#### **4. Swann / Rosenstrom / North Carolina ABM Group**

- **Patel et al.** [25], **Rosenstrom et al.** [34,36,4,6]:
  - State‑scale ABMs with strong focus on **child vaccination, masking policies, and boosters**.
- **Contribution**:
  - Detailed exploration of **pediatric vaccination timing**, showing its importance for **community protection and hospital load**.

#### **5. Marathe / Chen / Bhattacharya Network and AI Group**

- **Network‑based vaccine allocation** [3,8]:
  - Degree‑based and proximity‑time–based prioritization on **realistic social contact networks** (Virginia).
- **AI‑driven national modeling** [42]:
  - US‑scale ABM with **acceptance and production** modeled, supported by **big‑data workflows**.
- **Contribution**:
  - Pioneered **social‑network metric–based vaccination strategies** and **AI‑driven, HPC‑scale ABM workflows**.

#### **6. EpiGraph Group (Singh et al., Guzmán‑Merino et al.)**

- **Madrid** vaccination strategies [18] and **Omicron in Spain** [2]:
  - Highly parallel ABM with **city‑level resolution**, detailed **social and transport models**, and **multi‑vaccine, multi‑variant modules**.
- **Contribution**:
  - Proof‑of‑concept for **national‑scale ABMs with explicit multiple vaccines, waning, and boosters, calibrated to real campaigns**.

#### **7. Karabay / Varol Particle‑Based ABMs**

- **Sterilizing vs effective immunization** and **vaccine hesitancy** [40,41].
- **Contribution**:
  - Clarified how assumptions on **sterilizing vs non‑sterilizing vaccines** and **hesitancy** influence the perceived impact of vaccination strategies.

These clusters show a **clear pattern**: a few **flexible platforms (Covasim, GERDA, EpiGraph, COVAM, Epicast)** and **regional modeling teams** have sustained, iterative impact, adding layers of realism (variants, waning, behavior, logistics) while reusing and extending their simulation infrastructure.

---

### Implications and Future Directions

Based on the trajectory of the field:

- **Increasing biological realism**:
  - Expect further **routinization of multi‑variant, multi‑vaccine, waning immunity, and outcome‑specific VE modeling** in ABMs, with frameworks like [104] providing **standard calibration methods**.
- **Richer behavior and social processes**:
  - Trend toward explicit modeling of **hesitancy, norms, misinformation, and adaptive behavior** [30,41,42,64] will likely intensify, coupling ABMs with **behavioral and social‑network data.**
- **Embedded optimization and adaptive control**:
  - Simulation‑optimization [39,46] and RL‑based policies [59] foreshadow **closed‑loop policy tools** where ABM outputs guide real‑time optimization of vaccination and NPIs.
- **Equity and global perspective**:
  - Global ABMs [52,56,68] and mobility‑network studies [37,45] highlight that **local strategies cannot be decoupled from global allocation and spatial heterogeneity**—an area likely to grow, especially for future pandemics.

For your specific interest—**discrete operational simulations of COVID‑19 spread that include vaccination strategies**—the field has evolved from **conceptual ABMs with simple vaccination rules (2020)** to **large‑scale, data‑calibrated, multi‑variant, multi‑dose operational models with optimization/AI components (2022–2025)**. The main **methodological and conceptual milestones** have been:

1. **Deployment of general‑purpose ABM platforms with vaccination capabilities** [44,63].
2. **Policy‑driven prioritization and rollout studies** at regional/national scale [14,16,19,20,24,25,26,31,32,38].
3. **Recognition of contact structure and network heterogeneity in optimal vaccination** [1,7,21,23,39,62,65,74].
4. **Integration of variants, waning, and boosters** into individual‑level simulations [1,2,15,32,38,43,67,84,87,104].
5. **Coupling with optimization, reinforcement learning, and logistics models** [27,39,46,57,59].
6. **Shift from local to global allocation and equity concerns** [52,56,68,37,45].

These trends suggest that future work will likely emphasize **unified frameworks** that jointly model **viral evolution, immunity, behavior, and resource allocation** on **large, realistic contact networks**, with ABMs serving as **central engines in data‑assimilating decision‑support systems**.

## Foundational Work

### Which papers form the foundational references on this topic?

The below table shows the resources that are most often cited by the relevant papers on this topic. This is measured by the **reference rate**, which is the fraction of relevant papers that cite a resource. Use this table to determine the most important core papers to be familiar with if you want to deeply understand this topic. Some of these core papers may not be directly relevant to the topic, but provide important context.

| Ref. | Reference Rate | Topic Match | Title | Authors | Journal | Year | Total Citations | Cited By These Relevant Papers |
|---|---|---|---|---|---|---|---|---|
| [44] | 0.18 | 100% | Covasim: An agent-based model of COVID-19 dynamics and interventions | C. Kerr, ..., and D. Klein | PLoS Computational Biology | 2020 | 497 | [1, 10, 14, 16, 18, 32, 38, 46, 50, 51, 53, 54, 59, 63, 64, 66, 91, 104] |
| [526] | 0.12 | Not measured | Agent-Based Models of Virus Infection | Kathleen K. Steinhöfel, ..., and C. R. MacIntyre | Current Clinical Microbiology Reports | 2025 | 2 | [91] |
| [63] | 0.09 | 98% | OpenABM-Covid19—An agent-based model for non-pharmaceutical interventions against COVID-19 including contact tracing | R. Hinch, ..., and C. Fraser | PLoS Computational Biology | 2020 | 198 | [14, 16, 18, 44, 50, 51, 54, 67, 91, 104] |
| [527] | 0.08 | Not measured | Modelling transmission and control of the COVID-19 pandemic in Australia | S. Chang, ..., and M. Prokopenko | Nature Communications | 2020 | 530 | [1, 10, 14, 30, 44, 63, 66] |
| [352] | 0.07 | 1% | Clinical Outcomes Of A COVID-19 Vaccine: Implementation Over Efficacy. | A. Paltiel, ..., and Rochelle P. Walensky | Health affairs | 2020 | 155 | [25, 26, 29, 31, 33, 86] |
| [141] | 0.06 | 5% | Vaccine optimization for COVID-19: who to vaccinate first? | L. Matrajt, ..., and E. Brown | medRxiv | 2020 | 348 | [10, 18, 25, 32, 39, 50, 59, 97, 102] |
| [183] | 0.06 | 3% | Model-informed COVID-19 vaccine prioritization strategies by age and serostatus | Kate M. Bubar, ..., and D. Larremore | medRxiv | 2020 | 660 | [10, 18, 25, 30, 39, 50, 97] |
| [528] | 0.06 | Not measured | Report 9: Impact of non-pharmaceutical interventions (NPIs) to reduce COVID19 mortality and healthcare demand | N. Ferguson, ..., and A. Ghani | N/A | 2020 | 2538 | [1, 25, 30, 35, 44, 66, 91] |
| [529] | 0.05 | Not measured | A Reinforcement Learning Based Decision Support Tool for Epidemic Control: Validation Study for COVID-19 | M. Chadi and H. Mousannif | Applied Artificial Intelligence | 2022 | 17 | [59] |
| [14] | 0.05 | 100% | Returning to a Normal Life via COVID-19 Vaccines in the United States: A Large-scale Agent-Based Simulation Study | Junjiang Li and P. Giabbanelli | JMIR Medical Informatics | 2021 | 56 | [16, 32, 49, 54, 86] |
| [310] | 0.05 | 1% | Association of Simulated COVID-19 Vaccination and Nonpharmaceutical Interventions With Infections, Hospitalizations, and Mortality | Mehul D. Patel, ..., and J. Swann | JAMA Network Open | 2021 | 87 | [34, 36, 40, 53] |
| [20] | 0.04 | 100% | The impact of vaccination on COVID-19 outbreaks in the United States | S. Moghadas, ..., and A. Galvani | medRxiv | 2020 | 207 | [5, 16, 56, 109] |
| [68] | 0.04 | 96% | Optimizing global COVID-19 vaccine allocation: An agent-based computational model of 148 countries | Qingfeng Li and Yajing Huang | PLoS Computational Biology | 2022 | 11 | [53] |
| [371] | 0.04 | 1% | Simulated identification of silent COVID-19 infections among children and estimated future infection rates with vaccination | S. Moghadas, ..., and A. Galvani | medRxiv | 2021 | 12 | [34, 36, 56] |
| [530] | 0.03 | Not measured | A contribution to the mathematical theory of epidemics | W. O. Kermack and À. Mckendrick | Proceedings of The Royal Society A: Mathematical, Physical and Engineering Sciences | 1927 | 10533 | [1, 16, 23] |
| [531] | 0.03 | Not measured | Role of heterogeneity: National scale data-driven agent-based modeling for the US COVID-19 Scenario Modeling Hub. | Jiangzhuo Chen, ..., and M. Marathe | Epidemics | 2024 | 3 | [104] |
| [532] | 0.03 | Not measured | Effectiveness of non-pharmaceutical interventions on COVID-19 transmission in 190 countries from 23 January to 13 April 2020 | Y. Bo, ..., and X. Lao | International Journal of Infectious Diseases | 2020 | 238 | [27, 34, 36] |
| [533] | 0.03 | Not measured | Modelling the COVID-19 epidemic and implementation of population-wide interventions in Italy | G. Giordano, ..., and M. Colaneri | Nature Medicine | 2020 | 1542 | [32, 39, 44, 53] |
| [534] | 0.03 | Not measured | Projecting social contact matrices in 152 countries using contact surveys and demographic data | Kiesha Prem, ..., and M. Jit | PLoS Computational Biology | 2017 | 758 | [10, 30, 44] |
| [535] | 0.03 | Not measured | An agent-based model to evaluate the COVID-19 transmission risks in facilities | Erik Cuevas | Computers in Biology and Medicine | 2020 | 242 | [30, 54, 66] |

## Adjacent Work

### Which papers cite the same foundational papers as relevant papers?

Use this table to discover related papers on adjacent topics, to gain a broader understanding of the field and help generate ideas for useful new research directions.

| Ref. | Adjacency score | Topic Match | Title | Authors | Journal | Year | Total Citations | References These Foundational Papers |
|---|---|---|---|---|---|---|---|---|
| [547] | 5.46 | Not measured | Predictive models for health outcomes due to SARS-CoV-2, including the effect of vaccination: a systematic review | Oscar Espinosa, ..., and Oscar H. Franco | Systematic Reviews | 2024 | 0 | [14, 16, 31, 40, 41, 56, 63, 141] |
| [238] | 2.77 | 2% | Learning from the COVID-19 pandemic: A systematic review of mathematical vaccine prioritization models | G. González-Parra, ..., and C. Kadelka | Infectious Disease Modelling | 2024 | 0 | [30, 31, 40, 141, 353] |
| [548] | 2.07 | Not measured | A network-based model to assess vaccination strategies for the COVID-19 pandemic by using Bayesian optimization | G. González-Parra, ..., and Giulia Luebben | Chaos, Solitons &amp; Fractals | 2024 | 1 | [1, 31, 46, 141, 352] |
| [392] | 2.05 | 1% | Age-Stratified Model to Assess Health Outcomes of COVID-19 Vaccination Strategies, Ghana | S. K. Ofori, ..., and I. C. Fung | Emerging Infectious Diseases | 2023 | 6 | [19, 26, 141, 183] |
| [549] | 1.94 | Not measured | Using a real-world network to model the trade-off between stay-at-home restriction, vaccination, social distancing and working hours on COVID-19 dynamics | Ramin Nashebi, ..., and S. Kotil | PeerJ | 2022 | 2 | [1, 23, 25] |
| [221] | 1.87 | 2% | Limitations in creating artificial populations in agent-based epidemic modeling: a systematic review | Irina I. Maslova, ..., and E. Ilina | Journal of microbiology, epidemiology and immunobiology | 2024 | 0 | [1, 10, 30, 31, 63] |
| [550] | 1.84 | Not measured | Novel deterministic epidemic model considering mass vaccination and lockdown against coronavirus disease 2019 spread in Israel: a numerical study | M. Utamura, ..., and S. Kirikami | Biology Methods & Protocols | 2022 | 2 | [25, 29] |
| [551] | 1.84 | Not measured | Infection spread simulation technology in a mixed state of multi variant viruses | M. Koizumi, ..., and S. Kirikami | AIMS Public Health | 2021 | 2 | [25, 29] |
| [552] | 1.84 | Not measured | A novel deterministic epidemic model considering mass vaccination and lockdown against Covid-19 spread in Israel: Numerical study | M. Utamura, ..., and S. Kirikami | medRxiv | 2021 | 1 | [25, 29] |
| [383] | 1.81 | 1% | A Scoping Review of Three Dimensions for Long-Term COVID-19 Vaccination Models: Hybrid Immunity, Individual Drivers of Vaccinal Choice, and Human Errors | Jack T. Beerman, ..., and P. Giabbanelli | Vaccines | 2022 | 1 | [10, 14, 31] |
| [519] | 1.79 | 0% | The SARS-CoV-2 test scale-up in the USA: an analysis of the number of tests produced and used over time and their modelled impact on the COVID-19 pandemic | Steven Santos, ..., and R. Salerno | The Lancet. Public health | 2025 | 3 | [14, 19, 44] |
| [553] | 1.78 | Not measured | COVSIM: A stochastic agent-based COVID-19 SIMulation model for North Carolina. | Erik T. Rosenstrom, ..., and Julie L. Swann | Epidemics | 2024 | 6 | [14, 36, 63] |
| [444] | 1.77 | 1% | Data-driven strategies for model-informed decision-making during the COVID-19 pandemic: a systematic review | Mehdi Lotfi and L. Kaderali | BMJ Open | 2026 | 0 | [10, 14, 44] |
| [251] | 1.77 | 2% | Modelling multiscale infectious disease in complex systems | Jiajun Xian, ..., and Jinlin Ye | Physics Reports | 2025 | 0 | [44, 63, 141] |
| [230] | 1.75 | 2% | A Systematic Review of Spatial Epidemiological Modeling Approaches Applied During the COVID-19 Pandemic | K. Oshinubi, ..., and J. Mihaljevic | medRxiv | 2025 | 0 | [16, 44, 63] |
| [554] | 1.67 | Not measured | Differentiating behavioral impact with or without vaccination certification under mass vaccination and non-pharmaceutical interventions on mitigating COVID-19 | Hu Cao and Longbing Cao | Scientific Reports | 2024 | 2 | [16, 141] |
| [555] | 1.67 | Not measured | Effect of vaccination certification with mass vaccination and non-pharmaceutical interventions on mitigating COVID-19 | H. Cao and L. Cao | medRxiv | 2023 | 0 | [16, 141] |
| [350] | 1.66 | 1% | Smart epidemic control: A hybrid model blending ODEs and agent-based simulations for optimal, real-world intervention planning | Péter Polcz, ..., and G. Szederkényi | PLOS Computational Biology | 2025 | 0 | [1, 10, 44, 63] |
| [556] | 1.62 | Not measured | The inoculation dilemma: Partial vs Full immunization during the early rollout in a pandemic | Rajdeep Singh, ..., and Michael Freiberger | Omega | 2024 | 0 | [31, 141, 352] |
| [299] | 1.55 | 2% | Optimizing vaccine logistics: a taxonomy and narrative review | Jacob Locke, ..., and Ahmed Saif | INFOR: Information Systems and Operational Research | 2025 | 1 | [44, 46, 141] |
