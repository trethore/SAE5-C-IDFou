-- Entrypoint schema script; keeps execution order explicit for readability
\i T2_BDD/src/sql/schema/0_extensions_drop.sql
\i T2_BDD/src/sql/schema/1_tables.sql
\i T2_BDD/src/sql/schema/2_views.sql
\i T2_BDD/src/sql/schema/3_functions.sql
\i T2_BDD/src/sql/schema/4_triggers.sql
