-- Opted to not use migrator like liquibase since this is a toy project

CREATE TABLE "public"."question" (
  "id"       SERIAL,
  "question" TEXT    NOT NULL, -- Immutable, to be enforced by app
  "options"  JSONB   NOT NULL, -- Immutable, to be enforced by app
  "archived" BOOLEAN NOT NULL DEFAULT 'false', -- Determines whether question is eligible for user-display
  PRIMARY KEY ("id")
);

-- Keeps lookups for undeleted questions fast
CREATE INDEX "question_archived_idx"
  ON "public"."question" ("archived");

INSERT INTO "public"."question" ("id", "question", "options")
VALUES (1, 'Which animals race at the Kentucky Derby?', '[
  "Horses",
  "Weiner Dogs",
  "Baby Pandas"
]');

CREATE TABLE "public"."vote" (
  "id"          SERIAL,
  "question_id" INTEGER NOT NULL,
  "option_idx"  INTEGER NOT NULL, -- Constraint that option_idx must be between 0 and size of options list enforced in app
  "votes"       INTEGER NOT NULL DEFAULT '0',
  PRIMARY KEY ("id"),
  FOREIGN KEY ("question_id") REFERENCES "public"."question" ("id")
);

-- Keeps votes by question lookups fast while maintaining uniqueness
CREATE UNIQUE INDEX "vote_question_option_uq_idx"
  ON "public"."vote" ("question_id", "option_idx");

