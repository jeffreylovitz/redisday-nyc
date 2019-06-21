# Sample queries accompanying slides

### Labels and relationship types (1)
`GRAPH.QUERY worldbuilding "MATCH (a)-[e]->(b) RETURN DISTINCT LABELS(a), TYPE(e), LABELS(b)"`

### Running module commands (2)
`GRAPH.QUERY worldbuilding "MATCH (t:Tag) RETURN t.name LIMIT 3"`

### Filtering results with the WHERE clause (3)
`GRAPH.QUERY worldbuilding "MATCH (a:Answer) WHERE a.score > 500 RETURN a"`

### Variable-length paths (4)
`GRAPH.QUERY worldbuilding "MATCH (u:User)-[*]->(t:Tag) RETURN u.name, t LIMIT 20"`

### Using functions in queries (5)
`GRAPH.QUERY worldbuilding "MATCH (q:Question)-[e]->(t:Tag) RETURN t, SUM(q.score), COUNT(e)"`

### Combining queries with the WITH clause, 1 (6)
`GRAPH.QUERY worldbuilding "MATCH (u:User) WITH AVG(u.reputation) as mean, StDev(u.reputation) AS stdev MATCH (power_user:User) WHERE power_user.reputation > mean + stdev * 3 RETURN power_user"`

### Combining queries with the WITH clause, 2 (7)
`GRAPH.QUERY worldbuilding "MATCH (q1:Question) WITH AVG(q1.score) AS avg_score MATCH (q2:Question) WHERE q2.score > avg_scores RETURN q2"`

### Returning multiple entities (8)
`GRAPH.QUERY worldbuilding "MATCH (a:Answer)-[]->(q:Question)-[:HAS_TAG]->(t:Tag) RETURN q, a, t LIMIT 1"`
