#!/bin/bash

# AI Memory Database Helper Script
# Location: ./ai_db/ai_memory.db (relative to project root)

# Get script directory and resolve to database location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$SCRIPT_DIR/ai_memory.db"

# Function to query database
query() {
    sqlite3 "$DB_PATH" "$1"
}

# Function to add a session
add_session() {
    local session_name="$1"
    local summary="$2"
    local achievements="$3"
    local total_commits="$4"

    query "INSERT INTO sessions (session_name, summary, achievements, total_commits) VALUES ('$session_name', '$summary', '$achievements', $total_commits);"
}

# Function to add a code snippet
add_snippet() {
    local code="$1"
    local language="$2"
    local framework="$3"
    local pattern="$4"
    local purpose="$5"
    local file_path="$6"
    local line_start="$7"
    local line_end="$8"
    local session_id="$9"

    query "INSERT INTO code_snippets (code, language, framework, pattern, purpose, file_path, line_start, line_end, session_id) VALUES ('$code', '$language', '$framework', '$pattern', '$purpose', '$file_path', $line_start, $line_end, $session_id);"
}

# Function to add a bug solution
add_bug_solution() {
    local error_message="$1"
    local error_type="$2"
    local solution_code="$3"
    local explanation="$4"
    local root_cause="$5"
    local session_id="$6"

    query "INSERT INTO bug_solutions (error_message, error_type, solution_code, explanation, root_cause, session_id) VALUES ('$error_message', '$error_type', '$solution_code', '$explanation', '$root_cause', $session_id);"
}

# Function to add a decision
add_decision() {
    local decision="$1"
    local rationale="$2"
    local code_impact="$3"
    local session_id="$4"

    query "INSERT INTO decisions (decision, rationale, code_impact, session_id) VALUES ('$decision', '$rationale', '$code_impact', $session_id);"
}

# Function to search code snippets
search_snippets() {
    local search_term="$1"
    query "SELECT cs.id, cs.code, cs.purpose, cs.pattern, cs.file_path, cs.line_start, cs.line_end FROM code_snippets cs WHERE cs.code LIKE '%$search_term%' OR cs.purpose LIKE '%$search_term%' OR cs.pattern LIKE '%$search_term%' ORDER BY cs.created_at DESC;"
}

# Function to get session summary
get_session() {
    local session_name="$1"
    query "SELECT s.id, s.session_name, s.summary, s.achievements, s.total_commits, s.start_time FROM sessions s WHERE s.session_name LIKE '%$session_name%';"
}

# Function to get bug solutions
get_bug_solutions() {
    local error_type="$1"
    query "SELECT bs.id, bs.error_message, bs.solution_code, bs.explanation, s.session_name FROM bug_solutions bs JOIN sessions s ON bs.session_id = s.id WHERE bs.error_type LIKE '%$error_type%' ORDER BY bs.created_at DESC;"
}

# Function to get all sessions
list_sessions() {
    query "SELECT s.id, s.session_name, s.summary, s.total_commits, s.start_time FROM sessions s ORDER BY s.start_time DESC;"
}

# Function to get all code snippets
list_snippets() {
    query "SELECT cs.id, cs.code, cs.language, cs.purpose, cs.pattern, cs.file_path FROM code_snippets cs ORDER BY cs.created_at DESC;"
}

# Function to get all bug solutions
list_bugs() {
    query "SELECT bs.id, bs.error_message, bs.error_type, bs.explanation, s.session_name FROM bug_solutions bs JOIN sessions s ON bs.session_id = s.id ORDER BY bs.created_at DESC;"
}

# Function to get all decisions
list_decisions() {
    query "SELECT d.id, d.decision, d.rationale, s.session_name FROM decisions d JOIN sessions s ON d.session_id = s.id ORDER BY d.created_at DESC;"
}

# Function to show database statistics
show_stats() {
    echo "=== AI Memory Database Statistics ==="
    echo ""
    echo "Sessions:"
    query "SELECT COUNT(*) as count FROM sessions;"
    echo ""
    echo "Code Snippets:"
    query "SELECT COUNT(*) as count FROM code_snippets;"
    echo ""
    echo "Bug Solutions:"
    query "SELECT COUNT(*) as count FROM bug_solutions;"
    echo ""
    echo "Decisions:"
    query "SELECT COUNT(*) as count FROM decisions;"
    echo ""
    echo "Knowledge Links:"
    query "SELECT COUNT(*) as count FROM knowledge_links;"
    echo ""
    echo "Tags:"
    query "SELECT COUNT(*) as count FROM tags;"
}

# Main command dispatcher
case "$1" in
    query)
        query "$2"
        ;;
    add-session)
        add_session "$2" "$3" "$4" "$5"
        ;;
    add-snippet)
        add_snippet "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}"
        ;;
    add-bug)
        add_bug_solution "$2" "$3" "$4" "$5" "$6" "$7"
        ;;
    add-decision)
        add_decision "$2" "$3" "$4" "$5"
        ;;
    search)
        search_snippets "$2"
        ;;
    session)
        get_session "$2"
        ;;
    list-sessions)
        list_sessions
        ;;
    list-snippets)
        list_snippets
        ;;
    list-bugs)
        list_bugs
        ;;
    list-decisions)
        list_decisions
        ;;
    stats)
        show_stats
        ;;
    *)
        echo "AI Memory Database Helper"
        echo ""
        echo "Usage: $0 <command> [args...]"
        echo ""
        echo "Commands:"
        echo "  query <sql>              - Execute custom SQL query"
        echo "  add-session <name> <summary> <achievements> <commits>"
        echo "  add-snippet <code> <lang> <framework> <pattern> <purpose> <path> <start> <end> <session_id>"
        echo "  add-bug <error> <type> <solution> <explanation> <cause> <session_id>"
        echo "  add-decision <decision> <rationale> <impact> <session_id>"
        echo "  search <term>            - Search code snippets"
        echo "  session <name>           - Get session summary"
        echo "  list-sessions            - List all sessions"
        echo "  list-snippets             - List all code snippets"
        echo "  list-bugs                - List all bug solutions"
        echo "  list-decisions           - List all decisions"
        echo "  stats                    - Show database statistics"
        echo ""
        echo "Examples:"
        echo "  $0 stats"
        echo "  $0 list-sessions"
        echo "  $0 search 'override'"
        echo "  $0 session 'Session 9'"
        ;;
esac
