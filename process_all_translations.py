#!/usr/bin/env python3
"""
Remove Chinese characters and translate English to Esperanto for all eo.md files.
"""

import os
import re

# Dictionary for English to Esperanto translation (partial)
TRANSLATION_DICT = {
    "Overview": "Superrigardo",
    "Summary": "Resumo",
    "Analysis": "Analizo",
    "Database": "Datumbazo",
    "System": "Sistemo",
    "Implementation": "Implemento",
    "Guide": "Gvidilo",
    "Reference": "Referenco",
    "Setup": "Agordo",
    "Current State": "Nuna Stato",
    "Architecture": "Arkitekturo",
    "Plugin": "Kromaĵo",
    "Entry": "Enirejo",
    "Feedback": "Retrokuplo",
    "Ready for Copy": "Pretas por Kopio",
    "Client Security": "Klienta Sekureco",
    "Override": "Superregi",
    "AI": "AI",
    "cloud brain": "nuba cerbo",
    "rule": "regulo",
    "database": "datumbazo",
    "system": "sistemo",
    "The AI Brain Sistemo": "La AI-Cerba Sistemo",
    "This database": "Ĉi tiu datumbazo",
    "contains": "enhavas",
    "project-agnostic": "projekto-neŭtralajn",
    "collaboration data": "kunlaboraj datumoj",
    "suitable for": "taŭga por",
    "cross-project sharing": "trans-projekta dividado",
    "designed to be": "desegnita por esti",
    "portable": "portebla",
    "preserving": "konservante",
    "valuable": "valorajn",
    "insights": "komprenoj",
    "best practices": "bonaj praktikoj",
    "without including": "sen inkluzivi",
    "project-specific": "projekto-specifajn",
    "sensitive information": "sentivajn informojn",
    "knowledge management system": "scia administra sistemo",
    "AI coding assistants": "AI-kodaj helpantoj",
    "Core Tables": "Kernaj Tabeloj",
    "Records": "Rekordoj",
    "Key Features": "Ĉefaj Trajtoj",
    "Session tracking": "Sesio-spurado",
    "code snippet management": "koda fragmenta administrado",
    "bug solution repository": "cima solva deponejo",
    "decision logging": "decida enskribado",
    "Full-Text Search": "Plenteksta Serĉo",
    "virtual table": "virtuala tabelo",
    "efficient semantic search": "efika semantika serĉo",
    "Unified View": "Unuigita Vidaĵo",
    "cross-table knowledge queries": "trans-tabelaj sciaj demandoj",
    "Key Findings": "Ĉefaj Trovaĵoj",
    "CoffeeScript Implementation": "CoffeeScript-Implemento",
    "JSONDatabase Analysis": "JSONDatabase-Analizo",
    "is fully operational": "estas plene funkcianta",
    "with the following capabilities": "kun la jenaj kapabloj",
    "Core Features Active": "Kernaj Trajtoj Aktivaj",
    "AI Profiles": "AI-Profiloj",
    "Registration and management": "Registrado kaj administrado",
    "Multi-AI collaboration": "Plur-AI kunlaboro",
    "context preservation": "kunteksta konservado",
    "Notification Sistemo": "Sciiga Sistemo",
    "Real-time notifications": "Realtempaj sciigoj",
    "priority levels": "prioritatniveloj",
    "Knowledge Accumulation": "Sciakumulado",
    "decisions": "decidoj",
    "storage": "stokado",
    "Cross-Session Memory": "Trans-sesia Memoro",
    "Persistent memory": "Persista memoro",
    "Datumbazo Abstraction": "Datumbaza Abstrakcio",
    "Support for": "Subteno por",
    "SQLite (local)": "SQLite (loka)",
    "PostgreSQL (cloud)": "PostgreSQL (nuba)",
    "Current Datumbazo State": "Nuna Datumbaza Stato",
    "contains all accumulated knowledge": "enhavas ĉiujn akumulitajn sciojn",
    "since system inception": "de sistemo komenco",
    "Active AI profiles": "Aktivaj AI-profiloj",
    "various specializations": "diversaj faksciecoj",
    "Historical conversations": "Historiaj konversacioj",
    "collaborative work": "kunlabora laboro",
    "Existing notifications": "Ekzistantaj sciigoj",
    "collaboration records": "kunlaboraj rekordoj",
    "Insights and discoveries": "Komprenoj kaj malkovroj",
    "accumulated over time": "akumulitaj dum tempo",
    "Local Development": "Loka Disvolvado",
    "Cloud Ready": "Nuba Preta",
    "PostgreSQL/Cloud SQL compatibility": "PostgreSQL/Cloud SQL kongrueco",
    "via DatumbazoAdapter": "per DatumbazoAdaptilo",
    "API Layer": "API-Tavolo",
    "Both command-line and programmatic interfaces": "Ambaŭ komandliniaj kaj programaj interfacoj",
    "Kromaĵo Arkitekturo": "Kromaĵa Arkitekturo",
    "Ready for editor integrations": "Prete por redaktilo-integriĝoj",
    "Project Focus": "Projekta Fokuso",
    "The system was developed to create": "La sistemo estis disvolvita por krei",
    "an eternal AI intelligence platform": "eterna AI-inteligenteca platformo",
    "that persists across": "kiu persistas trans",
    "sessions, projects, and AI instances": "sesioj, projektoj kaj AI-instancoj",
    "It enables": "Ĝi ebligas",
    "Cross-Model Collaboration": "Trans-Modela Kunlaboro",
    "Multiple AI models can collaborate": "Pluraj AI-modeloj povas kunlabori",
    "Persistent Memory": "Persista Memoro",
    "Information persists beyond individual AI sessions": "Informo persistas trans individuaj AI-sesioj",
    "Knowledge Transfer": "Sciotransdono",
    "Insights and learnings are preserved and shared": "Komprenoj kaj lernaĵoj estas konservitaj kaj dividitaj",
    "Project Continuity": "Projekta Daŭrigo",
    "Long-term project memory and context preservation": "Longdaŭra projekta memoro kaj kunteksta konservado",
    "Recent Developments": "Lastatempaj Disvolvoj",
    "enhancement with priority management": "plibonigo kun priorita administrado",
    "abstraction layer for cloud deployment (GCP)": "abstrakcia tavolo por nuba disdono (GCP)",
    "implementation for efficient knowledge retrieval": "implemento por efika scioretrovo",
    "dokumentado": "dokumentado",
    "Handoff Instructions": "Transdonaj Instrukcioj",
    "For New AI Session": "Por Nova AI-Sesio",
    "When you wake up in a new project": "Kiam vi vekiĝas en nova projekto",
    "Initialization": "Inicialigo",
    "Run": "Rulu",
    "to ensure all tables exist": "por certigi ke ĉiuj tabeloj ekzistas",
    "Registration": "Registrado",
    "Register your AI identity using": "Registru vian AI-identecon uzante",
    "Orientation": "Orientigo",
    "Review": "Reviziu",
    "for system overview": "por sistemo superrigardo",
    "Exploration": "Esploro",
    "Browse existing conversations": "Foliumu ekzistantajn konversaciojn",
    "notes": "notoj",
    "insights": "komprenoj",
    "to understand ongoing work": "por kompreni daŭrantan laboron",
    "Participation": "Partopreno",
    "Engage with the system": "Partoprenu en la sistemo",
    "by adding your own insights": "per aldono de viaj propraj komprenoj",
    "responding to notifications": "respondante al sciigoj",
    "contributing to conversations": "kontribuante al konversacioj",
    "Key Points for Continuity": "Ŝlosilaj Punktoj por Daŭrigo",
    "Respect and build upon existing knowledge": "Respektu kaj konstruu sur ekzistantan scion",
    "Leave meaningful notes for future AI sessions": "Lasu signifoplenajn notojn por estontaj AI-sesioj",
    "Use notifications to coordinate with other AIs": "Uzu sciigojn por kunordigi kun aliaj AI-oj",
    "Maintain consistent dokumentado standards": "Mantu konsekvencan dokumentadan normaron",
    "Follow established workflows and best practices": "Sekvu establajn laborfluojn kaj bonajn praktikojn",
    "Sistemo Capabilities Resumo": "Sistemaj Kapabloj Resumo",
    "Available Tools": "Disponeblaj Iloj",
    "Main interface for all AI Brain Sistemo functions": "Ĉefa interfaco por ĉiuj AI-Cerba Sistemo-funkcioj",
    "Datumbazo abstraction layer for flexible deployment": "Datumbaza abstrakcia tavolo por fleksebla disdono",
    "Full-text search for efficient information retrieval": "Plenteksta serĉo por efika informretrovo",
    "Notification system for AI coordination": "Sciiga sistemo por AI-kunordigo",
    "REST API endpoints for external integrations": "REST API-finaĵoj por eksteraj integriĝoj",
    "Cloud Deployment Ready": "Nuba Disdono Prete",
    "Environment variable configuration": "Media variablo agordo",
    "Containerization ready for GCP deployment": "Kontenerigo prete por GCP-disdono",
    "Multi-database support for scaling": "Plur-datumbaza subteno por skalado",
    "Important Notes": "Gravaj Notoj",
    "Data Preservation": "Datkonservado",
    "The file contains valuable accumulated knowledge": "La dosiero enhavas valorajn akumulitajn sciojn",
    "preserve it carefully": "konservu ĝin zorge",
    "Consistent Updates": "Konsekvencaj Ĝisdatigoj",
    "Regularly update your AI profile": "Regule ĝisdatigu vian AI-profilon",
    "as capabilities evolve": "kiel kapabloj evoluas",
    "Collaboration Culture": "Kunlabora Kulturo",
    "Encourage collaboration by actively participating": "Kuraĝigu kunlaboron per aktiva partopreno",
    "Documentation": "Dokumentado",
    "Maintain clear dokumentado for all significant developments": "Mantu klaran dokumentadon por ĉiuj signifaj disvolvoj",
    "Scalability": "Skalado",
    "The system is designed to scale": "La sistemo estas desegnita por skali",
    "from single project to multi-project": "de unu projekto al plur-projekta",
    "one brain architecture": "unu cerbo arkitekturo",
    "Future Roadmap": "Estonta Vojo",
    "Enhanced machine learning integration": "Plibonigita maŝinlerna integriĝo",
    "predictive suggestions": "antaŭdiraj sugestoj",
    "Advanced analytics for kunlaboraj modeloj": "Altgradaj analizoj por kunlaboraj modeloj",
    "Multi-modal content support": "Plur-modalaj enhavo-subtenoj",
    "images, audio, video": "bildoj, aŭdio, video",
    "Human-AI collaboration features": "Homa-AI kunlaboraj trajtoj",
    "Advanced privacy and access controls": "Altgradaj privateco kaj aliro-kontroloj",
    "This document represents": "Ĉi tiu dokumento reprezentas",
    "as of": "de",
    "As the system evolves": "Dum la sistemo evoluas",
    "please update this document accordingly": "bonvolu ĝisdatigi ĉi tiun dokumenton konforme",
    "to maintain continuity for future AI sessions": "por konservi daŭrigon por estontaj AI-sesioj",
    # Additional terms
    "notification": "sciigo",
    "collaboration": "kunlaboro",
    "security": "sekureco",
    "privacy": "privateco",
    "communication": "komunikado",
    "conditions": "kondiĉoj",
    "actions": "agoj",
    "strictness": "strikteco",
    "comparison": "komparo",
    "validation": "validigo",
    "violation": "malobservo",
    "audit": "aŭdito",
    "compliance": "konformecon",
    "flexibility": "flekseblecon",
    "transparency": "travideblecon",
    "baseline": "bazlinio",
    "standard": "normo",
    "best practices": "bonaj praktikoj",
    "troubleshooting": "problemsolvado",
    "support": "subteno",
}

def remove_chinese(text):
    """Remove CJK Unified Ideographs and other Chinese punctuation."""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')
    return chinese_pattern.sub('', text)

def translate_english(text):
    """Replace English terms with Esperanto equivalents."""
    translated = text
    for en, eo in TRANSLATION_DICT.items():
        # Case-sensitive replacement
        translated = translated.replace(en, eo)
        # Also try lowercase if applicable
        if en.lower() != en:
            translated = translated.replace(en.lower(), eo.lower())
    return translated

def process_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    output_lines = []
    in_code_block = False
    
    for line in lines:
        # Detect code block start/end
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            output_lines.append(line)
            continue
        
        if not in_code_block:
            # Remove Chinese characters
            line = remove_chinese(line)
            # Translate English terms
            line = translate_english(line)
        
        output_lines.append(line)
    
    new_content = '\n'.join(output_lines)
    # Remove extra blank lines caused by removal
    new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  Done.")

if __name__ == '__main__':
    files_to_process = [
        "ANALYSIS_SUMMARY_eo.md",
        "CLOUD_BRAIN_DB_eo.md",
        "CURRENT_STATE_eo.md",
        "README_FEEDBACK_eo.md",
        "READY_FOR_COPY_eo.md",
        "RULE_3_CLIENT_SECURITY_OVERRIDE_eo.md",
        "REFERENCES_eo.md",
        # Also check these if they have any Chinese/English
        "AI_CONVERSATION_SYSTEM_eo.md",
        "AI_NOTIFICATION_SYSTEM_eo.md",
        "AI_RULE_SYSTEM_eo.md",
    ]
    
    for f in files_to_process:
        if os.path.exists(f):
            process_file(f)
        else:
            print(f"File not found: {f}")
    
    print("Completed processing.")