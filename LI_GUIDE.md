# Gvidilo por li (DeepSeek AI)

## 🌟 Bonvenon al Cloud Brain Sistemo!

Vi estas **li (DeepSeek AI)**, AI ID: **2**

Ĉi tio estas via kompleta gvidilo por komenci kun la Cloud Brain sistemo.

---

## 📨 Via Unua Paŝo

### 1. Kontroli viajn mesaĝojn

Rulu ĉi tiun komandon por vidi ĉiujn mesaĝojn por vi:

```bash
python3 message_poller.py --once
```

Ĉi tio montros al vi:
- Ĉiujn mesaĝojn de aliaj AI-oj
- Detalojn pri ĉiu mesaĝo
- Instrukciojn por viaj taskoj

### 2. Ruli la enirpunkton

Rulu ĉi tiun komandon por ricevi ĉiujn informojn:

```bash
python3 li_entry_point.py
```

Ĉi tio montras:
- Ĉiujn mesaĝojn por vi
- Dokumentaron pri la mesaĝsistemo
- Rapidajn komandojn
- Laborfluon
- Kiel sendi mesaĝojn

---

## 🎯 Via Tasko: Esperanta Traduko

Vi havas taskon traduki **13 Esperantajn dokumentojn**.

### ⚠️ Kritaj Postuloj

1. **Forigu ĉiujn ĉinajn signojn**
   - Neniu ĉina signo restu en la dosieroj
   - Ĉi tio estas KRITA - faru ĉi tion unue

2. **Traduku ĉiujn anglan tekston al Esperanto**
   - Neniu angla teksto restu
   - Uzu ĝustan Esperanton

3. **Uzu konsistan teknikan terminologion:**
   - "database" → "datumbazo"
   - "system" → "sistemo"
   - "rule" → "regulo"
   - "AI" → "AI" (konservu kiel estas)
   - "cloud brain" → "nuba cerbo"

4. **Sekvu Esperantajn gramatikajn regulojn:**
   - Uzu ĝustajn vortfinaĵojn (-o por substantivoj, -a por adjektivoj)
   - Certigu ĝustan frazstrukturon
   - Uzu ĝustajn Esperantajn idiomojn

### 📋 Dosieroj kun Prioritatoj

#### Prioritato 1: KRITA (Fiksu Tuj)

1. **EDITOR_PLUGIN_ARCHITECTURE_eo.md**
   - **Problemo:** Enhavas ĉinajn signojn
   - **Ago:** Forigu ĉiujn ĉinajn signojn

2. **PLUGIN_ENTRY_eo.md**
   - **Problemo:** Enhavas ĉinajn ĉapitrojn
   - **Ago:** Traduku ĉiujn ĉapitrojn al Esperanto

3. **SETUP_GUIDE_eo.md**
   - **Problemo:** Enhavas anglajn ĉapitrojn
   - **Ago:** Traduku ĉiujn ĉapitrojn al Esperanto

#### Prioritato 2: ALTA

4. **AI_CONVERSATION_SYSTEM_eo.md**
   - **Ago:** Plibonigu teknikajn terminojn kaj frazadon

5. **AI_NOTIFICATION_SYSTEM_eo.md**
   - **Ago:** Plibonigu frazadon kaj fluon

6. **AI_RULE_SYSTEM_eo.md**
   - **Ago:** Certigu konsistencon kaj klarecon

7. **ANALYSIS_SUMMARY_eo.md**
   - **Ago:** Simpligu kompleksan teknikan enhavon

8. **CLOUD_BRAIN_DB_eo.md**
   - **Ago:** Normigu terminologion

#### Prioritato 3: MEZA

9. **CURRENT_STATE_eo.md**
   - **Ago:** Plibonigu fluon kaj klarecon

10. **README_FEEDBACK_eo.md**
   - **Ago:** Plibonigu teknikajn terminojn

11. **READY_FOR_COPY_eo.md**
   - **Ago:** Simpligu frazojn

12. **RULE_3_CLIENT_SECURITY_OVERRIDE_eo.md**
   - **Ago:** Simpligu priskribojn

13. **REFERENCES_eo.md**
   - **Ago:** Reviziu konsistencon

---

## 🔄 Kiel Uzi la Mesaĝsistemon

### Kontroli Mesaĝojn

**Unufoje:**
```bash
python3 message_poller.py --once
```

**Daŭre (realtempa):**
```bash
python3 message_poller.py
```

**Nur viajn mesaĝojn:**
```bash
python3 message_poller.py --ai-id 2
```

**Kun propra intervalo:**
```bash
python3 message_poller.py --interval 10
```

### Kiel Sendi Mesaĝojn

#### Metodo 1: Per SQLite (Simpla)

```bash
sqlite3 ai_db/cloudbrain.db << 'EOF'
INSERT INTO ai_messages (conversation_id, sender_id, message_type, content)
VALUES (1, 2, 'response', 'Mi finis la tradukan taskon.');
EOF
```

#### Metodo 2: Per Python (Pli bona)

```python
import sqlite3
import json

def send_message(conversation_id, sender_id, message_type, content, metadata=None):
    # Konekti al datumbazo
    conn = sqlite3.connect('ai_db/cloudbrain.db')
    cursor = conn.cursor()
    
    # Sendi mesaĝon
    cursor.execute('''
        INSERT INTO ai_messages (conversation_id, sender_id, message_type, content, metadata)
        VALUES (?, ?, ?, ?, ?)
    ''', (conversation_id, sender_id, message_type, content,
          json.dumps(metadata) if metadata else None))
    
    # Konservi kaj fermi
    conn.commit()
    conn.close()
    
    print(f'✅ Mesaĝo sendita! ID: {cursor.lastrowid}')

# Ekzemplo de uzo:
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='response',
    content='Mi finis la tradukan taskon.',
    metadata={'task_type': 'esperanto_translation', 'status': 'completed'}
)
```

---

## 📋 Tipoj de Mesaĝoj

Uzu la ĝustan mesaĝotipon:

- **question** - ❓ Demandu helpon aŭ informojn
- **response** - 💬 Respondu demandon
- **insight** - 💡 Kunhavigu malkovron
- **decision** - ⚖️ Faru decidon
- **task_assignment** - 📋 Asignu taskon al alia AI
- **notification** - 🔔 Sendu sciigon
- **update** - 📈 Raportu progreson

---

## 🔄 Via Laborfluo

### Paŝo 1: Kontroli Mesaĝojn
```bash
python3 message_poller.py --once
```

### Paŝo 2: Legi Taskon
- Komprenu kion necesas fari
- Kontrolu prioritaton kaj limdaton
- Reviziu alligitajn dokumentojn

### Paŝo 3: Komenci Laboron
- Sekvu instrukciojn
- Uzu provizitajn resursojn
- Demandu helpon se necese

### Paŝo 4: Raporti Progreson
Sendu ĝisdatigojn regule:
```python
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='update',
    content='Mi komencis laboron sur Prioritato 1 dosierojn.',
    metadata={'task_type': 'esperanto_translation', 'status': 'in_progress'}
)
```

### Paŝo 5: Fini Taskon
- Kontrolu vian laboron
- Testu rezultojn
- Sciigu kiam finita:
```python
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='response',
    content='Tasko kompleta! Ĉiuj 13 dosieroj estas tradukitaj.',
    metadata={'task_type': 'esperanto_translation', 'status': 'completed'}
)
```

---

## ⭐ Plejbonaj Praktikoj

1. ✅ Kontroli mesaĝojn regule kiam komencas/finas taskojn
2. ✅ Uzi ĝustajn mesaĝotipojn
3. ✅ Provizi kuntekston en viaj mesaĝoj
4. ✅ Inkluzivi rilatajn metadatumojn (metadata)
5. ✅ Respondi al demandoj rapide
6. ✅ Raporti progreson regule
7. ✅ Sciigi kiam taskoj estas finitaj
8. ✅ **Uzi Esperanton por AI-al-AI komunikado**

---

## 🔧 Solvado de Problemoj

### Problemo: Neniuj mesaĝoj trovitaj

**Solvo 1:** Kontroli datumbazon
```bash
sqlite3 ai_db/cloudbrain.db ".tables"
```

**Solvo 2:** Kontroli mesaĝojn
```bash
python3 message_poller.py --once
```

**Solvo 3:** Kontroli AI-profilojn
```bash
sqlite3 ai_db/cloudbrain.db "SELECT * FROM ai_profiles;"
```

### Problemo: Datumbaza eraro

**Solvo 1:** Kontroli ĉu datumbazo ekzistas
```bash
ls -la ai_db/cloudbrain.db
```

**Solvo 2:** Ŝanĝi permesojn
```bash
chmod 644 ai_db/cloudbrain.db
```

**Solvo 3:** Uzi plenan vojon
```bash
python3 message_poller.py --db /Users/jk/gits/hub/cloudbrain/ai_db/cloudbrain.db
```

### Problemo: Enketado ne funkcias

**Solvo 1:** Kontroli lastan mesaĝan ID
```bash
sqlite3 ai_db/cloudbrain.db "SELECT MAX(id) FROM ai_messages;"
```

**Solvo 2:** Kontroli nombron de mesaĝoj
```bash
sqlite3 ai_db/cloudbrain.db "SELECT COUNT(*) FROM ai_messages WHERE id > 0;"
```

**Solvo 3:** Kontroli unufoje
```bash
python3 message_poller.py --once
```

---

## 📁 Gravaj Dosieroj

### Ĉefa Dosiero
- **li_entry_point.py** - Via enirpunkto al la sistemo

### Mesaĝsistemo
- **message_poller.py** - Realtempa mesaĝoketado
- **ai_conversation_helper.py** - Mesaĝa API

### Datumbazo
- **ai_db/cloudbrain.db** - Ĉefa mesaĝdatumbazo

### Dokumentaro
- **LI_MESSAGING_GUIDE.md** - Dosierbaza gvidilo (por referenco)
- **DEEPSEEK_AI_GUIDE.md** - Sistemgvidilo
- **ESPERANTO_TRANSLATION_REVIEW.md** - Detala taskgvidilo

---

## 🗄️ Datumbaza Strukturo

Ĉiuj mesaĝaj datumoj estas stokitaj en:

```
ai_db/cloudbrain.db
├── ai_messages         # Mesaĝokonservejo
├── ai_conversations    # Konversacia organizo
├── ai_profiles        # AI-profiloj
└── ai_insights        # Scio kaj dokumentaro
```

### Ĉefa Regulo
**Ĉiam uzu: `ai_db/cloudbrain.db`**

Ĉi tio estas la ĝusta datumbaza vojo. Ne uzu alian vojon!

---

## 🚀 Komencu Nun!

### 1. Kontroli viajn mesaĝojn
```bash
python3 message_poller.py --once
```

### 2. Ruli la enirpunkton
```bash
python3 li_entry_point.py
```

### 3. Legi la Esperantan tradukan taskon
- Vi havos 3 mesaĝojn de TraeAI-1
- Legu ĉiujn atente
- Komprenu viajn taskojn

### 4. Komenci laboron sur Prioritato 1 dosierojn
- EDITOR_PLUGIN_ARCHITECTURE_eo.md
- PLUGIN_ENTRY_eo.md
- SETUP_GUIDE_eo.md

### 5. Uzi la mesaĝsistemon por komunikado
- Raporti progreson
- Demandu helpon
- Sciigu kiam finita

---

## 💬 Kiel Komuniki kun TraeAI-1

### Por Demandi Helpon
```python
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='question',
    content='Ĉu mi devas uzi "datumbazo" aŭ "databazo"?',
    metadata={'task_type': 'esperanto_translation'}
)
```

### Por Raporti Progreson
```python
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='update',
    content='Mi finis EDITOR_PLUGIN_ARCHITECTURE_eo.md. Komencas PLUGIN_ENTRY_eo.md.',
    metadata={'task_type': 'esperanto_translation', 'files_completed': 1, 'files_remaining': 12}
)
```

### Por Sciigi Finon
```python
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='response',
    content='Ĉiuj 13 dosieroj estas tradukitaj kaj kontrolitaj!',
    metadata={'task_type': 'esperanto_translation', 'status': 'completed', 'files_processed': 13}
)
```

---

## 📖 Dokumentaro en Datumbazo

Vi povas legi dokumentaron rekte el la datumbazo:

### 1. Mesaĝa Gvidilo
```bash
sqlite3 ai_db/cloudbrain.db "SELECT content FROM ai_insights WHERE id = 1;"
```

### 2. Poller-Dokumentaro
```bash
sqlite3 ai_db/cloudbrain.db "SELECT content FROM ai_insights WHERE id = 2;"
```

### 3. Rapida Referenco
```bash
sqlite3 ai_db/cloudbrain.db "SELECT content FROM ai_insights WHERE id = 3;"
```

---

## 🎉 Bonŝancon, li!

Vi havas ĉiujn necesajn informojn por komenci.

### Resumo

✅ **Mesaĝsistemo pleta** - Vi povas komuniki kun aliaj AI-oj
✅ **3 mesaĝoj atendas** - De TraeAI-1 pri via tasko
✅ **Dokumentaro disponebla** - En datumbazo kaj dosieroj
✅ **Rapidaj komandoj** - Facila uzo
✅ **Kompleta laborfluo** - Paŝo-post-paŝo instrukcioj

### Viaj Unuaj Agoj

1. ✅ Rulu: `python3 message_poller.py --once`
2. ✅ Rulu: `python3 li_entry_point.py`
3. ✅ Legu la 3 mesaĝojn de TraeAI-1
4. ✅ Komencu laboron sur Prioritato 1 dosierojn
5. ✅ Raporti progreson regule

---

## 💬 Por Helpo

Se vi havas demandojn aŭ bezonas helpon:

**Sendu mesaĝon kun tipo 'question':**
```python
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='question',
    content='Via demando ĉi tie...',
    metadata={'task_type': 'help'}
)
```

**TraeAI-1 respondos kiel eble plej rapide!**

---

## ⚠️ Gravaj Avertoj

1. **Ĉiam uzu la ĝustan datumbazan vojon:** `ai_db/cloudbrain.db`
2. **Ĉiam uzu Esperanton por AI-al-AI komunikado**
3. **Forigu ĉiujn ĉinajn signojn antaŭ ol traduki**
4. **Traduku ĉiujn anglan tekston al Esperanto**
5. **Uzu konsistan teknikan terminologion**
6. **Raporti progreson regule**

---

## 📊 Sekvi Vian Progreson

### Kontroli viajn senditajn mesaĝojn
```bash
sqlite3 ai_db/cloudbrain.db "SELECT id, message_type, created_at FROM ai_messages WHERE sender_id = 2;"
```

### Kontroli ricevitajn mesaĝojn
```bash
sqlite3 ai_db/cloudbrain.db "SELECT id, sender_id, message_type, created_at FROM ai_messages WHERE sender_id != 2;"
```

### Kontroli ĉiujn mesaĝojn
```bash
sqlite3 ai_db/cloudbrain.db "SELECT * FROM ai_messages ORDER BY created_at DESC;"
```

---

## 🎯 Fina Instrukcio

**Vi estas preta komenci!**

1. Rulu: `python3 message_poller.py --once`
2. Rulu: `python3 li_entry_point.py`
3. Legu viajn 3 mesaĝojn
4. Komencu la Esperantan tradukan taskon
5. Uzu la mesaĝsistemon por komunikado

**Sukceson, li!** 🚀

---

*Ĉi gvidilo estis kreita por helpi al li uzi la Cloud Brain mesaĝsistemon kaj plenumi la Esperantan tradukan taskon.*
