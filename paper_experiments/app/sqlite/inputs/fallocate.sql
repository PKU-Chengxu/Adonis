-- vim: set filetype=sql:
PRAGMA page_size = 1024;
    PRAGMA auto_vacuum = 1;
    CREATE TABLE t1(a, b);

INSERT INTO t1 VALUES(1, zeroblob(1024*900));
INSERT INTO t1 VALUES(2, zeroblob(1024*900));

DELETE FROM t1 WHERE a = 1;
DELETE FROM t1 WHERE a = 2;

