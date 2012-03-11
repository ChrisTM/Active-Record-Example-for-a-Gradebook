BEGIN;

insert into student (first_name, last_name, alias) values ( "Susanne", "Richardson", "milgram");
insert into student (first_name, last_name, alias) values ( "Jamie", "Jacobs", "rooster");
insert into student (first_name, last_name, alias) values ( "Henry", "Fowler", "31337");
insert into student (first_name, last_name, alias) values ( "Ghostly", "McQuin", "Spectre");

insert into assignment (name, due_date, points) values ( "HW 1", date('2010-09-13'), 10);
insert into assignment (name, due_date, points) values ( "HW 2", date('2010-10-15'), 10);
insert into assignment (name, due_date, points) values ( "HW 3", date('2010-10-25'), 20);

insert into grade (student_pk, assignment_pk, points) values (1, 1, 8);
insert into grade (student_pk, assignment_pk, points) values (1, 2, 9);
insert into grade (student_pk, assignment_pk, points) values (1, 3, 20);
insert into grade (student_pk, assignment_pk, points) values (2, 1, 8);
insert into grade (student_pk, assignment_pk, points) values (2, 2, 7);
insert into grade (student_pk, assignment_pk, points) values (2, 3, 19);
-- Henry is missing a grade.
insert into grade (student_pk, assignment_pk, points) values (3, 1, 10);
insert into grade (student_pk, assignment_pk, points) values (3, 3, 19);
-- Ghostly has no grades.

COMMIT;
