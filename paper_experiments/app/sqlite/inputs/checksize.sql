-- vim: set filetype=sql:
CREATE TABLE t1(a, b);
    INSERT INTO t1 VALUES(1, 2);

PRAGMA wal_checkpoint;
