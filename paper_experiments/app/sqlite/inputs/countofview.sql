-- vim: set filetype=sql:
CREATE TABLE t2(c);
  CREATE TABLE t3(f);

  INSERT INTO t2 VALUES(1), (2);
  INSERT INTO t3 VALUES(3);

select c from t2 union all select f from t3 limit 1 offset 1;

select count(*) from (
    select c from t2 union all select f from t3 limit 1 offset 1
  );

select count(*) from (
    select c from t2 union all select f from t3
  );

CREATE TABLE t1(x);
  INSERT INTO t1 VALUES(1),(99),('abc');
  CREATE VIEW v1(x,y) AS SELECT x,1 FROM t1 UNION ALL SELECT x,2 FROM t1;
  SELECT count(*) FROM v1 WHERE x<>1;

SELECT count(*) FROM v1 GROUP BY y;
