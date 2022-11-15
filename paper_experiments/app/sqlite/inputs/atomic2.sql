-- vim: set filetype=sql:
CREATE TABLE t1(x, y);
  CREATE INDEX i1x ON t1(x);
  CREATE INDEX i2x ON t1(y);

WITH s(i) AS ( SELECT 1 UNION ALL SELECT i+1 FROM s WHERE i<100 )
  INSERT INTO t1 SELECT randomblob(400), randomblob(400) FROM s;
SELECT count(*) FROM t1;
