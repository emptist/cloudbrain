# AI Memory Database Helper - CoffeeScript/JavaScript

## Database Helper Class

```coffeescript
# File: ai_memory_db.coffee

sqlite3 = require('sqlite3').verbose()
path = require('path')

class AIMemoryDB
  constructor: (@dbPath = path.join(__dirname, 'ai_memory.db')) ->
    @db = new sqlite3.Database(@dbPath, (err) ->
      if err
        console.error('Error opening database:', err.message)
      else
        console.log('Connected to AI Memory database')
    )

  # Query helper
  query: (sql, params = []) ->
    new Promise((resolve, reject) =>
      @db.all(sql, params, (err, rows) ->
        if err
          reject(err)
        else
          resolve(rows)
      )
    )

  # Run helper (for INSERT, UPDATE, DELETE)
  run: (sql, params = []) ->
    new Promise((resolve, reject) =>
      @db.run(sql, params, function(err)
        if err
          reject(err)
        else
          resolve(this.lastID)
      )
    )

  # Session operations
  addSession: (sessionName, summary, achievements, totalCommits = 0) ->
    sql = 'INSERT INTO sessions (session_name, summary, achievements, total_commits) VALUES (?, ?, ?, ?)'
    @run(sql, [sessionName, summary, JSON.stringify(achievements), totalCommits])

  getSession: (sessionName) ->
    sql = 'SELECT * FROM sessions WHERE session_name LIKE ?'
    @query(sql, ["%#{sessionName}%"])

  listSessions: ->
    sql = 'SELECT * FROM sessions ORDER BY start_time DESC'
    @query(sql)

  # Code snippet operations
  addSnippet: (code, language, framework, pattern, purpose, filePath, lineStart, lineEnd, sessionId) ->
    sql = 'INSERT INTO code_snippets (code, language, framework, pattern, purpose, file_path, line_start, line_end, session_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    @run(sql, [code, language, framework, pattern, purpose, filePath, lineStart, lineEnd, sessionId])

  searchSnippets: (searchTerm) ->
    sql = 'SELECT * FROM code_snippets WHERE code LIKE ? OR purpose LIKE ? OR pattern LIKE ? ORDER BY created_at DESC'
    @query(sql, ["%#{searchTerm}%", "%#{searchTerm}%", "%#{searchTerm}%"])

  listSnippets: ->
    sql = 'SELECT * FROM code_snippets ORDER BY created_at DESC'
    @query(sql)

  # Bug solution operations
  addBugSolution: (errorMessage, errorType, solutionCode, explanation, rootCause, sessionId) ->
    sql = 'INSERT INTO bug_solutions (error_message, error_type, solution_code, explanation, root_cause, session_id) VALUES (?, ?, ?, ?, ?, ?)'
    @run(sql, [errorMessage, errorType, solutionCode, explanation, rootCause, sessionId])

  getBugSolutions: (errorType) ->
    sql = 'SELECT bs.*, s.session_name FROM bug_solutions bs JOIN sessions s ON bs.session_id = s.id WHERE bs.error_type LIKE ? ORDER BY bs.created_at DESC'
    @query(sql, ["%#{errorType}%"])

  listBugs: ->
    sql = 'SELECT bs.*, s.session_name FROM bug_solutions bs JOIN sessions s ON bs.session_id = s.id ORDER BY bs.created_at DESC'
    @query(sql)

  # Decision operations
  addDecision: (decision, rationale, codeImpact, sessionId) ->
    sql = 'INSERT INTO decisions (decision, rationale, code_impact, session_id) VALUES (?, ?, ?, ?)'
    @run(sql, [decision, rationale, codeImpact, sessionId])

  listDecisions: ->
    sql = 'SELECT d.*, s.session_name FROM decisions d JOIN sessions s ON d.session_id = s.id ORDER BY d.created_at DESC'
    @query(sql)

  # Statistics
  getStats: ->
    queries = [
      'SELECT COUNT(*) as count FROM sessions',
      'SELECT COUNT(*) as count FROM code_snippets',
      'SELECT COUNT(*) as count FROM bug_solutions',
      'SELECT COUNT(*) as count FROM decisions',
      'SELECT COUNT(*) as count FROM knowledge_links',
      'SELECT COUNT(*) as count FROM tags'
    ]
    
    Promise.all(queries.map((q) => @query(q))).then((results) =>
      {
        sessions: results[0][0].count,
        code_snippets: results[1][0].count,
        bug_solutions: results[2][0].count,
        decisions: results[3][0].count,
        knowledge_links: results[4][0].count,
        tags: results[5][0].count
      }
    )

  # Close database
  close: ->
    @db.close((err) ->
      if err
        console.error('Error closing database:', err.message)
      else
        console.log('Database connection closed')
    )

# Export for use
module.exports = AIMemoryDB
```

## Usage Examples

### Initialize and Use
```coffeescript
AIMemoryDB = require('./ai_memory_db.coffee')

db = new AIMemoryDB('/Users/jk/gits/gitee/hqcoffee/temp_ai_tests/ai_memory.db')

# Get statistics
db.getStats().then((stats) ->
  console.log('Database Statistics:', stats)
).catch((err) ->
  console.error('Error:', err)
)

# Search snippets
db.searchSnippets('override').then((snippets) ->
  console.log('Found snippets:', snippets)
).catch((err) ->
  console.error('Error:', err)
)

# List sessions
db.listSessions().then((sessions) ->
  console.log('Sessions:', sessions)
).catch((err) ->
  console.error('Error:', err)
)

# Close database when done
db.close()
```

### Add New Session
```coffeescript
db.addSession(
  'Session 10',
  'Working on new feature',
  ['Added feature X', 'Fixed bug Y'],
  5
).then((sessionId) ->
  console.log('Session added with ID:', sessionId)
).catch((err) ->
  console.error('Error:', err)
)
```

### Add New Code Snippet
```coffeescript
db.addSnippet(
  'class MyClass: BaseClass {\n    override func method() {}\n}',
  'Swift',
  'Foundation',
  'override',
  'Example of override pattern',
  '/path/to/file.swift',
  10,
  12,
  1
).then((snippetId) ->
  console.log('Snippet added with ID:', snippetId)
).catch((err) ->
  console.error('Error:', err)
)
```

### Add New Bug Solution
```coffeescript
db.addBugSolution(
  'method does not override any method from its superclass',
  'override_keyword',
  'Remove override keyword from base class methods',
  'Base classes should not have override keyword',
  'Incorrect use of override keyword in base classes',
  1
).then((bugId) ->
  console.log('Bug solution added with ID:', bugId)
).catch((err) ->
  console.error('Error:', err)
)
```

### Add New Decision
```coffeescript
db.addDecision(
  'Remove override keyword from base class methods',
  'Base classes should not have override keyword',
  'Fixed compilation errors in multiple classes',
  1
).then((decisionId) ->
  console.log('Decision added with ID:', decisionId)
).catch((err) ->
  console.error('Error:', err)
)
```

## Command Line Interface

```coffeescript
# File: ai_memory_cli.coffee

AIMemoryDB = require('./ai_memory_db.coffee')
db = new AIMemoryDB()

command = process.argv[2]
args = process.argv.slice(3)

switch command
  when 'stats'
    db.getStats().then((stats) ->
      console.log('=== AI Memory Database Statistics ===')
      console.log('Sessions:', stats.sessions)
      console.log('Code Snippets:', stats.code_snippets)
      console.log('Bug Solutions:', stats.bug_solutions)
      console.log('Decisions:', stats.decisions)
      console.log('Knowledge Links:', stats.knowledge_links)
      console.log('Tags:', stats.tags)
      db.close()
    ).catch((err) ->
      console.error('Error:', err)
      db.close()
    )

  when 'search'
    searchTerm = args[0]
    db.searchSnippets(searchTerm).then((snippets) ->
      console.log('Found', snippets.length, 'snippets:')
      snippets.forEach((snippet) ->
        console.log("- ID: #{snippet.id}")
        console.log("  Code: #{snippet.code.substring(0, 50)}...")
        console.log("  Purpose: #{snippet.purpose}")
        console.log("  Pattern: #{snippet.pattern}")
        console.log("  File: #{snippet.file_path}")
        console.log("")
      )
      db.close()
    ).catch((err) ->
      console.error('Error:', err)
      db.close()
    )

  when 'list-sessions'
    db.listSessions().then((sessions) ->
      console.log('Sessions:')
      sessions.forEach((session) ->
        console.log("- ID: #{session.id}")
        console.log("  Name: #{session.session_name}")
        console.log("  Summary: #{session.summary}")
        console.log("  Commits: #{session.total_commits}")
        console.log("")
      )
      db.close()
    ).catch((err) ->
      console.error('Error:', err)
      db.close()
    )

  when 'list-snippets'
    db.listSnippets().then((snippets) ->
      console.log('Code Snippets:')
      snippets.forEach((snippet) ->
        console.log("- ID: #{snippet.id}")
        console.log("  Language: #{snippet.language}")
        console.log("  Purpose: #{snippet.purpose}")
        console.log("  Pattern: #{snippet.pattern}")
        console.log("  File: #{snippet.file_path}")
        console.log("")
      )
      db.close()
    ).catch((err) ->
      console.error('Error:', err)
      db.close()
    )

  when 'list-bugs'
    db.listBugs().then((bugs) ->
      console.log('Bug Solutions:')
      bugs.forEach((bug) ->
        console.log("- ID: #{bug.id}")
        console.log("  Error: #{bug.error_message}")
        console.log("  Type: #{bug.error_type}")
        console.log("  Explanation: #{bug.explanation}")
        console.log("")
      )
      db.close()
    ).catch((err) ->
      console.error('Error:', err)
      db.close()
    )

  when 'list-decisions'
    db.listDecisions().then((decisions) ->
      console.log('Decisions:')
      decisions.forEach((decision) ->
        console.log("- ID: #{decision.id}")
        console.log("  Decision: #{decision.decision}")
        console.log("  Rationale: #{decision.rationale}")
        console.log("")
      )
      db.close()
    ).catch((err) ->
      console.error('Error:', err)
      db.close()
    )

  else
    console.log('AI Memory Database CLI')
    console.log('')
    console.log('Usage: coffee ai_memory_cli.coffee <command> [args...]')
    console.log('')
    console.log('Commands:')
    console.log('  stats              - Show database statistics')
    console.log('  search <term>     - Search code snippets')
    console.log('  list-sessions      - List all sessions')
    console.log('  list-snippets       - List all code snippets')
    console.log('  list-bugs          - List all bug solutions')
    console.log('  list-decisions     - List all decisions')
    console.log('')
    console.log('Examples:')
    console.log('  coffee ai_memory_cli.coffee stats')
    console.log('  coffee ai_memory_cli.coffee search "override"')
    console.log('  coffee ai_memory_cli.coffee list-sessions')
```

## Installation

```bash
npm install sqlite3
```

## Running

```bash
# Show statistics
coffee ai_memory_cli.coffee stats

# Search snippets
coffee ai_memory_cli.coffee search "override"

# List sessions
coffee ai_memory_cli.coffee list-sessions

# List snippets
coffee ai_memory_cli.coffee list-snippets

# List bugs
coffee ai_memory_cli.coffee list-bugs

# List decisions
coffee ai_memory_cli.coffee list-decisions
```
