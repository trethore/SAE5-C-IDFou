CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE preference_vector (
    account_id UUID,
    embedding VECTOR(71),
    PRIMARY KEY (account_id),
    FOREIGN KEY (account_id) REFERENCES "user"(account_id)
);
