// Set text property equal to id property for all nodes that are not Documents
MATCH (n)
WHERE NOT n:Document AND n.id IS NOT NULL
SET n.text = n.id
RETURN count(n) AS nodes_updated

// Add :NonDocument label to all nodes that don't have the Document label
MATCH (n)
WHERE NOT n:Document
SET n:NonDocument
RETURN count(n) AS nodes_labeled

// Add :Entity label to all nodes in the database
MATCH (n)
SET n:Entity
RETURN count(n) AS nodes_labeled

CREATE FULLTEXT INDEX entity_text_index IF NOT EXISTS
FOR (n:Entity)
ON EACH [n.text]

CALL db.index.fulltext.queryNodes("entity_text_index", "john")
YIELD node, score
RETURN node.id, node.text, score
