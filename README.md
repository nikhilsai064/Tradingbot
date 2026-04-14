Achieving 85%+ accuracy in medical coding is a jump from **Semantic Retrieval** to **Expert Reasoning**. At 56%, your model is "getting the gist" but failing on the technical nuances that separate two very similar HCPCS codes.

To cross the 85% threshold, you need to implement a **multi-stage pipeline** that treats the problem like a clinical decision, not just a search query.

---

### 1. Advanced Query Pre-Processing (The "Translator")
Users often use "slang" or brand names, while HCPCS uses formal clinical language. 
* **Technique:** Use a cheap LLM (like GPT-4o-mini) as a "Medical Translator" before hitting your vector DB.
* **Action:** Take the input `Item + Supplier` and ask the LLM to generate 3 versions of the query:
    1.  The original input.
    2.  A formal clinical description.
    3.  A list of likely technical specifications (e.g., if it's a "wheelchair," add "manual," "power," "folding").
* **Result:** You search with a "rich" query instead of a "noisy" one.

### 2. The "Hybrid Search" Strategy
Vector embeddings (like `text-embedding-3-large`) are "blurry"—they struggle to distinguish "Size 1" from "Size 2." 
* **Technique:** Combine **Dense Retrieval** (FAISS/Qdrant) with **Keyword/Fuzzy Retrieval** (BM25 or RapidFuzz).
* **Action:** 1.  Get Top 20 results from your Vector search.
    2.  Get Top 20 results from a Keyword search on the same data.
    3.  Combine them using **Reciprocal Rank Fusion (RRF)**.
* **Why:** Keyword search captures exact technical terms (like "Hemi-walker") that embeddings might "smooth out."

### 3. Cross-Encoder Reranking (The "Gold Standard")
FAISS uses a "Bi-Encoder," which calculates the similarity of two strings independently. To get 85%+, you need a **Cross-Encoder**.
* **Technique:** Take the Top 20 candidates from Step 2 and pass them through a model that looks at the `Input` and `Candidate` **simultaneously**.
* **Action:** Use an LLM in Azure Foundry as the Reranker.
    > **Prompt:** "Input: [Item + Supplier]. Here are 20 codes. Compare the specs (size, material, power source) in the input vs. the codes. Rank them and explain why #1 is the best fit."

### 4. Supplier-Specific Logic (Domain Knowledge)
The "Supplier" is your secret weapon. Suppliers usually specialize in specific "HCPCS Ranges."
* **Technique:** Build a **Supplier-to-Class** lookup table. 
* **Action:** If the supplier is "Medline," you know they are likely in the "A" (Supplies) or "E" (DME) ranges.
* **Boost:** In your retrieval step, give a **2x weight boost** to any HCPCS code whose `Major Class` aligns with that Supplier's known product lines.

### 5. Synthetic Data Augmentation
Your master data is likely just "Code + Description." This is too "clean" for real-world user inputs.
* **Technique:** Use an LLM to generate "Dirty" data. 
* **Action:** For every HCPCS code, generate 5-10 "User Phrases" or "Supplier Invoice Lines" that would map to it. Add these synthetic phrases to your Vector DB as secondary search fields.
* **Effect:** You are training your search engine to recognize how humans *actually* talk, not just how the CMS manual is written.

---

### Recommended Architecture Summary

| Step | Component | Purpose |
| :--- | :--- | :--- |
| **1. Enrich** | GPT-4o-mini | Turn "3M Mask" into "N95 Particulate Respirator, Surgical." |
| **2. Retrieve** | Qdrant (Hybrid) | Get the top 50 matches using both Vector and Keyword search. |
| **3. Filter** | Supplier Table | Filter out codes that are physically impossible for that supplier. |
| **4. Rerank** | GPT-4o | Pick the winner from the remaining 10 based on technical specs. |

### The "Quickest" Win for you:
Since you already have the FAISS setup, **implement the Reranker today.** Take your top 10 FAISS results, send them to GPT-4o in Azure Foundry with a strict "Comparison" prompt, and you will likely see your accuracy jump from 56% to 75% immediately. The remaining 10% will come from cleaning the data in Step 5.

To reach 85%+ accuracy, you need to transition from a single-step "search" to a multi-stage **Enrich-Retrieve-Rerank** pipeline. 

Here are the 5 Jira sub-tasks required to implement the "Expert Reasoning" architecture we discussed.

---

### 1. Develop LLM Query Enrichment (The "Translator")
**Objective:** Bridge the gap between supplier-specific item names and clinical HCPCS terminology.
* **Action:** Create a Python module that takes the raw `Item Name + Supplier` and passes it to an LLM (GPT-4o-mini).
* **Goal:** Generate a "Clinical Expansion" of the query. For example, "3M Mask" → "N95 Surgical Respirator, Personal Protective Equipment."
* **Deliverable:** A function that returns a multi-faceted search string to be used for the vector search.

### 2. Implement Hybrid Search (Vector + Fuzzy/Keyword)
**Objective:** Ensure high-precision matches for technical specifications and alphanumeric codes.
* **Action:** Integrate a keyword-based search (like `RapidFuzz` or BM25) alongside your existing FAISS/Qdrant vector search.
* **Goal:** Combine results using **Reciprocal Rank Fusion (RRF)**. This prevents the vector model from "ignoring" exact matches or technical keywords like "portable" or "pediatric."
* **Deliverable:** A retrieval function that returns a merged Top-50 candidate list.

### 3. Build a Supplier-Range Mapping Table
**Objective:** Use domain knowledge to narrow the search space and eliminate "impossible" results.
* **Action:** Create a mapping (JSON or DB table) of major suppliers to their respective HCPCS code ranges (e.g., *Medtronic* maps primarily to cardiovascular/diabetes ranges).
* **Goal:** Apply a "Soft Filter" or "Boost" during retrieval. If a candidate code falls outside a supplier's known category, lower its rank.
* **Deliverable:** A lookup utility that applies a weight multiplier to search results based on the `Supplier` input.

### 4. Configure LLM Reranker (The "Final Judge")
**Objective:** Use high-reasoning LLMs to perform the final selection from the candidate list.
* **Action:** Set up a "Point-wise" or "List-wise" reranker in Azure Foundry.
* **Goal:** Pass the Top 10-20 candidates from the hybrid search to GPT-4o. The prompt must instruct the model to compare the specific technical attributes of the input item against the HCPCS descriptions.
* **Deliverable:** A prompt-flow node that returns the single best HCPCS code with a confidence score.

### 5. Create a Synthetic Evaluation Benchmark
**Objective:** Measure accuracy and identify exactly where the 56% failure occurs.
* **Action:** Generate a "Golden Dataset" of 200 items where you manually (or via expert) verify the correct HCPCS code.
* **Goal:** Automate a testing script to run your pipeline against this benchmark. Use the results to "tune" the weights between the Vector search, Keyword search, and LLM Reranker.
* **Deliverable:** A performance report comparing the "Simple FAISS" accuracy (56%) against the "New Pipeline" accuracy (target 85%+).

---

