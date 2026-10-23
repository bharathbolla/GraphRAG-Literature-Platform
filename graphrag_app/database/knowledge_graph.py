import networkx as nx
from typing import List, Dict, Any, Optional, Set
from models.article import Article
from models.graph import GraphDataResponse

class KnowledgeGraphManager:
    """
    Manages the clinical knowledge graph using NetworkX.
    Supports node/edge synchronization, semantic pathfinding,
    and conversion to interactive Vis-Network format.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def clear(self):
        self.graph.clear()
        
    DRUG_CLASS_MAP = {
        # SGLT2i
        "empagliflozin": ("class_sglt2i", "SGLT2 inhibitors", "C3890289"),
        "dapagliflozin": ("class_sglt2i", "SGLT2 inhibitors", "C3890289"),
        "canagliflozin": ("class_sglt2i", "SGLT2 inhibitors", "C3890289"),
        "ertugliflozin": ("class_sglt2i", "SGLT2 inhibitors", "C3890289"),
        # ARNI / ACEi / MRAs
        "sacubitril": ("class_arni", "Angiotensin Receptor-Neprilysin Inhibitors (ARNI)", "C3890290"),
        "valsartan": ("class_arni", "Angiotensin Receptor-Neprilysin Inhibitors (ARNI)", "C3890290"),
        "enalapril": ("class_acei", "ACE Inhibitors", "C0003015"),
        "finerenone": ("class_mra", "Non-Steroidal Mineralocorticoid Receptor Antagonists", "C4082260"),
        # CDK4/6 Inhibitors
        "ribociclib": ("class_cdk46", "CDK4/6 Inhibitors", "C4052345"),
        "palbociclib": ("class_cdk46", "CDK4/6 Inhibitors", "C2987625"),
        "abemaciclib": ("class_cdk46", "CDK4/6 Inhibitors", "C4082269"),
        # Immune Checkpoint Inhibitors
        "pembrolizumab": ("class_ici", "PD-1 / PD-L1 Immune Checkpoint Inhibitors", "C3886580"),
        "nivolumab": ("class_ici", "PD-1 / PD-L1 Immune Checkpoint Inhibitors", "C3886580"),
        # Biologics & Monoclonal Antibodies
        "secukinumab": ("class_il17", "Interleukin-17A Inhibitors", "C3273840"),
        "ixekizumab": ("class_il17", "Interleukin-17A Inhibitors", "C3539828"),
        "guselkumab": ("class_il23", "Interleukin-23 Inhibitors", "C4085441"),
        "ofatumumab": ("class_cd20", "Anti-CD20 Monoclonal Antibodies", "C2719580"),
        "ocrelizumab": ("class_cd20", "Anti-CD20 Monoclonal Antibodies", "C1709426"),
        # Targeted Hematology
        "asciminib": ("class_stamp", "STAMP BCR-ABL1 Inhibitors", "C5205796"),
        "iptacopan": ("class_cfb", "Complement Factor B Inhibitors", "C5441712"),
        # Incretins / GLP-1
        "semaglutide": ("class_glp1", "GLP-1 Receptor Agonists", "C4085420"),
        "tirzepatide": ("class_glp1_gip", "Dual GIP / GLP-1 Receptor Agonists", "C5544711"),
        "lecanemab": ("class_amyloid", "Anti-Amyloid Beta Monoclonal Antibodies", "C5544719"),
    }

    def infer_drug_class(self, drug_name: str) -> tuple:
        """Dynamically resolves the therapeutic class for any drug using registry or USAN stems."""
        d_lower = drug_name.lower().strip()
        for k, v in self.DRUG_CLASS_MAP.items():
            if k in d_lower:
                return v

        if d_lower.endswith("mab"):
            return ("class_mab", "Monoclonal Antibodies", "C0003241")
        elif d_lower.endswith("nib"):
            return ("class_tki", "Targeted Kinase Inhibitors", "C1517728")
        elif d_lower.endswith("gliflozin"):
            return ("class_sglt2i", "SGLT2 inhibitors", "C3890289")
        elif d_lower.endswith("sartan"):
            return ("class_arb", "Angiotensin Receptor Blockers", "C0003016")
        elif d_lower.endswith("statin"):
            return ("class_statin", "HMG-CoA Reductase Inhibitors", "C0019614")
        elif d_lower.endswith("tide"):
            return ("class_peptide", "Peptide Therapeutic Agonists", "C0030880")
        elif d_lower.endswith("ciclib"):
            return ("class_cdk", "Cyclin-Dependent Kinase Inhibitors", "C4052345")

        clean_slug = "".join(c if c.isalnum() else "_" for c in drug_name).upper()[:14]
        return (f"class_{clean_slug}", f"Targeted Therapy: {drug_name}", None)

    def rebuild_from_articles(self, articles: List[Article]):
        """Reconstructs the full biomedical knowledge graph dynamically from the given article list."""
        self.clear()
        
        # Track registered class nodes to avoid duplicate creation
        registered_classes = set()

        for art in articles:
            pmid = art.pmid
            art_id = f"art_{pmid}"
            
            # 1. Article Node
            self.graph.add_node(
                art_id,
                label=f"PMID:{pmid}\n({art.journal.split()[0]} {art.year})",
                title=art.title,
                type="Article",
                pmid=pmid,
                year=art.year,
                journal=art.journal,
                study_design=art.study_design,
                sample_size=art.sample_size,
                color="#C7C7C7"
            )
            
            pico = art.pico
            if not pico:
                continue
                
            # 2. Population & Condition Nodes
            cond_id = None
            pop = pico.population
            if pop:
                pop_id = f"pop_{pmid}"
                self.graph.add_node(
                    pop_id,
                    label=f"Cohort (N={pop.n:,})" if pop.n else "Cohort (N/A)",
                    description=pop.description,
                    type="Population",
                    color="#F7B516",
                    title=f"Population: {pop.description}"
                )
                self.graph.add_edge(art_id, pop_id, relationship="ENROLLS")
                
                cond_cui = pop.condition_cui or f"CUI:AUTO:{pop.condition[:12].upper()}"
                cond_id = f"cond_{cond_cui}"
                self.graph.add_node(
                    cond_id,
                    label=pop.condition,
                    type="Condition",
                    cui=cond_cui,
                    color="#E74A21",
                    title=f"Clinical Indication: {pop.condition} (CUI: {cond_cui})"
                )
                self.graph.add_edge(pop_id, cond_id, relationship="HAS_CONDITION")
                
            # 3. Interventions & Drug Nodes & Dynamic Drug Class
            for inter in pico.interventions:
                drug_cui = inter.drug_cui or inter.name.lower().replace(" ", "_")
                drug_id = f"drug_{drug_cui}"
                self.graph.add_node(
                    drug_id,
                    label=inter.name,
                    type="Drug",
                    cui=inter.drug_cui,
                    rxnorm=inter.rxnorm,
                    color="#0460A9",
                    title=f"Therapeutic Agent: {inter.name} (RxNorm: {inter.rxnorm or 'N/A'})"
                )
                self.graph.add_edge(art_id, drug_id, relationship="STUDIES", dose=inter.dose)
                
                # Dynamic Class Node
                class_id, class_label, class_cui = self.infer_drug_class(inter.name)
                if class_id not in registered_classes:
                    self.graph.add_node(
                        class_id,
                        label=class_label,
                        type="DrugClass",
                        cui=class_cui or "C0000000",
                        color="#EC9A1E",
                        title=f"Pharmacologic Class: {class_label}"
                    )
                    registered_classes.add(class_id)
                self.graph.add_edge(drug_id, class_id, relationship="IS_A")

                # Connect Drug to Condition if present
                if cond_id:
                    self.graph.add_edge(drug_id, cond_id, relationship="TREATS")
                
            # 4. Clinical Outcomes
            for out in pico.outcomes:
                out_clean = out.name[:20].lower().replace(" ", "_")
                out_id = f"out_{pmid}_{out_clean}"
                self.graph.add_node(
                    out_id,
                    label=out.name[:24] + ("..." if len(out.name) > 24 else ""),
                    full_name=out.name,
                    type="Outcome",
                    color="#E74A21",
                    title=f"Endpoint: {out.name} | {out.measure} {out.effect} ({out.ci_low}-{out.ci_high})"
                )
                self.graph.add_edge(
                    art_id,
                    out_id,
                    relationship="REPORTS",
                    effect=out.effect,
                    measure=out.measure,
                    ci=f"{out.ci_low}-{out.ci_high}",
                    p_value=out.p_value,
                    evidence=out.evidence
                )

            # 5. Section Chunks
            for idx, chunk in enumerate(art.section_chunks):
                chunk_id = f"chunk_{pmid}_{idx}"
                self.graph.add_node(
                    chunk_id,
                    label=f"§ {chunk.section_name}",
                    type="Chunk",
                    color="#656565",
                    title=f"Section: {chunk.section_name} | PMID:{pmid}\n{chunk.content[:150]}..."
                )
                self.graph.add_edge(art_id, chunk_id, relationship="CONTAINS_SECTION")
                
    def get_vis_network_data(self) -> GraphDataResponse:
        """Serializes the graph into Vis-Network format with community cluster detection."""
        nodes = []
        edges = []
        
        # Calculate community clusters using Greedy Modularity
        try:
            undirected = self.graph.to_undirected()
            communities = list(nx.community.greedy_modularity_communities(undirected))
        except Exception:
            communities = []

        community_palette = [
            "#EC9A1E", "#E74A21", "#0460A9", "#8D1F1B", "#656565", "#C7C7C7", "#D97706", "#2563EB"
        ]
        node_community_map = {}
        for c_idx, comm in enumerate(communities):
            for node in comm:
                node_community_map[node] = c_idx
        
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get("type", "Entity")
            size = 28 if node_type == "DrugClass" else (22 if node_type == "Article" else (12 if node_type == "Chunk" else 16))
            c_id = node_community_map.get(node_id, 0)
            comm_color = community_palette[c_id % len(community_palette)]
            
            nodes.append({
                "id": node_id,
                "label": data.get("label", node_id),
                "title": data.get("title", data.get("description", node_id)),
                "group": node_type,
                "color": data.get("color", "#94A3B8"),
                "community_color": comm_color,
                "community_id": c_id + 1,
                "is_chunk": (node_type == "Chunk"),
                "size": size,
                "font": {"color": "#FFFFFF", "size": 10 if node_type == "Chunk" else 12, "face": "Inter"}
            })
            
        edge_idx = 1
        for u, v, data in self.graph.edges(data=True):
            rel = data.get("relationship", "RELATES_TO")
            is_chunk_edge = (rel == "CONTAINS_SECTION")
            edges.append({
                "id": f"e_{edge_idx}",
                "from": u,
                "to": v,
                "label": rel if not is_chunk_edge else "",
                "title": f"Relation: {rel}" + (f" | Effect: {data.get('effect')}" if data.get('effect') else ""),
                "arrows": "to",
                "color": {"color": "#475569" if is_chunk_edge else "#64748B", "highlight": "#38BDF8"},
                "font": {"color": "#94A3B8", "size": 9, "align": "middle"},
                "is_chunk": is_chunk_edge
            })
            edge_idx += 1
            
        return GraphDataResponse(nodes=nodes, edges=edges)

    def find_trials_by_drug_and_condition(self, drug_name: Optional[str] = None, condition_name: Optional[str] = None) -> Set[str]:
        """Finds article PMIDs connected to specified drugs and conditions."""
        matched_pmids = set()
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "Article":
                pmid = data.get("pmid")
                # Check drug neighbors
                out_edges = self.graph.out_edges(node, data=True)
                has_drug = True if not drug_name else False
                has_cond = True if not condition_name else False
                
                for _, target, edge_data in out_edges:
                    target_data = self.graph.nodes[target]
                    if edge_data.get("relationship") == "STUDIES" and drug_name:
                        if drug_name.lower() in target_data.get("label", "").lower():
                            has_drug = True
                    if edge_data.get("relationship") == "ENROLLS" and condition_name:
                        # Follow to condition
                        pop_edges = self.graph.out_edges(target, data=True)
                        for _, cond_target, pop_rel in pop_edges:
                            if pop_rel.get("relationship") == "HAS_CONDITION":
                                cond_data = self.graph.nodes[cond_target]
                                if condition_name.lower() in cond_data.get("label", "").lower():
                                    has_cond = True
                                    
                if has_drug and has_cond:
                    matched_pmids.add(pmid)
        return matched_pmids
