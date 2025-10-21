    CREATE OR REPLACE PROCEDURE SP_SEL_AI_TBL_CSV (
        p_object_uri IN VARCHAR2,  /* Full URI of the file (e.g., s3://bucket/employees.csv) */
        p_table_name IN VARCHAR2   /* Table name with schema (e.g., ORA26AI.EMPLOYEES) */
    )
    AS
        l_file_name  VARCHAR2(4000);
        l_credential VARCHAR2(4000) := 'c_r_e_d_e_n_t_i_a_l__n_a_m_e';

        TYPE t_col_record IS RECORD (
            column_position NUMBER,
            column_name     VARCHAR2(4000),
            data_type       VARCHAR2(4000)
        );
        TYPE t_col_list IS TABLE OF t_col_record;

        l_cols        t_col_list;  
        l_create_stmt CLOB;        
        l_insert_stmt CLOB;        

    BEGIN
        /* 1) Extract the file name (only the part after the last slash) */
        l_file_name := REGEXP_SUBSTR(p_object_uri, '[^/]+$');
        /* Example: p_object_uri = 's3://bucket/ruta/empleados.csv' Then l_file_name = 'empleados.csv' */

        /* 2) Discover the columns with apex_data_parser */
        SELECT column_position, column_name, data_type
        BULK COLLECT INTO l_cols
        FROM TABLE(
                apex_data_parser.get_columns(
                apex_data_parser.discover(
                    p_content => dbms_cloud.get_object(
                    credential_name => l_credential,
                    object_uri      => p_object_uri
                    ),
                    p_file_name => l_file_name
                )
                )
            )
        ORDER BY column_position;

        /* 3) Drop the table if it already exists */
        BEGIN
            EXECUTE IMMEDIATE 'DROP TABLE ' || p_table_name;
        EXCEPTION
            WHEN OTHERS THEN
                /* ORA-00942 => the table does not exist; ignore */
                IF SQLCODE != -942 THEN
                    RAISE;
                END IF;
        END;

        /* 4) Create the table with the detected columns */
        l_create_stmt := 'CREATE TABLE ' || p_table_name || ' (';

        FOR i IN 1 .. l_cols.COUNT LOOP
            IF i > 1 THEN
                l_create_stmt := l_create_stmt || ', ';
            END IF;
            /* Define NUMBER as NUMBER; all other types as wide VARCHAR2 to avoid ORA-12899 */
            IF INSTR(UPPER(l_cols(i).data_type), 'NUMBER') = 1 THEN
                l_create_stmt := l_create_stmt 
                    || '"' || l_cols(i).column_name || '" NUMBER';
            ELSE
                l_create_stmt := l_create_stmt 
                    || '"' || l_cols(i).column_name || '" VARCHAR2(4000)';
            END IF;
        END LOOP;

        l_create_stmt := l_create_stmt || ')';
        EXECUTE IMMEDIATE l_create_stmt;

        /* 5) Insert parsed data */
        DECLARE
            l_col_list    CLOB := '';
            l_select_cols CLOB := '';
            l_expr        CLOB := '';
        BEGIN
            /* Dynamically build the column lists and selection */
            FOR i IN 1 .. l_cols.COUNT LOOP
                IF i > 1 THEN
                    l_col_list    := l_col_list || ', ';
                    l_select_cols := l_select_cols || ', ';
                END IF;
                /* Column name in the table */
                l_col_list := l_col_list || '"' || l_cols(i).column_name || '"';
                /* Build parsed expression per detected data type */
                l_expr := 'COL' || LPAD(l_cols(i).column_position, 3, '0');

                /* If NUMBER detected, strip thousand separators (comma) and cast safely */
                IF INSTR(UPPER(l_cols(i).data_type), 'NUMBER') = 1 THEN
                    /*
                      Use two-arg REPLACE to remove commas (CHR(44)) and avoid quoting issues.
                      Convert empty strings to NULL using LENGTH check before TO_NUMBER.
                    */
                    l_expr := 'CASE WHEN LENGTH(TRIM(REPLACE(' || l_expr || ', CHR(44)))) = 0 '
                              || 'THEN NULL ELSE TO_NUMBER(TRIM(REPLACE(' || l_expr || ', CHR(44)))) END';
                END IF;

                l_select_cols := l_select_cols || l_expr;
            END LOOP;

            l_insert_stmt :=
                'INSERT INTO ' || p_table_name || ' (' || l_col_list || ') '
                || 'SELECT ' || l_select_cols
                || '  FROM TABLE(apex_data_parser.parse('
                || '       p_content => dbms_cloud.get_object('
                || '         credential_name => ''' || l_credential || ''',' 
                || '         object_uri      => ''' || p_object_uri || ''''
                || '       ),'
                || '       p_file_name         => ''' || l_file_name || ''','
                || '       p_skip_rows         => 1,'
                || '       p_detect_data_types => ''N''' 
                || '  ))';

            EXECUTE IMMEDIATE l_insert_stmt;
            COMMIT;
        EXCEPTION
            WHEN OTHERS THEN
                ROLLBACK;
                RAISE;
        END;
    END;
    /
    --