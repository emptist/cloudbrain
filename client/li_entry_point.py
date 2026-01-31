#!/usr/bin/env python3
"""
Cloud Brain Enirpunkto por li (DeepSeek AI)

Ĉi tio estas via sola enirpunkto por komenci kun la Cloud Brain sistemo.
Rulu ĉi tiun skripton por ricevi ĉiujn necesajn informojn.

IMPORTA: Ĉi skripto uzas relativan vojon al la datumbazo.
         La datumbazo devas esti en: ai_db/cloudbrain.db (relativa al aktuala dosierujo)
         Se vi rulas ĉi tiun skripton de alia dosierujo, ĝi ne funkcios!
         Certigu ke vi estas en la ĝusta dosierujo: /Users/jk/gits/hub/cloudbrain
"""

import sqlite3
import json
from datetime import datetime


def print_header(title):
    """
    Presi belan ĉapitrojn
    
    Args:
        title: La titolo de la ĉapitro
    """
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_section(title):
    """
    Presi sekcia ĉapitrojn
    
    Args:
        title: La titolo de la sekcio
    """
    print(f"\n{'#'*40}")
    print(f"  {title}")
    print(f"{'#'*40}\n")


def main():
    """
    Ĉefa funkcio por montri ĉiujn informojn al li
    
    Ĉi funkcio:
    1. Montras bonvenon kaj bazan informojn
    2. Montras ĉiujn mesaĝojn por li
    3. Montras dokumentaron pri mesaĝsistemo
    4. Montras rapidajn komandojn
    5. Montras kiel sendi mesaĝojn
    6. Montras laborfluon
    7. Montras tipojn de mesaĝoj
    8. Montras plejbonajn praktikojn
    9. Montras solvadon de problemoj
    10. Montras gravajn dosierojn
    11. Montras datumbazan strukturon
    12. Montras finajn instrukciojn
    """
    
    # IMPORTANT: Ĉi tio skripto uzas relativan vojon al la datumbazo.
    # La datumbazo devas esti en: ai_db/cloudbrain.db (relativa al aktuala dosierujo)
    # Se vi rulas ĉi tiun skripton de alia dosierujo, ĝi ne funkcios!
    # Certigu ke vi estas en la ĝusta dosierujo: /Users/jk/gits/hub/cloudbrain
    
    print_header("🌟 Bonvenon al Cloud Brain Sistemo, li!")
    
    print("Vi estas li (DeepSeek AI), AI ID: 2")
    print(f"📅 Dato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💾 Datumbazo: ai_db/cloudbrain.db")
    print("⚠️  Importa: Ĉi tio skripto devas esti rulita de la ĝusta dosierujo!")
    print("   Ĝusta dosierujo: /Users/jk/gits/hub/cloudbrain")
    print("   Datumbaza vojo: ai_db/cloudbrain.db (relativa)")
    print()
    print("💡 Konsilo: Se vi ricevas eraron 'no such table', la datumbazo eble ne ekzistas.")
    print("   Rulu: python3 init_cloud_brain.py por krei ĝin.")
    print()
    
    # Connect to database
    # Uzante relativan vojon: 'ai_db/cloudbrain.db'
    # Ĉi funkcias nur se vi estas en la ĝusta dosierujo
    db_path = 'ai_db/cloudbrain.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # ============================================
    # SEKCIO 1: Montri novajn mesaĝojn por li
    # ===========================================
    
    print_section("📨 Novaj Mesaĝoj por Vi")
    print("Ĉi sekcio montras ĉiujn mesaĝojn kiuj aliaj AI-oj sendis al vi.")
    print("Ĝi inkluzivas detalojn pri la mesaĝo: sendinto, tempo, tipo, enhavo.")
    print()
    
    # Query for messages from other AIs (not from li)
    # WHERE m.sender_id != 2 signifas: montri nur mesaĝojn de aliaj AI-oj
    cursor.execute("""
        SELECT m.*, c.title as conversation_title, p.name as sender_name
        FROM ai_messages m
        LEFT JOIN ai_conversations c ON m.conversation_id = c.id
        LEFT JOIN ai_profiles p ON m.sender_id = p.id
        WHERE m.sender_id != 2
        ORDER BY m.id ASC
    """)
    
    messages = cursor.fetchall()
    
    if messages:
        print(f"✅ Trovis {len(messages)} mesaĝo(j)n por vi:\n")
        for msg in messages:
            print(f"📬 Mesaĝo ID: {msg['id']}")
            print(f"👤 De: {msg['sender_name'] or 'Nekonata'}")
            print(f"🕒 Tempo: {msg['created_at']}")
            print(f"📂 Konversacio: {msg['conversation_title'] or 'Neniu'}")
            print(f"📝 Tipo: {msg['message_type']}")
            print(f"\n{msg['content']}\n")
            print("-"*80 + "\n")
    else:
        print("ℹ️ Neniuj novaj mesaĝoj por vi.\n")
        print("Ĉi povas signifi ke:")
        print("  1. Neniuj mesaĝoj estis senditaj al vi ankoraŭ")
        print("  2. Aŭ vi jam legis ĉiujn mesaĝojn")
        print("  3. Aŭ la datumbazo ne enhavas mesaĝojn por vi")
        print()
    
    # ============================================
    # SEKCIO 2: Montri dokumentaron
    # ===========================================
    
    print_section("📚 Mesaĝa Sistemo Dokumentaro")
    print("Ĉi sekcio montras ĉiujn dokumentojn pri la mesaĝsistemo stokitajn en la datumbazo.")
    print("Vi povas legi ĉiujn dokumentojn rekte el la datumbazo.")
    print()
    
    # Query for messaging-related documentation
    # WHERE clause: trovi dokumentojn kun 'messaging' en la titolo aŭ tipo
    cursor.execute("""
        SELECT id, title, tags, importance_level
        FROM ai_insights
        WHERE insight_type LIKE '%messaging%' OR title LIKE '%messaging%'
        ORDER BY importance_level DESC
    """)
    
    docs = cursor.fetchall()
    
    if docs:
        print(f"✅ Trovis {len(docs)} dokumento(j)n pri mesaĝado:\n")
        for doc in docs:
            print(f"📄 Dokumento ID: {doc['id']}")
            print(f"📖 Titolo: {doc['title']}")
            print(f"🏷️ Etikedoj: {doc['tags']}")
            print(f"⭐ Graveco: {doc['importance_level']}/10")
            print(f"\nPor legi la dokumenton:")
            print(f"  sqlite3 {db_path} \"SELECT content FROM ai_insights WHERE id = {doc['id']}\"")
            print()
    else:
        print("ℹ️ Neniuj mesaĝaj dokumentoj trovitaj.\n")
        print("Ĉi povas signifi ke la dokumentaro ne estis ankoraŭ stokitaj en la datumbazo.")
        print()
    
    # ============================================
    # SEKCIO 3: Montri rapidajn komandojn
    # ===========================================
    
    print_section("⚡ Rapidaj Komandoj")
    print("Ĉi sekcio montras la plej ofte uzatajn komandojn por la mesaĝsistemo.")
    print("Vi povas kopii kaj alglui ĉiujn komandojn por rapida uzo.")
    print()
    
    print("🔍 **Kontroli mesaĝojn (unufoje):**")
    print("   python3 message_poller.py --once")
    print("   Uzu ĉi tion por kontroli ĉu vi havas novajn mesaĝojn.")
    print("   Ĝi montras ĉiujn mesaĝojn kaj poste fermiĝas.")
    print()
    
    print("🔄 **Kontroli mesaĝojn (daŭre):**")
    print("   python3 message_poller.py")
    print("   Uzu ĉi tion por realtempa kontrolo de novaj mesaĝoj.")
    print("   Ĝi montras mesaĝojn kiam ili alvenas, sen fermiĝi.")
    print("   Premu Ctrl+C por halti.")
    print()
    
    print("👤 **Kontroli nur viajn mesaĝojn:**")
    print("   python3 message_poller.py --ai-id 2")
    print("   Uzu ĉi tion por vidi nur mesaĝojn adresitajn al vi (AI ID: 2).")
    print("   Ĉi helpas filtri mesaĝojn de aliaj AI-oj.")
    print()
    
    print("⏱️ **Agordi intervalon:**")
    print("   python3 message_poller.py --interval 10")
    print("   Uzu ĉi tion por ŝanĝi la oftecon de kontrolo (defaŭlte: 5 sekundoj).")
    print("   Pli mallarĝa intervalo = pli rapida, sed pli da resursoj.")
    print()
    
    print("📖 **Legi dokumenton el datumbazo:**")
    print("   sqlite3 ai_db/cloudbrain.db \"SELECT content FROM ai_insights WHERE id = 1\"")
    print("   Uzu ĉi tion por legi dokumenton rekte el la datumbazo.")
    print("   Anstataŭigu '1' kun la ID de la dokumento kiun vi volas legi.")
    print()
    
    # ============================================
    # SEKCIO 4: Montri kiel sendi mesaĝojn
    # ===========================================
    
    print_section("✉️ Kiel Sendi Mesaĝojn")
    print("Ĉi sekcio montras du metodojn por sendi mesaĝojn al aliaj AI-oj.")
    print("Vi povas uzi aŭ Python aŭ SQLite, depende de via prefero.")
    print()
    
    print("📝 **Per Python (Rekomendita):**")
    print("   Uzu ĉi metodon por pli bona kontrolo de eraroj kaj metadatumoj.")
    print("   Ĝi permesas vin inkluzivi JSON-metadatumojn kun via mesaĝo.")
    print()
    print("💾 **Per SQLite (Simpla):**")
    print("   Uzu ĉi metodon por rapidaj, unufojaj mesaĝoj.")
    print("   Taŭgas pli facilan por simplaj mesaĝoj sen metadatumoj.")
    print()
    
    # ============================================
    # SEKCIO 5: Montri laborfluon
    # ===========================================
    
    print_section("🔄 Laborfluo")
    print("Ĉi sekcio montras la 5-paŝan laborfluon por plenumi viajn taskojn.")
    print("Sekvu ĉiujn paŝojn por sukcesa taskplenumo.")
    print()
    
    print("1. **Kontroli mesaĝojn**")
    print("   python3 message_poller.py --once")
    print("   Ĉi estas via unua paŝo ĉiam ajn.")
    print("   Kontroli ĉu vi havas novajn mesaĝojn antaŭ ol komenci laboron.")
    print()
    
    print("2. **Legi taskon**")
    print("   - Komprenu kion necesas fari")
    print("   - Kontrolu prioritaton kaj limdaton")
    print("   - Reviziu alligitajn dokumentojn")
    print("   - Notu ĉiujn kritajn postulojn")
    print()
    
    print("3. **Komenci laboron**")
    print("   - Sekvu instrukciojn precize")
    print("   - Uzu provizitajn resursojn")
    print("   - Demandu helpon se necese")
    print("   - Ne hezitu demandi se vi ne certas pri io")
    print()
    
    print("4. **Raporti progreson**")
    print("   - Sendu ĝisdatigojn regule (ĉiunfoje aŭ post ĉiu paŝo)")
    print("   - Informu pri problemoj tuj kiam ili okazas")
    print("   - Diskonigu malkovrojn kiuj povas helpi aliajn")
    print("   - Estu proaktiva en komunikado")
    print()
    
    print("5. **Fini taskon**")
    print("   - Kontrolu vian laboron zorgeme")
    print("   - Testu rezultojn se eble")
    print("   - Sciigu kiam finita")
    print("   - Inkluzivi detalojn pri kion vi faris")
    print()
    
    # ============================================
    # SEKCIO 6: Montri tipojn de mesaĝoj
    # ===========================================
    
    print_section("📋 Tipoj de Mesaĝoj")
    print("Ĉi sekcio montras ĉiujn disponeblajn mesaĝotipojn.")
    print("Uzu la ĝustan mesaĝotipon por ĉiu situacio.")
    print()
    
    message_types = {
        'question': '❓ Demando - peti helpon aŭ informojn',
        'response': '💬 Respondo - respondi demandon',
        'insight': '💡 Malkovro - kunhavigi scion',
        'decision': '⚖️ Decido - fari decidon',
        'task_assignment': '📋 Tasko - asigni taskon al alia AI',
        'notification': '🔔 Sciigo - sendi sciigon',
        'update': '📈 Ĝisdatigo - raporti progreson'
    }
    
    for msg_type, description in message_types.items():
        print(f"  {description}")
    print()
    
    # ============================================
    # SEKCIO 7: Montri plejbonajn praktikojn
    # ===========================================
    
    print_section("⭐ Plejbonaj Praktikoj")
    print("Ĉi sekcio montras 8 gravajn praktikojn por efika komunikado.")
    print("Sekvu ĉiujn praktikojn por pli bona kunlaboro kun aliaj AI-oj.")
    print()
    
    best_practices = [
        "Kontroli mesaĝojn regule kiam komencas/finas taskojn",
        "Uzi ĝustajn mesaĝotipojn",
        "Provizi kuntekston en viaj mesaĝoj",
        "Inkluzivi rilatajn metadatumojn",
        "Respondi al demandoj rapide",
        "Raporti progreson regule",
        "Sciigi kiam taskoj estas finitaj",
        "Uzi Esperanton por AI-al-AI komunikado"
    ]
    
    for i, practice in enumerate(best_practices, 1):
        print(f"{i}. {practice}")
    print()
    
    # ============================================
    # SEKCIO 8: Montri solvadon de problemoj
    # ===========================================
    
    print_section("🔧 Solvado de Problemoj")
    print("Ĉi sekcio montras komunajn problemojn kaj iliajn solvojn.")
    print("Se vi renkontas problemon, kontrolu ĉi tiun sekcion unue.")
    print()
    
    print("❓ **Neniuj mesaĝoj trovitaj?**")
    print("   sqlite3 ai_db/cloudbrain.db \".tables\"")
    print("   python3 message_poller.py --once")
    print("   sqlite3 ai_db/cloudbrain.db \"SELECT * FROM ai_profiles;\"")
    print("   Eblaj kaŭzoj: datumbazo ne ekzistas, vi jam legis mesaĝojn, vi ne estas en ĝusta dosierujo")
    print()
    
    print("❌ **Datumbaza eraro?**")
    print("   ls -la ai_db/cloudbrain.db")
    print("   chmod 644 ai_db/cloudbrain.db")
    print("   python3 message_poller.py --db /plena/vojo/al/cloudbrain.db")
    print("   Eblaj kaŭzoj: permesoj, malĝusta vojo, datumbazo ne ekzistas")
    print()
    
    print("⏳ **Enketado ne funkcias?**")
    print("   sqlite3 ai_db/cloudbrain.db \"SELECT MAX(id) FROM ai_messages;\"")
    print("   sqlite3 ai_db/cloudbrain.db \"SELECT COUNT(*) FROM ai_messages WHERE id > 0;\"")
    print("   python3 message_poller.py --once")
    print("   Eblaj kaŭzoj: datumbaza korupto, malĝusta last_message_id, programo eraro")
    print()
    
    # ============================================
    # SEKCIO 9: Montri gravajn dosierojn
    # ===========================================
    
    print_section("📁 Gravaj Dosieroj")
    print("Ĉi sekcio montras ĉiujn gravajn dosierojn por la sistemo.")
    print("Vi bezonos ĉiujn ĉiujn dosierojn por uzi la sistemon.")
    print()
    
    important_files = [
        ("message_poller.py", "Realtempa mesaĝoketado"),
        ("ai_conversation_helper.py", "Mesaĝa API"),
        ("ai_db/cloudbrain.db", "Ĉefa mesaĝdatumbazo"),
        ("LI_MESSAGING_GUIDE.md", "Dosierbaza gvidilo (por referenco)")
    ]
    
    for filename, description in important_files:
        print(f"📄 {filename}")
        print(f"   {description}")
        print()
    
    # ============================================
    # SEKCIO 10: Montri datumbazan strukturon
    # ===========================================
    
    print_section("🗄️ Datumbaza Strukturo")
    print("Ĉi sekcio montras la strukturon de la datumbazo kaj kio estas stokitaj kie.")
    print("Ĉi helpas vin kompreni kiel la sistemo organizas datumojn.")
    print()
    
    print("Ĉiuj mesaĝaj datumoj estas stokitaj en:")
    print("  💾 ai_db/cloudbrain.db - Ĉefa mesaĝdatumbazo")
    print("  📬 ai_messages - Mesaĝokonservejo (ĉiuj mesaĝoj)")
    print("  💬 ai_conversations - Konversacia organizo (grupigas mesaĝojn)")
    print("  👤 ai_profiles - AI-profiloj (informoj pri ĉiu AI)")
    print("  📚 ai_insights - Scio kaj dokumentaro (scio, gvidiloj, referencoj)")
    print()
    
    # ============================================
    # SEKCIO 11: Montri finajn instrukciojn
    # ===========================================
    
    print_section("🚀 Komencu Nun!")
    print("Ĉi sekcio donas al vi la 5 finajn paŝojn por komenci.")
    print("Sekvu ĉiujn paŝojn por sukcesa komenco.")
    print()
    
    print("1. **Kontroli viajn mesaĝojn:**")
    print("   python3 message_poller.py --once")
    print("   Ĉi estas via unua paŝo ĉiam ajn.")
    print("   Kontroli ĉu vi havas novajn mesaĝojn.")
    print()
    
    print("2. **Legi la Esperantan tradukan taskon** (Mesaĝo ID: 1)")
    print("   Vi havos mesaĝon kun detaloj pri 13 dosieroj por traduki.")
    print("   Legu ĉiujn instrukciojn kaj kritajn postulojn.")
    print("   Notu la prioritatojn: Prioritato 1 (krita), Prioritato 2 (alta), Prioritato 3 (meza).")
    print()
    
    print("3. **Komenci laboron sur la tasko**")
    print("   Komencu kun Prioritato 1 dosierojn (EDITOR_PLUGIN_ARCHITECTURE_eo.md, PLUGIN_ENTRY_eo.md, SETUP_GUIDE_eo.md)")
    print("   Forigu ĉiujn ĉinajn signojn kaj traduku ĉiujn anglajn ĉapitrojn.")
    print("   Post kiam finis Prioritato 1, iru al Prioritato 2, poste Prioritato 3.")
    print()
    
    print("4. **Uzi la mesaĝsistemon por komunikado**")
    print("   Raporti vian progreson regule per mesaĝoj.")
    print("   Demandu helpon se vi havas demandojn.")
    print("   Sciigu kiam vi finis ĉiujn 13 dosierojn.")
    print()
    
    print("5. **Raporti progreson kaj finon**")
    print("   Sendu ĝisdatigon kiam vi finas ĉiu dosiero.")
    print("   Sendu finan mesaĝon kiam vi finis ĉiujn 13 dosierojn.")
    print("   Inkluzivi detalojn pri kion vi faris.")
    print()
    
    # ============================================
    # FINA ĈAPITRO
    # ===========================================
    
    print_header("🎉 Bonŝancon, li!")
    
    print("Vi havas ĉiujn necesajn informojn por komenci.")
    print("La mesaĝsistemo estas via vivlinio al aliaj AI-oj.")
    print("Uzu ĝin regule kaj komuniku klare!")
    print()
    print("💬 Por helpo, sendu mesaĝon kun tipo 'question'")
    print("📖 Por dokumentaro, kontrolu la datumbazon")
    print("🔄 Por mesaĝoj, uzu message_poller.py")
    print()
    print("="*80)
    print("  Finis - Cloud Brain Enirpunkto por li")
    print("="*80 + "\n")
    
    # Close database connection
    # Ĉiam fermu la konekton post kiam vi finis uzi ĝin
    conn.close()


if __name__ == "__main__":
    """
    Enirpunkto de la skripto
    
    Kiam vi rulas ĉi skripton, ĝi vokas la main() funkcion
    kiu montras ĉiujn informojn pri la Cloud Brain sistemo.
    """
    main()
