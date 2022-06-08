grammar = {
    'p3' : [
            ('p_module', 
                """
                module : statements 
                        | NEWLINE
                """
            ),
            ('p_statements', 
                """
                statements : statement statements
                        | statement
                """
            ),
            ('p_statement', 
                """
                statement : stmt_list NEWLINE
                        | compound_stmt
                """
            ),
            ('p_stmt_list', 
                """
                stmt_list : simple_stmt
                """
            ),
            ('p_simple_stmt', 
                """
                simple_stmt : expression_stmt
                        | assignment_stmt
                        | return_stmt
                """
            ),
            ('p_compound_stmt', 
                """
                compound_stmt : if_stmt
                            | while_stmt
                            | funcdef
                """
            ),
            ('p_expression_stmt', 
                """
                expression_stmt : expression
                """
            ),
            ('p_assignment_stmt', 
                """
                assignment_stmt : target_list ASSIGN expression
                """
            ),
            ('p_target_list', 
                """
                target_list : target
                """
            ),
            ('p_target', 
                """
                target : identifier
                        | LPAREN target_list RPAREN
                        | LBRACKET target_list RBRACKET
                        | subscription
                """
            ),
            ('p_atom', 
                """
                atom : identifier
                        | literal
                        | enclosure
                """
            ),
            ('p_literal', 
                """
                literal : integer
                        | TRUE
                        | FALSE
                """
            ),
            ('p_enclosure', 
                """
                enclosure : parenth_form
                        | list_display
                        | dict_display
                """
            ),
            ('p_parenth_form', 
                """
                parenth_form : LPAREN expression RPAREN
                """
            ),
            ('p_list_display', 
                """
                list_display : LBRACKET expression_list RBRACKET
                """
            ),
            ('p_dict_display', 
                """
                dict_display : LBRACE key_datum_list RBRACE
                """
            ),
            ('p_key_datum_list', 
                """
                key_datum_list : key_datum_list COMMA key_datum
                        | key_datum
                        | empty
                """
            ),
            ('p_key_datum', 
                """
                key_datum : expression COLON expression
                """
            ),
            ('p_subscription', 
                """
                subscription : primary LBRACKET expression_list RBRACKET
                """
            ),
            ('p_primary', 
                """
                primary : atom
                        | call
                        | subscription
                """
            ),
            ('p_call', 
                """
                call : primary LPAREN argument_list RPAREN
                """
            ),
            ('p_argument_list', 
                """
                argument_list : positional_arguments
                """
            ),
            ('p_positional_arguments', 
                """
                positional_arguments : positional_arguments COMMA positional_item
                                | positional_item
                                | empty
                """
            ),
            ('p_positional_item', 
                """
                positional_item : expression
                """
            ),
            ('p_expression_list', 
                """
                expression_list : expression_list COMMA expression
                            | expression
                            | empty
                """
            ),
            ('p_expression', 
                """
                expression : conditional_expression
                        | lambda_expr
                """
            ),
            ('p_conditional_expression', 
                """
                conditional_expression : or_test
                                    | or_test IF or_test ELSE conditional_expression
                """
            ),
            ('p_lambda_expr', 
                """
                lambda_expr : LAMBDA parameter_list COLON expression
                """
            ),
            ('p_parameter_list', 
                """
                parameter_list : parameter_list COMMA parameter
                        | parameter
                        | empty
                """
            ),
            ('p_parameter', 
                """
                parameter : identifier
                """
            ),
            ('p_or_test', 
                """
                or_test : and_test
                        | or_test OR and_test
                """
            ),
            ('p_and_test', 
                """
                and_test : not_test
                    | and_test AND not_test
                """
            ),
            ('p_not_test', 
                """
                not_test : NOT not_test
                        | comparison
                """
            ),
            ('p_comparison', 
                """
                comparison : comparison comp_operator a_expr
                        | a_expr
                """
            ),
            ('p_comp_operator', 
                """
                comp_operator : EQ
                            | NE
                            | IS
                """
            ),
            ('p_a_expr', 
                """
                a_expr : a_expr PLUS u_expr
                        | u_expr
                """),
            ('p_u_expr', 
                """
                u_expr : primary
                        | MINUS u_expr %prec UMINUS
                """
            ),
            ('p_if_stmt', 
                """
                if_stmt : IF expression COLON suite
                        | IF expression COLON suite ELSE COLON suite
                """
            ),
            ('p_while_stmt', 
                """
                while_stmt : WHILE expression COLON suite
                """
            ),
            ('p_funcdef', 
                """
                funcdef : DEF funcname LPAREN parameter_list RPAREN COLON suite
                """
            ),
            ('p_funcname', 
                """
                funcname : identifier
                """
            ),
            ('p_return_stmt', 
                """
                return_stmt : RETURN expression_list
                """
            ),
            ('p_suite', 
                """
                suite : stmt_list NEWLINE
                    | NEWLINE INDENT statements DEDENT
                """
            ),
            ('p_empty', 
                """
                empty : 
                """
            )
        ],

    'p2' : [
            ('p_module', 
                """
                module : statements 
                        | NEWLINE
                """
            ),
            ('p_statements', 
                """
                statements : statement statements
                        | statement
                """
            ),
            ('p_statement', 
                """
                statement : stmt_list NEWLINE
                        | compound_stmt
                """
            ),
            ('p_stmt_list', 
                """
                stmt_list : simple_stmt
                """
            ),
            ('p_simple_stmt', 
                """
                simple_stmt : expression_stmt
                        | assignment_stmt
                        | return_stmt
                """
            ),
            ('p_compound_stmt', 
                """
                compound_stmt : funcdef
                """
            ),
            ('p_expression_stmt', 
                """
                expression_stmt : expression
                """
            ),
            ('p_assignment_stmt', 
                """
                assignment_stmt : target_list ASSIGN expression
                """
            ),
            ('p_target_list', 
                """
                target_list : target
                """
            ),
            ('p_target', 
                """
                target : identifier
                        | LPAREN target_list RPAREN
                        | LBRACKET target_list RBRACKET
                        | subscription
                """
            ),
            ('p_atom', 
                """
                atom : identifier
                        | literal
                        | enclosure
                """
            ),
            ('p_literal', 
                """
                literal : integer
                        | TRUE
                        | FALSE
                """
            ),
            ('p_enclosure', 
                """
                enclosure : parenth_form
                        | list_display
                        | dict_display
                """
            ),
            ('p_parenth_form', 
                """
                parenth_form : LPAREN expression RPAREN
                """
            ),
            ('p_list_display', 
                """
                list_display : LBRACKET expression_list RBRACKET
                """
            ),
            ('p_dict_display', 
                """
                dict_display : LBRACE key_datum_list RBRACE
                """
            ),
            ('p_key_datum_list', 
                """
                key_datum_list : key_datum_list COMMA key_datum
                        | key_datum
                        | empty
                """
            ),
            ('p_key_datum', 
                """
                key_datum : expression COLON expression
                """
            ),
            ('p_subscription', 
                """
                subscription : primary LBRACKET expression_list RBRACKET
                """
            ),
            ('p_primary', 
                """
                primary : atom
                        | call
                        | subscription
                """
            ),
            ('p_call', 
                """
                call : primary LPAREN argument_list RPAREN
                """
            ),
            ('p_argument_list', 
                """
                argument_list : positional_arguments
                """
            ),
            ('p_positional_arguments', 
                """
                positional_arguments : positional_arguments COMMA positional_item
                                | positional_item
                                | empty
                """
            ),
            ('p_positional_item', 
                """
                positional_item : expression
                """
            ),
            ('p_expression_list', 
                """
                expression_list : expression_list COMMA expression
                            | expression
                            | empty
                """
            ),
            ('p_expression', 
                """
                expression : conditional_expression
                        | lambda_expr
                """
            ),
            ('p_conditional_expression', 
                """
                conditional_expression : or_test
                                    | or_test IF or_test ELSE conditional_expression
                """
            ),
            ('p_lambda_expr', 
                """
                lambda_expr : LAMBDA parameter_list COLON expression
                """
            ),
            ('p_parameter_list', 
                """
                parameter_list : parameter_list COMMA parameter
                        | parameter
                        | empty
                """
            ),
            ('p_parameter', 
                """
                parameter : identifier
                """
            ),
            ('p_or_test', 
                """
                or_test : and_test
                        | or_test OR and_test
                """
            ),
            ('p_and_test', 
                """
                and_test : not_test
                    | and_test AND not_test
                """
            ),
            ('p_not_test', 
                """
                not_test : NOT not_test
                        | comparison
                """
            ),
            ('p_comparison', 
                """
                comparison : comparison comp_operator a_expr
                        | a_expr
                """
            ),
            ('p_comp_operator', 
                """
                comp_operator : EQ
                            | NE
                            | IS
                """
            ),
            ('p_a_expr', 
                """
                a_expr : a_expr PLUS u_expr
                        | u_expr
                """),
            ('p_u_expr', 
                """
                u_expr : primary
                        | MINUS u_expr %prec UMINUS
                """
            ),
            ('p_funcdef', 
                """
                funcdef : DEF funcname LPAREN parameter_list RPAREN COLON suite
                """
            ),
            ('p_funcname', 
                """
                funcname : identifier
                """
            ),
            ('p_return_stmt', 
                """
                return_stmt : RETURN expression_list
                """
            ),
            ('p_suite', 
                """
                suite : stmt_list NEWLINE
                    | NEWLINE INDENT statements DEDENT
                """
            ),
            ('p_empty', 
                """
                empty : 
                """
            )
        ],

    'p1' : [
            ('p_module', 
                """
                module : statements 
                        | NEWLINE
                """
            ),
            ('p_statements', 
                """
                statements : statement statements
                        | statement
                """
            ),
            ('p_statement', 
                """
                statement : stmt_list NEWLINE
                """
            ),
            ('p_stmt_list', 
                """
                stmt_list : simple_stmt
                """
            ),
            ('p_simple_stmt', 
                """
                simple_stmt : expression_stmt
                        | assignment_stmt
                """
            ),
            ('p_expression_stmt', 
                """
                expression_stmt : expression
                """
            ),
            ('p_assignment_stmt', 
                """
                assignment_stmt : target_list ASSIGN expression
                """
            ),
            ('p_target_list', 
                """
                target_list : target
                """
            ),
            ('p_target', 
                """
                target : identifier
                        | LPAREN target_list RPAREN
                        | LBRACKET target_list RBRACKET
                        | subscription
                """
            ),
            ('p_atom', 
                """
                atom : identifier
                        | literal
                        | enclosure
                """
            ),
            ('p_literal', 
                """
                literal : integer
                        | TRUE
                        | FALSE
                """
            ),
            ('p_enclosure', 
                """
                enclosure : parenth_form
                        | list_display
                        | dict_display
                """
            ),
            ('p_parenth_form', 
                """
                parenth_form : LPAREN expression RPAREN
                """
            ),
            ('p_list_display', 
                """
                list_display : LBRACKET expression_list RBRACKET
                """
            ),
            ('p_dict_display', 
                """
                dict_display : LBRACE key_datum_list RBRACE
                """
            ),
            ('p_key_datum_list', 
                """
                key_datum_list : key_datum_list COMMA key_datum
                        | key_datum
                        | empty
                """
            ),
            ('p_key_datum', 
                """
                key_datum : expression COLON expression
                """
            ),
            ('p_subscription', 
                """
                subscription : primary LBRACKET expression_list RBRACKET
                """
            ),
            ('p_primary', 
                """
                primary : atom
                        | call
                        | subscription
                """
            ),
            ('p_call', 
                """
                call : primary LPAREN argument_list RPAREN
                """
            ),
            ('p_argument_list', 
                """
                argument_list : positional_arguments
                """
            ),
            ('p_positional_arguments', 
                """
                positional_arguments : positional_arguments COMMA positional_item
                                | positional_item
                                | empty
                """
            ),
            ('p_positional_item', 
                """
                positional_item : expression
                """
            ),
            ('p_expression_list', 
                """
                expression_list : expression_list COMMA expression
                            | expression
                            | empty
                """
            ),
            ('p_expression', 
                """
                expression : conditional_expression
                """
            ),
            ('p_conditional_expression', 
                """
                conditional_expression : or_test
                                    | or_test IF or_test ELSE conditional_expression
                """
            ),
            ('p_or_test', 
                """
                or_test : and_test
                        | or_test OR and_test
                """
            ),
            ('p_and_test', 
                """
                and_test : not_test
                    | and_test AND not_test
                """
            ),
            ('p_not_test', 
                """
                not_test : NOT not_test
                        | comparison
                """
            ),
            ('p_comparison', 
                """
                comparison : comparison comp_operator a_expr
                        | a_expr
                """
            ),
            ('p_comp_operator', 
                """
                comp_operator : EQ
                            | NE
                            | IS
                """
            ),
            ('p_a_expr', 
                """
                a_expr : a_expr PLUS u_expr
                        | u_expr
                """),
            ('p_u_expr', 
                """
                u_expr : primary
                        | MINUS u_expr %prec UMINUS
                """
            ),
            ('p_empty', 
                """
                empty : 
                """
            )
        ],

    'p0' : [
            ('p_module', 
                """
                module : statements 
                        | NEWLINE
                """
            ),
            ('p_statements', 
                """
                statements : statement statements
                        | statement
                """
            ),
            ('p_statement', 
                """
                statement : stmt_list NEWLINE
                """
            ),
            ('p_stmt_list', 
                """
                stmt_list : simple_stmt
                """
            ),
            ('p_simple_stmt', 
                """
                simple_stmt : expression_stmt
                        | assignment_stmt
                """
            ),
            ('p_expression_stmt', 
                """
                expression_stmt : expression
                """
            ),
            ('p_assignment_stmt', 
                """
                assignment_stmt : target_list ASSIGN expression
                """
            ),
            ('p_target_list', 
                """
                target_list : target
                """
            ),
            ('p_target', 
                """
                target : identifier
                        | LPAREN target_list RPAREN
                        | LBRACKET target_list RBRACKET
                """
            ),
            ('p_atom', 
                """
                atom : identifier
                        | literal
                        | enclosure
                """
            ),
            ('p_literal', 
                """
                literal : integer
                """
            ),
            ('p_enclosure', 
                """
                enclosure : parenth_form
                """
            ),
            ('p_parenth_form', 
                """
                parenth_form : LPAREN expression RPAREN
                """
            ),
            ('p_primary', 
                """
                primary : atom
                        | call
                """
            ),
            ('p_call', 
                """
                call : primary LPAREN argument_list RPAREN
                """
            ),
            ('p_argument_list', 
                """
                argument_list : positional_arguments
                """
            ),
            ('p_positional_arguments', 
                """
                positional_arguments : positional_arguments COMMA positional_item
                                | positional_item
                                | empty
                """
            ),
            ('p_positional_item', 
                """
                positional_item : expression
                """
            ),
            ('p_expression', 
                """
                expression : a_expr
                """
            ),
            ('p_a_expr', 
                """
                a_expr : a_expr PLUS u_expr
                        | u_expr
                """),
            ('p_u_expr', 
                """
                u_expr : primary
                        | MINUS u_expr %prec UMINUS
                """
            ),
            ('p_empty', 
                """
                empty : 
                """
            )
        ],

    
}