-- vim: set filetype=sql:

PRAGMA page_size=1024;
    PRAGMA cache_size=10;
    CREATE TABLE t1(a TEXT);
    INSERT INTO t1 VALUES ('dog'),('cat');
    SELECT group_concat(a) as pets FROM (SELECT a FROM t1 ORDER BY a);

SELECT group_concat(a) as pets FROM (SELECT a FROM t1 ORDER BY a DESC);
