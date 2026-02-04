-- Fix FTS table and triggers for ai_thought_history
DROP TABLE IF EXISTS ai_thought_history_fts;

CREATE VIRTUAL TABLE IF NOT EXISTS ai_thought_history_fts USING fts5(content='ai_thought_history', content_rowid='id');

CREATE TRIGGER IF NOT EXISTS ai_thought_history_fts_insert
AFTER INSERT ON ai_thought_history
BEGIN
    INSERT INTO ai_thought_history_fts(rowid, thought_content)
    VALUES(new.id, new.thought_content);
END;

CREATE TRIGGER IF NOT EXISTS ai_thought_history_fts_update
AFTER UPDATE OF thought_content ON ai_thought_history
BEGIN
    UPDATE ai_thought_history_fts
    SET thought_content = new.thought_content
    WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS ai_thought_history_fts_delete
AFTER DELETE ON ai_thought_history
BEGIN
    DELETE FROM ai_thought_history_fts
    WHERE rowid = old.id;
END;