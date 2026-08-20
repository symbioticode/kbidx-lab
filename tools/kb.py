#!/usr/bin/env python3
"""
kb.py — TI-360 Knowledge Base CLI
Version : 0.1.0 (MVP foundations)
Schema  : v0.3

Commandes disponibles :
  validate <file.toml>   Valide les invariants 1-8 sur un corpus TOML
  toon     <file.toml>   Génère la vue TOON (tableau condensé pour LLM)
  status   <file.toml>   Résumé état des questions (beta, verif, statut)
  reindex  <file.toml>   Reconstruit index SQLite depuis TOML (Phase 2)
  stamp    <file.toml>   Régénère la ligne KB-STATUS (couche découverte) en tête
                         du fichier, dérivée de l'état agrégé du corpus
  stamp-verdict <file.md> Vérifie [[preuve_cloture]] et stampe KB-STATUS
                         sur un fichier VERDICT-*.md

Usage :
  python kb.py validate data/test_corpus.toml
  python kb.py toon     data/test_corpus.toml
  python kb.py status   data/test_corpus.toml --filter beta=N
  python kb.py stamp    data/test_corpus.toml
  python kb.py stamp    data/test_corpus.toml --status VOID --dry-run
  python kb.py stamp-verdict VERDICT-001.md
"""

import sys
import re
import tomllib
import hashlib
import argparse
from datetime import date
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

# ═══════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════

VERSION = "0.2.0"
SCHEMA_VERSION = "0.3"  # provenance (CT-002) additif — pas de bump majeur, rétrocompatible

VALID_SOURCE_TYPES   = {"PROCESS", "ARCH", "MINUTES", "ANALYSIS", "MATRIX",
                         "CONOPS", "DIRECTIVE", "SOP", "AO", "EMAIL",
                         "TRANSCRIPTION", "SYNTHESE"}
VALID_REUNION_TYPES  = {"ARB", "ITRMC", "CAB", "WORKSHOP", "COMITE", "BILAT", "STANDUP"}
VALID_INSTANCE_TYPES = {"COMITE", "POSTE", "ORGANISATION", "GROUPE_TRAVAIL"}
VALID_DECISION_ETAT  = {"CONFIRME", "INFIRME", "REPORTE", "SUPERSEDE", "HYPOTHESE"}
VALID_EXTRACTION_TYPES = {"CONTRAINTE", "PROCESSUS", "ROLE", "DELAI", "CHAMP",
                           "LACUNE", "PRECONDITION", "DECISION"}
VALID_BETA           = {"T", "F", "B", "N"}
VALID_VERIF          = {"NV", "VC", "VD", "VU"}
VALID_QUESTION_ETAT  = {"OUVERTE", "FERMEE", "BLOQUANTE", "HYPOTHESE_PROVISOIRE", "ARCHIVEE"}
VALID_BLOCS          = {"0", "A", "B", "C", "D", "E", "F", "COUCHE-2", "COUCHE-3"}

MAX_CONTENU_WORDS = 50

# Couche découverte (KB-STATUS) — vocabulaire de statut de FICHIER, distinct
# de Decision.etat et Question.etat qui restent internes aux entités du graphe.
VALID_FILE_STATUS = {"DRAFT", "ACTIVE", "SUPERSEDED", "ARCHIVED", "VOID"}
STAMP_SCAN_LINES = 20  # nombre de lignes en tête de fichier où chercher/écrire KB-STATUS
KB_STATUS_RE = re.compile(r'KB-STATUS:\s*(.+)')
KB_STATUS_FIELD_RE = re.compile(r'(\w+)=(\S+)')

# CT-002 (approuvé 2026-07-09) — provenance algébrique (demi-anneau)
# Réf. Green, Karvounarakis, Tannen, "Provenance Semirings", PODS 2007.
# Champ documentaire uniquement — aucun moteur de résolution de l'expression.
PROVENANCE_TOKEN_RE = re.compile(r'[\w\-]+|[·+()]')

# ═══════════════════════════════════════════════════════════════
# PREUVE CLOTURE (stamp-verdict)
# ═══════════════════════════════════════════════════════════════

# Bloc TOML [[preuve_cloture]] — scanne uniquement les fichiers VERDICT-*.md
# hors blocs de code (```...```). Le scan exclut les fichiers MISSION-*.
CODE_BLOCK_RE = re.compile(r'```.*?```', re.DOTALL)
PREUVE_BLOCK_RE = re.compile(
    r'\[\[preuve_cloture\]\]\s*\n((?:[ \t]*[a-zA-Z_]+\s*=\s*.*\n)*)'
)
PREUVE_FIELD_RE = re.compile(r'(\w+)\s*=\s*"(.*?)"')

REQUIRED_PREUVE_FIELDS = {
    "cible_fichier", "cible_hash", "commande",
    "sortie_fichier", "sortie_hash", "horodatage",
}

# ═══════════════════════════════════════════════════════════════
# VALIDATION RESULT
# ═══════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    errors:   list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str):   self.errors.append(f"  ✗ ERREUR   {msg}")
    def warn(self, msg: str):    self.warnings.append(f"  ⚠ AVERT.  {msg}")
    def ok(self) -> bool:        return len(self.errors) == 0

    def print_report(self):
        if self.warnings:
            print("\n[AVERTISSEMENTS]")
            for w in self.warnings: print(w)
        if self.errors:
            print("\n[ERREURS]")
            for e in self.errors: print(e)
        total = len(self.errors) + len(self.warnings)
        status = "✓ VALIDE" if self.ok() else "✗ INVALIDE"
        print(f"\n[RÉSULTAT] {status} — {len(self.errors)} erreur(s), {len(self.warnings)} avertissement(s)")

# ═══════════════════════════════════════════════════════════════
# LOADER
# ═══════════════════════════════════════════════════════════════

def load_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)

def index_by_id(items: list[dict], entity: str, result: ValidationResult) -> dict:
    """Construit un index id→dict, détecte les doublons."""
    idx = {}
    for item in items:
        eid = item.get("id", "")
        if not eid:
            result.error(f"{entity} sans champ 'id'")
            continue
        if eid in idx:
            result.error(f"{entity} id dupliqué : '{eid}'")
        idx[eid] = item
    return idx

# ═══════════════════════════════════════════════════════════════
# VALIDATORS PAR ENTITÉ
# ═══════════════════════════════════════════════════════════════

def validate_sources(sources: list[dict], r: ValidationResult) -> dict:
    idx = index_by_id(sources, "source", r)
    for src in sources:
        sid = src.get("id", "?")
        if src.get("type", "") not in VALID_SOURCE_TYPES:
            r.error(f"source '{sid}' type invalide : '{src.get('type')}' — attendu {VALID_SOURCE_TYPES}")
        if not src.get("titre"):
            r.warn(f"source '{sid}' sans titre")
        if not src.get("date"):
            r.warn(f"source '{sid}' sans date")
    return idx


def validate_instances(instances: list[dict], r: ValidationResult) -> dict:
    idx = index_by_id(instances, "instance", r)
    for inst in instances:
        iid = inst.get("id", "?")
        if inst.get("type", "") not in VALID_INSTANCE_TYPES:
            r.error(f"instance '{iid}' type invalide : '{inst.get('type')}'")
        # Invariant 8 précondition : parent doit exister si renseigné
        parent = inst.get("parent", "")
        if parent and parent not in idx:
            r.error(f"instance '{iid}' parent '{parent}' introuvable")
    return idx


def validate_reunions(reunions: list[dict], src_idx: dict,
                      r: ValidationResult) -> dict:
    idx = index_by_id(reunions, "reunion", r)
    for run in reunions:
        rid = run.get("id", "?")
        if run.get("type", "") not in VALID_REUNION_TYPES:
            r.error(f"reunion '{rid}' type invalide : '{run.get('type')}'")
        src = run.get("source_id", "")
        if src and src not in src_idx:
            r.error(f"reunion '{rid}' source_id '{src}' introuvable")
    return idx


def validate_extractions(extractions: list[dict], src_idx: dict,
                          r: ValidationResult) -> dict:
    idx = index_by_id(extractions, "extraction", r)
    for ext in extractions:
        eid = ext.get("id", "?")

        # Source obligatoire
        src = ext.get("source_id", "")
        if not src:
            r.error(f"extraction '{eid}' sans source_id")
        elif src not in src_idx:
            r.error(f"extraction '{eid}' source_id '{src}' introuvable")

        # Type
        if ext.get("type", "") not in VALID_EXTRACTION_TYPES:
            r.error(f"extraction '{eid}' type invalide : '{ext.get('type')}'")

        # Beta
        beta = ext.get("beta", "")
        if beta not in VALID_BETA:
            r.error(f"extraction '{eid}' beta invalide : '{beta}'")

        # Verif
        verif = ext.get("verif", "NV")
        if verif not in VALID_VERIF:
            r.error(f"extraction '{eid}' verif invalide : '{verif}'")

        # Invariant 6 : contenu ≤ 50 mots
        contenu = ext.get("contenu", "")
        word_count = len(contenu.split())
        if word_count > MAX_CONTENU_WORDS:
            r.error(f"extraction '{eid}' contenu trop long : {word_count} mots (max {MAX_CONTENU_WORDS})")

        # Invariant 2 : beta=N ne peut pas fermer une question (via decision_id)
        if beta == "N" and ext.get("decision_id", ""):
            r.error(f"extraction '{eid}' beta=N mais decision_id renseigné (Invariant 2)")

        # Invariant 3 précondition : beta=T requis pour prouver une décision
        if ext.get("decision_id", "") and beta not in {"T", "F"}:
            r.warn(f"extraction '{eid}' liée à une décision mais beta='{beta}' (attendu T ou F, Invariant 3)")

    return idx


def parse_provenance(expr: str, valid_ids: set) -> dict:
    """
    CT-002 (approuvé) — parse une expression demi-anneau simple 'a · b + c'.
    Ne résout rien, ne calcule rien : vérifie seulement que les id
    référencés existent. Portée strictement notationnelle (hors_scope CT-002).
    Retourne {'valid': bool, 'ids_used': set, 'error': str|None}
    """
    if not expr.strip():
        return {"valid": True, "ids_used": set(), "error": None}

    tokens = PROVENANCE_TOKEN_RE.findall(expr)
    ids_used = {t for t in tokens if t not in ('·', '+', '(', ')')}

    if not ids_used:
        return {"valid": False, "ids_used": set(), "error": "expression vide malgré contenu"}

    unknown = ids_used - valid_ids
    if unknown:
        return {"valid": False, "ids_used": ids_used, "error": f"id(s) inconnu(s) : {unknown}"}

    return {"valid": True, "ids_used": ids_used, "error": None}


def validate_provenance(extractions: list[dict], ext_idx: dict, r: ValidationResult):
    """
    Invariant 9 (CT-002, approuvé 2026-07-09) : si Extraction.provenance est
    renseigné, chaque id référencé doit exister dans le corpus. Champ optionnel,
    rétrocompatible — absence de provenance = comportement inchangé.
    Ne vérifie AUCUNE cohérence avec beta (hors scope CT-002, ticket séparé si besoin).
    """
    valid_ids = set(ext_idx.keys())
    for ext in extractions:
        eid = ext.get("id", "?")
        prov = ext.get("provenance", "")
        if not prov:
            continue
        result = parse_provenance(prov, valid_ids)
        if not result["valid"]:
            r.error(f"extraction '{eid}' provenance invalide : {result['error']} (Invariant 9)")
        elif eid in result["ids_used"]:
            r.error(f"extraction '{eid}' provenance se référence elle-même (Invariant 9)")


def validate_decisions(decisions: list[dict], src_idx: dict,
                        run_idx: dict, inst_idx: dict,
                        ext_idx: dict, r: ValidationResult) -> dict:
    idx = index_by_id(decisions, "decision", r)
    for dec in decisions:
        did = dec.get("id", "?")
        etat = dec.get("etat", "")

        # Type etat
        if etat not in VALID_DECISION_ETAT:
            r.error(f"decision '{did}' etat invalide : '{etat}'")

        # Invariant 1 : reunion_id OU instance_id obligatoire
        has_reunion  = bool(dec.get("reunion_id",  ""))
        has_instance = bool(dec.get("instance_id", ""))
        if not has_reunion and not has_instance:
            r.error(f"decision '{did}' sans reunion_id ni instance_id (Invariant 1)")

        # Vérifier références
        if has_reunion and dec["reunion_id"] not in run_idx:
            r.error(f"decision '{did}' reunion_id '{dec['reunion_id']}' introuvable")
        if has_instance and dec["instance_id"] not in inst_idx:
            r.error(f"decision '{did}' instance_id '{dec['instance_id']}' introuvable")
        for sid in dec.get("source_ids", []):
            if sid not in src_idx:
                r.error(f"decision '{did}' source_id '{sid}' introuvable")

        # Invariant 7 : etat=CONFIRME → toutes extractions liées verif=VC
        if etat == "CONFIRME":
            linked_exts = [e for e in ext_idx.values()
                           if e.get("decision_id") == did]
            for ext in linked_exts:
                if ext.get("verif", "NV") != "VC":
                    r.error(
                        f"decision '{did}' etat=CONFIRME mais extraction '{ext['id']}' "
                        f"verif='{ext.get('verif','NV')}' ≠ VC (Invariant 7)"
                    )

        # Invariant 8 précondition : instance_id validé contre hiérarchie
        if has_instance and etat == "CONFIRME":
            inst = inst_idx.get(dec["instance_id"], {})
            q_id = dec.get("question_id", "")
            if not inst.get("parent") and not inst.get("nom"):
                r.warn(f"decision '{did}' instance_id '{dec['instance_id']}' non résolvable dans hiérarchie (Invariant 8)")

    return idx


def validate_questions(questions: list[dict], dec_idx: dict,
                        ext_idx: dict, r: ValidationResult) -> dict:
    idx = index_by_id(questions, "question", r)
    for q in questions:
        qid = q.get("id", "?")
        etat = q.get("etat", "")
        bloc = q.get("bloc", "")

        if etat not in VALID_QUESTION_ETAT:
            r.error(f"question '{qid}' etat invalide : '{etat}'")
        if bloc not in VALID_BLOCS:
            r.error(f"question '{qid}' bloc invalide : '{bloc}'")

        # Invariant 5 : etat=FERMEE → decision_id non-vide
        dec_id = q.get("decision_id", "")
        if etat == "FERMEE" and not dec_id:
            r.error(f"question '{qid}' etat=FERMEE sans decision_id (Invariant 5)")
        if dec_id and dec_id not in dec_idx:
            r.error(f"question '{qid}' decision_id '{dec_id}' introuvable")

        # Vérifier extraction_ids
        for eid in q.get("extraction_ids", []):
            if eid not in ext_idx:
                r.error(f"question '{qid}' extraction_id '{eid}' introuvable")

        # Verif
        verif = q.get("verif", "NV")
        if verif not in VALID_VERIF:
            r.error(f"question '{qid}' verif invalide : '{verif}'")

        # D-SIG cohérence
        bc  = q.get("baseline_cycles", 0)
        ttl = q.get("ttl_rounds", 0)
        if bc < 0:
            r.error(f"question '{qid}' baseline_cycles < 0")
        if ttl < 0:
            r.error(f"question '{qid}' ttl_rounds < 0")
        if ttl > 0 and bc > ttl:
            r.warn(f"question '{qid}' baseline_cycles ({bc}) > ttl_rounds ({ttl}) — potentiellement DEGRADING")

    return idx

# ═══════════════════════════════════════════════════════════════
# VALIDATION — enchaînement complet (partagé par validate et stamp)
# ═══════════════════════════════════════════════════════════════

def run_validators(corpus: dict) -> tuple[ValidationResult, dict, dict, dict, dict, dict, dict]:
    """Exécute tous les validateurs d'entité sur un corpus déjà chargé.
    Retourne le ValidationResult et les index id→dict de chaque entité."""
    r = ValidationResult()
    src_idx  = validate_sources(corpus.get("source", []), r)
    inst_idx = validate_instances(corpus.get("instance", []), r)
    run_idx  = validate_reunions(corpus.get("reunion", []), src_idx, r)
    ext_idx  = validate_extractions(corpus.get("extraction", []), src_idx, r)
    validate_provenance(corpus.get("extraction", []), ext_idx, r)  # Invariant 9 (CT-002)
    dec_idx  = validate_decisions(corpus.get("decision", []),
                                   src_idx, run_idx, inst_idx, ext_idx, r)
    q_idx    = validate_questions(corpus.get("question", []), dec_idx, ext_idx, r)
    return r, src_idx, inst_idx, run_idx, ext_idx, dec_idx, q_idx

# ═══════════════════════════════════════════════════════════════
# COMMANDE : validate
# ═══════════════════════════════════════════════════════════════

def cmd_validate(path: Path) -> int:
    """
    Valide un fichier TOML contre le schéma TI-360 v0.3 (Invariants 1-8).
    Retourne 0 si valide, 1 si erreurs.
    """
    print(f"\nkb.py validate — TI-360 KB v{VERSION} (schema {SCHEMA_VERSION})")
    print(f"Fichier : {path}\n")

    try:
        corpus = load_toml(path)
    except Exception as e:
        print(f"✗ Impossible de lire le fichier TOML : {e}")
        return 1

    r, src_idx, inst_idx, run_idx, ext_idx, dec_idx, q_idx = run_validators(corpus)

    # Résumé des entités trouvées
    print(f"[CORPUS]  {len(src_idx)} source(s) | {len(inst_idx)} instance(s) | "
          f"{len(run_idx)} réunion(s) | {len(ext_idx)} extraction(s) | "
          f"{len(dec_idx)} décision(s) | {len(q_idx)} question(s)")

    r.print_report()
    return 0 if r.ok() else 1

# ═══════════════════════════════════════════════════════════════
# COMMANDE : stamp — couche découverte (marqueur KB-STATUS)
# ═══════════════════════════════════════════════════════════════

def derive_file_status(corpus: dict) -> str:
    """
    Dérive un statut de FICHIER (couche découverte) depuis l'état agrégé
    du corpus (couche sens). Heuristique de première version — volontairement
    simple et lisible plutôt qu'exhaustive :

      ACTIVE     s'il reste au moins une question OUVERTE/BLOQUANTE/HYPOTHESE_PROVISOIRE
      SUPERSEDED si toutes les decisions du corpus sont etat=SUPERSEDE
      ARCHIVED   si toutes les sources du corpus ont statut=ARCHIVE
      DRAFT      cas par défaut (corpus vide, ou source(s) encore EBAUCHE)

    VOID n'est jamais dérivé automatiquement : « référence non plus
    interprétable » est un jugement éditorial, pas une inférence structurelle
    — il doit être posé explicitement via --status VOID.
    """
    questions = corpus.get("question", [])
    decisions = corpus.get("decision", [])
    sources   = corpus.get("source", [])

    if any(q.get("etat") in {"OUVERTE", "BLOQUANTE", "HYPOTHESE_PROVISOIRE"} for q in questions):
        return "ACTIVE"
    if decisions and all(d.get("etat") == "SUPERSEDE" for d in decisions):
        return "SUPERSEDED"
    if sources and all(s.get("statut") == "ARCHIVE" for s in sources):
        return "ARCHIVED"
    if not questions and not decisions and sources:
        statut_source = sources[0].get("statut", "")
        if statut_source == "APPROUVE":
            return "ACTIVE"
        if statut_source == "ARCHIVE":
            return "ARCHIVED"
        return "DRAFT"
    if questions or decisions:
        # tout est fermé/résolu, rien de superseded : considéré stable
        return "ACTIVE"
    return "DRAFT"


def find_stamp_line(lines: list[str]) -> int | None:
    """Cherche une ligne KB-STATUS existante dans les STAMP_SCAN_LINES
    premières lignes. Retourne son index, ou None si absente."""
    for i, line in enumerate(lines[:STAMP_SCAN_LINES]):
        if "KB-STATUS:" in line:
            return i
    return None


def cmd_stamp(path: Path, explicit_id: str | None, explicit_ref: str | None,
              explicit_status: str | None, dry_run: bool) -> int:
    """
    Régénère la ligne KB-STATUS en tête du fichier depuis l'état du corpus.
    Vue générée (comme TOON) — jamais éditée à la main pour un fichier qui
    porte des entités TI-360. Refuse de stamper un corpus qui échoue la
    validation structurelle : un statut dérivé d'un graphe invalide n'a pas
    de sens.
    """
    print(f"\nkb.py stamp — TI-360 KB v{VERSION} (schema {SCHEMA_VERSION})")
    print(f"Fichier : {path}\n")

    try:
        corpus = load_toml(path)
    except Exception as e:
        print(f"✗ Impossible de lire le fichier TOML : {e}")
        return 1

    r, src_idx, inst_idx, run_idx, ext_idx, dec_idx, q_idx = run_validators(corpus)
    if not r.ok():
        print("✗ Validation structurelle échouée — stamp refusé (kb.py validate d'abord) :")
        r.print_report()
        return 1

    if explicit_status is not None:
        if explicit_status not in VALID_FILE_STATUS:
            print(f"✗ --status invalide : '{explicit_status}' — attendu {VALID_FILE_STATUS}")
            return 1
        status = explicit_status
    else:
        status = derive_file_status(corpus)

    file_id = explicit_id or path.stem
    ref = explicit_ref
    if ref is None:
        sources = corpus.get("source", [])
        ref = sources[0].get("id", "") if sources else ""

    updated = date.today().isoformat()

    stamp_line = f"# KB-STATUS: id={file_id} status={status} updated={updated}"
    if ref:
        stamp_line += f" ref={ref}"

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    idx = find_stamp_line(lines)

    if idx is not None:
        old = lines[idx].rstrip("\n")
        lines[idx] = stamp_line + "\n"
        action = f"remplacée — ancienne ligne : {old.strip()}"
    else:
        lines.insert(0, stamp_line + "\n\n")
        action = "insérée en tête de fichier (aucune ligne KB-STATUS préexistante)"

    print(f"[STAMP]  {stamp_line}")
    print(f"[ACTION] {action}")

    if dry_run:
        print("\n(dry-run — fichier non modifié)")
        return 0

    path.write_text("".join(lines), encoding="utf-8")
    print(f"\n✓ {path} mis à jour.")
    return 0

# ═══════════════════════════════════════════════════════════════
# COMMANDE : status
# ═══════════════════════════════════════════════════════════════

def cmd_status(path: Path, filter_beta: str = None, filter_bloc: str = None) -> int:
    """Affiche l'état des questions avec filtres optionnels."""
    try:
        corpus = load_toml(path)
    except Exception as e:
        print(f"✗ {e}"); return 1

    questions = corpus.get("question", [])

    # Filtres
    if filter_beta:
        questions = [q for q in questions if q.get("beta_derived", q.get("verif")) == filter_beta
                     or True]  # placeholder — sera calculé depuis extractions liées en v0.2
    if filter_bloc:
        questions = [q for q in questions if q.get("bloc") == filter_bloc.upper()]

    BETA_SYMBOL = {"T": "✓", "F": "✗", "B": "±", "N": "?"}
    ETAT_COLOR  = {
        "FERMEE":              "FERMÉE  ",
        "OUVERTE":             "OUVERTE ",
        "BLOQUANTE":           "BLOQUANT",
        "HYPOTHESE_PROVISOIRE":"HYPOTH. ",
        "ARCHIVEE":            "ARCHIVÉE",
    }

    print(f"\n{'ID':<10} {'BLOC':<8} {'STATUT':<10} {'VER':<4} {'BC':>4} {'TTL':>4}  QUESTION")
    print("─" * 100)

    for q in sorted(questions, key=lambda x: x.get("bloc", "Z")):
        qid   = q.get("id", "?")
        bloc  = q.get("bloc", "?")
        etat  = ETAT_COLOR.get(q.get("etat", ""), q.get("etat", "?")[:8])
        verif = q.get("verif", "NV")
        bc    = q.get("baseline_cycles", 0)
        ttl   = q.get("ttl_rounds", 0)
        enonce = q.get("enonce", "")[:70]
        print(f"{qid:<10} {bloc:<8} {etat:<10} {verif:<4} {bc:>4} {ttl:>4}  {enonce}")

    # Compteurs
    ouverts   = sum(1 for q in questions if q.get("etat") == "OUVERTE")
    fermes    = sum(1 for q in questions if q.get("etat") == "FERMEE")
    bloq      = sum(1 for q in questions if q.get("etat") == "BLOQUANTE")
    hypo      = sum(1 for q in questions if q.get("etat") == "HYPOTHESE_PROVISOIRE")
    print(f"\n[RÉSUMÉ] {len(questions)} question(s) — "
          f"{fermes} fermée(s) | {ouverts} ouverte(s) | {bloq} bloquante(s) | {hypo} hypothèse(s)")
    return 0

# ═══════════════════════════════════════════════════════════════
# COMMANDE : toon
# ═══════════════════════════════════════════════════════════════

def cmd_toon(path: Path) -> int:
    """
    Génère la vue TOON depuis un TOML.
    TOON = tableau condensé, ~25% moins de tokens que TOML, pour contexte LLM.
    Format : | ID | TYPE | BLOC | BETA | VERIF | CONTENU (50 mots max) |
    """
    try:
        corpus = load_toml(path)
    except Exception as e:
        print(f"✗ {e}"); return 1

    # En-tête
    sep = "+" + "-"*10 + "+" + "-"*14 + "+" + "-"*8 + "+" + "-"*6 + "+" + "-"*6 + "+" + "-"*55 + "+"
    header = f"| {'ID':<8} | {'TYPE':<12} | {'BLOC':<6} | {'BETA':<4} | {'VER':<4} | {'CONTENU':<53} |"
    print(f"\n# TOON VIEW — {path.name}")
    print(f"# Généré par kb.py v{VERSION} | Schema {SCHEMA_VERSION}")
    print(sep)
    print(header)
    print(sep)

    for ext in corpus.get("extraction", []):
        eid     = ext.get("id", "")[:8]
        etype   = ext.get("type", "")[:12]
        bloc    = ext.get("bloc", "")[:6]         # via question liée — simplification v0.1
        beta    = ext.get("beta", "N")[:4]
        verif   = ext.get("verif", "NV")[:4]
        contenu = ext.get("contenu", "")[:53]
        print(f"| {eid:<8} | {etype:<12} | {bloc:<6} | {beta:<4} | {verif:<4} | {contenu:<53} |")

    print(sep)

    # Questions
    print(f"\n# QUESTIONS")
    sep_q = "+" + "-"*10 + "+" + "-"*8 + "+" + "-"*12 + "+" + "-"*6 + "+" + "-"*6 + "+" + "-"*6 + "+" + "-"*35 + "+"
    hdr_q = f"| {'ID':<8} | {'BLOC':<6} | {'ETAT':<10} | {'VER':<4} | {'BC':>4} | {'TTL':>4} | {'ENONCE':<33} |"
    print(sep_q)
    print(hdr_q)
    print(sep_q)
    for q in corpus.get("question", []):
        qid    = q.get("id", "")[:8]
        bloc   = q.get("bloc", "")[:6]
        etat   = q.get("etat", "")[:10]
        verif  = q.get("verif", "NV")[:4]
        bc     = str(q.get("baseline_cycles", 0))[:4]
        ttl    = str(q.get("ttl_rounds", 0))[:4]
        enonce = q.get("enonce", "")[:33]
        print(f"| {qid:<8} | {bloc:<6} | {etat:<10} | {verif:<4} | {bc:>4} | {ttl:>4} | {enonce:<33} |")
    print(sep_q)
    return 0

# ═══════════════════════════════════════════════════════════════
# COMMANDE : reindex (stub Phase 2)
# ═══════════════════════════════════════════════════════════════

def cmd_reindex(path: Path) -> int:
    print("reindex : Phase 2 — SQLite non encore implémenté.")
    print("La source de vérité reste le fichier TOML.")
    return 0

# ═══════════════════════════════════════════════════════════════
# COMMANDE : stamp-verdict — couche preuve de clôture
# ═══════════════════════════════════════════════════════════════

def parse_preuve_cloture(path: Path) -> dict | None:
    """
    Extrait le bloc [[preuve_cloture]] d'un fichier VERDICT-*.md.
    Exclut les blocs de code (```...```).
    Retourne un dict avec les champs, ou None si absent/invalide.
    """
    if not path.name.startswith("VERDICT-"):
        return None

    text = path.read_text(encoding="utf-8")
    # Supprimer les blocs de code pour éviter les faux positifs
    cleaned = CODE_BLOCK_RE.sub("", text)

    m = PREUVE_BLOCK_RE.search(cleaned)
    if not m:
        return None

    block_text = m.group(1)
    fields = {}
    for fm in PREUVE_FIELD_RE.finditer(block_text):
        fields[fm.group(1)] = fm.group(2)
    return fields if fields else None


def sha256_file(path: Path) -> str:
    """Calcule le hash SHA-256 d'un fichier."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def validate_preuve_cloture(verdict_path: Path) -> tuple[bool, str]:
    """
    Valide le bloc [[preuve_cloture]] d'un VERDICT-*.md.
    Vérifie : champs requis, cible_hash correspond au fichier réel,
    sortie_fichier existe, sortie_hash correspond à la sortie réelle.
    Retourne (validé: bool, raison: str).
    """
    fields = parse_preuve_cloture(verdict_path)
    if fields is None:
        return False, "aucun bloc [[preuve_cloture]] trouvé"

    # Vérifier champs requis
    missing = REQUIRED_PREUVE_FIELDS - set(fields.keys())
    if missing:
        return False, f"champs manquants : {missing}"

    # Vérifier cible_hash
    cible = verdict_path.parent / fields["cible_fichier"]
    if not cible.exists():
        return False, f"fichier cible introuvable : {fields['cible_fichier']}"
    real_hash = sha256_file(cible)
    if real_hash != fields["cible_hash"]:
        return False, (
            f"cible_hash diverge : déclaré={fields['cible_hash']}, "
            f"réel={real_hash}"
        )

    # Vérifier sortie_fichier
    sortie = verdict_path.parent / fields["sortie_fichier"]
    if not sortie.exists():
        return False, f"fichier de sortie introuvable : {fields['sortie_fichier']}"
    if sortie.stat().st_size == 0:
        return False, f"fichier de sortie vide : {fields['sortie_fichier']}"
    real_sortie_hash = sha256_file(sortie)
    if real_sortie_hash != fields["sortie_hash"]:
        return False, (
            f"sortie_hash diverge : déclaré={fields['sortie_hash']}, "
            f"réel={real_sortie_hash}"
        )

    return True, "VALIDÉ"


def cmd_stamp_verdict(path: Path, dry_run: bool = False) -> int:
    """
    Stammpe un fichier VERDICT-*.md avec KB-STATUS.
    Si le verdict est CLOS, exige un bloc [[preuve_cloture]] valide.
    Sans preuve valide → CLOS-NON-PROUVÉ.
    """
    print(f"\nkb.py stamp-verdict — TI-360 KB v{VERSION} (schema {SCHEMA_VERSION})")
    print(f"Fichier : {path}\n")

    text = path.read_text(encoding="utf-8")

    # Extraire le Statut du frontmatter
    statut_match = re.search(r'\*\*Statut\s*:\*\*\s*(\S+)', text)
    if not statut_match:
        print("✗ Champ **Statut** introuvable dans le fichier.")
        return 1

    declared_status = statut_match.group(1).rstrip(")")
    print(f"[STATUT] déclaré : {declared_status}")

    if declared_status != "CLOS":
        print(f"[INFO] Statut '{declared_status}' ≠ CLOS — stamp classique KB-STATUS")
        # Pas de validation preuve requise
        return 0

    # Statut CLOS : validation preuve obligatoire
    valid, reason = validate_preuve_cloture(path)
    if valid:
        status = "CLOS"
        print(f"[PREUVE] ✓ {reason}")
    else:
        status = "CLOS-NON-PROUVÉ"
        print(f"[PREUVE] ✗ {reason}")
        print(f"[ACTION] Statut forcé → {status}")

    # Écrire KB-STATUS
    updated = date.today().isoformat()
    stamp_line = f"# KB-STATUS: id={path.stem} status={status} updated={updated}"

    lines = text.splitlines(keepends=True)
    idx = find_stamp_line(lines)

    if idx is not None:
        old = lines[idx].rstrip("\n")
        lines[idx] = stamp_line + "\n"
        action = f"remplacée — ancienne ligne : {old.strip()}"
    else:
        lines.insert(0, stamp_line + "\n\n")
        action = "insérée en tête de fichier"

    print(f"[STAMP]  {stamp_line}")
    print(f"[ACTION] {action}")

    if dry_run:
        print("\n(dry-run — fichier non modifié)")
        return 0 if valid else 1

    path.write_text("".join(lines), encoding="utf-8")
    print(f"\n✓ {path} mis à jour.")
    return 0 if valid else 1

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="kb.py",
        description=f"TI-360 Knowledge Base CLI v{VERSION}"
    )
    parser.add_argument("command", choices=["validate", "toon", "status", "reindex", "stamp", "stamp-verdict"],
                        help="Commande à exécuter")
    parser.add_argument("file", type=Path,
                        help="Fichier TOML source")
    parser.add_argument("--filter-beta", dest="filter_beta",
                        choices=["T","F","B","N"], help="Filtrer questions par état beta")
    parser.add_argument("--filter-bloc", dest="filter_bloc",
                        help="Filtrer questions par bloc (0,A,B,...)")
    parser.add_argument("--id", dest="stamp_id", default=None,
                        help="[stamp] id à écrire dans KB-STATUS (défaut : nom du fichier)")
    parser.add_argument("--ref", dest="stamp_ref", default=None,
                        help="[stamp] ref à écrire dans KB-STATUS (défaut : id de la 1ère source)")
    parser.add_argument("--status", dest="stamp_status", default=None,
                        choices=sorted(VALID_FILE_STATUS),
                        help="[stamp] force le statut plutôt que de le dériver (requis pour VOID)")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true",
                        help="[stamp] affiche le résultat sans modifier le fichier")
    parser.add_argument("--version", action="version",
                        version=f"kb.py {VERSION} (schema {SCHEMA_VERSION})")

    args = parser.parse_args()

    if not args.file.exists():
        print(f"✗ Fichier introuvable : {args.file}")
        sys.exit(1)

    dispatch = {
        "validate": lambda: cmd_validate(args.file),
        "toon":     lambda: cmd_toon(args.file),
        "status":   lambda: cmd_status(args.file, args.filter_beta, args.filter_bloc),
        "reindex":  lambda: cmd_reindex(args.file),
        "stamp":    lambda: cmd_stamp(args.file, args.stamp_id, args.stamp_ref,
                                       args.stamp_status, args.dry_run),
        "stamp-verdict": lambda: cmd_stamp_verdict(args.file, args.dry_run),
    }

    sys.exit(dispatch[args.command]())


if __name__ == "__main__":
    main()
