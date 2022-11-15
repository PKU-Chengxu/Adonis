-- vim: set filetype=sql:

CREATE TABLE one(a int PRIMARY KEY, b text);
    INSERT INTO one VALUES(1,'one');
    INSERT INTO one VALUES(2,'two');
    INSERT INTO one VALUES(3,'three');
    SELECT b FROM one ORDER BY a;

CREATE TABLE two(a int PRIMARY KEY, b text);
    INSERT INTO two VALUES(1,'I');
    INSERT INTO two VALUES(5,'V');
    INSERT INTO two VALUES(10,'X');
    SELECT b FROM two ORDER BY a;

SELECT b FROM one ORDER BY a;
SELECT b FROM two ORDER BY a;
