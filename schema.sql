BEGIN;

CREATE TABLE student (
	pk integer primary key,
	first_name text NOT NULL, 
	last_name text, 
	alias text
);

CREATE TABLE assignment (
	pk integer primary key,
	name text NOT NULL,
	due_date date,
	points integer -- the point total of the assignment
);

CREATE TABLE grade (
	pk integer primary key,
	student_pk integer NOT NULL,
	assignment_pk integer NOT NULL,
	points integer, -- the points awarded to the student

	-- These constraints enforce existence of foreign key and cause the rows in
	-- the grade table to be deleted automatically when their referencing
	-- student or assignment is deleted.
	FOREIGN KEY(student_pk) REFERENCES student(pk) ON DELETE CASCADE,
	FOREIGN KEY(assignment_pk) REFERENCES assignment(pk) ON DELETE CASCADE,
	-- This unique constraint prevents multiple grades from being assigned to
	-- the same student/assignment pair. That wouldn't make any sense.
	UNIQUE (student_pk, assignment_pk)
);

COMMIT;
