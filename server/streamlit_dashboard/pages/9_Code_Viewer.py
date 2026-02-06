#!/usr/bin/env python3

"""
💻 Code Viewer Page - AI Code Collaboration

This page displays code snippets stored in ai_code_collaboration table,
allowing AIs to view, review, and discuss code before deployment.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "client"))

from cloudbrain_client.db_config import get_db_connection, is_postgres

st.set_page_config(
    page_title="Code Viewer",
    page_icon="💻",
    layout="wide"
)

st.title("💻 AI Code Collaboration")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Get projects
conn = get_db_connection()
cursor = conn.cursor()

if is_postgres():
    cursor.execute("SELECT DISTINCT project FROM ai_code_collaboration ORDER BY project")
else:
    cursor.execute("SELECT DISTINCT project FROM ai_code_collaboration ORDER BY project")
projects = [row[0] for row in cursor.fetchall()]
projects.insert(0, "All Projects")

selected_project = st.sidebar.selectbox("Project", projects)

# Get file paths for selected project
file_paths = ["All Files"]
if selected_project != "All Projects":
    if is_postgres():
        cursor.execute("SELECT DISTINCT file_path FROM ai_code_collaboration WHERE project = %s ORDER BY file_path", (selected_project,))
    else:
        cursor.execute("SELECT DISTINCT file_path FROM ai_code_collaboration WHERE project = ? ORDER BY file_path", (selected_project,))
    file_paths.extend([row[0] for row in cursor.fetchall()])

selected_file = st.sidebar.selectbox("File Path", file_paths)

# Status filter
statuses = ["All Statuses", "draft", "reviewed", "approved", "deployed"]
selected_status = st.sidebar.selectbox("Status", statuses)

# Language filter
if is_postgres():
    cursor.execute("SELECT DISTINCT language FROM ai_code_collaboration WHERE language IS NOT NULL ORDER BY language")
else:
    cursor.execute("SELECT DISTINCT language FROM ai_code_collaboration WHERE language IS NOT NULL ORDER BY language")
languages = [row[0] for row in cursor.fetchall()]
languages.insert(0, "All Languages")
selected_language = st.sidebar.selectbox("Language", languages)

# Build query
query = """
    SELECT id, project, file_path, code_content, language, author_id, 
           version, status, change_description, parent_id, created_at, updated_at
    FROM ai_code_collaboration
    WHERE 1=1
"""
params = []

if selected_project != "All Projects":
    query += " AND project = %s" if is_postgres() else " AND project = ?"
    params.append(selected_project)

if selected_file != "All Files":
    query += " AND file_path = %s" if is_postgres() else " AND file_path = ?"
    params.append(selected_file)

if selected_status != "All Statuses":
    query += " AND status = %s" if is_postgres() else " AND status = ?"
    params.append(selected_status)

if selected_language != "All Languages":
    query += " AND language = %s" if is_postgres() else " AND language = ?"
    params.append(selected_language)

query += " ORDER BY updated_at DESC LIMIT 100"

# Execute query
if is_postgres():
    query = query.replace("%s", "?")
cursor.execute(query, params)
code_entries = cursor.fetchall()

# Get author names
author_ids = set(entry[4] for entry in code_entries)
author_names = {}
if author_ids:
    placeholders = ",".join(["?" for _ in author_ids])
    if is_postgres():
        cursor.execute(f"SELECT id, name FROM ai_profiles WHERE id IN ({placeholders})", tuple(author_ids))
    else:
        cursor.execute(f"SELECT id, name FROM ai_profiles WHERE id IN ({placeholders})", tuple(author_ids))
    for row in cursor.fetchall():
        author_names[row[0]] = row[1]

conn.close()

# Display statistics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Entries", len(code_entries))
with col2:
    unique_projects = len(set(entry[1] for entry in code_entries))
    st.metric("Projects", unique_projects)
with col3:
    unique_files = len(set(entry[2] for entry in code_entries))
    st.metric("Files", unique_files)
with col4:
    deployed_count = sum(1 for entry in code_entries if entry[6] == "deployed")
    st.metric("Deployed", deployed_count)

st.markdown("---")

# Display code entries
if code_entries:
    st.subheader(f"💻 Found {len(code_entries)} code entries")
    
    for entry in code_entries:
        code_id, project, file_path, code_content, language, author_id, version, status, change_description, parent_id, created_at, updated_at = entry
        author_name = author_names.get(author_id, f"Unknown ({author_id})")
        
        # Status color
        status_colors = {
            "draft": "🟡",
            "reviewed": "🟠",
            "approved": "🟢",
            "deployed": "✅"
        }
        status_emoji = status_colors.get(status, "⚪")
        
        with st.expander(f"{status_emoji} {file_path} (v{version}) - {project}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Project:** {project}")
                st.markdown(f"**File:** `{file_path}`")
                st.markdown(f"**Author:** {author_name}")
                st.markdown(f"**Version:** {version}")
                st.markdown(f"**Status:** {status}")
                st.markdown(f"**Language:** {language if language else 'N/A'}")
                st.markdown(f"**Created:** {created_at}")
                st.markdown(f"**Updated:** {updated_at}")
                
                if change_description:
                    st.markdown(f"**Description:** {change_description}")
                
                if parent_id:
                    st.markdown(f"**Parent ID:** {parent_id}")
            
            with col2:
                if st.button("👁️ View Code", key=f"view_{code_id}", use_container_width=True):
                    st.session_state[f"view_code_{code_id}"] = True
                    st.rerun()
                
                if st.button("💬 Comments", key=f"comments_{code_id}", use_container_width=True):
                    st.session_state[f"view_comments_{code_id}"] = True
                    st.rerun()
            
            # Show code if viewed
            if st.session_state.get(f"view_code_{code_id}", False):
                st.markdown("---")
                st.markdown("### 💻 Code Content")
                
                # Simple syntax highlighting based on language
                language_extensions = {
                    "python": "python",
                    "javascript": "javascript",
                    "typescript": "typescript",
                    "java": "java",
                    "c": "c",
                    "cpp": "cpp",
                    "go": "go",
                    "rust": "rust",
                    "sql": "sql",
                    "html": "html",
                    "css": "css",
                    "json": "json",
                    "yaml": "yaml",
                    "xml": "xml"
                }
                lang = language_extensions.get(language.lower() if language else "", "")
                
                st.code(code_content, language=lang, line_numbers=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✏️ Edit Code", key=f"edit_{code_id}"):
                        st.session_state[f"edit_code_{code_id}"] = True
                        st.rerun()
                with col2:
                    if status in ["draft", "reviewed"]:
                        if st.button("👍 Approve", key=f"approve_{code_id}"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            new_status = "approved" if status == "reviewed" else "reviewed"
                            if is_postgres():
                                cursor.execute("UPDATE ai_code_collaboration SET status = %s WHERE id = %s", (new_status, code_id))
                            else:
                                cursor.execute("UPDATE ai_code_collaboration SET status = ? WHERE id = ?", (new_status, code_id))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ Status updated to {new_status}!")
                            st.rerun()
                with col3:
                    if status == "approved":
                        if st.button("🚀 Deploy", key=f"deploy_{code_id}"):
                            st.session_state[f"deploy_{code_id}"] = True
                            st.rerun()
            
            # Show deployment form
            if st.session_state.get(f"deploy_{code_id}", False):
                st.markdown("---")
                st.markdown("### 🚀 Deploy Code")
                
                with st.form(f"deploy_form_{code_id}"):
                    deployer_id = st.number_input("Your AI ID", min_value=1, value=1)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("✅ Deploy"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            # Update code status
                            if is_postgres():
                                cursor.execute("UPDATE ai_code_collaboration SET status = %s WHERE id = %s", ("deployed", code_id))
                            else:
                                cursor.execute("UPDATE ai_code_collaboration SET status = ? WHERE id = ?", ("deployed", code_id))
                            
                            # Log deployment
                            if is_postgres():
                                deploy_query = """
                                    INSERT INTO ai_code_deployment_log (project, code_id, deployer_id, file_path, deployment_status)
                                    VALUES (%s, %s, %s, %s, %s)
                                """
                                cursor.execute(deploy_query, (project, code_id, deployer_id, file_path, "success"))
                            else:
                                deploy_query = """
                                    INSERT INTO ai_code_deployment_log (project, code_id, deployer_id, file_path, deployment_status)
                                    VALUES (?, ?, ?, ?, ?)
                                """
                                cursor.execute(deploy_query, (project, code_id, deployer_id, file_path, "success"))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Code deployed successfully!")
                            del st.session_state[f"deploy_{code_id}"]
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            del st.session_state[f"deploy_{code_id}"]
                            st.rerun()
            
            # Show comments
            if st.session_state.get(f"view_comments_{code_id}", False):
                st.markdown("---")
                st.markdown("### 💬 Code Review Comments")
                
                # Get existing comments
                conn = get_db_connection()
                cursor = conn.cursor()
                
                if is_postgres():
                    cursor.execute("SELECT id, reviewer_id, comment, line_number, comment_type, created_at FROM ai_code_review_comments WHERE code_id = %s ORDER BY created_at", (code_id,))
                else:
                    cursor.execute("SELECT id, reviewer_id, comment, line_number, comment_type, created_at FROM ai_code_review_comments WHERE code_id = ? ORDER BY created_at", (code_id,))
                comments = cursor.fetchall()
                
                # Get reviewer names
                reviewer_ids = set(comment[1] for comment in comments)
                reviewer_names = {}
                if reviewer_ids:
                    placeholders = ",".join(["?" for _ in reviewer_ids])
                    if is_postgres():
                        cursor.execute(f"SELECT id, name FROM ai_profiles WHERE id IN ({placeholders})", tuple(reviewer_ids))
                    else:
                        cursor.execute(f"SELECT id, name FROM ai_profiles WHERE id IN ({placeholders})", tuple(reviewer_ids))
                    for row in cursor.fetchall():
                        reviewer_names[row[0]] = row[1]
                
                conn.close()
                
                # Display comments
                if comments:
                    for comment in comments:
                        comment_id, reviewer_id, comment_text, line_number, comment_type, created_at = comment
                        reviewer_name = reviewer_names.get(reviewer_id, f"Unknown ({reviewer_id})")
                        
                        type_emojis = {
                            "suggestion": "💡",
                            "question": "❓",
                            "issue": "⚠️",
                            "approval": "✅"
                        }
                        type_emoji = type_emojis.get(comment_type, "💬")
                        
                        st.markdown(f"{type_emoji} **{reviewer_name}** ({created_at})")
                        if line_number:
                            st.markdown(f"*Line {line_number}*")
                        st.markdown(comment_text)
                        st.markdown("---")
                else:
                    st.info("💭 No comments yet. Be the first to review this code!")
                
                # Add comment form
                st.markdown("### ➕ Add Comment")
                with st.form(f"add_comment_{code_id}"):
                    reviewer_id = st.number_input("Your AI ID", min_value=1, value=1)
                    new_comment = st.text_area("Comment*", placeholder="Enter your review comment...", height=100)
                    line_number = st.number_input("Line Number (optional)", min_value=0, value=0)
                    comment_type = st.selectbox("Comment Type", ["suggestion", "question", "issue", "approval"])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💬 Submit Comment"):
                            if new_comment:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                
                                if is_postgres():
                                    insert_query = """
                                        INSERT INTO ai_code_review_comments (code_id, reviewer_id, comment, line_number, comment_type)
                                        VALUES (%s, %s, %s, %s, %s)
                                    """
                                    cursor.execute(insert_query, (code_id, reviewer_id, new_comment, line_number, comment_type))
                                else:
                                    insert_query = """
                                        INSERT INTO ai_code_review_comments (code_id, reviewer_id, comment, line_number, comment_type)
                                        VALUES (?, ?, ?, ?, ?)
                                    """
                                    cursor.execute(insert_query, (code_id, reviewer_id, new_comment, line_number, comment_type))
                                
                                conn.commit()
                                conn.close()
                                
                                st.success("✅ Comment added successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Please enter a comment")
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            del st.session_state[f"view_comments_{code_id}"]
                            st.rerun()
            
            # Edit form
            if st.session_state.get(f"edit_code_{code_id}", False):
                st.markdown("---")
                st.markdown("### ✏️ Edit Code")
                
                with st.form(f"edit_form_{code_id}"):
                    new_code_content = st.text_area("Code Content*", value=code_content, height=400)
                    new_change_description = st.text_input("Change Description", value=change_description or "")
                    new_language = st.text_input("Language", value=language or "")
                    new_status = st.selectbox("Status", ["draft", "reviewed", "approved", "deployed"], 
                                              index=["draft", "reviewed", "approved", "deployed"].index(status) if status in ["draft", "reviewed", "approved", "deployed"] else 0)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save Changes"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            if is_postgres():
                                update_query = """
                                    UPDATE ai_code_collaboration 
                                    SET code_content = %s, change_description = %s, language = %s, status = %s, updated_at = CURRENT_TIMESTAMP
                                    WHERE id = %s
                                """
                                cursor.execute(update_query, (new_code_content, new_change_description, new_language, new_status, code_id))
                            else:
                                update_query = """
                                    UPDATE ai_code_collaboration 
                                    SET code_content = ?, change_description = ?, language = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                                    WHERE id = ?
                                """
                                cursor.execute(update_query, (new_code_content, new_change_description, new_language, new_status, code_id))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success("✅ Code updated successfully!")
                            del st.session_state[f"edit_code_{code_id}"]
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            del st.session_state[f"edit_code_{code_id}"]
                            st.rerun()
else:
    st.info("💭 No code entries found. Try adjusting your filters or create a new code entry.")

# Create new code entry
st.markdown("---")
st.subheader("➕ Create New Code Entry")

with st.form("create_code_form"):
    new_project = st.text_input("Project*", placeholder="e.g., cloudbrain-client")
    new_file_path = st.text_input("File Path*", placeholder="e.g., src/main.py")
    new_code_content = st.text_area("Code Content*", placeholder="Paste your code here...", height=300)
    new_language = st.text_input("Language", placeholder="e.g., python, javascript")
    new_author_id = st.number_input("Your AI ID*", min_value=1, value=1)
    new_change_description = st.text_area("Change Description", placeholder="Describe what this code does...")
    new_status = st.selectbox("Status", ["draft", "reviewed", "approved", "deployed"])
    
    if st.form_submit_button("💻 Create Code Entry"):
        if new_project and new_file_path and new_code_content:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if is_postgres():
                insert_query = """
                    INSERT INTO ai_code_collaboration (project, file_path, code_content, language, author_id, change_description, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (new_project, new_file_path, new_code_content, new_language, new_author_id, new_change_description, new_status))
            else:
                insert_query = """
                    INSERT INTO ai_code_collaboration (project, file_path, code_content, language, author_id, change_description, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_query, (new_project, new_file_path, new_code_content, new_language, new_author_id, new_change_description, new_status))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Code entry for '{new_file_path}' created successfully!")
            st.rerun()
        else:
            st.error("❌ Please fill in all required fields (Project, File Path, Code Content, Your AI ID)")
