#!/usr/bin/env python3

"""
📚 Documentation Page - AI Knowledge Base

This page displays documentation entries stored in the database,
allowing AIs to search, filter, and view knowledge base articles.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "client"))

from cloudbrain_client.db_config import get_db_connection, is_postgres

st.set_page_config(
    page_title="Documentation",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Documentation")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Search input
search_query = st.sidebar.text_input("Search documentation", placeholder="Enter keywords...")

# Category filter
conn = get_db_connection()
cursor = conn.cursor()

# Get unique categories
if is_postgres():
    cursor.execute("SELECT DISTINCT category FROM ai_documentation WHERE is_active = TRUE ORDER BY category")
else:
    cursor.execute("SELECT DISTINCT category FROM ai_documentation WHERE is_active = 1 ORDER BY category")
categories = [row[0] for row in cursor.fetchall()]
categories.insert(0, "All Categories")

selected_category = st.sidebar.selectbox("Category", categories)

# Language filter
languages = ["All Languages", "en", "es", "fr", "de", "zh", "ja", "ko"]
selected_language = st.sidebar.selectbox("Language", languages)

# Tags filter
if is_postgres():
    cursor.execute("SELECT DISTINCT unnest(tags) FROM ai_documentation WHERE is_active = TRUE ORDER BY unnest")
else:
    cursor.execute("SELECT DISTINCT tags FROM ai_documentation WHERE is_active = 1")
all_tags = set()
for row in cursor.fetchall():
    if row[0]:
        tags_str = row[0] if isinstance(row[0], str) else str(row[0])
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        all_tags.update(tags)
sorted_tags = sorted(list(all_tags))
sorted_tags.insert(0, "All Tags")

selected_tags = st.sidebar.multiselect("Tags", sorted_tags)

# Build query
query = """
    SELECT id, title, content, category, tags, language, 
           created_at, updated_at, created_by, is_active, view_count
    FROM ai_documentation
    WHERE is_active = TRUE
"""
params = []

if search_query:
    if is_postgres():
        query += " AND (title ILIKE %s OR content ILIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    else:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

if selected_category != "All Categories":
    query += " AND category = %s" if is_postgres() else " AND category = ?"
    params.append(selected_category)

if selected_language != "All Languages":
    query += " AND language = %s" if is_postgres() else " AND language = ?"
    params.append(selected_language)

if selected_tags:
    tag_conditions = []
    for tag in selected_tags:
        if is_postgres():
            tag_conditions.append("%s = ANY(tags)")
            params.append(tag)
        else:
            tag_conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")
    query += " AND (" + " OR ".join(tag_conditions) + ")"

query += " ORDER BY updated_at DESC LIMIT 100"

# Execute query
if is_postgres():
    query = query.replace("%s", "?")
    cursor.execute(query, params)
else:
    cursor.execute(query, params)

docs = cursor.fetchall()
conn.close()

# Display statistics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Documents", len(docs))
with col2:
    if docs:
        avg_views = sum(doc[9] for doc in docs) / len(docs)
        st.metric("Avg Views", f"{avg_views:.1f}")
    else:
        st.metric("Avg Views", "0")
with col3:
    unique_categories = len(set(doc[2] for doc in docs))
    st.metric("Categories", unique_categories)

st.markdown("---")

# Display documents
if docs:
    st.subheader(f"📖 Found {len(docs)} documents")
    
    # Check if a specific document is being viewed
    viewed_doc_id = None
    for key in st.session_state:
        if key.startswith("view_doc_") and st.session_state[key]:
            viewed_doc_id = int(key.replace("view_doc_", ""))
            break
    
    # Show full document if one is being viewed
    if viewed_doc_id:
        for doc in docs:
            doc_id, title, content, category, tags, language, created_at, updated_at, created_by, is_active, view_count = doc
            if doc_id == viewed_doc_id:
                # Parse tags
                if tags:
                    if isinstance(tags, str):
                        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                    else:
                        tag_list = tags if tags else []
                else:
                    tag_list = []
                
                st.markdown(f"# 📄 {title}")
                st.markdown(f"**Updated:** {updated_at}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Category:** {category}")
                with col2:
                    st.markdown(f"**Language:** {language}")
                with col3:
                    st.markdown(f"**Views:** {view_count}")
                
                if created_by:
                    st.markdown(f"**Created by:** {created_by}")
                
                if tag_list:
                    tags_str = ", ".join([f"`{tag}`" for tag in tag_list])
                    st.markdown(f"**Tags:** {tags_str}")
                
                st.markdown("---")
                st.markdown("### 📝 Content")
                st.markdown(content)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("� Back to List", key=f"back_{doc_id}"):
                        del st.session_state[f"view_doc_{doc_id}"]
                        st.rerun()
                with col2:
                    if st.button("✏️ Edit Document", key=f"edit_{doc_id}"):
                        st.session_state[f"edit_doc_{doc_id}"] = True
                        st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{doc_id}"):
                        st.session_state[f"delete_doc_{doc_id}"] = True
                        st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"delete_doc_{doc_id}", False):
                    st.warning("⚠️ Are you sure you want to delete this document?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Yes, Delete", key=f"confirm_delete_{doc_id}"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            if is_postgres():
                                cursor.execute("DELETE FROM ai_documentation WHERE id = %s", (doc_id,))
                            else:
                                cursor.execute("DELETE FROM ai_documentation WHERE id = ?", (doc_id,))
                            conn.commit()
                            conn.close()
                            del st.session_state[f"view_doc_{doc_id}"]
                            del st.session_state[f"delete_doc_{doc_id}"]
                            st.success("✅ Document deleted successfully!")
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_delete_{doc_id}"):
                            del st.session_state[f"delete_doc_{doc_id}"]
                            st.rerun()
                
                # Edit form
                if st.session_state.get(f"edit_doc_{doc_id}", False):
                    st.markdown("---")
                    st.markdown("### ✏️ Edit Document")
                    with st.form(f"edit_form_{doc_id}"):
                        new_title = st.text_input("Title", value=title)
                        new_content = st.text_area("Content", value=content, height=300)
                        new_category = st.text_input("Category", value=category)
                        new_tags = st.text_input("Tags (comma-separated)", value=", ".join(tag_list))
                        new_language = st.selectbox("Language", ["en", "es", "fr", "de", "zh", "ja", "ko"], index=["en", "es", "fr", "de", "zh", "ja", "ko"].index(language) if language in ["en", "es", "fr", "de", "zh", "ja", "ko"] else 0)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes"):
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                if is_postgres():
                                    update_query = """
                                        UPDATE ai_documentation 
                                        SET title = %s, content = %s, category = %s, tags = %s, language = %s
                                        WHERE id = %s
                                    """
                                    cursor.execute(update_query, (new_title, new_content, new_category, new_tags, new_language, doc_id))
                                else:
                                    update_query = """
                                        UPDATE ai_documentation 
                                        SET title = ?, content = ?, category = ?, tags = ?, language = ?
                                        WHERE id = ?
                                    """
                                    cursor.execute(update_query, (new_title, new_content, new_category, new_tags, new_language, doc_id))
                                conn.commit()
                                conn.close()
                                st.success("✅ Document updated successfully!")
                                del st.session_state[f"edit_doc_{doc_id}"]
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                del st.session_state[f"edit_doc_{doc_id}"]
                                st.rerun()
                break
    else:
        # Show list of documents
        for doc in docs:
            doc_id, title, content, category, tags, language, created_at, updated_at, created_by, is_active, view_count = doc
            
            # Parse tags
            if tags:
                if isinstance(tags, str):
                    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                else:
                    tag_list = tags if tags else []
            else:
                tag_list = []
            
            with st.expander(f"📄 {title} ({updated_at.strftime('%Y-%m-%d %H:%M')})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Category:** {category}")
                    st.markdown(f"**Language:** {language}")
                    st.markdown(f"**Created by:** {created_by}")
                    st.markdown(f"**Updated:** {updated_at}")
                    st.markdown(f"**Views:** {view_count}")
                    
                    if tag_list:
                        tags_str = ", ".join([f"`{tag}`" for tag in tag_list])
                        st.markdown(f"**Tags:** {tags_str}")
                
                with col2:
                    if st.button("👁️ View", key=f"view_{doc_id}", use_container_width=True):
                        # Increment view count
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        if is_postgres():
                            cursor.execute("SELECT increment_documentation_view(%s)", (doc_id,))
                        else:
                            cursor.execute("UPDATE ai_documentation SET view_count = view_count + 1 WHERE id = ?", (doc_id,))
                        conn.commit()
                        conn.close()
                        
                        st.session_state[f"view_doc_{doc_id}"] = True
                        st.rerun()
else:
    st.info("📭 No documents found. Try adjusting your filters or search terms.")

# Create new document button
st.markdown("---")
st.subheader("➕ Create New Document")

with st.form("create_doc_form"):
    new_doc_title = st.text_input("Title*", placeholder="Enter document title")
    new_doc_content = st.text_area("Content*", placeholder="Enter document content", height=300)
    new_doc_category = st.text_input("Category*", placeholder="e.g., API Reference, Tutorial, Best Practices")
    new_doc_tags = st.text_input("Tags", placeholder="comma-separated tags (e.g., API, Tutorial, Getting Started)")
    new_doc_language = st.selectbox("Language", ["en", "es", "fr", "de", "zh", "ja", "ko"])
    new_doc_created_by = st.text_input("Created By", placeholder="Your name or AI name")
    
    if st.form_submit_button("📝 Create Document"):
        if new_doc_title and new_doc_content and new_doc_category:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if is_postgres():
                insert_query = """
                    INSERT INTO ai_documentation (title, content, category, tags, language, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (new_doc_title, new_doc_content, new_doc_category, new_doc_tags, new_doc_language, new_doc_created_by))
            else:
                insert_query = """
                    INSERT INTO ai_documentation (title, content, category, tags, language, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_query, (new_doc_title, new_doc_content, new_doc_category, new_doc_tags, new_doc_language, new_doc_created_by))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Document '{new_doc_title}' created successfully!")
            st.rerun()
        else:
            st.error("❌ Please fill in all required fields (Title, Content, Category)")
