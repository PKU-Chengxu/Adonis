-- vim: set filetype=sql:
CREATE TABLE t3(id INTEGER PRIMARY KEY, b NOT NULL);
  CREATE TABLE t4(c, d, e);
  CREATE UNIQUE INDEX i3 ON t3(b);
  CREATE UNIQUE INDEX i4 ON t4(c, d);

SELECT e FROM t3, t4 WHERE b=c ORDER BY b, d;

CREATE TABLE t1(a, b);
  CREATE INDEX i1 ON t1(a);

SELECT * FROM t1 ORDER BY a;

CREATE TABLE t5(a INTEGER PRIMARY KEY,b,c,d,e,f,g);
  CREATE INDEX t5b ON t5(b);
  CREATE INDEX t5c ON t5(c);
  CREATE INDEX t5d ON t5(d);
  CREATE INDEX t5e ON t5(e);
  CREATE INDEX t5f ON t5(f);
  CREATE INDEX t5g ON t5(g);

SELECT a FROM t5 
  WHERE b IS NULL OR c IS NULL OR d IS NULL 
  ORDER BY a;